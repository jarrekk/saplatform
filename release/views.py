# -*- coding: utf-8 -*-
import datetime
import os

from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.utils.encoding import force_text

from assets.models import Auth
from release.forms import TestForm, ProjectForm
from release.models import Project, SvnControl, ReleaseRecord, Test, PreRecord, RollBack
from release.tasks import mail_task, git_co_task
from saplatform.api import rrsync, lrsync, set_log, git_co, http_success, http_error, paginator_fun, SaltApi
from saplatform.settings import EMAIL_HOST_USER, SALTAPI_URL, SALTAPI_USER, SALTAPI_PASSWORD


# Create your views here.


@login_required()
def project(request):
    projects = Project.objects.all()
    for i in projects:
        i.pre_host_list = list(eval(i.pre_host_list))
        i.pro_host_list = list(eval(i.pro_host_list))
    return render_to_response('release/project.html', locals(), RequestContext(request))


@permission_required('release.add_project', login_url='perm_deny')
def add_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project'))
    else:
        form = ProjectForm()
    return render_to_response('release/add_project.html', locals(), RequestContext(request))


@permission_required('release.change_project', login_url='perm_deny')
def edit_project(request, ID):
    the_project = Project.objects.get(id=str(ID))
    the_project.pre_host_list = list(eval(the_project.pre_host_list))
    the_project.pro_host_list = list(eval(the_project.pro_host_list))
    if request.method == "POST":
        form = ProjectForm(request.POST, instance=the_project)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('project'))
    else:
        form = ProjectForm(instance=the_project)
    return render_to_response('release/edit_project.html', locals(), RequestContext(request))


@login_required()
def pre_record(request):
    projects = SvnControl.objects.all().order_by('project').values_list('project', flat=True).distinct()
    pre_records = PreRecord.objects.all().order_by('-no_version')
    return render_to_response('release/pre_record.html', locals(), RequestContext(request))


# @permission_required('release.view_test', login_url='perm_deny')
# def svn_pre_result(request, ID):
#     the_svn = SvnControl.objects.get(id=str(ID))
#     the_project = Project.objects.get(name=the_svn.project)
#     the_auth = Auth.objects.get(id=the_project.auth)
#     username = the_auth.username if the_auth.username else ''
#     password = the_auth.password if the_auth.password else ''
#     pre_host_list = list(eval(the_project.pre_host_list))
#     pre_url = the_project.url.strip()
#     pre_no_version = the_svn.no_version
#     pre_server_path = os.path.abspath(the_project.server_path)
#     pre_local_path = os.path.join('/ops/pre', pre_server_path.lstrip('/'), str(ID))
#     # svn_co(pre_url, pre_local_path, pre_no_version, username, password)
#     for i in pre_host_list:
#         stdout = rrsync(pre_local_path, i, pre_server_path, ['.svn*', '.git*'])
#     pre = ReleaseRecord(project=the_project.name, environment=u'预发布', no_version=pre_no_version,
#                         release_user=request.user)
#     pre.save()
#     loger = set_log(level='debug', filename='pre_product_release_%s.log' % datetime.date.today().strftime('%Y-%m-%d'))
#     loger.debug('pre_product released by %s, detail : %s' % (request.user, stdout))
#     result = stdout.replace('\n', '</br>')
#     if request.user.email:
#         mail_task.delay(subject=u'项目 %s 预发布发布结果 版本号:%s' % (the_project.name, pre_no_version),
#                         message=stdout,
#                         from_email=EMAIL_HOST_USER,
#                         recipient_list=[request.user.email],
#                         fail_silently=False)
#     return render_to_response('release/svn_pre_result.html', locals(), RequestContext(request))
#
#
# @permission_required('release.view_test', login_url='perm_deny')
# @permission_required('release.view_project', login_url='perm_deny')
# def svn_pro_result(request, ID):
#     the_svn = SvnControl.objects.get(id=str(ID))
#     the_project = Project.objects.get(name=the_svn.project)
#     the_auth = Auth.objects.get(id=the_project.auth)
#     username = the_auth.username if the_auth.username else ''
#     password = the_auth.password if the_auth.password else ''
#     pro_host_list = list(eval(the_project.pro_host_list))
#     pro_url = the_project.url.strip()
#     pro_no_version = the_svn.no_version
#     pro_server_path = os.path.abspath(the_project.server_path)
#     pro_local_path = os.path.join('/ops/pro', pro_server_path.lstrip('/'), str(ID))
#     # svn_co(pro_url, pro_local_path, pro_no_version, username, password)
#     for i in pro_host_list:
#         stdout = rrsync(pro_local_path, i, pro_server_path, ['.svn*', '.git*'])
#     pro = ReleaseRecord(project=the_project.name, environment=u'正式', no_version=pro_no_version,
#                         release_user=request.user)
#     pro.save()
#     loger = set_log(level='debug', filename='product_release_%s.log' % datetime.date.today().strftime('%Y-%m-%d'))
#     loger.debug('product released by %s, detail : %s' % (request.user, stdout))
#     result = stdout.replace('\n', '</br>')
#     if request.user.email:
#         mail_task.delay(subject=u'项目 %s 正式发布结果 版本号:%s' % (the_project.name, pro_no_version),
#                         message=stdout,
#                         from_email=EMAIL_HOST_USER,
#                         recipient_list=[request.user.email],
#                         fail_silently=False)
#     return render_to_response('release/svn_pro_result.html', locals(), RequestContext(request))


