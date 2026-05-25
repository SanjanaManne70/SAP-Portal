from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import PasswordChangeForm

from .forms import LoginForm, RegisterForm, ProfileUpdateForm, DepartmentSwitchForm
from .models import CustomUser, DepartmentChangeLog


# ── helpers ─────────────────────────────────────────────────────────────────

def _role_redirect(user):
    """Return the redirect target URL name for a given user's role."""
    if user.is_admin_or_trainer:
        return 'portal:admin_dashboard'
    return 'portal:user_dashboard'


# ── auth views ───────────────────────────────────────────────────────────────

from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import LoginForm
from .models import CustomUser


def login_view(request):
    if request.user.is_authenticated:
        return redirect(_role_redirect(request.user))

    form = LoginForm(request, data=request.POST or None)

    if request.method == 'POST':

        user_input = request.POST.get('username')
        password = request.POST.get('password')

        # Check employee ID
        try:
            user_obj = CustomUser.objects.get(employee_id=user_input)
            username = user_obj.username
        except CustomUser.DoesNotExist:
            username = user_input

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.display_name}!')

            next_url = request.GET.get('next')
            return redirect(next_url if next_url else _role_redirect(user))

        
    return render(request, 'accounts/login.html', {'form': form})

def register_view(request):
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        role = form.cleaned_data.get('role')
        if role == 'admin':
            messages.success(request, f'Admin account created! Welcome, {user.display_name}.')
        else:
            messages.success(request, f'Account created! Welcome to BHEL SAP Portal, {user.display_name}.')
        return redirect(_role_redirect(user))   # already handles admin vs user
    return render(request, 'accounts/register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


# ── profile views ─────────────────────────────────────────────────────────────

@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html', {'user': request.user})


@login_required
def profile_edit_view(request):
    form = ProfileUpdateForm(
        request.POST or None, request.FILES or None, instance=request.user
    )
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('accounts:profile')
    return render(request, 'accounts/profile_edit.html', {'form': form})


@login_required
def change_password_view(request):
    form = PasswordChangeForm(request.user, request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Password changed successfully.')
        return redirect('accounts:profile')
    return render(request, 'accounts/change_password.html', {'form': form})


# ── department switch ─────────────────────────────────────────────────────────

@login_required
def switch_department_view(request):
    """
    POST-only: lets any authenticated user switch their department.
    Logs every switch in DepartmentChangeLog for audit purposes.
    """
    if request.method != 'POST':
        return redirect('portal:user_dashboard')

    form = DepartmentSwitchForm(request.POST)
    if form.is_valid():
        new_dept = form.cleaned_data['department']
        reason   = form.cleaned_data.get('reason', '')
        old_dept = request.user.department

        if old_dept == new_dept:
            messages.warning(request, f'You are already assigned to {new_dept.name}.')
        else:
            DepartmentChangeLog.objects.create(
                user            = request.user,
                from_department = old_dept,
                to_department   = new_dept,
                reason          = reason,
            )
            request.user.department = new_dept
            request.user.save(update_fields=['department'])
            messages.success(
                request,
                f'Department switched to <strong>{new_dept.name}</strong>. '
                f'Your dashboard now shows {new_dept.name} content.',
            )
    else:
        messages.error(request, 'Invalid department selection. Please try again.')

    return redirect('portal:user_dashboard')

# accounts/views.py
def forgot_password(request):
    email_sent = False
    masked_email = ''
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)   # sends Django's built-in reset email
            email = form.cleaned_data['email']
            # mask: j***@bhel.in
            local, domain = email.split('@')
            masked_email = local[0] + '***@' + domain
            email_sent = True
    else:
        form = PasswordResetForm()
    return render(request, 'accounts/forgot_password.html', {
        'form': form, 'email_sent': email_sent, 'masked_email': masked_email
    })