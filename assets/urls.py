from django.conf.urls import patterns, url

urlpatterns = patterns('',

                       # url(r'^$', 'monitor.views.index',name='index'),
                       url(r'^assets/$', 'assets.views.assets', name='assets'),
                       url(r'^add_assets/$', 'assets.views.add_assets', name='add_assets'),
                       url(r'^edit_assets/(?P<ID>\d+)/$', 'assets.views.edit_assets', name='edit_assets'),

                       url(r'^assets_init/(?P<ID>\d+)/$', 'assets.views.assets_init', name='assets_init'),
                       url(r'^assets_info/(?P<ID>\d+)/$', 'assets.views.assets_info', name='assets_info'),

                       url(r'^auth/$', 'assets.views.auth', name='auth'),
                       url(r'^add_auth/$', 'assets.views.add_auth', name='add_auth'),
                       url(r'^edit_auth/(?P<ID>\d+)/$', 'assets.views.edit_auth', name='edit_auth'),

                       )
