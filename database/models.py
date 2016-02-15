from django.db import models


# Create your models here.

class DbConfig(models.Model):
    name = models.CharField(max_length=64, unique=True)
    address = models.CharField(max_length=128, blank=True, null=True)
    auth = models.IntegerField(blank=True, null=True)
    desc = models.CharField(max_length=2014, blank=True, null=True)

