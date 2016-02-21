# -*- coding: utf-8 -*-
from django import forms
from database.models import DbConfig
from assets.models import Auth


class DbConfigForm(forms.ModelForm):
    name = forms.CharField(label=u'DB连接名', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    auth = forms.ChoiceField(label=u'登陆认证', required=True,
                             widget=forms.Select(attrs={'class': 'form-control'}))
    address = forms.CharField(label=u'数据库地址', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = DbConfig
        fields = ('name', 'address', 'auth')

    def __init__(self, *args, **kwargs):
        super(DbConfigForm, self).__init__(*args, **kwargs)
        self.fields['auth'].choices = ((x.id, x.name) for x in Auth.objects.all())
