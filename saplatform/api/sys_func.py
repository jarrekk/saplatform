# -*- coding: utf-8 -*-
import os
import subprocess
import time

import MySQLdb
import paramiko
import svn.local
import svn.remote

from req import http_error


def git_co(request, git_url, branch, key_path, local_path):
    if os.path.exists(local_path):
        os.chdir(local_path)
        os.system('GIT_SSH=%s' % key_path)
        os.system('git checkout master')
        os.system('git pull')
    else:
        try:
            os.system('mkdir -p %s' % local_path)
            os.system('GIT_SSH=%s' % key_path)
            os.system('git clone %s %s' % (git_url, local_path))
        except:
            return http_error(request, u'代码拉取失败')
    if branch:
        try:
            os.chdir(local_path)
            os.system('git checkout %s' % branch)
        except:
            return http_error(request, u'分支不存在')


def svn_co(svn_url, local_path, versionnum, username, password):
    if os.path.exists(local_path):
        pass
    else:
        os.makedirs(local_path)
    if username and password:
        # os.system('svn co %s %s --username %s --password %s' % (svn_url, local_path, username, password))
        r = svn.remote.RemoteClient(svn_url, username=username, password=password)
    else:
        # os.system('svn co %s %s' % (svn_url, local_path))
        r = svn.remote.RemoteClient(svn_url)
    if str(versionnum):
        r.checkout(local_path)
        os.chdir(local_path)
        os.system('svn up -r %s' % str(versionnum))
    else:
        r.checkout(local_path)


def svn_version(local_path):
    s = svn.local.LocalClient(local_path)
    version_num = s.info()['commit#revision']
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


def local_cmd(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    return stdout


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
