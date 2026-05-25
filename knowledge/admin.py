from django.contrib import admin
from .models import SAPModule, Process, SecurityScan, Workflow, Document, FAQ, TCodeDirectory, Announcement


admin.site.register(SecurityScan)

@admin.register(SAPModule)
class SAPModuleAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'process_count', 'is_active', 'order']
    list_editable = ['order', 'is_active']
    search_fields = ['code', 'name']
    prepopulated_fields = {'slug': ('code',)}


class WorkflowInline(admin.TabularInline):
    model = Workflow
    extra = 1
    fields = ['step_number', 'title', 't_code', 'responsible_role', 'description']


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 't_code', 'difficulty', 'view_count', 'is_active']
    list_filter = ['module', 'difficulty', 'is_active']
    search_fields = ['title', 't_code', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [WorkflowInline]
    readonly_fields = ['view_count', 'created_at', 'updated_at']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'doc_type', 'uploaded_by', 'uploaded_at', 'download_count']
    list_filter = ['module', 'doc_type', 'is_active']
    search_fields = ['title', 'description']
    readonly_fields = ['download_count', 'uploaded_at']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'module', 'helpful_count', 'is_active']
    list_filter = ['module', 'is_active']
    search_fields = ['question', 'answer']


@admin.register(TCodeDirectory)
class TCodeDirectoryAdmin(admin.ModelAdmin):
    list_display = ['t_code', 'description', 'module', 'is_active']
    list_filter = ['module', 'is_active']
    search_fields = ['t_code', 'description']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'is_active']
    list_filter = ['is_active']