from django.db import models
from django.contrib.auth.models import User


class LineId(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='line')
    line_id = models.CharField(max_length=100)

    class Meta:
        db_table = "lineId"