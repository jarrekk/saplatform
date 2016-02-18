# -*- coding: utf-8 -*-
from __future__ import absolute_import
from celery import task
from celery.utils.log import get_task_logger
# from celery import shared_task
from django.core.mail import send_mail
from saplatform.api import mysql_cmd
from saplatform.settings import EMAIL_HOST_USER
from database.models import SQLResult

logger = get_task_logger(__name__)


@task
def mail_task(subject, message, from_email, recipient_list, fail_silently):
    return send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list,
                     fail_silently=fail_silently)


@task
def mysql_cmd_task(host, username, password, sql, user):
    # return mysql_cmd(host, username, password, sql)
    result = mysql_cmd(host, username, password, sql)
    if not result:
        result = 'success'
    r = SQLResult(content=sql, result=str(result), user=user)