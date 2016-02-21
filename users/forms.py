# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User, Group

from saplatform.api import en2cn, perm_filter
from users.models import UserPerm, GroupPerm


class LoginForm(forms.Form):
    username = forms.CharField(required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'用户名'}))
    password = forms.CharField(required=True,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': u'密码'}))


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(required=True,
                                   widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': u'原始密码'}))
    new_password1 = forms.CharField(required=True,
                                    widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': u'新密码'}))
    new_password2 = forms.CharField(required=True,
                                    widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': u'再次输入'}))


class ForgetPasswordForm(forms.Form):
    username = forms.CharField(required=True,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'用户名'}))
    email = forms.EmailField(required=True,
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': u'邮箱'}))


class ProfileFrom(forms.ModelForm):
    nickname = forms.CharField(label=u'昵称', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(label=u'姓', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label=u'名', required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sex = forms.ChoiceField(label=u'性别', required=True, widget=forms.RadioSelect())
    tel = forms.IntegerField(label=u'手机号', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label=u'邮箱', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    birthday = forms.CharField(label=u'出生日期', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.ChoiceField(label=u'所在地', required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    headimg = forms.FileField(label=u'选择图片')

    class Meta:
        model = User
        fields = ('nickname', 'first_name', 'last_name', 'tel', 'sex', 'email', 'birthday', 'city', 'headimg')

    def __init__(self, *args, **kwargs):
        super(ProfileFrom, self).__init__(*args, **kwargs)
        self.fields['sex'].choices = ((x, x) for x in [u'男', u'女'])
        self.fields['city'].choices = ((x, x) for x in
                                       [u'广东', u'广西', u'湖北', u'湖南', u'河北', u'河南', u'山东', u'山西', u'新疆维吾尔族自治区', u'黑龙江',
                                        u'浙江', u'江西', u'江苏', u'宁夏回族自治区', u'辽宁', u'青海', u'陕西', u'甘肃', u'云南', u'贵州',
                                        u'西藏自治区', u'四川', u'北京', u'上海', u'天津', u'内蒙古自治区', u'台湾', u'海南', u'福建', u'吉林',
                                        u'安徽', u'重庆', u'香港特别行政区', u'澳门特别行政区'])


class AddUserFrom(forms.ModelForm):
    username = forms.CharField(label=u'用户名', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label=u'密码', required=True, widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    tel = forms.IntegerField(label=u'手机号', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label=u'邮箱', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ('username', 'password', 'nickname', 'first_name', 'last_name', 'tel', 'sex', 'email')


class AddGroupFrom(forms.ModelForm):
    name = forms.CharField(label=u'用户组名', required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Group
        fields = ('name',)


class UserPermForm(forms.ModelForm):
    group_list = forms.MultipleChoiceField(required=False, label=u'用户组',
                                           widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}))
    perm_list = forms.MultipleChoiceField(required=False, label=u'权限',
                                          widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}))

    class Meta:
        model = UserPerm
        fields = ('group_list', 'perm_list')

    def __init__(self, *args, **kwargs):
        super(UserPermForm, self).__init__(*args, **kwargs)
        self.fields['perm_list'].choices = ((x.id, en2cn(x.codename)) for x in perm_filter())
        self.fields['group_list'].choices = ((x.id, x.name) for x in Group.objects.all())


class GroupPermForm(forms.ModelForm):
    perm_list = forms.MultipleChoiceField(required=False, label=u'权限',
                                          widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-control'}))

    class Meta:
        model = GroupPerm
        fields = ('perm_list',)

    def __init__(self, *args, **kwargs):
        super(GroupPermForm, self).__init__(*args, **kwargs)
        self.fields['perm_list'].choices = ((x.id, en2cn(x.codename)) for x in perm_filter())
