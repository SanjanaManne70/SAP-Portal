from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser, Department


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Employee ID or Username',
            'autofocus': True,
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'Password',
        })
    )


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    employee_id = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Employee ID'})
    )
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label='Select Department',
    )

    # "Admin / Trainer" card submits value 'admin'
    # The two selectable roles from the UI are: employee | admin
    role = forms.ChoiceField(
        choices=[('employee', 'Employee'), ('admin', 'Admin')],
        initial='employee',
        widget=forms.HiddenInput(),
    )
    admin_code = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter the access code provided by your administrator',
            'autocomplete': 'off',
        })
    )

    class Meta:
        model  = CustomUser
        fields = [
            'username', 'first_name', 'last_name', 'email',
            'employee_id', 'department', 'role', 'password1', 'password2',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ['username', 'password1', 'password2']:
            self.fields[field_name].widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned    = super().clean()
        role       = cleaned.get('role', 'employee')
        admin_code = (cleaned.get('admin_code') or '').strip()

        if role == 'admin':
            from django.conf import settings as s
            expected = getattr(s, 'ADMIN_REGISTRATION_CODE', 'BHEL@Admin2025')
            if not admin_code:
                self.add_error('admin_code',
                    'An access code is required to register as Admin.')
            elif admin_code != expected:
                self.add_error('admin_code',
                    'Invalid access code. Please contact your system administrator.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        # 'admin' role from the form maps to 'admin' role in the model.
        # Superusers/Django-admin can later promote someone to 'trainer' if needed.
        user.role = self.cleaned_data.get('role', 'employee')
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'department', 'bio', 'profile_picture',
        ]
        widgets = {
            'first_name':      forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':       forms.TextInput(attrs={'class': 'form-control'}),
            'email':           forms.EmailInput(attrs={'class': 'form-control'}),
            'phone':           forms.TextInput(attrs={'class': 'form-control'}),
            'department':      forms.Select(attrs={'class': 'form-select'}),
            'bio':             forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }


class DepartmentSwitchForm(forms.Form):
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select form-select-lg'}),
        empty_label='— Select New Department —',
    )
    reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class':       'form-control',
            'rows':        2,
            'placeholder': 'Reason for switching department (optional)',
        })
    )