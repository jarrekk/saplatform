# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64)),
                ('code_type', models.CharField(max_length=24, null=True, blank=True)),
                ('url', models.CharField(unique=True, max_length=192)),
                ('auth', models.IntegerField(null=True, blank=True)),
                ('pre_host_list', models.TextField(null=True, blank=True)),
                ('pro_host_list', models.TextField(null=True, blank=True)),
                ('server_path', models.CharField(max_length=256, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project', models.CharField(max_length=64, null=True, blank=True)),
                ('environment', models.CharField(max_length=24, null=True, blank=True)),
                ('no_version', models.IntegerField(null=True, blank=True)),
                ('release_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('release_user', models.CharField(max_length=64, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SvnControl',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('project', models.CharField(max_length=64, null=True, blank=True)),
                ('no_version', models.IntegerField(null=True, blank=True)),
                ('ci_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('desc', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64)),
                ('project', models.CharField(max_length=64, null=True, blank=True)),
                ('code_type', models.CharField(max_length=24, null=True, blank=True)),
                ('repo_type', models.CharField(max_length=16, null=True, blank=True)),
                ('repo_url', models.CharField(max_length=256, null=True, blank=True)),
                ('before_cmd', models.CharField(max_length=256, null=True, blank=True)),
                ('after_cmd', models.CharField(max_length=256, null=True, blank=True)),
                ('auth', models.IntegerField(null=True, blank=True)),
                ('branch', models.CharField(max_length=1024, null=True, blank=True)),
                ('last_branch', models.CharField(max_length=64, null=True, blank=True)),
                ('host_list', models.TextField(null=True, blank=True)),
                ('server_path', models.CharField(max_length=256, null=True, blank=True)),
                ('desc', models.TextField(null=True, blank=True)),
            ],
        ),
    ]
