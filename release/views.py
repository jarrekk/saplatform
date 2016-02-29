# -*- coding: utf-8 -*-
import os

from django.contrib.auth.decorators import login_required, permission_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext
from django.utils.encoding import force_text

from assets.models import Auth
from release.forms import TestForm, ProjectForm
from release.models import Project, ReleaseRecord, Test, PreRecord, RollBack
from release.tasks import mail_task, git_co_task
from saplatform.api import rrsync, set_log, git_co, http_success, http_error, paginator_fun, SaltApi, git_hash
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
    projects = Project.objects.all().order_by('name').values_list('name', flat=True).distinct()
    pre_records = PreRecord.objects.all()
    return render_to_response('release/pre_record.html', locals(), RequestContext(request))


@login_required()
def del_pre_record(request, ID):
    PreRecord.objects.get(id=ID).delete()
    return render_to_response('release/pre_record.html', locals(), RequestContext(request))


@login_required()
def complete_pre(request, ID):
    the_pre_record = PreRecord.objects.get(id=ID)
    the_release = Test.objects.all().get(id=the_pre_record.test_id)
    the_project = Project.objects.get(name=the_release.project)
    test_server_path = os.path.abspath(the_release.server_path)
    local_path = os.path.join('/ops/%s' % the_project.name, test_server_path.lstrip('/'), str(the_pre_record.test_id))
    branch = the_pre_record.branch
    os.chdir(local_path)
    os.system('git checkout master')
    os.system('git pull')
    os.system('git checkout %s' % branch)
    os.system('git pull')
    os.system('git checkout master')
    os.system('git merge %s -m "merge"' % branch)
    os.system('git push')
    PreRecord.objects.get(id=ID).delete()
    return render_to_response('release/pre_record.html', locals(), RequestContext(request))


@login_required()
def test(request):
    tests = Test.objects.all()
    for i in tests:
        i.host_list = list(eval(i.host_list))
    return render_to_response('release/test.html', locals(), RequestContext(request))


@permission_required('release.view_test', login_url='perm_deny')
def test_release(request, ID):
    the_release = Test.objects.get(id=str(ID))
    try:
        branch = request.GET["branch"]
    except:
        branch = ''
    if PreRecord.objects.all().filter(project=the_release.project):
        return http_error(request, u'发布失败,请查看预发布记录')
    else:
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
        the_release.last_hash = git_hash(local_path)
        the_release.save()
        return render_to_response('release/release_result.html', locals(), RequestContext(request))


@permission_required('release.view_test', login_url='perm_deny')
def pre_release(request, ID):
    the_release = Test.objects.all().get(id=str(ID))
    if PreRecord.objects.all().filter(project=the_release.project):
        return http_error(request, u'有项目分支正在预发布!')
    else:
        the_project = Project.objects.get(name=the_release.project)
        pre_host_list = list(eval(the_project.pre_host_list))
        test_server_path = os.path.abspath(the_release.server_path)
        pre_server_path = os.path.abspath(the_project.server_path)
        local_path = os.path.join('/ops/%s' % the_project.name, test_server_path.lstrip('/'), str(ID))
        for i in pre_host_list:
            stdout = rrsync(local_path, i, pre_server_path, ['.git*'])
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
        ln_path = os.path.abspath(the_project.server_path)
        test_server_path = os.path.abspath(the_release.server_path)
        pro_server_path = os.path.abspath(the_project.server_path) + "_%s" % the_release.last_hash
        local_path = os.path.join('/ops/%s' % the_project.name, test_server_path.lstrip('/'),
                                  str(the_pre_record.test_id))
        host_list_str = ','.join(pro_host_list)
        salt = SaltApi(SALTAPI_URL, SALTAPI_USER, SALTAPI_PASSWORD)
        salt.login()
        for i in pro_host_list:
            stdout = rrsync(local_path, i, pro_server_path, ['.git*'])
            result = stdout.replace('\n', '</br>')
        salt.cmd(host_list_str, 'rm -rf %s' % ln_path)
        salt.cmd(host_list_str, 'ln -s %s %s' % (pro_server_path, ln_path))
        salt.logout()
        try:
            the_rollback = RollBack.objects.get(in_use=True)
            the_rollback.in_use = False
            the_rollback.save()
        except:
            pass
        i_rollback = RollBack(project=the_project.name,
                               branch=the_release.last_branch,
                               hash=the_release.last_hash,
                               in_use=True)
        i_rollback.save()
        pro = ReleaseRecord(project=the_project.name,
                            branch=the_release.last_branch,
                            hash=the_release.last_hash,
                            release_user=request.user)
        pro.save()
        return render_to_response('release/release_result.html', locals(), RequestContext(request))
    except:
        return http_error(request, u'发布出现错误,请检查预发布记录')


@login_required()
def rollback(request):
    rollbacks = RollBack.objects.all()
    projects = Project.objects.all().order_by('name').values_list('name', flat=True).distinct()
    return render_to_response('release/rollback.html', locals(), RequestContext(request))


@login_required()
def del_rollback(request, ID):
    the_rollback = RollBack.objects.get(id=ID)
    if the_rollback.in_use:
        return http_error(request, u'不能删除正在使用的版本')
    else:
        the_project = Project.objects.get(name=the_rollback.project)
        pro_server_path = os.path.abspath(the_project.server_path) + "_%s" % the_rollback.hash
        pro_host_list = list(eval(the_project.pro_host_list))
        host_list_str = ','.join(pro_host_list)
        salt = SaltApi(SALTAPI_URL, SALTAPI_USER, SALTAPI_PASSWORD)
        salt.login()
        salt.cmd(host_list_str, 'rm -rf %s' % pro_server_path)
        salt.logout()
        the_rollback.delete()
        return http_success(request, u'版本删除成功')


@login_required()
def exec_rollback(request, ID):
    the_rollback = RollBack.objects.get(id=ID)
    if the_rollback.in_use:
        return http_error(request, u'正式环境为此版本')
    else:
        old_rollback = RollBack.objects.get(in_use=True)
        old_rollback.in_use = False
        old_rollback.save()
        the_project = Project.objects.get(name=the_rollback.project)
        ln_path = os.path.abspath(the_project.server_path)
        pro_server_path = os.path.abspath(the_project.server_path) + "_%s" % the_rollback.hash
        pro_host_list = list(eval(the_project.pro_host_list))
        host_list_str = ','.join(pro_host_list)
        salt = SaltApi(SALTAPI_URL, SALTAPI_USER, SALTAPI_PASSWORD)
        salt.login()
        salt.cmd(host_list_str, 'rm -f %s' % ln_path)
        salt.cmd(host_list_str, 'ln -s %s %s' % (pro_server_path, ln_path))
        salt.logout()
        the_rollback.in_use = True
        the_rollback.save()
        pro = ReleaseRecord(project=the_project.name,
                            branch=the_rollback.branch,
                            hash=the_rollback.hash,
                            release_user=request.user)
        pro.save()
        return http_success(request, u'版本回退成功')


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
    releases = ReleaseRecord.objects.all().order_by("-id")[:100]
    releases = paginator_fun(request, releases)
    return render_to_response('release/release_list.html', locals(), RequestContext(request))
