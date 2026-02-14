"""
URL configuration for AI Voice Cloning application.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def health_check(request):
    """Health check endpoint for deployment."""
    return JsonResponse({'status': 'healthy'})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/voices/', include('apps.voices.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/health/', health_check, name='health_check'),
]

# Serve media files in production (since backend runs Gunicorn without Nginx/S3)
from django.conf.urls.static import static
from django.views.static import serve
from django.urls import re_path

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    # Only need static in debug, media is now covered above
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
