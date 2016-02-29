from django.conf.urls import patterns, url

urlpatterns = patterns('',

                       # url(r'^$', 'monitor.views.index',name='index'),
                       url(r'^project/$', 'release.views.project', name='project'),
                       url(r'^add_project/$', 'release.views.add_project', name='add_project'),
                       url(r'^edit_project/(?P<ID>\d+)/$', 'release.views.edit_project', name='edit_project'),

                       url(r'^test/$', 'release.views.test', name='test'),
                       url(r'^add_test/$', 'release.views.add_test', name='add_test'),
                       url(r'^edit_test/(?P<ID>\d+)/$', 'release.views.edit_test', name='edit_test'),

                       url(r'^test_release/(?P<ID>\d+)/', 'release.views.test_release', name='test_release'),
                       url(r'^pre_release/(?P<ID>\d+)/$', 'release.views.pre_release', name='pre_release'),
                       url(r'^pro_release/(?P<ID>\d+)/$', 'release.views.pro_release', name='pro_release'),

                       url(r'^pre_record/$', 'release.views.pre_record', name='pre_record'),
                       url(r'^del_pre_record/(?P<ID>\d+)/$', 'release.views.del_pre_record', name='del_pre_record'),
                       url(r'^complete_pre/(?P<ID>\d+)/$', 'release.views.complete_pre', name='complete_pre'),

                       url(r'^rollback/$', 'release.views.rollback', name='rollback'),
                       url(r'^exec_rollback/(?P<ID>\d+)/$', 'release.views.exec_rollback', name='exec_rollback'),
                       url(r'^del_rollback/(?P<ID>\d+)/$', 'release.views.del_rollback', name='del_rollback'),
                       url(r'^release_record/$', 'release.views.release_record', name='release_record'),

                       )
