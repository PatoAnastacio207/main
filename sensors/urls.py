from django.urls import path
from . import views

app_name = "sensors"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("latest/", views.latest_reading, name="latest"),
    path("graph/pm", views.draw_pm_graph, name="pm"),
    path("graph/nc", views.draw_nc_graph, name="nc"),
    path("graph/nc_pm", views.draw_nc_pm_graph, name="nc_pm")
]