#papago/map/models.py
from django.db import models
from django.contrib.auth.models import User


class TripInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trips') # 使用者
    trip_name = models.CharField(max_length=255) # 旅遊名稱
    trip_day = models.IntegerField() # 旅遊天數
    location_name = models.CharField(max_length=255) # 旅遊地點
    latitude = models.FloatField()  # 緯度
    longitude = models.FloatField()  # 經度