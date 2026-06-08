from django.db import models

class Component(models.Model):
    uid_rfid = models.CharField(max_length=100)
    mpn = models.CharField(max_length=100)
    quantity = models.IntegerField(default=0)
    datasheet_url= models.URLField(max_length=500)
    component_type = models.CharField(max_length=100)
    unit_price = models.FloatField(default=0.0)
    comment = models.CharField(max_length=400)
    created_at = models.DateTimeField(auto_now_add=True)