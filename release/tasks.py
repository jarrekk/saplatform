# -*- coding: utf-8 -*-
from __future__ import absolute_import

from celery import task
from celery.utils.log import get_task_logger

# from celery import shared_task
from django.core.mail import send_mail
from release.models import Test
from assets.models import Auth
from django.utils.encoding import force_text
from saplatform.api import git_co
import svn.remote
import svn.local
import os

logger = get_task_logger(__name__)


@task
def mail_task(subject, message, from_email, recipient_list, fail_silently):
    return send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list,
                     fail_silently=fail_silently)


@task
def git_co_task(ID):
    if ID != 0:
        the_test = Test.objects.get(id=ID)
    else:
        the_test = Test.objects.order_by('-id')[0]
    if the_test.repo_type == 'git':
        local_path = os.path.join('/ops/test', the_test.server_path.lstrip('/'), str(the_test.id))
        the_auth = Auth.objects.get(id=the_test.auth)
        key = force_text(the_auth.key) if the_auth.key else ''
        git_co(the_test.repo_url, '', key, local_path)
        the_test.branch = '["master"]'
        # the_test.branch = str(git_branch(the_test.repo_url, key, local_path))
        the_test.save()
    else:
        the_test.branch = '["master"]'
        the_test.save()


@task
def svn_co_task(svn_url, local_path, versionnum, username, password):
    if os.path.exists(local_path):
        pass
    else:
        os.makedirs(local_path)
    if username and password:
        r = svn.remote.RemoteClient(svn_url, username=username, password=password)
    else:
        r = svn.remote.RemoteClient(svn_url)
    if str(versionnum):
        r.checkout(local_path)
        os.chdir(local_path)
        os.system('svn up -r %s' % str(versionnum))
    else:
        r.checkout(local_path)
