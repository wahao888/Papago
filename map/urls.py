from django.urls import path
from . import views

urlpatterns = [
    path('generate_itinerary/', views.generate_itinerary, name='generate_itinerary'),
    path('get_weather_forecast/', views.get_weather_forecast, name='get_weather_forecast'),
]
