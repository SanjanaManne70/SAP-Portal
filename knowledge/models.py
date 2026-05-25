from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager
from accounts.models import CustomUser


class SAPModule(models.Model):
    """Top-level SAP modules: MM, FI, HR, SD, PM, QM etc."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text='Bootstrap icon class, e.g. bi-box-seam')
    color = models.CharField(max_length=20, default='primary', help_text='Bootstrap color: primary, success, warning...')
    slug = models.SlugField(unique=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'SAP Module'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.code)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.code} - {self.name}"

    def process_count(self):
        return self.processes.filter(is_active=True).count()


class Process(models.Model):
    """Business processes within each SAP module."""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    module = models.ForeignKey(SAPModule, on_delete=models.CASCADE, related_name='processes')
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    t_code = models.CharField(max_length=20, blank=True, verbose_name='T-Code',
                               help_text='Primary SAP Transaction Code')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    steps = models.TextField(blank=True, help_text='Step-by-step instructions (use numbered list)')
    prerequisites = models.TextField(blank=True)
    related_processes = models.ManyToManyField('self', blank=True, symmetrical=True)
    tags = TaggableManager(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_processes')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Processes'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            n = 1
            while Process.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.module.code}] {self.title}"


class Workflow(models.Model):
    """Workflow steps/diagrams for a process."""
    process = models.ForeignKey(Process, on_delete=models.CASCADE, related_name='workflows')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    step_number = models.PositiveIntegerField(default=1)
    t_code = models.CharField(max_length=20, blank=True)
    responsible_role = models.CharField(max_length=100, blank=True)
    input_required = models.TextField(blank=True)
    output_produced = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['step_number']

    def __str__(self):
        return f"Step {self.step_number}: {self.title} ({self.process.title})"


class Document(models.Model):
    """PDFs, guides, manuals uploaded by admins/trainers."""
    DOC_TYPE_CHOICES = [
        ('pdf', 'PDF Guide'),
        ('manual', 'User Manual'),
        ('sop', 'Standard Operating Procedure'),
        ('policy', 'Policy Document'),
        ('template', 'Template'),
        ('other', 'Other'),
    ]

    module = models.ForeignKey(SAPModule, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    process = models.ForeignKey(Process, on_delete=models.SET_NULL, null=True, blank=True, related_name='documents')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    doc_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES, default='pdf')
    file = models.FileField(upload_to='documents/%Y/%m/')
    file_size = models.PositiveIntegerField(default=0, help_text='In KB')
    uploaded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='uploaded_docs')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = TaggableManager(blank=True)
    download_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.title

    def file_extension(self):
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return ''


class FAQ(models.Model):
    """Frequently Asked Questions per module or process."""
    module = models.ForeignKey(SAPModule, on_delete=models.CASCADE, related_name='faqs', null=True, blank=True)
    process = models.ForeignKey(Process, on_delete=models.SET_NULL, null=True, blank=True, related_name='faqs')
    question = models.CharField(max_length=400)
    answer = models.TextField()
    tags = TaggableManager(blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_faqs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    helpful_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-helpful_count', 'question']
        verbose_name = 'FAQ'

    def __str__(self):
        return self.question[:80]


class TCodeDirectory(models.Model):
    """Searchable SAP T-Code directory."""
    t_code = models.CharField(max_length=20, unique=True, verbose_name='T-Code')
    description = models.CharField(max_length=300)
    module = models.ForeignKey(SAPModule, on_delete=models.SET_NULL, null=True, related_name='tcodes')
    process = models.ForeignKey(Process, on_delete=models.SET_NULL, null=True, blank=True, related_name='tcodes')
    menu_path = models.CharField(max_length=400, blank=True, help_text='SAP menu path')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['t_code']
        verbose_name = 'T-Code Directory'
        verbose_name_plural = 'T-Code Directory'

    def __str__(self):
        return f"{self.t_code} - {self.description}"


class Announcement(models.Model):
    """Portal announcements shown on dashboard."""
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
class SecurityScan(models.Model):

    RISK_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    issue_name = models.CharField(max_length=200)

    risk_level = models.CharField(
        max_length=20,
        choices=RISK_CHOICES
    )

    affected_url = models.CharField(max_length=300)

    status = models.CharField(
        max_length=20,
        default='Open'
    )

    detected_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.issue_name} ({self.risk_level})"