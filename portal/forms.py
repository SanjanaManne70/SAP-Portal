from django import forms
from knowledge.models import SAPModule, Document


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class BulkCSVUploadForm(forms.Form):
    UPLOAD_TYPE_CHOICES = [
        ('process', 'SAP Processes'),
        ('tcode', 'T-Code Directory'),
    ]

    upload_type = forms.ChoiceField(
        choices=UPLOAD_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Import Type',
    )

    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        label='CSV File',
        help_text=(
            'Process CSV columns: title, module_code, description, '
            't_code, difficulty, steps<br>'
            'T-Code CSV columns: t_code, description, '
            'module_code, menu_path, notes'
        ),
    )


class BulkDocumentUploadForm(forms.Form):
    module = forms.ModelChoiceField(
        queryset=SAPModule.objects.filter(is_active=True),
        required=False,
        empty_label='— All Modules —',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
    )

    doc_type = forms.ChoiceField(
        choices=Document.DOC_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
    )

    documents = forms.FileField(
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.xlsx,.pptx,.txt',
        }),
        label='Select Files (multiple allowed)',
    )