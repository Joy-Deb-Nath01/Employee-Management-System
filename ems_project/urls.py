"""
URL configuration for ems_project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth endpoints
    path('accounts/', include('accounts.urls')),
    
    # App modules
    path('employees/', include('employees.urls')),
    path('departments/', include('departments.urls')),
    path('attendance/', include('attendance.urls')),
    path('leave/', include('leave.urls')),
    
    # Root redirects to dashboard views
    path('', include('dashboard.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
