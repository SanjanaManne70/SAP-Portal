from knowledge.models import TCodeDirectory


def portal_context(request):
    """
    Injects portal-wide context into every template.
    popular_tcodes powers the T-Code FAB popup on every page.
    """
    if not request.user.is_authenticated:
        return {}

    return {
        'popular_tcodes': TCodeDirectory.objects.filter(is_active=True)[:12],
    }