from django.urls import path
from django.urls import re_path as url
import blog.views
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page


urlpatterns = [
    # path("hello/", blog.views.hello, name="hello"),
    url(r'^profile/', TemplateView.as_view(template_name='profile.html')),
    url(r'^saved/', blog.views.SaveProfile, name='SaveProfile'),
    url(r'^show/',blog.views.show,name='show'),
    url(r'^createlog/', blog.views.create_travel_log, name='create_travel_log'),
    url(r'^dailylog/', blog.views.view_travel_logs, name='travel_logs'),
]
