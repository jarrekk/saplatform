# -*- coding: utf-8 -*-
from __future__ import absolute_import

from celery import task
from celery.utils.log import get_task_logger

# from celery import shared_task
from django.core.mail import send_mail
from release.models import Test, Project
from assets.models import Auth
from django.utils.encoding import force_text
from saplatform.api import git_co, git_hash
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
    the_project = Project.objects.get(name=the_test.project)
    the_auth = Auth.objects.get(id=the_project.auth)
    local_path = os.path.join('/ops/%s' % the_test.project, the_test.server_path.lstrip('/'), str(the_test.id))
    key = force_text(the_auth.key) if the_auth.key else ''
    git_co(the_project.url, '', key, local_path)
    the_test.last_branch = 'master'
    the_test.last_hash = git_hash(local_path)
    the_test.save()


@task
def svn_co_task(svn_url, local_path, versionnum, username, password):
    if os.path.exists(local_path):
        pass
    else:
        os.makedirs(local_path)
    if username and password:
        # os.system('svn co %s %s --username %s --password %s' % (svn_url, local_path, username, password))
        r = svn.remote.RemoteClient(svn_url, username=username, password=password)
    else:
        # os.system('svn co %s %s' % (svn_url, local_path))
        r = svn.remote.RemoteClient(svn_url)
    if str(versionnum):
        r.checkout(local_path)
        os.chdir(local_path)
        os.system('svn up -r %s' % str(versionnum))
    else:
        r.checkout(local_path)
