import csv
import io

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse

from knowledge.models import SAPModule, Process, Document, FAQ, Announcement, TCodeDirectory,SecurityScan
from forum.models import Question
from accounts.models import CustomUser, Department
from .forms import BulkCSVUploadForm, BulkDocumentUploadForm


# ── helpers ──────────────────────────────────────────────────────────────────

def _admin_required(request):
    """Returns True if user may access admin dashboard."""
    return request.user.is_authenticated and request.user.is_admin_or_trainer


# ── root redirect ─────────────────────────────────────────────────────────────

def role_redirect(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    if request.user.is_admin_or_trainer:
        return redirect('portal:admin_dashboard')
    return redirect('portal:user_dashboard')


# ── USER DASHBOARD ────────────────────────────────────────────────────────────

@login_required
def user_dashboard(request):
    """
    Department-scoped dashboard for employees and interns.
    Content (modules, processes, documents, T-codes) is filtered
    to the modules assigned to the user's department.
    If the department has no allowed_modules, all modules are shown.
    """
    user = request.user
    dept = user.department

    # Resolve which modules this user may see
    if dept and dept.allowed_modules.exists():
        modules = dept.allowed_modules.filter(is_active=True)
    else:
        modules = SAPModule.objects.filter(is_active=True)

    module_ids = list(modules.values_list('id', flat=True))

    popular_processes    = (Process.objects
                            .filter(is_active=True, module_id__in=module_ids)
                            .order_by('-view_count')[:5])
    recent_docs          = (Document.objects
                            .filter(is_active=True, module_id__in=module_ids)
                            .order_by('-uploaded_at')[:3])
    popular_tcodes       = (TCodeDirectory.objects
                            .filter(is_active=True, module_id__in=module_ids)[:10])
    recent_announcements = Announcement.objects.filter(is_active=True)[:3]
    recent_questions     = (Question.objects
                            .select_related('asked_by')
                            .order_by('-asked_at')[:4])
    all_departments      = Department.objects.all()

    # Default P2P process-flow diagram (shown when dept has MM access)
    p2p_steps = [
        {'label': 'Purchase Requisition', 'tcode': 'ME51N'},
        {'label': 'Purchase Order',       'tcode': 'ME21N'},
        {'label': 'Goods Receipt',        'tcode': 'MIGO'},
        {'label': 'Invoice Verification', 'tcode': 'MIRO'},
        {'label': 'Payment Process',      'tcode': 'F110'},
    ]

    context = {
        'modules':               modules,
        'popular_processes':     popular_processes,
        'recent_announcements':  recent_announcements,
        'recent_questions':      recent_questions,
        'recent_docs':           recent_docs,
        'popular_tcodes':        popular_tcodes,
        'p2p_steps':             p2p_steps,
        'all_departments':       all_departments,
        'current_dept':          dept,
        'total_processes':       Process.objects.filter(is_active=True, module_id__in=module_ids).count(),
        'total_documents':       Document.objects.filter(is_active=True, module_id__in=module_ids).count(),
        'total_faqs':            FAQ.objects.filter(is_active=True, module_id__in=module_ids).count(),
        'total_questions':       Question.objects.count(),
    }
    return render(request, 'portal/user_dashboard.html', context)


# ── ADMIN DASHBOARD ───────────────────────────────────────────────────────────

@login_required
def admin_dashboard(request):
    """Full-access dashboard for Admin and Trainer roles."""
    if not _admin_required(request):
        messages.error(request, 'You do not have permission to access the admin dashboard.')
        return redirect('portal:user_dashboard')

    # Platform-wide stats
    stats = {
        'total_users':     CustomUser.objects.count(),
        'total_processes': Process.objects.filter(is_active=True).count(),
        'total_documents': Document.objects.filter(is_active=True).count(),
        'total_faqs':      FAQ.objects.filter(is_active=True).count(),
        'total_questions': Question.objects.count(),
        'total_modules':   SAPModule.objects.filter(is_active=True).count(),
        'total_depts':     Department.objects.count(),
    }

    # Department breakdown
    dept_stats = []
    for dept in Department.objects.all():
        dept_stats.append({
            'dept':       dept,
            'user_count': dept.employees.count(),
            'mod_count':  dept.allowed_modules.count() or SAPModule.objects.filter(is_active=True).count(),
        })
            # Security monitoring
        high_risks = SecurityScan.objects.filter(
            risk_level='high'
        ).count()

        medium_risks = SecurityScan.objects.filter(
            risk_level='medium'
        ).count()

        security_issues = SecurityScan.objects.order_by(
            '-detected_at'
        )[:5]

    context = {
        **stats,
        'dept_stats':            dept_stats,
        'recent_users':          CustomUser.objects.order_by('-date_joined')[:6],
        'recent_docs':           Document.objects.filter(is_active=True).order_by('-uploaded_at')[:5],
        'recent_announcements':  Announcement.objects.filter(is_active=True)[:4],
        'recent_questions':      Question.objects.select_related('asked_by').order_by('-asked_at')[:5],
        'popular_processes':     Process.objects.filter(is_active=True).order_by('-view_count')[:8],
        'modules':               SAPModule.objects.filter(is_active=True),
        'csv_form':              BulkCSVUploadForm(),
        'doc_form':              BulkDocumentUploadForm(),
        'high_risks': high_risks,
        'medium_risks': medium_risks,
        'security_issues': security_issues,
    }
    return render(request, 'portal/admin_dashboard.html', context)


# ── BULK UPLOAD: CSV ──────────────────────────────────────────────────────────

@login_required
def bulk_csv_upload(request):
    """
    Admin/Trainer only.
    Accepts a CSV file to bulk-create Processes or TCodeDirectory entries.

    Process CSV  columns : title, module_code, description, t_code, difficulty, steps
    T-Code CSV   columns : t_code, description, module_code, menu_path, notes
    """
    if not _admin_required(request):
        messages.error(request, 'Permission denied.')
        return redirect('portal:admin_dashboard')

    if request.method != 'POST':
        return redirect('portal:admin_dashboard')

    upload_type = request.POST.get('upload_type', 'process')
    csv_file    = request.FILES.get('csv_file')

    if not csv_file:
        messages.error(request, 'No CSV file was uploaded.')
        return redirect('portal:admin_dashboard')

    if not csv_file.name.lower().endswith('.csv'):
        messages.error(request, 'Please upload a file with a .csv extension.')
        return redirect('portal:admin_dashboard')

    try:
        decoded = csv_file.read().decode('utf-8-sig')   # handle BOM from Excel
        reader  = csv.DictReader(io.StringIO(decoded))
        created = 0
        skipped = 0
        errors  = []

        if upload_type == 'process':
            for i, row in enumerate(reader, start=2):   # row 1 = header
                try:
                    code   = row.get('module_code', '').strip().upper()
                    module = SAPModule.objects.get(code=code, is_active=True)
                    obj, was_created = Process.objects.get_or_create(
                        title=row['title'].strip(),
                        defaults={
                            'module':      module,
                            'description': row.get('description', '').strip(),
                            't_code':      row.get('t_code', '').strip().upper(),
                            'difficulty':  row.get('difficulty', 'beginner').strip().lower(),
                            'steps':       row.get('steps', '').strip(),
                            'created_by':  request.user,
                        },
                    )
                    if was_created:
                        created += 1
                    else:
                        skipped += 1
                except SAPModule.DoesNotExist:
                    errors.append(f"Row {i}: Module code '{row.get('module_code')}' not found.")
                except KeyError as exc:
                    errors.append(f"Row {i}: Missing required column — {exc}")

        elif upload_type == 'tcode':
            for i, row in enumerate(reader, start=2):
                try:
                    code   = row.get('module_code', '').strip().upper()
                    module = SAPModule.objects.get(code=code, is_active=True)
                    obj, was_created = TCodeDirectory.objects.get_or_create(
                        t_code=row['t_code'].strip().upper(),
                        defaults={
                            'description': row.get('description', '').strip(),
                            'module':      module,
                            'menu_path':   row.get('menu_path', '').strip(),
                            'notes':       row.get('notes', '').strip(),
                        },
                    )
                    if was_created:
                        created += 1
                    else:
                        skipped += 1
                except SAPModule.DoesNotExist:
                    errors.append(f"Row {i}: Module code '{row.get('module_code')}' not found.")
                except KeyError as exc:
                    errors.append(f"Row {i}: Missing required column — {exc}")

        summary = f'{created} record(s) imported'
        if skipped:
            summary += f', {skipped} duplicate(s) skipped'
        if errors:
            messages.warning(request, f'{summary}. Errors: ' + ' | '.join(errors[:5]))
        else:
            messages.success(request, f'{summary} successfully.')

    except Exception as exc:
        messages.error(request, f'Could not process file: {exc}')

    return redirect('portal:admin_dashboard')


# ── BULK UPLOAD: DOCUMENTS ────────────────────────────────────────────────────

@login_required
def bulk_document_upload(request):
    """Admin/Trainer only. Accepts multiple files in a single form submission."""
    if not _admin_required(request):
        messages.error(request, 'Permission denied.')
        return redirect('portal:admin_dashboard')

    if request.method != 'POST':
        return redirect('portal:admin_dashboard')

    files      = request.FILES.getlist('documents')
    module_id  = request.POST.get('module')
    doc_type   = request.POST.get('doc_type', 'pdf')

    if not files:
        messages.error(request, 'No files were selected.')
        return redirect('portal:admin_dashboard')

    module = None
    if module_id:
        try:
            module = SAPModule.objects.get(pk=module_id)
        except SAPModule.DoesNotExist:
            pass

    uploaded = 0
    for f in files:
        # Generate a human-readable title from the filename
        raw_name  = f.name.rsplit('.', 1)[0]
        title     = raw_name.replace('_', ' ').replace('-', ' ').title()
        Document.objects.create(
            title       = title,
            file        = f,
            doc_type    = doc_type,
            module      = module,
            uploaded_by = request.user,
            file_size   = f.size // 1024,
        )
        uploaded += 1

    messages.success(request, f'{uploaded} document(s) uploaded successfully.')
    return redirect('portal:admin_dashboard')


# ── CSV TEMPLATE DOWNLOAD ─────────────────────────────────────────────────────

@login_required
def download_csv_template(request):
    """Serves a ready-to-fill CSV template for the requested upload type."""
    if not _admin_required(request):
        messages.error(request, 'Permission denied.')
        return redirect('portal:admin_dashboard')

    upload_type = request.GET.get('type', 'process')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{upload_type}_template.csv"'
    writer = csv.writer(response)

    if upload_type == 'process':
        writer.writerow(['title', 'module_code', 'description', 't_code', 'difficulty', 'steps'])
        writer.writerow(['Create Purchase Order', 'MM', 'Creates a PO in SAP', 'ME21N', 'beginner', '1. Open ME21N\n2. Enter vendor\n3. Save'])
    else:
        writer.writerow(['t_code', 'description', 'module_code', 'menu_path', 'notes'])
        writer.writerow(['ME21N', 'Create Purchase Order', 'MM', 'Logistics > MM > Purchasing', ''])

    return response