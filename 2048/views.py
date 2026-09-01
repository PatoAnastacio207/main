from django.shortcuts import HttpResponse, render
from django.template.loader import get_template

def home(request):
    """Launch screen of the website. Requires a logged-in user, like
    every other page here."""
    return render(request, "home.html")
