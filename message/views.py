# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render_to_response, RequestContext

from message.models import Alert
from saplatform.api import request_user_id


# Create your views here.

@login_required()
def alert(request):
    alerts = Alert.objects.filter(to_user_id=request_user_id(request)).order_by("-gen_time")
    num = alerts.count()
    return render_to_response('message/alert.html', locals(), RequestContext(request))


@login_required()
def delete_alert(request, ID):
    Alert.objects.get(id=ID).delete()
    return HttpResponse('ok')
