from django.urls import path
from . import views

urlpatterns = [
    path('', views.generate_itinerary, name='generate_itinerary'),
    path('get_weather_forecast/', views.get_weather_forecast, name='get_weather_forecast'),
    path('save_trip/', views.save_trip, name='save_trip'),
    # path('get_latest_trip_locations/', views.get_latest_trip_locations, name='get_latest_trip_locations'),
]
