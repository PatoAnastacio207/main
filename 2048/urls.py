"""
URL configuration for blogs2048 project.

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
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.generic import TemplateView
from django.views.static import serve

from .pwa import manifest
from .views import home

urlpatterns = [
    path("blog/", include("blog.urls")),
    path("admin/", admin.site.urls),
    path("sensors/", include("sensors.urls")),
    path("priorities/", include("priorities.urls")),
    path("", home, name="home"),
    # The service worker must be served from the site root: its scope is the
    # directory it is served from, so a copy under /static/ could only ever
    # control /static/*.
    path(
        "sw.js",
        TemplateView.as_view(
            template_name="sw.js",
            content_type="application/javascript",
        ),
        name="service_worker",
    ),
    # One manifest per section, so each installs as its own home screen app.
    path(
        "manifest/<slug:slug>.webmanifest",
        manifest,
        name="pwa_manifest",
    ),
    path(
        "offline/",
        TemplateView.as_view(template_name="offline.html"),
        name="offline",
    ),
]

# Uploaded article images. Django serves these itself, which is fine at this
# project's traffic level; put them behind nginx/caddy if that ever changes.
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
