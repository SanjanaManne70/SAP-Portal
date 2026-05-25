"""
Management command: python manage.py import_csv_data

Perfectly matched to your actual CSV files:

modules.csv        → 'Module Name'(code), 'Full Form'(name), 'Short Description'
processes.csv      → 'Process Name', 'T-Code', 'SAP Module', 'Short Description', 'Workflow Stage'
workflows.csv      → 'workflow_name', 'step_number', 'process_name', 'tcode', 'previous_step', 'next_step'
QA.csv             → 'Question', 'Answer', 'SAP Module', 'Related T-Code', 'Question Status', 'Difficulty Level'
documents.csv      → 'document_title', 'file_type', 'module', 'related_process', 'category', 'description'
T-codedirectory.csv → 't_code', 'description', 'module_code', 'menu_path', 'notes'
"""

import os
import csv
from django.core.management.base import BaseCommand
from django.conf import settings
from accounts.models import Department
from knowledge.models import SAPModule, Process, Workflow, FAQ, TCodeDirectory, Document


DATA_DIR = os.path.join(settings.BASE_DIR, 'data')


def read_csv(filename):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        return None, f"File not found: {path}"
    rows = []
    with open(path, newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cleaned = {k.strip(): (v.strip() if v else '') for k, v in row.items()}
            rows.append(cleaned)
    return rows, None


class Command(BaseCommand):
    help = 'Import SAP data from CSV files in /data/ directory'

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING('\n=== SAP Portal CSV Import ===\n'))
        self._import_departments()
        self._import_modules()
        self._import_processes()
        self._import_workflows()
        self._import_qa()
        self._import_documents()
        self._import_tcodes()          # ← new
        self.stdout.write(self.style.SUCCESS('\n✅ Import complete!\n'))

    # ── Departments ──────────────────────────────────────────────────────────
    def _import_departments(self):
        depts = [
            ('Materials Management',   'MM'),
            ('Finance & Controlling',  'FICO'),
            ('Sales & Distribution',   'SD'),
            ('Plant Maintenance',      'PM'),
            ('Quality Management',     'QM'),
            ('Human Resources',        'HR'),
            ('Production Planning',    'PP'),
            ('Information Technology', 'IT'),
        ]
        created = 0
        for name, code in depts:
            _, c = Department.objects.get_or_create(
                name=name,
                defaults={'code': code}
            )
            if c:
                created += 1
        self.stdout.write(f'  Departments: {created} created')

    # ── Modules ───────────────────────────────────────────────────────────────
    def _import_modules(self):
        rows, err = read_csv('modules.csv')
        if err:
            self.stdout.write(self.style.WARNING(f'  {err}'))
            return

        style_map = {
            'MM':     ('bi-box-seam',          'primary'),
            'FICO':   ('bi-currency-rupee',    'success'),
            'FI':     ('bi-currency-rupee',    'success'),
            'CO':     ('bi-bar-chart',         'success'),
            'SD':     ('bi-cart3',             'info'),
            'HR':     ('bi-people',            'secondary'),
            'HR/HCM': ('bi-people',            'secondary'),
            'PM':     ('bi-tools',             'warning'),
            'QM':     ('bi-patch-check',       'danger'),
            'PP':     ('bi-diagram-3',         'dark'),
            'PP-PI':  ('bi-diagram-3',         'dark'),
            'WM':     ('bi-archive',           'primary'),
            'EWM':    ('bi-archive',           'primary'),
            'PS':     ('bi-kanban',            'info'),
            'SCM':    ('bi-truck',             'warning'),
            'CRM':    ('bi-person-lines-fill', 'info'),
            'SRM':    ('bi-handshake',         'secondary'),
            'BASIS':  ('bi-server',            'dark'),
            'ABAP':   ('bi-code-slash',        'dark'),
            'BI/BW':  ('bi-graph-up',          'primary'),
            'GRC':    ('bi-shield-check',      'danger'),
            'EHS':    ('bi-heart-pulse',       'danger'),
            'DMS':    ('bi-file-earmark',      'secondary'),
            'TM':     ('bi-truck',             'warning'),
            'ARIBA':  ('bi-cloud',             'info'),
            'APO':    ('bi-calendar3',         'warning'),
        }

        created = 0
        skipped = 0
        for i, row in enumerate(rows):
            code = row.get('Module Name', '').strip().upper()
            name = row.get('Full Form', '').strip()
            desc = row.get('Short Description', '').strip()

            if not code or code in ('NAN', ''):
                skipped += 1
                continue

            icon, color = style_map.get(code, ('bi-grid', 'primary'))
            _, c = SAPModule.objects.get_or_create(
                code=code,
                defaults={
                    'name':        name or code,
                    'description': desc,
                    'icon':        icon,
                    'color':       color,
                    'order':       i + 1,
                }
            )
            if c:
                created += 1

        self.stdout.write(f'  Modules: {created} created, {skipped} skipped')

    # ── Processes ─────────────────────────────────────────────────────────────
    def _import_processes(self):
        rows, err = read_csv('processes.csv')
        if err:
            self.stdout.write(self.style.WARNING(f'  {err}'))
            return

        created = 0
        skipped = 0
        for row in rows:
            title       = row.get('Process Name', '').strip()
            t_code      = row.get('T-Code', '').strip().upper()
            module_code = row.get('SAP Module', '').strip().upper()
            description = row.get('Short Description', '').strip()
            steps       = row.get('Workflow Stage', '').strip()

            if not title or not module_code:
                skipped += 1
                continue

            try:
                module = SAPModule.objects.get(code=module_code)
            except SAPModule.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'    Module "{module_code}" not found for "{title}" — skipping')
                )
                skipped += 1
                continue

            process, c = Process.objects.get_or_create(
                title=title,
                module=module,
                defaults={
                    'description': description,
                    't_code':      t_code,
                    'difficulty':  'beginner',
                    'steps':       steps,
                }
            )

            # Mirror into T-Code directory (from processes.csv)
            if t_code and c:
                TCodeDirectory.objects.get_or_create(
                    t_code=t_code,
                    defaults={
                        'description': title,
                        'module':      module,
                        'process':     process,
                    }
                )

            if c:
                created += 1

        self.stdout.write(f'  Processes: {created} created, {skipped} skipped')

    # ── Workflows ─────────────────────────────────────────────────────────────
    def _import_workflows(self):
        rows, err = read_csv('workflows.csv')
        if err:
            self.stdout.write(self.style.WARNING(f'  {err}'))
            return

        created = 0
        skipped = 0
        for row in rows:
            process_name  = row.get('process_name', '').strip()
            step_num      = row.get('step_number', '1').strip()
            workflow_name = row.get('workflow_name', '').strip()
            t_code        = row.get('tcode', '').strip().upper()
            next_step     = row.get('next_step', '').strip()
            prev_step     = row.get('previous_step', '').strip()

            if not process_name:
                skipped += 1
                continue

            process = (
                Process.objects.filter(title=process_name).first() or
                Process.objects.filter(title__iexact=process_name).first()
            )
            if not process:
                skipped += 1
                continue

            try:
                step_num = int(float(step_num))
            except (ValueError, TypeError):
                step_num = 1

            notes = ''
            if prev_step and prev_step.lower() not in ('nan', ''):
                notes += f'Previous: {prev_step}. '
            if next_step and next_step.lower() not in ('nan', ''):
                notes += f'Next: {next_step}.'

            _, c = Workflow.objects.get_or_create(
                process=process,
                step_number=step_num,
                defaults={
                    'title':       workflow_name or process_name,
                    't_code':      t_code,
                    'description': f'Part of {workflow_name} workflow.' if workflow_name else '',
                    'notes':       notes.strip(),
                }
            )
            if c:
                created += 1

        self.stdout.write(f'  Workflows: {created} created, {skipped} skipped')

    # ── Q&A → FAQs ────────────────────────────────────────────────────────────
    def _import_qa(self):
        rows, err = read_csv('QA.csv')
        if err:
            self.stdout.write(self.style.WARNING(f'  {err}'))
            return

        created = 0
        skipped = 0
        for row in rows:
            question    = row.get('Question', '').strip()
            answer      = row.get('Answer', '').strip()
            module_code = row.get('SAP Module', '').strip().upper()
            t_code      = row.get('Related T-Code', '').strip().upper()

            if not question or not answer:
                skipped += 1
                continue

            module  = SAPModule.objects.filter(code=module_code).first() if module_code else None
            process = Process.objects.filter(t_code=t_code).first() if t_code else None

            _, c = FAQ.objects.get_or_create(
                question=question,
                defaults={
                    'answer':  answer,
                    'module':  module,
                    'process': process,
                }
            )
            if c:
                created += 1
            else:
                skipped += 1

        self.stdout.write(f'  FAQs (from QA.csv): {created} created, {skipped} skipped')

    # ── Documents (metadata only) ─────────────────────────────────────────────
    def _import_documents(self):
        rows, err = read_csv('documents.csv')
        if err:
            self.stdout.write(self.style.WARNING(f'  {err}'))
            return

        created = 0
        skipped = 0
        for row in rows:
            title       = row.get('document_title', '').strip()
            module_code = row.get('module', '').strip().upper()
            description = row.get('description', '').strip()
            category    = row.get('category', '').strip().lower()

            if not title or title.lower() in ('nan', ''):
                skipped += 1
                continue

            module = SAPModule.objects.filter(code=module_code).first() if module_code else None

            process_name = row.get('related_process', '').strip()
            process = (
                Process.objects.filter(title__iexact=process_name).first()
                if process_name else None
            )

            if   'sop'      in category: doc_type = 'sop'
            elif 'training' in category or 'manual' in category: doc_type = 'manual'
            elif 'policy'   in category: doc_type = 'policy'
            elif 'template' in category or 'checklist' in category: doc_type = 'template'
            else: doc_type = 'pdf'

            _, c = Document.objects.get_or_create(
                title=title,
                defaults={
                    'module':      module,
                    'process':     process,
                    'description': description,
                    'doc_type':    doc_type,
                    'file':        '',
                }
            )
            if c:
                created += 1

        self.stdout.write(f'  Documents (metadata): {created} created, {skipped} skipped')

    # ── T-Code Directory ──────────────────────────────────────────────────────
    def _import_tcodes(self):
        """
        T-codedirectory.csv columns:
          't_code', 'description', 'module_code', 'menu_path', 'notes'
        """
        rows, err = read_csv('T-codedirectory.csv')
        if err:
            self.stdout.write(self.style.WARNING(f'  {err}'))
            return

        created = 0
        skipped = 0
        updated = 0

        for row in rows:
            t_code      = row.get('t_code', '').strip().upper()
            description = row.get('description', '').strip()
            module_code = row.get('module_code', '').strip().upper()
            menu_path   = row.get('menu_path', '').strip()
            notes       = row.get('notes', '').strip()

            # Skip blank or placeholder rows
            if not t_code or t_code in ('NAN', ''):
                skipped += 1
                continue

            module = SAPModule.objects.filter(code=module_code).first() if module_code else None

            # Link to existing process with this T-Code if one exists
            process = Process.objects.filter(t_code=t_code).first()

            obj, c = TCodeDirectory.objects.get_or_create(
                t_code=t_code,
                defaults={
                    'description': description,
                    'module':      module,
                    'process':     process,
                    'menu_path':   menu_path,
                    'notes':       notes,
                }
            )

            if c:
                created += 1
            else:
                # Entry already exists (seeded from processes.csv) — fill in
                # menu_path and notes if they were blank before
                changed = False
                if menu_path and not obj.menu_path:
                    obj.menu_path = menu_path
                    changed = True
                if notes and not obj.notes:
                    obj.notes = notes
                    changed = True
                if description and not obj.description:
                    obj.description = description
                    changed = True
                if changed:
                    obj.save()
                    updated += 1
                else:
                    skipped += 1

        self.stdout.write(
            f'  T-Codes: {created} created, {updated} updated, {skipped} skipped'
        )