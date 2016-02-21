from django.conf.urls import patterns, url

urlpatterns = patterns('',

                       # url(r'^$', 'monitor.views.index',name='index'),
                       url(r'^alert/$', 'message.views.alert', name='alert'),
                       url(r'^delete_alert/(?P<ID>\d+)/$', 'message.views.delete_alert', name='delete_alert'),

                       )
