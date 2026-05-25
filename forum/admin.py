from django.contrib import admin
from .models import Question, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['answered_by', 'answered_at', 'upvotes']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'asked_by', 'module', 'status', 'is_pinned', 'answer_count', 'asked_at']
    list_filter = ['status', 'module', 'is_pinned']
    search_fields = ['title', 'body']
    inlines = [AnswerInline]
    list_editable = ['status', 'is_pinned']

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['question', 'answered_by', 'is_accepted', 'upvotes', 'answered_at']
    list_filter = ['is_accepted']