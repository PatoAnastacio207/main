from datetime import timedelta

from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

from .models import Sps30Data, WeatherData

DATA_PREFIX = "DATA,"


def dashboard(request):
    return render(request, "dashboard.html")


def get_latest_sps(request):

    sps30Data = cache.get("sps30_latest_reading", {"value": None, "timestamp": None})
    print("get_latest_sps called")

    if sps30Data.get("value") and sps30Data.get("value").startswith(DATA_PREFIX):
        return JsonResponse(sps30Data)


    return JsonResponse("No data Available", status=404)

def get_latest_weather(request):
    weatherData = cache.get("weather_latest_reading", {"value": None, "timestamp": None})
    
    if weatherData.get("value"):
        return JsonResponse(weatherData)


    return JsonResponse("No data Available", status=404)

def get_pm_graph(request):
    qs = Sps30Data.objects.filter(timestamp__gte=timezone.now() - timedelta(days=1)).order_by('timestamp')

    data = {
        "labels": [e.timestamp.strftime("%Y-%m-%d %H:%M:%S") for e in qs],
        "pm1":  [e.pm1  for e in qs],
        "pm25": [e.pm25 for e in qs],
        "pm4":  [e.pm4  for e in qs],
        "pm10": [e.pm10 for e in qs],
    }

    return JsonResponse(data)


def get_nc_graph(request):
    qs = Sps30Data.objects.filter(timestamp__gte=timezone.now() - timedelta(days=1)).order_by('timestamp')

    data = {
        "labels": [e.timestamp.strftime("%Y-%m-%d %H:%M:%S") for e in qs],
        "nc0":  [e.nc0  for e in qs],
        "nc1": [e.nc1 for e in qs],
        "nc25":  [e.nc4  for e in qs],
        "nc10": [e.nc10 for e in qs],
    }

    return JsonResponse(data)


def get_nc_pm_graph(request):
    qs = Sps30Data.objects.filter(timestamp__gte=timezone.now() - timedelta(days=1)).order_by('timestamp')

    data = {
        "labels": [e.timestamp.strftime("%m-%d %H:%M") for e in qs],
        "pm1": [e.pm1 for e in qs],
        "pm25": [e.pm25 for e in qs],
        "nc0":  [e.nc0  for e in qs],
        "nc1": [e.nc1 for e in qs],
        "nc25":  [e.nc4  for e in qs],
    }

    return JsonResponse(data)


def get_weather_graph(request):
    qs = WeatherData.objects.filter(timestamp__gte=timezone.now() - timedelta(days=1)).order_by('timestamp')

    data = {
        "labels": [e.timestamp.strftime("%Y-%m-%d %H:%M:%S") for e in qs],
        "temperature": [float(e.temperature) if e.temperature is not None else None for e in qs],
        "humidity": [float(e.humidity) if e.humidity is not None else None for e in qs],
    }

    return JsonResponse(data)