from django.db import models


# Create your models here.

class DbConfig(models.Model):
    name = models.CharField(max_length=64, unique=True)
    address = models.CharField(max_length=128, blank=True, null=True)
    auth = models.IntegerField(blank=True, null=True)
    desc = models.CharField(max_length=1024, blank=True, null=True)


class SQLResult(models.Model):
    sql_name = models.CharField(max_length=64, blank=True, null=True)
    content = models.CharField(max_length=1024, blank=True, null=True)
    exec_time = models.DateTimeField(blank=True, null=True, auto_now_add=True)
    result = models.TextField(blank=True, null=True)
    user = models.CharField(max_length=64, blank=True, null=True)
