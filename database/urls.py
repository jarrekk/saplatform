from django.conf.urls import patterns, url

urlpatterns = patterns('',

                       url(r'^db_config/$', 'database.views.db_config', name='db_config'),
                       url(r'^add_db_config/$', 'database.views.add_db_config', name='add_db_config'),
                       url(r'^edit_db_config/(?P<ID>\d+)/$', 'database.views.edit_db_config', name='edit_db_config'),
                       url(r'^sqls/$', 'database.views.sqls', name='sqls'),
                       url(r'^exec_sql/', 'database.views.exec_sql', name='exec_sql'),
                       url(r'^upload/$', 'database.views.upload', name='upload'),
                       url(r'^sql_result/$', 'database.views.sql_result', name='sql_result'),
                       url(r'^sql_input/$', 'database.views.sql_input', name='sql_input'),

                       )