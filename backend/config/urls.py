"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path('healthz/', views.health_check, name='health-check'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('core.urls')),
    path('api/v1/', include('partners.urls')),
]

# Local dev only: serve uploaded images (backend/media/) so admin uploads
# show up before Cloudinary is configured. static() does nothing unless
# DEBUG is on, and with CLOUDINARY_URL set images come from Cloudinary.
if settings.DEBUG and not settings.CLOUDINARY_URL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
