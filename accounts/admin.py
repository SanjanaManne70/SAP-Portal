from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Department


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'created_at']
    search_fields = ['name', 'code']


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ['username', 'get_full_name', 'email', 'role', 'department', 'is_verified', 'is_active']
    list_filter = ['role', 'department', 'is_verified', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    fieldsets = UserAdmin.fieldsets + (
        ('BHEL Portal Info', {
            'fields': ('role', 'department', 'employee_id', 'phone', 'bio', 'profile_picture', 'joined_at', 'is_verified')
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('BHEL Portal Info', {
            'fields': ('role', 'department', 'employee_id', 'phone')
        }),
    )