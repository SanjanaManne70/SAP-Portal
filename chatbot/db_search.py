from django.db.models import Q

from knowledge.models import (
    SAPModule,
    Process,
    Workflow,
    Document,
    FAQ,
    TCodeDirectory,
    Announcement
)

from forum.models import Question


def search_database(query):

    query = query.strip()


    # ═══════════════════════════════════════
    # 1. SEARCH T-CODES
    # ═══════════════════════════════════════

    tcode = TCodeDirectory.objects.filter(

        Q(t_code__icontains=query) |
        Q(description__icontains=query) |
        Q(notes__icontains=query) |
        Q(menu_path__icontains=query)

    ).first()

    if tcode:

        return {
            "found": True,
            "source": "database",
            "answer": f"""
📘 T-Code: {tcode.t_code}

{tcode.description}
"""
        }


    # ═══════════════════════════════════════
    # 2. SEARCH SAP MODULES
    # ═══════════════════════════════════════

    module = SAPModule.objects.filter(

        Q(name__icontains=query) |
        Q(code__icontains=query) |
        Q(description__icontains=query)

    ).first()

    if module:

        return {
            "found": True,
            "source": "database",
            "answer": f"""
📦 SAP Module: {module.code}

{module.name}

{module.description[:300]}
"""
        }


    # ═══════════════════════════════════════
    # 3. SEARCH BUSINESS PROCESSES
    # ═══════════════════════════════════════

    process = Process.objects.filter(

        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(t_code__icontains=query) |
        Q(steps__icontains=query)

    ).first()

    if process:

        return {
            "found": True,
            "source": "database",
            "answer": f"""
⚙️ Process: {process.title}

Primary T-Code: {process.t_code}

{process.description[:350]}
"""
        }


    # ═══════════════════════════════════════
    # 4. SEARCH WORKFLOWS
    # ═══════════════════════════════════════

    workflow = Workflow.objects.filter(

        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(t_code__icontains=query) |
        Q(notes__icontains=query)

    ).first()

    if workflow:

        return {
            "found": True,
            "source": "database",
            "answer": f"""
🔄 Workflow Step: {workflow.title}

Process: {workflow.process.title}

T-Code: {workflow.t_code}
"""
        }


    # ═══════════════════════════════════════
    # 5. SEARCH FAQS
    # ═══════════════════════════════════════

    faq = FAQ.objects.filter(

        Q(question__icontains=query) |
        Q(answer__icontains=query)

    ).first()

    if faq:

        return {
            "found": True,
            "source": "database",
            "answer": f"""
❓ FAQ

Q: {faq.question}

A: {faq.answer[:350]}
"""
        }


    # ═══════════════════════════════════════
    # 6. SEARCH DOCUMENTS
    # ═══════════════════════════════════════

    document = Document.objects.filter(

        Q(title__icontains=query) |
        Q(description__icontains=query)

    ).first()

    if document:

        return {
            "found": True,
            "source": "database",
            "answer": f"""
📄 Document: {document.title}

{document.description[:300]}
"""
        }


    # ═══════════════════════════════════════
    # 7. SEARCH ANNOUNCEMENTS
    # ═══════════════════════════════════════

    announcement = Announcement.objects.filter(

        Q(title__icontains=query) |
        Q(body__icontains=query)

    ).first()

    if announcement:

        return {
            "found": True,
            "source": "database",
            "answer": f"""
📢 Announcement

{announcement.title}

{announcement.body[:300]}
"""
        }


    # ═══════════════════════════════════════
    # 8. SEARCH COMMUNITY QUESTIONS
    # ═══════════════════════════════════════

    question = Question.objects.filter(

        Q(title__icontains=query) |
        Q(body__icontains=query)

    ).first()

    if question:

        return {
            "found": True,
            "source": "database",
            "answer": f"""
💬 Community Question

{question.title}
"""
        }


    # ═══════════════════════════════════════
    # NOTHING FOUND
    # ═══════════════════════════════════════

    return {
        "found": False,
        "source": None,
        "answer": None
    }