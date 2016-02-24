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
from release.models import Project, SvnControl, ReleaseRecord, Test
from release.tasks import mail_task, git_co_task
from saplatform.api import svn_co, svn_commit, svn_version, rrsync, lrsync, set_log, git_co, http_success, paginator_fun
from saplatform.settings import EMAIL_HOST_USER

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
def svn(request):
    projects = SvnControl.objects.all().order_by('project').values_list('project', flat=True).distinct()
    svns = SvnControl.objects.all().order_by('-no_version')[:25]
    return render_to_response('release/svn.html', locals(), RequestContext(request))


@permission_required('release.view_test', login_url='perm_deny')
def svn_pre_result(request, ID):
    the_svn = SvnControl.objects.get(id=str(ID))
    the_project = Project.objects.get(name=the_svn.project)
    the_auth = Auth.objects.get(id=the_project.auth)
    username = the_auth.username if the_auth.username else ''
    password = the_auth.password if the_auth.password else ''
    pre_host_list = list(eval(the_project.pre_host_list))
    pre_url = the_project.url.strip()
    pre_no_version = the_svn.no_version
    pre_server_path = os.path.abspath(the_project.server_path)
    pre_local_path = os.path.join('/ops/pre', pre_server_path.lstrip('/'), str(ID))
    svn_co(pre_url, pre_local_path, pre_no_version, username, password)
    for i in pre_host_list:
        stdout = rrsync(pre_local_path, i, pre_server_path, ['.svn*', '.git*'])
    pre = ReleaseRecord(project=the_project.name, environment=u'预发布', no_version=pre_no_version, release_user=request.user)
    pre.save()
    loger = set_log(level='debug', filename='pre_product_release_%s.log' % datetime.date.today().strftime('%Y-%m-%d'))
    loger.debug('pre_product released by %s, detail : %s' % (request.user, stdout))
    result = stdout.replace('\n', '</br>')
    if request.user.email:
        mail_task.delay(subject=u'项目 %s 预发布发布结果 版本号:%s' % (the_project.name, pre_no_version),
                        message=stdout,
                        from_email=EMAIL_HOST_USER,
                        recipient_list=[request.user.email],
                        fail_silently=False)
    return render_to_response('release/svn_pre_result.html', locals(), RequestContext(request))


@permission_required('release.view_test', login_url='perm_deny')
@permission_required('release.view_project', login_url='perm_deny')
def svn_pro_result(request, ID):
    the_svn = SvnControl.objects.get(id=str(ID))
    the_project = Project.objects.get(name=the_svn.project)
    the_auth = Auth.objects.get(id=the_project.auth)
    username = the_auth.username if the_auth.username else ''
    password = the_auth.password if the_auth.password else ''
    pro_host_list = list(eval(the_project.pro_host_list))
    pro_url = the_project.url.strip()
    pro_no_version = the_svn.no_version
    pro_server_path = os.path.abspath(the_project.server_path)
    pro_local_path = os.path.join('/ops/pro', pro_server_path.lstrip('/'), str(ID))
    svn_co(pro_url, pro_local_path, pro_no_version, username, password)
    for i in pro_host_list:
        stdout = rrsync(pro_local_path, i, pro_server_path, ['.svn*', '.git*'])
    pro = ReleaseRecord(project=the_project.name, environment=u'正式', no_version=pro_no_version, release_user=request.user)
    pro.save()
    loger = set_log(level='debug', filename='product_release_%s.log' % datetime.date.today().strftime('%Y-%m-%d'))
    loger.debug('product released by %s, detail : %s' % (request.user, stdout))
    result = stdout.replace('\n', '</br>')
    if request.user.email:
        mail_task.delay(subject=u'项目 %s 正式发布结果 版本号:%s' % (the_project.name, pro_no_version),
                        message=stdout,
                        from_email=EMAIL_HOST_USER,
                        recipient_list=[request.user.email],
                        fail_silently=False)
    return render_to_response('release/svn_pro_result.html', locals(), RequestContext(request))


@login_required()
def php(request):
    tests = Test.objects.all().filter(code_type='php')
    for i in tests:
        i.host_list = list(eval(i.host_list))
    return render_to_response('release/php.html', locals(), RequestContext(request))


@login_required()
def nodejs(request):
    return render_to_response('release/nodejs.html', RequestContext(request))


@login_required()
def java(request):
    return render_to_response('release/java.html', RequestContext(request))


@permission_required('release.view_test', login_url='perm_deny')
def php_result(request, ID):
    try:
        branch = request.GET["branch"]
    except:
        branch = ''
    test_release = Test.objects.all().get(id=str(ID))
    host_list, repo_type, repo_url, repo_last_branch, test_auth, server_path, stdout, before_cmd, after_cmd = \
        list(eval(test_release.host_list)), test_release.repo_type, test_release.repo_url.strip(), \
        test_release.last_branch, test_release.auth, os.path.abspath(
                test_release.server_path), '', test_release.before_cmd, test_release.after_cmd
    the_auth = Auth.objects.get(id=test_auth)
    username = the_auth.username if the_auth.username else ''
    password = the_auth.password if the_auth.password else ''
    key = force_text(the_auth.key) if the_auth.key else ''
    local_path = os.path.join('/ops/test', server_path.lstrip('/'), str(ID))
    repo_branch = repo_last_branch if not branch else branch
    if repo_type == 'git':
        git_co(repo_url, repo_branch, key, local_path)
        if before_cmd:
            os.chdir(local_path)
            os.system(before_cmd)
        for i in host_list:
            stdout = rrsync(local_path, i, server_path, ['.svn*', '.git*'])
            result = stdout.replace('\n', '</br>')
        test_release.last_branch = repo_branch
        test_release.save()
    else:
        svn_co(repo_url, local_path, '', username, password)
        for i in host_list:
            stdout = rrsync(local_path, i, server_path, ['.svn*', '.git*'])
            result = stdout.replace('\n', '</br>')
    return render_to_response('release/php_result.html', locals(), RequestContext(request))


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


@permission_required('release.add_svncontrol', login_url='perm_deny')
def code_save(request, ID):
    the_test = Test.objects.get(id=ID)
    desc = the_test.last_branch
    the_svn = Project.objects.get(name=the_test.project)
    svn_url, auth, server_path = the_svn.url, the_svn.auth, os.path.abspath(
            the_test.server_path)
    the_auth = Auth.objects.get(id=auth)
    username = the_auth.username if the_auth.username else ''
    password = the_auth.password if the_auth.password else ''
    local_path = os.path.join('/ops/test', server_path.lstrip('/'), str(ID))
    svn_path = os.path.join('/ops/svn', server_path.lstrip('/'), str(ID))
    svn_co(svn_url, svn_path, '', username, password)
    stdout = lrsync(local_path, svn_path, ['.svn*', '.git*'])
    svn_commit(svn_path, 'new')
    no_version = svn_version(svn_path)
    i_svn = SvnControl(project=the_test.project, no_version=no_version, desc=desc)
    i_svn.save()
    result = u'留档成功!版本号:' + str(no_version)
    return render_to_response('release/svn_pre_result.html', locals(), RequestContext(request))


@login_required()
def release_record(request):
    releases = ReleaseRecord.objects.all().order_by("-id")
    releases = paginator_fun(request, releases)
    return render_to_response('release/release_list.html', locals(), RequestContext(request))
