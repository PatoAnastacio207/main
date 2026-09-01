from django.urls import path

from . import views

app_name = "priorities"

urlpatterns = [
    path("", views.task_list, name="list"),
    path("<int:pk>/", views.task_action, name="action"),
]
