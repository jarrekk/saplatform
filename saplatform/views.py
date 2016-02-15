# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from saplatform.api import *
import datetime


@login_required()
def index(request):
    content = u'欢迎来到自动化运维系统!'
    username = request.user
    nowtime = datetime.datetime.now()
    '''
    日志使用和邮件使用例子
    '''
    # logger.debug('user login')
    # send_mail(subject='publish result', message='test', from_email=EMAIL_HOST_USER,
    #           recipient_list=[request.user.email], fail_silently=False)
    return render_to_response('index.html', locals(), RequestContext(request))


def skin_config(request):
    return render_to_response('skin_config.html')


def perm_deny(request):
    return render_to_response('perm_deny.html', locals(), RequestContext(request))


def server404(request):
    return render_to_response('404.html', locals(), RequestContext(request))