@login_required()
def php(request):
    tests = Test.objects.all()
    for i in tests:
        i.host_list = list(eval(i.host_list))
    return render_to_response('release/test.html', locals(), RequestContext(request))


@login_required()
def nodejs(request):
    return render_to_response('release/nodejs.html', RequestContext(request))


@login_required()
def java(request):
    return render_to_response('release/java.html', RequestContext(request))


@permission_required('release.view_test', login_url='perm_deny')
def test_release(request, ID):
    try:
        branch = request.GET["branch"]
    except:
        branch = ''
    if PreRecord.objects.all() and PreRecord.objects.all()[0].test_id == ID:
        http_error(request, u'发布失败,请查看预发布记录')
    else:
        the_release = Test.objects.all().get(id=str(ID))
        host_list, server_path, stdout, before_cmd, after_cmd = list(eval(the_release.host_list)), os.path.abspath(
                the_release.server_path), '', the_release.before_cmd, the_release.after_cmd
        the_project = Project.objects.get(name=the_release.project)
        the_auth = Auth.objects.get(id=the_project.auth)
        key = force_text(the_auth.key) if the_auth.key else ''
        local_path = os.path.join('/ops/%s' % the_project.name, server_path.lstrip('/'), str(ID))
        repo_branch = the_release.last_branch if not branch else branch
        git_co(the_project.url, repo_branch, key, local_path)
        if before_cmd:
            os.chdir(local_path)
            os.system(before_cmd)
        for i in host_list:
            stdout = rrsync(local_path, i, server_path, ['.git*'])
            result = stdout.replace('\n', '</br>')
        the_release.last_branch = repo_branch
        the_release.save()
        return render_to_response('release/release_result.html', locals(), RequestContext(request))


@permission_required('release.view_test', login_url='perm_deny')
def pre_release(request, ID):
    if PreRecord.objects.all():
        return http_error(request, u'有项目分支正在预发布!')
    else:
        the_release = Test.objects.all().get(id=str(ID))
        the_project = Project.objects.get(name=the_release.project)
        pre_host_list = list(eval(the_project.pre_host_list))
        server_path = os.path.abspath(the_release.server_path)
        local_path = os.path.join('/ops/%s' % the_project.name, server_path.lstrip('/'), str(ID))
        for i in pre_host_list:
            stdout = rrsync(local_path, i, server_path, ['.git*'])
            result = stdout.replace('\n', '</br>')
        i_pre_release = PreRecord(project=the_project.name,
                                  branch=the_release.last_branch,
                                  hash=the_release.last_hash,
                                  test_id=the_release.id)
        i_pre_release.save()
        return render_to_response('release/release_result.html', locals(), RequestContext(request))


@permission_required('release.view_test', login_url='perm_deny')
def pro_release(request, ID):
    try:
        the_pre_record = PreRecord.objects.get(id=ID)
        the_release = Test.objects.all().get(id=the_pre_record.test_id)
        the_project = Project.objects.get(name=the_release.project)
        pro_host_list = list(eval(the_project.pro_host_list))
        ln_path = os.path.abspath(the_release.server_path)
        server_path = os.path.abspath(the_release.server_path)+"_%s" % the_release.last_hash
        local_path = os.path.join('/ops/%s' % the_project.name, server_path.lstrip('/'), str(ID))
        host_list_str = ','.join(pro_host_list)
        salt = SaltApi(SALTAPI_URL, SALTAPI_USER, SALTAPI_PASSWORD)
        salt.login()
        for i in pro_host_list:
            stdout = rrsync(local_path, i, server_path, ['.git*'])
            result = stdout.replace('\n', '</br>')
        salt.cmd(host_list_str, 'ln -s %s %s' % (server_path, ln_path))
        salt.logout()
        i_roll_back = RollBack(project=the_project.name,
                               branch=the_release.last_branch,
                               hash=the_release.last_hash)
        i_roll_back.save()
        pro = ReleaseRecord(project=the_project.name,
                            branch=the_release.last_branch,
                            hash=the_release.last_hash,
                            release_user=request.user)
        pro.save()
        return render_to_response('release/release_result.html', locals(), RequestContext(request))
    except:
        return http_error(request, u'发布出现错误,请检查预发布记录')


@login_required()
def nodejs_result(request):
    return render_to_response('release/nodejs.html', RequestContext(request))


@login_required()
def java_result(request):
    return render_to_response('release/nodejs.html', RequestContext(request))


@permission_required('release.add_test', login_url='perm_deny')
def add_test(request):
    if request.method == "POST":
        form = TestForm(request.POST)
        if form.is_valid():
            form.save()
            git_co_task.delay(0)
            return http_success(request, u'测试例添加成功')
    else:
        form = TestForm()
    return render_to_response('release/add_test.html', locals(), RequestContext(request))


@permission_required('release.change_test', login_url='perm_deny')
def edit_test(request, ID):
    the_test = Test.objects.get(id=ID)
    the_test.host_list = list(eval(the_test.host_list))
    if request.method == "POST":
        form = TestForm(request.POST, instance=the_test)
        if form.is_valid():
            form.save()
            git_co_task.delay(ID)
            return http_success(request, u'测试例修改成功')
    else:
        form = TestForm(instance=the_test)
    return render_to_response('release/edit_test.html', locals(), RequestContext(request))


@login_required()
def release_record(request):
    releases = ReleaseRecord.objects.all().order_by("-id")
    releases = paginator_fun(request, releases)
    return render_to_response('release/release_list.html', locals(), RequestContext(request))
