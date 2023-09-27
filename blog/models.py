from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

from datetime import datetime
# Create your models here.


def get_folder():
    now = datetime.now()
    time = now.strftime("%Y_%m_%d")
    return f'profile_pictures/{time}'


def get_upload_path(instance, filename):
    now = datetime.now()
    time = now.strftime("%Y_%m_%d")
    return f'profile_pictures/{time}/{filename}'  # 將路徑改為相對於 MEDIA_ROOT 的子目錄


class Profile(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='profile')
    now = datetime.now()
    time = now.strftime("%Y_%m_%d")
    name = models.CharField(max_length=50)
    picture = models.ImageField(upload_to=get_upload_path)
    folder = models.CharField(max_length=100, default=get_folder)

    class Meta:
        db_table = "profile"


class TravelLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='blog')
    title = models.CharField(max_length=200)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
