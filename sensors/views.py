from django.shortcuts import render

# Create your views here.
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render

from .models import Sps30Data

CACHE_KEY = "arduino_latest_reading"
DATA_PREFIX = "DATA,"


def dashboard(request):
    return render(request, "dashboard.html")


def latest_reading(request):
    data = cache.get(CACHE_KEY, {"value": None, "timestamp": None})

    print('last reading', data)

    if data.get("value") and data.get("value").startswith(DATA_PREFIX):
        _, pm1, pm25, pm4, pm10, nc0, nc1, nc25, nc4, nc10, typicalParticleSize = data.split(',')
        data = { pm1, pm25, pm4, pm10, nc0, nc1, nc25, nc4, nc10, typicalParticleSize }
    
    return JsonResponse(data)

def draw_pm_graph(request):
    qs = Sps30Data.objects.all().order_by('timestamp')

    data = {
        "labels": [e.timestamp.strftime("%Y-%m-%d %H:%M:%S") for e in qs],
        "pm1":  [e.pm1  for e in qs],
        "pm25": [e.pm25 for e in qs],
        "pm4":  [e.pm4  for e in qs],
        "pm10": [e.pm10 for e in qs],
    }

    return JsonResponse(data)

def draw_nc_graph(request):
    qs = Sps30Data.objects.all().order_by('timestamp')

    data = {
        "labels": [e.timestamp.strftime("%Y-%m-%d %H:%M:%S") for e in qs],
        "nc0":  [e.nc0  for e in qs],
        "nc1": [e.nc1 for e in qs],
        "nc25":  [e.nc4  for e in qs],
        "nc10": [e.nc10 for e in qs],
    }

    

    return JsonResponse(data)

def draw_nc_pm_graph(request):
    qs = Sps30Data.objects.all().order_by('timestamp')
    
    data = {
            "labels": [e.timestamp.strftime("%m-%d %H:%M") for e in qs],
            "pm1": [e.pm1 for e in qs],
            "pm25": [e.pm25 for e in qs], 
            "nc0":  [e.nc0  for e in qs],
            "nc1": [e.nc1 for e in qs],
            "nc25":  [e.nc4  for e in qs],
            
        }
    
    return JsonResponse(data)