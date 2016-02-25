# -*- coding: utf-8 -*-
import os

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, RequestContext

from assets.models import Auth
from database.forms import DbConfigForm
from database.models import DbConfig, SQLResult
from database.tasks import mysql_cmd_task, script_mysql_task
from saplatform.api import http_success, File, local_cmd, mysql_cmd
from saplatform.settings import BASE_DIR, SQL_DIRS


# from django.utils.encoding import force_text
# Create your views here.

def db_config(request):
    db_configs = DbConfig.objects.all()
    return render_to_response('database/db_config.html', locals(), RequestContext(request))


def add_db_config(request):
    if request.method == "POST":
        form = DbConfigForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('db_config'))
    else:
        form = DbConfigForm()
    return render_to_response('database/add_db_config.html', locals(), RequestContext(request))


def edit_db_config(request, ID):
    the_db_config = DbConfig.objects.get(id=ID)
    if request.method == "POST":
        form = DbConfigForm(request.POST, instance=the_db_config)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('db_config'))
    else:
        form = DbConfigForm(instance=the_db_config)
    return render_to_response('database/edit_db_config.html', locals(), RequestContext(request))


def sqls(request):
    sql_list = []
    id_num = 0
    for dir_path, dir_names, file_names in os.walk(SQL_DIRS):
        for file_name in file_names:
            the_file = File()
            the_file.get_info(os.path.join(dir_path, file_name), id_num)
            sql_list.append(the_file)
            id_num += 1
    db_configs = DbConfig.objects.all()
    return render_to_response('database/sqls.html', locals(), RequestContext(request))


def exec_sql(request):
    file_name = request.GET["file_name"]
    ID = request.GET["db_config"]
    exec_method = request.GET["exec_method"]
    the_db_config = DbConfig.objects.get(id=ID)
    the_auth = Auth.objects.get(id=the_db_config.auth)
    f = open(os.path.join(SQL_DIRS, file_name))
    sql = f.read()
    if exec_method:
        script_mysql_task.delay(the_db_config.address,
                                the_auth.username,
                                the_auth.password,
                                sql,
                                file_name,
                                request.user.username)
    else:
        mysql_cmd_task.delay(the_db_config.address,
                             the_auth.username,
                             the_auth.password,
                             sql,
                             request.user.username,
                             file_name)
    return http_success(request, u'操作成功,请等待执行结果,在SQL执行结果查看.')


def upload(request):
    if request.method == "POST":
        os.system('rm -rf %s/static/sql/*' % BASE_DIR)
        upload_files = request.FILES.getlist('file[]', None)
        for upload_file in upload_files:
            file_path = '%s/%s/%s' % (BASE_DIR, 'static/sql', upload_file.name)
            if os.path.exists(file_path):
                os.remove(file_path)
            if upload_file.name[-4:] == '.sql':
                with open(file_path, 'w') as f:
                    for chunk in upload_file.chunks():
                        f.write(chunk)
        return http_success(request, 'ok')
    return render_to_response('database/upload.html', locals(), RequestContext(request))


def sql_result(request):
    sql_results = SQLResult.objects.all().order_by('-exec_time')
    for i in sql_results:
        i.result = eval(i.result)
    return render_to_response('database/sql_result.html', locals(), RequestContext(request))


def sql_input(request):
    db_configs = DbConfig.objects.all()
    # if request.method == "GET":
    #     pass
    try:
        sql = request.GET["context"]
        ID = request.GET["db_config"]
        the_db_config = DbConfig.objects.get(id=ID)
        the_auth = Auth.objects.get(id=the_db_config.auth)
        sql = "%s %s %s" % ("select", sql, "limit 100;")
        # print sql
        # mysql_cmd_task.delay(the_db_config.address,
        #                      the_auth.username,
        #                      the_auth.password,
        #                      sql,
        #                      request.user.username,
        #                      u'SQL语句执行')
        result = mysql_cmd(the_db_config.address, the_auth.username, the_auth.password, sql)
        if not result:
            result = ({'result': 'success'},)
        r = SQLResult(content=sql, result=str(result), user=request.user.username, sql_name=u'SQL语句')
        r.save()
        return http_success(request, u'操作成功,请等待执行结果,在SQL执行结果查看.')
    except:
        return render_to_response('database/sql_input.html', locals(), RequestContext(request))
