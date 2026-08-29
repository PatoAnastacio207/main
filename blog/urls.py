from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.article_list, name="article_list"),
    path("<int:pk>/", views.article_detail, name="blog_detail"),
    path("new/", views.article_create, name="blog_create"),
    # Only login/logout are wired up on purpose: including the full
    # django.contrib.auth URLconf would also expose password reset, which
    # needs email configuration this project does not have.
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="blog_login.html",
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="article_list"),
        name="logout",
    ),
]
