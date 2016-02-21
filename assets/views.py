# -*- coding: utf-8 -*-
import os

from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.utils.encoding import force_text

from assets.forms import AssetsForm, AuthForm
from assets.models import Auth, Assets
from saplatform.api import sftp, ssh_cmd, SaltApi, sizeformat
from saplatform.settings import BASE_DIR, SALTAPI_URL, SALTAPI_USER, SALTAPI_PASSWORD, SALT_MASTER


# Create your views here.


@login_required()
def assets(request):
    hosts = Assets.objects.all()
    return render_to_response('assets/assets.html', locals(), RequestContext(request))


@permission_required('assets.add_assets', login_url='perm_deny')
def add_assets(request):
    if request.method == "POST":
        form = AssetsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('assets'))
    else:
        form = AssetsForm()
    return render_to_response('assets/add_assets.html', locals(), RequestContext(request))


@permission_required('assets.change_assets', login_url='perm_deny')
def edit_assets(request, ID):
    the_asset = Assets.objects.get(id=ID)
    if request.method == "POST":
        form = AssetsForm(request.POST, instance=the_asset)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('assets'))
    else:
        form = AssetsForm(instance=the_asset)
    return render_to_response('assets/edit_assets.html', locals(), RequestContext(request))


@permission_required('assets.change_assets', login_url='perm_deny')
def assets_init(request, ID):
    the_asset = Assets.objects.get(id=ID)
    ip = the_asset.lan_ip
    authid = the_asset.auth
    the_auth = Auth.objects.get(id=authid)
    port = the_auth.port if the_auth.port else 22
    username = the_auth.username if the_auth.username else ''
    password = the_auth.password if the_auth.password else ''
    key = force_text(the_auth.key) if the_auth.key else ''
    sftp(ip, port, username, password, key, os.path.join(BASE_DIR, 'saplatform/scripts/init.sh'), '/tmp/init.sh')
    stdout = ssh_cmd(ip, port, username, password, key, '/bin/sh /tmp/init.sh %s %s' % (SALT_MASTER, ip))
    ssh_cmd(ip, port, username, password, key, 'rm -rf /tmp/init.sh')
    result = u'操作完成!'
    return render_to_response('assets/init_result.html', locals(), RequestContext(request))


@permission_required('assets.add_assets', login_url='perm_deny')
def assets_info(request, ID):
    salt_api = SaltApi(SALTAPI_URL, SALTAPI_USER, SALTAPI_PASSWORD)
    salt_api.login()
    the_asset = Assets.objects.get(id=ID)
    ip = the_asset.lan_ip
    res = eval(salt_api.fun(ip, 'grains.items'))['return'][0][ip]
    the_asset.hostname = res['host']
    the_asset.mac = res['hwaddr_interfaces']['eth0']
    the_asset.cpu_model = res['cpu_model']
    the_asset.cpu_num = res['num_cpus']
    the_asset.memory = sizeformat(res['mem_total'], unit='MB')
    the_asset.system_type = res['os']
    the_asset.system_version = '.'.join(map(str, res['osrelease_info'])) if type(res['osrelease_info']) == list else str(
            res['osrelease_info'])
    the_asset.system_arch = res['osarch']
    the_asset.kernel = res['kernel']
    the_asset.kernel_version = res['kernelrelease']
    res = eval(salt_api.fun(ip, 'disk.usage'))['return'][0][ip]
    disk_status = 'Disk Usage:</br>'
    for key1 in res.keys():
        disk_status += key1 + ':</br>'
        for key2 in res[key1]:
            if key2 in ['available', 'used', ]:
                disk_status += '%s -- %s</br>' % (key2, sizeformat(res[key1][key2], unit='KB'))
            elif key2 in ['filesystem']:
                disk_status += '%s -- %s</br>' % (key2, res[key1][key2])
    the_asset.desc = disk_status
    the_asset.save()
    salt_api.logout()
    hosts = Assets.objects.all()
    return render_to_response('assets/assets.html', locals(), RequestContext(request))


@login_required()
def auth(request):
    auths = Auth.objects.all()
    return render_to_response('assets/auth.html', locals(), RequestContext(request))


@permission_required('assets.add_auth', login_url='perm_deny')
def add_auth(request):
    if request.method == "POST":
        form = AuthForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('auth'))
    else:
        form = AuthForm()
    return render_to_response('assets/add_auth.html', locals(), RequestContext(request))


@permission_required('assets.change_auth', login_url='perm_deny')
def edit_auth(request, ID):
    the_auth = Auth.objects.get(id=ID)
    if request.method == "POST":
        form = AuthForm(request.POST, instance=the_auth)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('auth'))
    else:
        form = AuthForm(instance=the_auth)
    return render_to_response('assets/edit_auth.html', locals(), RequestContext(request))
