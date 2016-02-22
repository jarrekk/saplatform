from django.conf.urls import include, url, patterns
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('saplatform.views',
                       # Examples:
                       # url(r'^admin/', include(admin.site.urls)),

                       url(r'^$', 'index', name='index'),
                       url(r'^skin_config/$', 'skin_config', name='skin_config'),

                       url(r'^perm_deny$', 'perm_deny', name='perm_deny'),

                       # release model
                       url(r'^release/', include('release.urls')),
                       # users model
                       url(r'^users/', include('users.urls')),
                       # assets model
                       url(r'^assets/', include('assets.urls')),
                       # message model
                       url(r'^message/', include('message.urls')),
                       # database model
                       url(r'^database/', include('database.urls')),

                       )

handler404 = 'saplatform.views.server404'
