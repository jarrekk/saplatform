## 自动化运维平台使用说明

![autoops](autoops.jpg)

### 一、用户\权限
只有超级管理员可以对用户和用户组进行管理，在左上角个人头像下面点击，会有用户管理和用户组管理。
在用户中可以添加用户，修改用户信息、权限以及所在组，在用户组中可以添加用户组，修改用户组权限。

### 二、资产
资产分为两个：
  * 服务器资产
  * 登陆认证资产
服务器资产是作为项目管理以及其他管理的基础，登陆认证资产包括服务器登陆，代码仓库登陆等认证。

所以在录入操作中，请先录入相关登陆认证信息。

### 三、项目
项目流程从测试开始，测试没问题的代码转移到运维的svn仓库存档，以便发布到预发布环境和正式环境。
项目信息的录入流程为：项目录入->测试录入
  * 项目录入包括：预发布和正式服务器及路径，运维svn仓库认证配置（在项目信息中）

  * 测试录入包括：测试服务器及路径，开发仓库认证配置（在xx测试发布中）

发布流程为：测试->存档到svn->预发布环境发布->正式环境发布

  * 测试 在xx测试发布中，将开发仓库代码发布到测试环境中

  * 存档svn 在xx测试发布中，将测试通过的代码存档到运维svn仓库

  * 预发布环境发布 在运维版本发布中，选择svn仓库中项目对应的版本号发布

  * 正式环境发布 在运维版本发布中，选择svn仓库中项目对应的版本号发布
预发布环境和正式环境的发布日志可以在发布记录中查看

### 四、数据库

通过上传SQL脚本，向指定数据库执行SQL脚本，执行过程为异步执行，执行结果保存在数据库中。

### 五、其他功能
用户个人信息，密码更改，密码找回，系统消息，邮件发送。

### 六、安装说明

#### pip安装文件

``` bash
# pip freeze
amqp==1.4.9
anyjson==0.3.3
backports-abc==0.4
backports.ssl-match-hostname==3.5.0.1
billiard==3.3.0.22
celery==3.1.20
certifi==2015.11.20.1
decorator==4.0.6
Django==1.8
django-guardian==1.4.1
dulwich==0.9.1
funky==0.0.2
futures==3.0.4
gitdb==0.6.4
ipython==4.0.3
ipython-genutils==0.1.0
Jinja2==2.8
kombu==3.0.33
MarkupSafe==0.23
meld3==1.0.2
msgpack-python==0.4.6
MySQL-python==1.2.5
paramiko==1.10.0
path.py==8.1.2
pexpect==4.0.1
pickleshare==0.6
ptyprocess==0.5
pycrypto==2.6
python-dateutil==2.2
pytz==2015.7
PyYAML==3.11
pyzmq==15.2.0
redis==2.10.5
requests==2.9.1
salt==2015.8.3
salt-api==0.8.4.1
simplegeneric==0.8.1
singledispatch==3.4.0.3
six==1.7.2
smmap==0.9.0
supervisor==3.2.1
svn==0.3.36
tornado==4.3
traitlets==4.1.0
uWSGI==2.0.12
```

#### celery添加环境变量：

```
export DJANGO_SETTINGS_MODULE=saplatform.settings
```

#### supervisord(python2.7)配置示例：

