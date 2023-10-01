# main/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('map/', views.map, name='map'),
    path('accounts/login/', views.login, name='login'),
    path('blog/', views.blog, name='blog'),
    path('blog/create_travel_log/', views.create_travel_log, name='create_travel_log'),
]
