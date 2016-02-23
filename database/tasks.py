# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import task
from celery.utils.log import get_task_logger
# from celery import shared_task
from django.core.mail import send_mail
from saplatform.api import mysql_cmd, local_cmd
from saplatform.settings import SQL_DIRS, BASE_DIR
from database.models import SQLResult
import os

logger = get_task_logger(__name__)


@task
def mail_task(subject, message, from_email, recipient_list, fail_silently):
    return send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list,
                     fail_silently=fail_silently)


@task
def mysql_cmd_task(host, username, password, sql, user, sql_name):
    # return mysql_cmd(host, username, password, sql)
    result = mysql_cmd(host, username, password, sql)
    if not result:
        result = ({'result': 'success'},)
    r = SQLResult(content=sql, result=str(result), user=user, sql_name=sql_name)
    r.save()


@task
def script_mysql_task(host, username, password, sql, file_name, user):
    file_path = os.path.join(SQL_DIRS, file_name)
    cmd = "php %s/saplatform/scripts/SchemaTool.php %s %s %s %s" % (BASE_DIR, host, username, password, file_path)
    result = local_cmd(cmd)
    r = SQLResult(sql_name=file_name, content=sql, result=result, user=user)
    r.save()
