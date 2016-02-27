from django.db import models
# from django.db.models import Q


# Create your models here.

class Test(models.Model):
    name = models.CharField(max_length=64, unique=True)
    project = models.CharField(max_length=64, blank=True, null=True)
    before_cmd = models.CharField(max_length=256, blank=True, null=True)
    after_cmd = models.CharField(max_length=256, blank=True, null=True)
    last_branch = models.CharField(max_length=64, null=True, blank=True)
    last_hash = models.CharField(max_length=16, null=True, blank=True)
    host_list = models.TextField(blank=True, null=True)
    server_path = models.CharField(max_length=256, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)


class SvnControl(models.Model):
    project = models.CharField(max_length=64, blank=True, null=True)
    no_version = models.IntegerField(blank=True, null=True)
    ci_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    desc = models.TextField(blank=True, null=True)


class Project(models.Model):
    name = models.CharField(max_length=64, unique=True)
    code_type = models.CharField(max_length=24, blank=True, null=True)
    url = models.CharField(max_length=192, unique=True)
    auth = models.IntegerField(blank=True, null=True)
    pre_host_list = models.TextField(blank=True, null=True)
    pro_host_list = models.TextField(blank=True, null=True)
    server_path = models.CharField(max_length=256, blank=True, null=True)


class ReleaseRecord(models.Model):
    project = models.CharField(max_length=64, blank=True, null=True)
    branch = models.CharField(max_length=64, blank=True, null=True)
    hash = models.CharField(max_length=16, blank=True, null=True)
    release_time = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    release_user = models.CharField(max_length=64, blank=True, null=True)


class PreRecord(models.Model):
    project = models.CharField(max_length=64, blank=True, null=True)
    branch = models.CharField(max_length=64, null=True, blank=True)
    hash = models.CharField(max_length=16, null=True, blank=True)
    test_id = models.CharField(max_length=16, null=True, blank=True)


class RollBack(models.Model):
    project = models.CharField(max_length=64, blank=True, null=True)
    branch = models.CharField(max_length=64, null=True, blank=True)
    hash = models.CharField(max_length=16, null=True, blank=True)
    time = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    in_use = models.BooleanField(default=False)
