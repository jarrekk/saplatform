# -*- coding: utf-8 -*-
import logging
import os

from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from message.models import Alert
from req import request_user_id
from saplatform.settings import LOG_DIRS


def set_log(level, filename='saplatform.log'):
    log_file = os.path.join(LOG_DIRS, filename)
    if not os.path.isfile(log_file):
        os.mknod(log_file)
        os.chmod(log_file, 0777)
    log_level_total = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARN, 'error': logging.ERROR,
                       'critical': logging.CRITICAL}
    logger_f = logging.getLogger('saplatform')
    logger_f.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file)
    fh.setLevel(log_level_total.get(level, logging.DEBUG))
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger_f.addHandler(fh)
    return logger_f


def admin_required():
    def _deco(func):
        def __deco(request, *args, **kwargs):
            if not request.user.is_superuser:
                return HttpResponseRedirect(reverse('perm_deny'))
            return func(request, *args, **kwargs)

        return __deco

    return _deco


def paginator_fun(request, objects):
    paginator = Paginator(objects, 25)
    page = request.GET.get('page')
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    return objects


def alert(request, text):
    a = Alert(text=text, to_user_id=request_user_id(request))
    a.save()
