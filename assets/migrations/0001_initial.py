# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Assets',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hostname', models.CharField(max_length=32, null=True, blank=True)),
                ('group', models.CharField(max_length=32, null=True, blank=True)),
                ('lan_ip', models.CharField(unique=True, max_length=24)),
                ('wlan_ip', models.CharField(max_length=64, null=True, blank=True)),
                ('auth', models.IntegerField(null=True, blank=True)),
                ('mac', models.CharField(max_length=32, null=True, blank=True)),
                ('kernel', models.CharField(max_length=32, null=True, blank=True)),
                ('kernel_version', models.CharField(max_length=64, null=True, blank=True)),
                ('cpu_model', models.CharField(max_length=64, null=True, blank=True)),
                ('cpu_num', models.CharField(max_length=4, null=True, blank=True)),
                ('memory', models.CharField(max_length=128, null=True, blank=True)),
                ('disk', models.CharField(max_length=1024, null=True, blank=True)),
                ('system_type', models.CharField(max_length=32, null=True, blank=True)),
                ('system_version', models.CharField(max_length=8, null=True, blank=True)),
                ('system_arch', models.CharField(max_length=16, null=True, blank=True)),
                ('service', models.CharField(max_length=128, null=True, blank=True)),
                ('status', models.CharField(max_length=16, null=True, blank=True)),
                ('sa', models.CharField(max_length=24, null=True, blank=True)),
                ('environment', models.CharField(max_length=24, null=True, blank=True)),
                ('desc', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssetsGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64)),
                ('usage', models.CharField(max_length=128, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Auth',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64)),
                ('username', models.CharField(max_length=24, null=True, blank=True)),
                ('password', models.CharField(max_length=24, null=True, blank=True)),
                ('key', models.CharField(max_length=256, null=True, blank=True)),
                ('port', models.IntegerField(null=True, blank=True)),
            ],
        ),
    ]
