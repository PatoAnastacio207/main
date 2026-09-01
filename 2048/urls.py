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
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_not_required
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
    # Site-wide, not blog-specific: LoginRequiredMiddleware sends every
    # anonymous request here. Only login/logout are wired up on purpose —
    # including the full django.contrib.auth URLconf would also expose
    # password reset, which needs email configuration this project does not
    # have.
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="login"),
        name="logout",
    ),
    # The PWA shell is exempt from the login wall. It carries no user data,
    # and a service worker that cached a redirect to the login page — or an
    # offline fallback that could not be reached while logged out — would
    # break the installed apps rather than protect anything.
    #
    # The service worker must be served from the site root: its scope is the
    # directory it is served from, so a copy under /static/ could only ever
    # control /static/*.
    path(
        "sw.js",
        login_not_required(
            TemplateView.as_view(
                template_name="sw.js",
                content_type="application/javascript",
            )
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
        login_not_required(TemplateView.as_view(template_name="offline.html")),
        name="offline",
    ),
]

# Uploaded article images. Django serves these itself, which is fine at this
# project's traffic level; put them behind nginx/caddy if that ever changes.
# Left inside the login wall on purpose — an unguessable URL is not access
# control, and these belong to articles only logged-in users can read.
urlpatterns += [
    re_path(
        r"^media/(?P<path>.*)$",
        serve,
        {"document_root": settings.MEDIA_ROOT},
    ),
]
