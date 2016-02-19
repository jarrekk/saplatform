# -*- coding: utf-8 -*-
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, RequestContext
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Permission, ContentType, User
from saplatform.settings import *
from message.models import Alert
import os
import time
import requests
import subprocess
import logging
import svn.remote
import svn.local
import paramiko
import MySQLdb
from gittle import Gittle, GittleAuth

requests.packages.urllib3.disable_warnings()

str_dict = {
    '_': '',
    'add': u'添加',
    'change': u'修改',
    'delete': u'删除',
    'view': u'操作'
}

perm_dict = {
    'test': u'测试例',
    'svncontrol': u'运维版本',
    'project': u'项目',
    'releaserecord': u'发布记录',
    'group': u'组',
    'assets': u'资产',
    'auth': u'登录认证',
    'dbconfig': u'数据库配置'
}

no_perm_list = ['auth', 'contenttypes', 'sessions', 'users', 'message', 'djcelery', 'guardian']


def set_log(level, filename='saplatform.log'):
    log_file = os.path.join(LOG_DIRS, filename)
    if not os.path.isfile(log_file):
        os.mknod(log_file)
        os.chmod(log_file, 0777)
    log_level_total = {'debug': logging.DEBUG, 'info': logging.INFO, 'warning': logging.WARN, 'error': logging.ERROR,
                       'critical': logging.CRITICAL}
    logger_f = logging.getLogger('saplatform')
    logger_f.setLevel(logging.DEBUG)
    fh = logging.FileHandler(log_file)
    fh.setLevel(log_level_total.get(level, logging.DEBUG))
    formatter = logging.Formatter('%(asctime)s - %(filename)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger_f.addHandler(fh)
    return logger_f


class SaltApi:
    def __init__(self, url, username, password):
        self.__url = url
        self.__username = username
        self.__password = password
        self.__token_id = ''
        self.__eauth = 'pam'
        self.__Accept = 'application/json'

    def login(self):
        data1 = {
            'username': self.__username,
            'password': self.__password,
            'eauth': self.__eauth
        }
        head1 = {'Accept': self.__Accept}
        url = self.__url.rstrip('/') + '/login'
        try:
            r = requests.post(url, data=data1, headers=head1, verify=False)
            self.__token_id = eval(r.content)['return'][0]['token']
            return True
        except:
            return False

    def cmd(self, host, cmd):
        head1 = {
            'Accept': self.__Accept,
            'X-Auth-Token': self.__token_id
        }
        data1 = {'client': 'local'}
        if host:
            data1['tgt'] = host
        else:
            data1['tgt'] = '*'
        data1['fun'] = 'cmd.run'
        data1['arg'] = cmd
        r = requests.post(self.__url, data=data1, headers=head1, verify=False)
        return r.content.replace('true', 'True').replace('false', 'False')

    def fun(self, host, fun):
        head1 = {
            'Accept': self.__Accept,
            'X-Auth-Token': self.__token_id
        }
        data1 = {'client': 'local'}
        if host:
            data1['tgt'] = host
        else:
            data1['tgt'] = '*'
        data1['fun'] = fun
        r = requests.post(self.__url, data=data1, headers=head1, verify=False)
        return r.content.replace('true', 'True').replace('false', 'False')

    def logout(self):
        head1 = {
            'Accept': self.__Accept,
            'X-Auth-Token': self.__token_id
        }
        url = self.__url.rstrip('/') + '/logout'
        requests.post(url, headers=head1, verify=False)


class File:
    def __init__(self):
        self.name = ''
        self.ctime = ''
        self.content = ''
        self.id_num = ''

    def get_info(self, file_path, id_num):
        self.name = os.path.basename(file_path)
        info = os.stat(file_path)
        self.ctime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info.st_ctime))
        f = open(file_path)
        self.content = f.read()
        self.id_num = id_num


def mysql_cmd(host, username, password, sql):
    con = None
    try:
        con = MySQLdb.connect(host, username, password)
        with con:
            cur = con.cursor(MySQLdb.cursors.DictCursor)
            cur.execute(sql)
            rows = cur.fetchall()
            result = rows
            # for row in rows:
            #     for key in row.keys():
            #         print "%s %s" % (key, row[key])
    except Exception, e:
        result = e
    finally:
        if con:
            con.close()
    return result


def admin_required():
    def _deco(func):
        def __deco(request, *args, **kwargs):
            if not request.user.is_superuser:
                return HttpResponseRedirect(reverse('perm_deny'))
            return func(request, *args, **kwargs)

        return __deco

    return _deco


def git_co(git_url, branch, key_path, local_path):
    if os.path.exists(local_path):
        os.chdir(local_path)
        os.system('GIT_SSH=%s' % key_path)
        os.system('git pull')
        ## repo.auth(username='jiak',password='jiak@zaijiadd.com')
        # repo.pull()
    else:
        try:
            os.system('GIT_SSH=%s' % key_path)
            os.system('git clone %s %s' % (git_url, local_path))
            # key_file = open(key_path)
            # auth = GittleAuth(pkey=key_file)
            # Gittle.clone(git_url, local_path, auth=auth, mode=0755)
        except:
            pass
    if branch == '':
        pass
    else:
        try:
            os.chdir(local_path)
            os.system('git checkout %s' % branch)
            # key_file = open(key_path)
            # repo = Gittle(local_path, origin_uri=git_url)
            # repo.auth(pkey=key_file)
            # repo.switch_branch(branch)
        except:
            pass


