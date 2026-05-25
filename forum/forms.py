from django import forms
from .models import Question, Answer


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['title', 'body', 'module', 'process']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. How do I create a Purchase Requisition in SAP MM?'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 5,
                'placeholder': 'Describe your question in detail...'
            }),
            'module': forms.Select(attrs={'class': 'form-select'}),
            'process': forms.Select(attrs={'class': 'form-select'}),
        }


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 4,
                'placeholder': 'Write your answer here...'
            })
        }
        labels = {'body': 'Your Answer'}