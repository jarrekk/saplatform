# -*- coding: utf-8 -*-
from django import forms
from release.models import Test, Project
from assets.models import Auth, Assets
# from django.core.validators import *


class TestForm(forms.ModelForm):
    project = forms.ChoiceField(label=u'项目名', required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    host_list = forms.MultipleChoiceField(label=u'服务器组', required=True,
                                          widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    # auth = forms.ChoiceField(label=u'登陆认证', required=True, widget=forms.Select(attrs={'class': 'form-control'}))
    name = forms.CharField(label=u'测试例', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    before_cmd = forms.CharField(label=u'发布前命令', required=False,
                                 widget=forms.TextInput(attrs={'class': 'form-control'}))
    after_cmd = forms.CharField(label=u'发布后命令', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    # code_type = forms.ChoiceField(label=u'代码语言', required=True, widget=forms.RadioSelect())
    # repo_type = forms.ChoiceField(label=u'仓库类型', required=True, widget=forms.RadioSelect())
    # repo_url = forms.CharField(label=u'仓库地址', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    server_path = forms.CharField(label=u'远程服务器路径', required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    desc = forms.CharField(label=u'描述', required=False,
                           widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '4'}))

    class Meta:
        model = Test
        fields = ('name', 'project', 'before_cmd', 'after_cmd', 'host_list', 'server_path', 'desc')

    def __init__(self, *args, **kwargs):
        super(TestForm, self).__init__(*args, **kwargs)
        self.fields['host_list'].choices = ((x.lan_ip, x.lan_ip) for x in Assets.objects.all())
        self.fields['project'].choices = ((x.name, x.name) for x in Project.objects.all())
        # self.fields['auth'].choices = ((x.id, x.name) for x in Auth.objects.all())
        # self.fields['code_type'].choices = ((x, x) for x in ['php', 'java', 'nodejs'])
        # self.fields['repo_type'].choices = ((x, x) for x in ['git', 'svn'])


class ProjectForm(forms.ModelForm):
    name = forms.CharField(label=u'项目名', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    code_type = forms.ChoiceField(widget=forms.RadioSelect(), label=u'代码类型', required=True)
    url = forms.CharField(label=u'SVN仓库地址', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    pre_host_list = forms.MultipleChoiceField(required=True, label=u'预发布服务器',
                                              widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    pro_host_list = forms.MultipleChoiceField(required=True, label=u'预发布服务器',
                                              widget=forms.SelectMultiple(attrs={'class': 'form-control'}))
    server_path = forms.CharField(label=u'远程服务器路径', required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control'}))
    auth = forms.ChoiceField(label=u'登陆认证', required=True, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Project
        fields = ('name', 'code_type', 'url', 'auth', 'pre_host_list', 'pro_host_list', 'server_path')

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['code_type'].choices = ((x, x) for x in ['php', 'java', 'nodejs'])
        self.fields['pre_host_list'].choices = ((x.lan_ip, x.lan_ip) for x in Assets.objects.all())
        self.fields['pro_host_list'].choices = ((x.lan_ip, x.lan_ip) for x in Assets.objects.all())
        self.fields['auth'].choices = ((x.id, x.name) for x in Auth.objects.all())
