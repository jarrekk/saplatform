from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',

                       # url(r'^$', 'monitor.views.index',name='index'),
                       url(r'^project/$', 'release.views.project', name='project'),
                       url(r'^add_project/$', 'release.views.add_project', name='add_project'),
                       url(r'^edit_project/(?P<ID>\d+)/$', 'release.views.edit_project', name='edit_project'),
                       url(r'^svn/$', 'release.views.svn', name='svn'),
                       url(r'^svn_pre_result/(?P<ID>\d+)/$', 'release.views.svn_pre_result', name='svn_pre_result'),
                       url(r'^svn_pro_result/(?P<ID>\d+)/$', 'release.views.svn_pro_result', name='svn_pro_result'),
                       url(r'^php/$', 'release.views.php', name='php'),
                       url(r'^nodejs/$', 'release.views.nodejs', name='nodejs'),
                       url(r'^java/$', 'release.views.java', name='java'),

                       url(r'^php_result/(?P<ID>\d+)/', 'release.views.php_result', name='php_result'),
                       url(r'^nodejs_result/(?P<ID>\d+)/$', 'release.views.nodejs_result', name='nodejs_result'),
                       url(r'^java_result/(?P<ID>\d+)/$', 'release.views.java_result', name='java_result'),
                       url(r'^add_test/$', 'release.views.add_test', name='add_test'),
                       url(r'^edit_test/(?P<ID>\d+)/$', 'release.views.edit_test', name='edit_test'),
                       # url(r'^refresh_branch/(?P<ID>\d+)/$', 'release.views.refresh_branch', name='refresh_branch'),
                       url(r'^code_save/(?P<ID>\d+)/$', 'release.views.code_save', name='code_save'),
                       url(r'^release_record/$', 'release.views.release_record', name='release_record'),



                       )
