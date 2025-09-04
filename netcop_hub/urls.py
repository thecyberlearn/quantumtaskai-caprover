"""
URL configuration for netcop_hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('wallet/', include('wallet.urls')),
    
    # REST API-based agents system (web interface + API)
    path('agents/', include('agents.urls')),
    
    path('', include('core.urls')),
]

# Development tools (only in DEBUG mode)
if settings.DEBUG:
    # Serve static and media files during development
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    try:
        import debug_toolbar
        urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
    except ImportError:
        pass

# Custom error handlers (work in production when DEBUG=False)
handler404 = 'core.error_views.custom_404_view'
handler500 = 'core.error_views.custom_500_view'
handler403 = 'core.error_views.custom_403_view'
handler400 = 'core.error_views.custom_400_view'
