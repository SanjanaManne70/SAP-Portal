from django.contrib.auth.models import AbstractUser
from django.db import models


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True)
    # Modules this dept has access to; empty = access to ALL modules
    allowed_modules = models.ManyToManyField(
        'knowledge.SAPModule',
        blank=True,
        related_name='departments',
        help_text='Leave empty to allow access to all SAP modules.',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.code})"


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin',    'Admin'),
        ('trainer',  'Trainer / Department Head'),
        ('employee', 'Employee'),
        ('intern',   'Trainee / Intern'),
    ]

    role            = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    department      = models.ForeignKey(
                          Department, on_delete=models.SET_NULL,
                          null=True, blank=True, related_name='employees')
    employee_id     = models.CharField(max_length=20, blank=True, unique=True, null=True)
    phone           = models.CharField(max_length=15, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    bio             = models.TextField(blank=True)
    joined_at       = models.DateField(null=True, blank=True)
    is_verified     = models.BooleanField(default=False)

    class Meta:
        verbose_name        = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.get_full_name() or self.username} [{self.get_role_display()}]"

    @property
    def is_admin_or_trainer(self):
        return self.role in ('admin', 'trainer') or self.is_superuser

    @property
    def display_name(self):
        return self.get_full_name() or self.username

    @property
    def initials(self):
        parts = self.display_name.split()
        return ''.join(p[0].upper() for p in parts[:2]) if parts else 'U'


class DepartmentChangeLog(models.Model):
    """Audit trail for every department switch a user performs."""
    user            = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                                        related_name='dept_changes')
    from_department = models.ForeignKey(Department, on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='users_left')
    to_department   = models.ForeignKey(Department, on_delete=models.SET_NULL,
                                        null=True, blank=True, related_name='users_joined')
    reason          = models.TextField(blank=True)
    changed_at      = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering        = ['-changed_at']
        verbose_name    = 'Department Change Log'

    def __str__(self):
        return (
            f"{self.user.display_name}: "
            f"{self.from_department} → {self.to_department} "
            f"({self.changed_at.date()})"
        )