# -*- coding: utf-8 -*-
from django.contrib.auth.decorators import login_required, permission_required
from database.tasks import *
from database.forms import *
from database.models import DbConfig
from saplatform.api import *
from django.utils.encoding import force_text
from django.http import HttpResponse


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
    f = open(os.path.join(SQL_DIRS, file_name))
    sql = f.read()
    the_db_config = DbConfig.objects.get(id=ID)
    the_auth = Auth.objects.get(id=the_db_config.auth)
    mysql_cmd_task.delay(the_db_config.address,
                         the_auth.username,
                         the_auth.password,
                         sql,
                         request.user.username,
                         file_name)
    return http_success(request, u'操作成功,请等待执行结果,在SQL执行结果查看.')


def upload(request):
    if request.method == "POST":
        upload_files = request.FILES.getlist('file[]', None)
        for upload_file in upload_files:
            file_path = '%s/%s/%s' % (BASE_DIR, 'static/sql', upload_file.name)
            if os.path.exists(file_path):
                os.remove(file_path)
            if upload_file.name[-4:] == '.sql':
                with open(file_path, 'w') as f:
                    for chunk in upload_file.chunks():
                        f.write(chunk)
        print 'ok'
        return http_success(request, 'ok')
    return render_to_response('database/upload.html', locals(), RequestContext(request))


def sql_result(request):
    sql_results = SQLResult.objects.all().order_by('-exec_time')
    return render_to_response('database/sql_result.html', locals(), RequestContext(request))
