from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',

                       url(r'^login/$', 'users.views.login', name='login'),
                       url(r'^logout/$', 'users.views.logout', name='logout'),
                       url(r'^profile/$', 'users.views.profile', name='profile'),
                       url(r'^change_password/$', 'users.views.change_password', name='change_password'),
                       url(r'^forget_password/$', 'users.views.forget_password', name='forget_password'),

                       url(r'^user_list/$', 'users.views.user_list', name='user_list'),
                       url(r'^add_user/$', 'users.views.add_user', name='add_user'),
                       url(r'^edit_user/(?P<ID>\d+)/$', 'users.views.edit_user', name='edit_user'),
                       url(r'^delete_user/(?P<ID>\d+)/$', 'users.views.delete_user', name='delete_user'),
                       url(r'^user2perm/(?P<ID>\d+)/$', 'users.views.user2perm', name='user2perm'),

                       url(r'^group_list/$', 'users.views.group_list', name='group_list'),
                       url(r'^add_group/$', 'users.views.add_group', name='add_group'),
                       url(r'^edit_group/(?P<ID>\d+)/$', 'users.views.edit_group', name='edit_group'),
                       url(r'^delete_group/(?P<ID>\d+)/$', 'users.views.delete_group', name='delete_group'),
                       url(r'^group2perm/(?P<ID>\d+)/$', 'users.views.group2perm', name='group2perm'),

                       )
