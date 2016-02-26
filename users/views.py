# -*- coding: utf-8 -*-
from __future__ import absolute_import

import random
import sys

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext

from saplatform.api import http_success, admin_required, en2cn, alert
from saplatform.settings import EMAIL_HOST_USER
from users.forms import UserPermForm, AddGroupFrom, AddUserFrom, LoginForm, ChangePasswordForm, ForgetPasswordForm, \
    ProfileFrom, GroupPermForm
from users.models import UserPerm, GroupPerm
from users.tasks import mail_task
# from celery.task.http import URL

reload(sys)
sys.setdefaultencoding("utf-8")


# Create your views here.


def login(request):
    form = LoginForm()
    error = ''
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('index'))
    if request.method == 'GET':
        return render_to_response('users/login.html', locals(), RequestContext(request))
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        if username and password:
            user = auth.authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    auth.login(request, user)
                    return HttpResponseRedirect(request.session.get('pre_url', '/'))
                else:
                    error = u'用户未激活'
            else:
                error = u'用户名或密码错误'
        else:
            error = u'用户名或密码错误'
    return render_to_response('users/login.html', locals(), RequestContext(request))


@login_required()
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required()
def profile(request):
    username = request.user
    the_user = User.objects.get(username=username)
    user_perm_list = list(the_user.get_all_permissions())
    for i in range(len(user_perm_list)):
        user_perm_list[i] = en2cn(user_perm_list[i].split('.')[1])
    # group_perm_list = list(the_user.get_group_permissions())
    # for i in range(len(group_perm_list)):
    #     group_perm_list[i] = en2cn(group_perm_list[i].split('.')[1])
    if request.method == 'POST':
        form = ProfileFrom(request.POST, request.FILES, instance=the_user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('index'))
    else:
        form = ProfileFrom(instance=the_user)
    return render_to_response('users/profile.html', locals(), RequestContext(request))


@login_required()
def change_password(request):
    form = ChangePasswordForm()
    error = ''
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        user = auth.authenticate(username=request.user, password=old_password)
        if user is not None:
            if new_password1 == new_password2:
                if len(new_password1) >= 6:
                    user = auth.get_user(request)
                    user.set_password(new_password2)
                    user.save()
                    return HttpResponseRedirect(reverse('index'))
                else:
                    error = u'新密码长度小于6位'
            else:
                error = u'两次输入不匹配'
        else:
            error = u'原密码错误'
        return render_to_response('users/change_password.html', locals(), RequestContext(request))
    else:
        return render_to_response('users/change_password.html', locals(), RequestContext(request))


def forget_password(request):
    form = ForgetPasswordForm()
    error = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        the_user = User.objects.get(username=username)
        if the_user.email == email:
            new_password = ''.join(
                    random.sample([chr(i) for i in range(97, 123)] + [chr(i) for i in range(65, 91)], 8)).replace(
                    ' ', '')
            the_user.set_password(new_password)
            the_user.save()
            # res = URL('%s/tasks/mail' % LOCAL_URL).get_async(subject='test',
            #                                            message='success',
            #                                            from_email=EMAIL_HOST_USER,
            #                                            recipient_list='[the_user.email]',
            #                                            fail_silently=False)
            #
            mail_task.delay(subject=u'用户 %s 密码找回' % the_user.username,
                            message=u'Hi %s:你的新密码为: %s ,请重新登录.' % (the_user.username, new_password),
                            from_email=EMAIL_HOST_USER, recipient_list=[the_user.email], fail_silently=False)
            return http_success(request, u'密码重置成功')
        else:
            error = u'用户名邮箱不匹配'
        return render_to_response('users/forget_password.html', locals(), RequestContext(request))
    else:
        return render_to_response('users/forget_password.html', locals(), RequestContext(request))


@admin_required()
def user_list(request):
    users = User.objects.filter(id__gt=0)
    return render_to_response('users/users.html', locals(), RequestContext(request))


