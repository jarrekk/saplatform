#!/bin/sh

Salt_Server=$1
Local_Ip=$2

# yum -y groupinstall "Development Tools"

rpm -qa | grep salt
if [ $? -eq 0 ];then
        echo "Salt is installed,please check"
        exit 0
fi

Salt_minion_conf="/etc/salt/minion"
Check_salt_pro=$(ps aux | grep salt | grep -v grep > /dev/null 2>&1)

if [ -f $Salt_minion_conf ];then
        echo "Salt-minion is installed,Please check"
        exit 0
else
        rpm -ivh http://download.fedoraproject.org/pub/epel/6/i386/epel-release-6-8.noarch.rpm
        #rpm -Uvh http://ftp.linux.ncsu.edu/pub/epel/6/i386/epel-release-6-8.noarch.rpm
        #rpm -Uvh http://ftp.linux.ncsu.edu/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
        #sed -i -r 's/baseurl/#baseurl/g' /etc/yum.repos.d/epel.repo
        #sed -i -r 's/#mirrorlist/mirrorlist/g' /etc/yum.repos.d/epel.repo
        echo "Salt-minion is not installed,now install it"
        yum -y install salt-minion
        if [ $? -eq 0 ];then
                echo "master: ${Salt_Server}" > $Salt_minion_conf
                echo "id: ${Local_Ip}" >> $Salt_minion_conf
        else
                echo "Salt-minion install error, please check it"
        fi
fi

/etc/init.d/salt-minion restart

rpm -qa|grep rsync || yum -y install rsync
rpm -qa|grep vim || yum -y install vim
rpm -qa|grep wget || yum -y install wget
