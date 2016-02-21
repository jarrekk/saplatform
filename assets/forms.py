# -*- coding: utf-8 -*-
from django import forms
from django.core.validators import *
from assets.models import Assets, Auth


class AssetsForm(forms.ModelForm):
    lan_ip = forms.CharField(label=u'内网IP', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}),
                             validators=[validate_ipv4_address])
    auth = forms.ChoiceField(label=u'登陆认证', required=True,
                             widget=forms.Select(attrs={'class': 'form-control'}))
    service = forms.CharField(label=u'运行服务', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sa = forms.CharField(label=u'管理员', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    environment = forms.ChoiceField(label=u'环境', required=True,
                                    widget=forms.RadioSelect())
    status = forms.ChoiceField(label=u'状态', required=True,
                               widget=forms.RadioSelect())

    class Meta:
        model = Assets
        fields = ('lan_ip', 'auth', 'service', 'sa', 'environment', 'status')

    def __init__(self, *args, **kwargs):
        super(AssetsForm, self).__init__(*args, **kwargs)
        self.fields['auth'].choices = ((x.id, x.name) for x in Auth.objects.all())
        self.fields['status'].choices = ((x, x) for x in [u'正常', u'待使用', u'关机', u'维修'])
        self.fields['environment'].choices = ((x, x) for x in [u'测试', u'预发布', u'正式'])


class AuthForm(forms.ModelForm):
    name = forms.CharField(label=u'认证名称', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(label=u'用户名', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label=u'密码', widget=forms.PasswordInput(attrs={'class': 'form-control'}), required=False)
    key = forms.CharField(label=u'密钥路径', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    port = forms.IntegerField(label=u'端口', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Auth
        fields = ('name', 'username', 'password', 'key', 'port')
