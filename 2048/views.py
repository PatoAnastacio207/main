from django.shortcuts import HttpResponse, render
from django.template.loader import get_template

def home(request):
    """Public view: Home view of the website"""
    return render(request, "home.html")
