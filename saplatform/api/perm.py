# -*- coding: utf-8 -*-
from django.contrib.auth.models import Permission, ContentType

str_dict = {
    '_': '',
    'add': u'添加',
    'change': u'修改',
    'delete': u'删除',
    'view': u'操作'
}

perm_dict = {
    'test': u'测试例',
    'svncontrol': u'运维版本',
    'project': u'项目',
    'releaserecord': u'发布记录',
    'group': u'组',
    'assets': u'资产',
    'auth': u'登录认证',
    'dbconfig': u'数据库配置',
    'sqlresult': u'SQL执行结果',
    'prerecord': u'预发布记录',
    'rollback': u'回滚记录'
}

no_perm_list = ['auth', 'contenttypes', 'sessions', 'users', 'message', 'djcelery', 'guardian']


def en2cn(string):
    for i in str_dict.keys():
        string = string.replace(i, str_dict[i])
    for i in perm_dict.keys():
        string = string.replace(i, perm_dict[i])
    return string


def perm_filter():
    content_types = ContentType.objects.all()
    list1 = []
    for name in no_perm_list:
        content_types = content_types.exclude(app_label=name)
    for i in content_types:
        list1.append(i.id)
    permissions = Permission.objects.filter(content_type_id__in=list1)
    return permissions
