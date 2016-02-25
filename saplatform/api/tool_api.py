# -*- coding: utf-8 -*-
import requests

requests.packages.urllib3.disable_warnings()


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
        data1['expr_form'] = 'list'
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
        data1['expr_form'] = 'list'
        r = requests.post(self.__url, data=data1, headers=head1, verify=False)
        return r.content.replace('true', 'True').replace('false', 'False')

    def logout(self):
        head1 = {
            'Accept': self.__Accept,
            'X-Auth-Token': self.__token_id
        }
        url = self.__url.rstrip('/') + '/logout'
        requests.post(url, headers=head1, verify=False)
