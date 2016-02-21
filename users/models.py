# -*- coding: utf-8 -*-  
import datetime

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.db import models


class ProfileBase(type):
    def __new__(cls, name, bases, attrs):
        module = attrs.pop('__module__')
        parents = [b for b in bases if isinstance(b, ProfileBase)]
        if parents:
            fields = []
            for obj_name, obj in attrs.items():
                if isinstance(obj, models.Field): fields.append(obj_name)
                User.add_to_class(obj_name, obj)
            UserAdmin.fieldsets = list(UserAdmin.fieldsets)
            UserAdmin.fieldsets.append((name, {'fields': fields}))
        return super(ProfileBase, cls).__new__(cls, name, bases, attrs)


class Profile(object):
    __metaclass__ = ProfileBase


class MyProfile(Profile):
    nickname = models.CharField(max_length=255, blank=True, null=True)
    tel = models.BigIntegerField(blank=True, null=True)
    birthday = models.DateField(null=True, blank=True)
    city = models.CharField(max_length=32, blank=True, null=True)
    sex = models.CharField(max_length=4, blank=True, null=True)
    headimg = models.FileField(blank=True, null=True, upload_to='./static/images/touxiang/',
                               default='./static/images/touxiang/tou.gif')

    def is_today_birthday(self):
        return self.birthday.date() == datetime.date.today()


class UserPerm(models.Model):
    user_id = models.IntegerField(unique=True)
    group_list = models.CharField(max_length=1024, blank=True, null=True)
    perm_list = models.CharField(max_length=2014, blank=True, null=True)


class GroupPerm(models.Model):
    group_id = models.IntegerField(unique=True)
    perm_list = models.CharField(max_length=1024, blank=True, null=True)
