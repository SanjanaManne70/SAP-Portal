from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import JsonResponse, FileResponse

from .models import SAPModule, Process, Workflow, Document, FAQ, TCodeDirectory, Announcement
from .forms import ProcessForm, DocumentUploadForm, FAQForm, AnnouncementForm


# ── decorators ────────────────────────────────────────────────────────────────

def trainer_required(view_func):
    """Allows only admin or trainer roles."""
    from functools import wraps
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_admin_or_trainer:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('portal:dashboard')   # resolves via portal.urls → role_redirect
        return view_func(request, *args, **kwargs)
    return wrapper


def dept_module_filter(request, queryset):
    """
    Helper: filters a queryset of objects that have a `module` FK
    to only those accessible by the current user's department.
    Admins/trainers always see everything.
    """
    user = request.user
    if user.is_admin_or_trainer:
        return queryset
    dept = getattr(user, 'department', None)
    if dept and dept.allowed_modules.exists():
        return queryset.filter(module__in=dept.allowed_modules.all())
    return queryset


# ── module views ──────────────────────────────────────────────────────────────

@login_required
def module_list(request):
    modules = SAPModule.objects.filter(is_active=True)
    # Non-admin users only see their department's modules
    user = request.user
    if not user.is_admin_or_trainer:
        dept = getattr(user, 'department', None)
        if dept and dept.allowed_modules.exists():
            modules = dept.allowed_modules.filter(is_active=True)
    return render(request, 'knowledge/module_list.html', {'modules': modules})


@login_required
def module_detail(request, slug):
    module    = get_object_or_404(SAPModule, slug=slug, is_active=True)
    processes = module.processes.filter(is_active=True)
    documents = module.documents.filter(is_active=True)[:6]
    faqs      = module.faqs.filter(is_active=True)[:5]
    tcodes    = module.tcodes.filter(is_active=True)
    return render(request, 'knowledge/module_detail.html', {
        'module': module, 'processes': processes,
        'documents': documents, 'faqs': faqs, 'tcodes': tcodes,
    })


# ── process views ─────────────────────────────────────────────────────────────

@login_required
def process_detail(request, slug):
    process = get_object_or_404(Process, slug=slug, is_active=True)
    Process.objects.filter(pk=process.pk).update(view_count=process.view_count + 1)
    workflows  = process.workflows.all()
    documents  = process.documents.filter(is_active=True)
    faqs       = process.faqs.filter(is_active=True)
    related    = process.related_processes.filter(is_active=True)[:4]
    return render(request, 'knowledge/process_detail.html', {
        'process': process, 'workflows': workflows,
        'documents': documents, 'faqs': faqs, 'related_processes': related,
    })


@login_required
def process_explorer(request):
    modules          = SAPModule.objects.filter(is_active=True).prefetch_related('processes')
    selected_module  = request.GET.get('module')
    processes        = Process.objects.filter(is_active=True).select_related('module')
    # dept filter for non-admins
    processes = dept_module_filter(request, processes)
    if selected_module:
        processes = processes.filter(module__slug=selected_module)
    paginator = Paginator(processes, 15)
    page      = paginator.get_page(request.GET.get('page'))
    return render(request, 'knowledge/process_explorer.html', {
        'modules': modules, 'processes': page,
        'selected_module': selected_module,
    })


# ── T-code views ──────────────────────────────────────────────────────────────

@login_required
def tcode_directory(request):
    query         = request.GET.get('q', '')
    module_filter = request.GET.get('module', '')
    tcodes        = TCodeDirectory.objects.filter(is_active=True).select_related('module', 'process')
    tcodes        = dept_module_filter(request, tcodes)
    if query:
        tcodes = tcodes.filter(Q(t_code__icontains=query) | Q(description__icontains=query))
    if module_filter:
        tcodes = tcodes.filter(module__slug=module_filter)
    modules   = SAPModule.objects.filter(is_active=True)
    paginator = Paginator(tcodes, 20)
    page      = paginator.get_page(request.GET.get('page'))
    return render(request, 'knowledge/tcode_directory.html', {
        'tcodes': page, 'query': query,
        'modules': modules, 'selected_module': module_filter,
    })


@login_required
def tcode_search_ajax(request):
    query   = request.GET.get('q', '').strip().upper()
    results = []
    if query:
        qs = TCodeDirectory.objects.filter(
            Q(t_code__icontains=query) | Q(description__icontains=query),
            is_active=True,
        )[:10]
        results = [
            {
                't_code':       t.t_code,
                'description':  t.description,
                'module':       t.module.code if t.module else '',
                'process_slug': t.process.slug if t.process else '',
            }
            for t in qs
        ]
    return JsonResponse({'results': results})


# ── document views ────────────────────────────────────────────────────────────

