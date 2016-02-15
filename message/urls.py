from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',

                       # url(r'^$', 'monitor.views.index',name='index'),
                       url(r'^alert/$', 'message.views.alert', name='alert'),
                       url(r'^delete_alert/(?P<ID>\d+)/$', 'message.views.delete_alert', name='delete_alert'),

                       )
