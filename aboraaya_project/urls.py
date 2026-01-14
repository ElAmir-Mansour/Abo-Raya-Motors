"""
URL configuration for aboraaya_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

from django.contrib.auth import views as auth_views

# Non-i18n URLs (admin, media, social auth)
urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Allauth social login URLs
    path('accounts/', include('allauth.urls')),
    
    # Password Reset URLs (outside i18n so links work properly)
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'),
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'),
         name='password_reset_complete'),
]

# i18n URLs (will be prefixed with /ar/ or /en/)
urlpatterns += i18n_patterns(
    path('', include('core.urls')),
)

# Media files serving (development only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0] if settings.STATICFILES_DIRS else None)

# Custom error handlers - defined as functions in project level
# These are only active when DEBUG=False
def custom_404_view(request, exception):
    from django.shortcuts import render
    return render(request, '404.html', status=404)

def custom_500_view(request):
    from django.shortcuts import render
    return render(request, '500.html', status=500)

handler404 = custom_404_view
handler500 = custom_500_view

