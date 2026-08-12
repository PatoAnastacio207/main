from django.urls import path
from . import views

app_name = "sensors"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("latest/sps", views.get_latest_sps, name="latest_sps"),
    path("latest/weather", views.get_latest_weather, name="latest_weather"),
    path("graph/pm", views.get_pm_graph, name="pm"),
    path("graph/nc", views.get_nc_graph, name="nc"),
    path("graph/nc_pm", views.get_nc_pm_graph, name="nc_pm"),
    path("graph/weather", views.get_weather_graph, name="weather_graph")
]