from django.db import models
from accounts.models import CustomUser
from knowledge.models import SAPModule, Process


class Question(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('answered', 'Answered'),
        ('closed', 'Closed'),
    ]

    title = models.CharField(max_length=400)
    body = models.TextField()
    module = models.ForeignKey(SAPModule, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    process = models.ForeignKey(Process, on_delete=models.SET_NULL, null=True, blank=True, related_name='questions')
    asked_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='questions')
    asked_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    view_count = models.PositiveIntegerField(default=0)
    is_pinned = models.BooleanField(default=False)

    class Meta:
        ordering = ['-is_pinned', '-asked_at']

    def __str__(self):
        return self.title[:100]

    def answer_count(self):
        return self.answers.count()

    def accepted_answer(self):
        return self.answers.filter(is_accepted=True).first()


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    body = models.TextField()
    answered_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='answers')
    answered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_accepted = models.BooleanField(default=False)
    upvotes = models.PositiveIntegerField(default=0)
    upvoted_by = models.ManyToManyField(CustomUser, blank=True, related_name='upvoted_answers')

    class Meta:
        ordering = ['-is_accepted', '-upvotes', 'answered_at']

    def __str__(self):
        return f"Answer to: {self.question.title[:60]}"