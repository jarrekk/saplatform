# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, RequestContext


def my_render(template, data, request):
    return render_to_response(template, data, context_instance=RequestContext(request))


def http_success(request, msg):
    return render_to_response('success.html', locals())


def http_error(request, emg):
    message = emg
    return render_to_response('error.html', locals())


def request_user_id(request):
    request_user = User.objects.get(username=request.user)
    return request_user.id


# def message(title, text, msg_type, to_user_id, from_user_id, status=0):
#     m = Message(title=title, text=text, msg_type=msg_type, to_user_id=to_user_id, from_user_id=from_user_id,
#                 status=status)
#     m.save()

# logger = set_log(level='debug')

# if __name__ == '__main__':
#     salttest = SaltApi('https://192.168.10.80:8000', 'salttest', 'salttest')
#     salttest.login()
#     result = salttest.cmd('192.168.10.82', 'ip a')
#     print result