@admin_required()
def add_user(request):
    if request.method == 'POST':
        form = AddUserFrom(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            the_user = User.objects.get(username=request.POST.get('username'))
            the_user.set_password(request.POST.get('password'))
            the_user.save()
            user_perm = UserPerm(user_id=the_user.id)
            user_perm.save()
            alert(request, u'用户%s已添加.' % the_user.username)
            return HttpResponseRedirect(reverse('user_list'))
    else:
        form = AddUserFrom()
    return render_to_response('users/add_user.html', locals(), RequestContext(request))


@admin_required()
def edit_user(request, ID):
    the_user = User.objects.get(id=ID)
    if request.method == 'POST':
        form = ProfileFrom(request.POST, request.FILES, instance=the_user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user_list'))
    else:
        form = ProfileFrom(instance=the_user)
    return render_to_response('users/edit_user.html', locals(), RequestContext(request))


@admin_required()
def delete_user(request, ID):
    User.objects.get(id=ID).delete()
    UserPerm.objects.get(user_id=ID).delete()
    return 'ok'
    # return HttpResponseRedirect(reverse('user_list'))


@admin_required()
def group_list(request):
    groups = Group.objects.all()
    return render_to_response('users/groups.html', locals(), RequestContext(request))


@admin_required()
def add_group(request):
    if request.method == 'POST':
        form = AddGroupFrom(request.POST)
        if form.is_valid():
            form.save()
            the_group = Group.objects.get(name=request.POST.get('name'))
            group_perm = GroupPerm(group_id=the_group.id)
            group_perm.save()
            alert(request, u'用户组%s已添加.' % the_group.name)
            return HttpResponseRedirect(reverse('group_list'))
    else:
        form = AddGroupFrom()
    return render_to_response('users/add_group.html', locals(), RequestContext(request))


@admin_required()
def edit_group(request, ID):
    the_group = Group.objects.get(id=ID)
    if request.method == 'POST':
        form = AddGroupFrom(request.POST, instance=the_group)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('group_list'))
    else:
        form = AddGroupFrom(instance=the_group)
    return render_to_response('users/edit_group.html', locals(), RequestContext(request))


@admin_required()
def delete_group(request, ID):
    Group.objects.get(id=ID).delete()
    GroupPerm.objects.get(group_id=ID).delete()
    return HttpResponseRedirect(reverse('group_list'))


@admin_required()
def user2perm(request, ID):
    the_user = User.objects.get(id=ID)
    the_user_perm = UserPerm.objects.get(user_id=ID)
    the_user_perm.perm_list = list(eval(the_user_perm.perm_list)) if the_user_perm.perm_list else []
    the_user_perm.group_list = list(eval(the_user_perm.group_list)) if the_user_perm.group_list else []
    if request.method == 'POST':
        form = UserPermForm(request.POST, instance=the_user_perm)
        if form.is_valid():
            form.save()
            perms = list(eval(UserPerm.objects.get(user_id=ID).perm_list))
            groups = list(eval(UserPerm.objects.get(user_id=ID).group_list))
            the_user.user_permissions.clear()
            for i in perms:
                the_user.user_permissions.add(i)
            the_user.groups.clear()
            for i in groups:
                the_user.groups.add(i)
            return HttpResponseRedirect(reverse('user_list'))
    else:
        form = UserPermForm(instance=the_user_perm)
    return render_to_response('users/user2perm.html', locals(), RequestContext(request))


@admin_required()
def group2perm(request, ID):
    the_group = Group.objects.get(id=ID)
    the_group_perm = GroupPerm.objects.get(group_id=ID)
    the_group_perm.perm_list = list(eval(the_group_perm.perm_list)) if the_group_perm.perm_list else []
    if request.method == 'POST':
        form = GroupPermForm(request.POST, instance=the_group_perm)
        if form.is_valid():
            form.save()
            perms = list(eval(GroupPerm.objects.get(group_id=ID).perm_list))
            the_group.permissions.clear()
            for i in perms:
                the_group.permissions.add(i)
            return HttpResponseRedirect(reverse('group_list'))
    else:
        form = GroupPermForm(instance=the_group_perm)
    return render_to_response('users/group2perm.html', locals(), RequestContext(request))
