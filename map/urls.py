from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('generate_itinerary/', views.generate_itinerary, name='generate_itinerary'),
    path('get_weather_forecast/', views.get_weather_forecast, name='get_weather_forecast'),
    path('save_trip/', views.save_trip, name='save_trip'),
    path('get_saved_trip/', views.get_saved_trip, name='get_saved_trip'),
    path('logout/', LogoutView.as_view(next_page='index'), name='logout'),
]
