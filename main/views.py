# main/views.py

from django.http import HttpResponse

def index(request):
    return HttpResponse("Hello, this is the homepage.")