``` ini
[root@94_54 ~]# cat /etc/supervisord.conf
[supervisord]
http_port=/var/tmp/supervisor.sock ; (default is to run a UNIX domain socket server)
;http_port=127.0.0.1:9001  ; (alternately, ip_address:port specifies AF_INET)
;sockchmod=0700              ; AF_UNIX socketmode (AF_INET ignore, default 0700)
;sockchown=nobody.nogroup     ; AF_UNIX socket uid.gid owner (AF_INET ignores)
;umask=022                   ; (process file creation umask;default 022)
logfile=/var/log/supervisor/supervisord.log ; (main log file;default $CWD/supervisord.log)
logfile_maxbytes=50MB       ; (max main logfile bytes b4 rotation;default 50MB)
logfile_backups=10          ; (num of main logfile rotation backups;default 10)
loglevel=info               ; (logging level;default info; others: debug,warn)
pidfile=/var/run/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
nodaemon=false              ; (start in foreground if true;default false)
minfds=1024                 ; (min. avail startup file descriptors;default 1024)
minprocs=200                ; (min. avail process descriptors;default 200)

;nocleanup=true              ; (don't clean up tempfiles at start;default false)
;http_username=user          ; (default is no username (open system))
;http_password=123           ; (default is no password (open system))
;childlogdir=/tmp            ; ('AUTO' child log dir, default $TEMP)
;user=chrism                 ; (default is current user, required if root)
;directory=/tmp              ; (default is not to cd during start)
;environment=KEY=value       ; (key value pairs to add to environment)

[supervisorctl]
serverurl=unix:///var/tmp/supervisor.sock ; use a unix:// URL  for a unix socket
;serverurl=http://127.0.0.1:9001 ; use an http:// url to specify an inet socket
;username=chris              ; should be same as http_username if set
;password=123                ; should be same as http_password if set
;prompt=mysupervisor         ; cmd line prompt (default "supervisor")

; The below sample program section shows all possible program subsection values,
; create one or more 'real' program: sections to be able to control them under
; supervisor.

;[program:theprogramname]
;command=/bin/cat            ; the program (relative uses PATH, can take args)
;priority=999                ; the relative start priority (default 999)
;autostart=true              ; start at supervisord start (default: true)
;autorestart=true            ; retstart at unexpected quit (default: true)
;startsecs=10                ; number of secs prog must stay running (def. 10)
;startretries=3              ; max # of serial start failures (default 3)
;exitcodes=0,2               ; 'expected' exit codes for process (default 0,2)
;stopsignal=QUIT             ; signal used to kill process (default TERM)
;stopwaitsecs=10             ; max num secs to wait before SIGKILL (default 10)
;user=chrism                 ; setuid to this UNIX account to run the program
;log_stdout=true             ; if true, log program stdout (default true)
;log_stderr=true             ; if true, log program stderr (def false)
;logfile=/var/log/cat.log    ; child log path, use NONE for none; default AUTO
;logfile_maxbytes=1MB        ; max # logfile bytes b4 rotation (default 50MB)
;logfile_backups=10          ; # of logfile backups (default 10)


; ==================================
;  celery worker supervisor example
; ==================================
[program:celery]
directory=/data/html/saplatform/
command=/usr/local/python27/bin/celery worker -A saplatform --loglevel=INFO
user=root
numprocs=1
stdout_logfile=/var/log/celery/worker.log
stderr_logfile=/var/log/celery/worker.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
killasgroup=true
priority=998

[program:tornado]
directory=/data/html/saplatform/
command=/usr/local/python27/bin/python2.7 /data/html/saplatform/t_server.py
user=root
numprocs=1
stdout_logfile=/var/log/tornado/tornado.log
stderr_logfile=/var/log/tornado/tornado.log
autostart=true
autorestart=true
startsecs=10
stopwaitsecs = 600
killasgroup=true
priority=998
```

t_server.py文件内容(tornado启动django)

``` python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

from tornado.options import options, define, parse_command_line
# import django.core.handlers.wsgi
from django.core.wsgi import get_wsgi_application
import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.wsgi

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ['DJANGO_SETTINGS_MODULE'] = "saplatform.settings"

define('port', type=int, default=8088)


def main():
    parse_command_line()

    # wsgi_app = tornado.wsgi.WSGIContainer(django.core.handlers.wsgi.WSGIHandler())
    wsgi_app = tornado.wsgi.WSGIContainer(get_wsgi_application())

    tornado_app = tornado.web.Application([('.*', tornado.web.FallbackHandler, dict(fallback=wsgi_app)), ])
    server = tornado.httpserver.HTTPServer(tornado_app)
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
```

其次还需要安装redis，MySQL，saltstack，salt-api。