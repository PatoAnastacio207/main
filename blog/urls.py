from django.urls import path

from . import views

urlpatterns = [
    path("", views.article_list, name="article_list"),
    path("<int:pk>/", views.article_detail, name="blog_detail"),
    path("new/", views.article_create, name="blog_create"),
]