def git_branch(git_url, key_path, local_path):
    key_file = open(key_path)
    repo = Gittle(local_path, git_url)
    repo.auth(username=None, password=None, pkey=key_file)
    branch = repo.branches
    return branch.keys()


def svn_co(svn_url, local_path, versionnum, username, password):
    if os.path.exists(local_path):
        pass
    else:
        os.makedirs(local_path)
    if username and password:
        r = svn.remote.RemoteClient(svn_url, username=username, password=password)
    else:
        r = svn.remote.RemoteClient(svn_url)
    if str(versionnum):
        r.checkout(local_path)
        os.chdir(local_path)
        os.system('svn up -r %s' % str(versionnum))
    else:
        r.checkout(local_path)


def svn_version(local_path):
    s = svn.local.LocalClient(local_path)
    version_num = s.info()['entry_revision']
    return version_num


def svn_commit(local_path, committext):
    commit_cmd = 'svn add --force * && svn commit -m "%s"' % str(committext)
    os.chdir(local_path)
    os.system(commit_cmd)


def mkdir(dir_name, username='', mode=0755):
    if not os.path.isdir(dir_name):
        os.makedirs(dir_name)
        os.chmod(dir_name, mode)
        # if username:
        #     chown(dir_name, username)


def my_render(template, data, request):
    return render_to_response(template, data, context_instance=RequestContext(request))


def http_success(request, msg):
    return render_to_response('success.html', locals())


def http_error(request, emg):
    message = emg
    return render_to_response('error.html', locals())


def sizeformat(size, unit='B', Standard=1000):
    division = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB', 'BB', 'NB', 'DB', 'CB', 'XB']
    loc = division.index(unit.upper())
    division = division[loc:]
    if not size:
        raise TypeError("Required argument 'size' (pos 1) not found")
    else:
        try:
            size = float(size)
        except:
            raise TypeError("Object of size must be number, not '%s'" % (type(size)))
        else:
            if (Standard != 1024) and (Standard != 1000):
                raise Exception("Convert Standard must be '1000' or '1024', not '%s'" % (Standard))
            else:
                if size < Standard:
                    return str(size) + ' ' + division[0]
                loc += 1
                for cube in range(0, len(division)):
                    if Standard ** cube >= size >= Standard ** (cube - 1):
                        if size == Standard ** cube:
                            return str(round(float(size) / Standard ** cube)) + " " + division[cube]
                        else:
                            return str(round(float(size) / Standard ** (cube - 1))) + " " + division[cube - 1]
                    else:
                        continue
                raise Exception("Out of the maximum conversion range (%s^14 %s)" % (Standard, unit))


def rrsync(local_path, remote_ip, remote_path, exlist):
    if os.path.isdir(local_path):
        local_path = os.path.abspath(local_path) + '/'
    if os.path.isdir(remote_path):
        remote_path = os.path.abspath(remote_path) + '/'
    if exlist:
        exstring = ''
        for filename in exlist:
            exstring += '--exclude="%s" ' % filename
    cmd = 'rsync -avz -e ssh %s %s root@%s:%s' % (exstring, local_path, remote_ip, remote_path)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    return stdout


def lrsync(merge_path, local_path, exlist):
    if os.path.isdir(local_path):
        local_path = os.path.abspath(local_path) + '/'
    if os.path.isdir(merge_path):
        merge_path = os.path.abspath(merge_path) + '/'
    if exlist:
        ex_string = ''
        for filename in exlist:
            ex_string += '--exclude="%s" ' % filename
    cmd = 'rsync -avz %s %s %s' % (ex_string, merge_path, local_path)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    return stdout


def sftp(ip, port, username, password, key_path, local_file, remote_file):
    t = paramiko.Transport((ip, int(port)))
    if password:
        t.connect(username=username, password=password)
    else:
        key = paramiko.RSAKey.from_private_key_file(key_path)
        t.connect(username=username, pkey=key)
    ssh_ftp = paramiko.SFTPClient.from_transport(t)
    ssh_ftp.put(local_file, remote_file)
    t.close()


def ssh_cmd(ip, port, username, password, key_path, cmd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if password:
        ssh.connect(ip, port=port, username=username, password=password)
    else:
        key = paramiko.RSAKey.from_private_key_file(key_path)
        ssh.connect(ip, port=port, username=username, pkey=key)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout = stdout.readlines() if stdout.readlines() else ''
    ssh.close()
    return stdout


def en2cn(string):
    for i in str_dict.keys():
        string = string.replace(i, str_dict[i])
    for i in perm_dict.keys():
        string = string.replace(i, perm_dict[i])
    return string


def perm_filter():
    content_types = ContentType.objects.all()
    list1 = []
    for name in no_perm_list:
        content_types = content_types.exclude(app_label=name)
    for i in content_types:
        list1.append(i.id)
    permissions = Permission.objects.filter(content_type_id__in=list1)
    return permissions


def request_user_id(request):
    request_user = User.objects.get(username=request.user)
    return request_user.id


def alert(request, text):
    a = Alert(text=text, to_user_id=request_user_id(request))
    a.save()


# def message(title, text, msg_type, to_user_id, from_user_id, status=0):
#     m = Message(title=title, text=text, msg_type=msg_type, to_user_id=to_user_id, from_user_id=from_user_id,
#                 status=status)
#     m.save()

# logger = set_log(level='debug')

# if __name__ == '__main__':
#     salttest = SaltApi('https://192.168.10.80:8000', 'salttest', 'salttest')
#     salttest.login()
#     result = salttest.cmd('192.168.10.82', 'ip a')
#     print result
