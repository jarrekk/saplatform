from django.db import models


# Create your models here.
# class AssetsManager(models.Manager):
#     def KeyWord(self,keyword):
#         return self.filter(Q(sa__icontains=keyword))


class Assets(models.Model):
    hostname = models.CharField(max_length=32, blank=True, null=True)
    group = models.CharField(max_length=32, blank=True, null=True)
    lan_ip = models.CharField(max_length=24, unique=True)
    wlan_ip = models.CharField(max_length=64, blank=True, null=True)
    auth = models.IntegerField(blank=True, null=True)
    mac = models.CharField(max_length=32, blank=True, null=True)
    kernel = models.CharField(max_length=32, blank=True, null=True)
    kernel_version = models.CharField(max_length=64, blank=True, null=True)
    cpu_model = models.CharField(max_length=64, blank=True, null=True)
    cpu_num = models.CharField(max_length=4, blank=True, null=True)
    memory = models.CharField(max_length=128, blank=True, null=True)
    disk = models.CharField(max_length=1024, blank=True, null=True)
    system_type = models.CharField(max_length=32, blank=True, null=True)
    system_version = models.CharField(max_length=8, blank=True, null=True)
    system_arch = models.CharField(max_length=16, blank=True, null=True)
    service = models.CharField(max_length=128, blank=True, null=True)
    status = models.CharField(max_length=16, blank=True, null=True)
    sa = models.CharField(max_length=24, blank=True, null=True)
    environment = models.CharField(max_length=24, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)
    # objects=AssetsManager()


class AssetsGroup(models.Model):
    name = models.CharField(max_length=64, unique=True)
    usage = models.CharField(max_length=128, blank=True, null=True)


class Auth(models.Model):
    name = models.CharField(max_length=64, unique=True)
    username = models.CharField(max_length=24, blank=True, null=True)
    password = models.CharField(max_length=24, blank=True, null=True)
    key = models.CharField(max_length=256, blank=True, null=True)
    port = models.IntegerField(blank=True, null=True)
