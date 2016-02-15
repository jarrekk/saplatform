# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GroupPerm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_id', models.IntegerField(unique=True)),
                ('perm_list', models.CharField(max_length=1024, null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserPerm',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user_id', models.IntegerField(unique=True)),
                ('group_list', models.CharField(max_length=1024, null=True, blank=True)),
                ('perm_list', models.CharField(max_length=2014, null=True, blank=True)),
            ],
        ),
    ]
