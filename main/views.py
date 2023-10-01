# main/views.py

from django.shortcuts import render

def index(request):
    return render(request, "index.html")

def map(request):
    return render(request, 'map/map.html')

def login(request):
    return render(request, 'accounts/login/login.html')

def blog(request):
    return render(request, 'blog/show.html')

def create_travel_log(request):
    return render(request, 'blog/create_travel_log.html')