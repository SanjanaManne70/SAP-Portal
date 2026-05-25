from django import forms
from .models import Process, Document, FAQ, Announcement, SAPModule


class ProcessForm(forms.ModelForm):
    class Meta:
        model = Process
        fields = ['module', 'title', 'description', 't_code', 'difficulty', 'steps', 'prerequisites']
        widgets = {
            'module': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            't_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. ME51N'}),
            'difficulty': forms.Select(attrs={'class': 'form-select'}),
            'steps': forms.Textarea(attrs={'class': 'form-control', 'rows': 8,
                                           'placeholder': '1. Login to SAP\n2. Navigate to...\n3. Fill in fields...'}),
            'prerequisites': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class DocumentUploadForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['module', 'process', 'title', 'description', 'doc_type', 'file']
        widgets = {
            'module': forms.Select(attrs={'class': 'form-select'}),
            'process': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'doc_type': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx,.xlsx,.pptx'}),
        }


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ['module', 'process', 'question', 'answer']
        widgets = {
            'module': forms.Select(attrs={'class': 'form-select'}),
            'process': forms.Select(attrs={'class': 'form-select'}),
            'question': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type the question...'}),
            'answer': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }