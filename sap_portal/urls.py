#from django.contrib import admin
#from django.urls import path, include
#from django.conf import settings
#from django.conf.urls.static import static

#urlpatterns = [
#    path('admin/', admin.site.urls),
#    path('', include('portal.urls')),
#    path('accounts/', include('accounts.urls')),
#    path('knowledge/', include('knowledge.urls')),
#    path('forum/', include('forum.urls')),
#] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Customize admin site
#admin.site.site_header = 'BHEL SAP Portal Administration'
#admin.site.site_title = 'BHEL SAP Portal'
#admin.site.index_title = 'Portal Management'
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/',      admin.site.urls),

    # Portal (root + dashboards + bulk upload)
    path('',            include('portal.urls')),

    # Accounts (login, register, profile, switch-department)
    path('accounts/',   include('accounts.urls')),

    # Knowledge base
    path('knowledge/',  include('knowledge.urls')),

    # Q&A Forum
    path('forum/',      include('forum.urls')),
    path('accounts/password-reset-confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(),name='password_reset_confirm'),

    path('accounts/password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(),
         name='password_reset_complete'),
    path('chatbot/', include('chatbot.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)