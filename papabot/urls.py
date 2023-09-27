from django.urls import path
from django.urls import re_path as url
from . import views

urlpatterns = [
    url(r'^callback/', views.callback, name='callback'),

]