@login_required
def document_list(request):
    module_filter = request.GET.get('module', '')
    doc_type      = request.GET.get('type', '')
    query         = request.GET.get('q', '')
    docs          = Document.objects.filter(is_active=True).select_related('module', 'uploaded_by')
    docs          = dept_module_filter(request, docs)
    if module_filter:
        docs = docs.filter(module__slug=module_filter)
    if doc_type:
        docs = docs.filter(doc_type=doc_type)
    if query:
        docs = docs.filter(Q(title__icontains=query) | Q(description__icontains=query))
    modules   = SAPModule.objects.filter(is_active=True)
    paginator = Paginator(docs, 12)
    page      = paginator.get_page(request.GET.get('page'))
    return render(request, 'knowledge/document_list.html', {
        'documents': page, 'modules': modules,
        'selected_module': module_filter, 'query': query,
        'doc_types': Document.DOC_TYPE_CHOICES, 'selected_type': doc_type,
    })


@login_required
def document_download(request, pk):
    doc = get_object_or_404(Document, pk=pk, is_active=True)
    Document.objects.filter(pk=pk).update(download_count=doc.download_count + 1)
    return FileResponse(doc.file, as_attachment=True)


# ── FAQ views ─────────────────────────────────────────────────────────────────

@login_required
def faq_list(request):
    module_filter = request.GET.get('module', '')
    query         = request.GET.get('q', '')
    faqs          = FAQ.objects.filter(is_active=True).select_related('module', 'process')
    faqs          = dept_module_filter(request, faqs)
    if module_filter:
        faqs = faqs.filter(module__slug=module_filter)
    if query:
        faqs = faqs.filter(Q(question__icontains=query) | Q(answer__icontains=query))
    modules   = SAPModule.objects.filter(is_active=True)
    paginator = Paginator(faqs, 15)
    page      = paginator.get_page(request.GET.get('page'))
    return render(request, 'knowledge/faq_list.html', {
        'faqs': page, 'modules': modules,
        'selected_module': module_filter, 'query': query,
    })


# ── global search ─────────────────────────────────────────────────────────────

@login_required
def global_search(request):
    query   = request.GET.get('q', '').strip()
    results = {'processes': [], 'documents': [], 'faqs': [], 'tcodes': []}
    if query:
        base_proc = Process.objects.filter(is_active=True)
        base_doc  = Document.objects.filter(is_active=True)
        base_faq  = FAQ.objects.filter(is_active=True)
        base_tc   = TCodeDirectory.objects.filter(is_active=True)

        # Apply dept filter for regular users
        base_proc = dept_module_filter(request, base_proc)
        base_doc  = dept_module_filter(request, base_doc)
        base_faq  = dept_module_filter(request, base_faq)
        base_tc   = dept_module_filter(request, base_tc)

        results['processes'] = base_proc.filter(
            Q(title__icontains=query) | Q(description__icontains=query) | Q(t_code__icontains=query)
        )[:10]
        results['documents'] = base_doc.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:8]
        results['faqs'] = base_faq.filter(
            Q(question__icontains=query) | Q(answer__icontains=query)
        )[:8]
        results['tcodes'] = base_tc.filter(
            Q(t_code__icontains=query) | Q(description__icontains=query)
        )[:8]

    total = sum(len(v) for v in results.values())
    return render(request, 'knowledge/search_results.html', {
        'query': query, 'results': results, 'total': total,
    })


# ── admin/trainer write views ─────────────────────────────────────────────────

@login_required
@trainer_required
def process_create(request):
    form = ProcessForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        process             = form.save(commit=False)
        process.created_by  = request.user
        process.save()
        form.save_m2m()
        messages.success(request, f'Process "{process.title}" created!')
        return redirect('knowledge:process_detail', slug=process.slug)
    return render(request, 'knowledge/process_form.html', {'form': form, 'action': 'Create'})


@login_required
@trainer_required
def process_edit(request, slug):
    process = get_object_or_404(Process, slug=slug)
    form    = ProcessForm(request.POST or None, instance=process)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Process updated!')
        return redirect('knowledge:process_detail', slug=process.slug)
    return render(request, 'knowledge/process_form.html', {
        'form': form, 'action': 'Edit', 'process': process,
    })


@login_required
@trainer_required
def document_upload(request):
    form = DocumentUploadForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        doc             = form.save(commit=False)
        doc.uploaded_by = request.user
        if doc.file:
            doc.file_size = doc.file.size // 1024
        doc.save()
        messages.success(request, f'Document "{doc.title}" uploaded!')
        return redirect('knowledge:document_list')
    return render(request, 'knowledge/document_upload.html', {'form': form})


@login_required
@trainer_required
def faq_create(request):
    form = FAQForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        faq            = form.save(commit=False)
        faq.created_by = request.user
        faq.save()
        messages.success(request, 'FAQ created!')
        return redirect('knowledge:faq_list')
    return render(request, 'knowledge/faq_form.html', {'form': form, 'action': 'Create'})


@login_required
@trainer_required
def announcement_create(request):
    form = AnnouncementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        ann            = form.save(commit=False)
        ann.created_by = request.user
        ann.save()
        messages.success(request, 'Announcement posted!')
        return redirect('portal:dashboard')
    return render(request, 'knowledge/announcement_form.html', {'form': form})