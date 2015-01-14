#!/bin/sh -x

# grab any updates and cleanup
apt-get -y update
apt-get -y upgrade

# install ztps-related related packages
apt-get -y install python-dev
apt-get -y install python-pip
apt-get -y install libapache2-mod-wsgi
apt-get -y install libyaml-dev
apt-get -y install screen
apt-get -y install git
apt-get -y install lldpad
apt-get -y install apache2
apt-get -y install isc-dhcp-server
apt-get -y install bind9 dnsutils
apt-get -y install ejabberd
apt-get -y install ntp

# add ztpsadmin to sudo group
adduser ztpsadmin sudo

######################################
# CONFIGURE FIREWALL
######################################
# disable UFW
ufw disable
ufw status
ifconfig

echo "auto eth1
iface eth1 inet static
address 172.16.130.10
netmask 255.255.255.0
" >> /etc/network/interfaces
ifup eth1

######################################
# CONFIGURE LLDP
######################################
service lldpad start
lldptool -L -i eth1 adminStatus=rxtx
lldptool -T -i eth1 -V sysName enableTx=yes
lldptool -T -i eth1 -V sysDesc enableTx=yes

######################################
# CONFIGURE SCREEN
######################################
cp /tmp/packer/screenrc /home/ztpsadmin/.screenrc
cp /tmp/packer/screenrc /root/.screenrc

######################################
# CONFIGURE ntp
######################################
cp /tmp/packer/ntp.conf /etc/ntp.conf
service ntp restart

######################################
# CONFIGURE rsyslog
######################################
mv /etc/rsyslog.conf /etc/rsyslog.conf.bak
cp /tmp/packer/rsyslog.conf /etc/rsyslog.conf
service rsyslog restart
netstat -tuplen | grep syslog

######################################
# CONFIGURE eJabberd
######################################
mv /etc/ejabberd/ejabberd.cfg /etc/ejabberd/ejabberd.cfg.bak
cp /tmp/packer/ejabberd.cfg /etc/ejabberd/ejabberd.cfg
echo -e "127.0.0.1 ztps ztps.ztps-test.com" >> /etc/hosts
service ejabberd restart
sleep 3
ejabberdctl register cvx im.ztps-test.com eosplus
ejabberdctl register ztpsadmin im.ztps-test.com eosplus
ejabberdctl register bootstrap im.ztps-test.com eosplus
ejabberdctl register veos-dc1-pod1-tor1 im.ztps-test.com eosplus
ejabberdctl register veos-dc1-pod1-tor2 im.ztps-test.com eosplus
ejabberdctl register veos-dc1-pod1-tor3 im.ztps-test.com eosplus
ejabberdctl register veos-dc1-pod1-tor4 im.ztps-test.com eosplus
ejabberdctl register veos-dc1-pod1-tor5 im.ztps-test.com eosplus
ejabberdctl register veos-dc1-pod1-tor6 im.ztps-test.com eosplus
ejabberdctl register veos-dc1-pod1-spine1 im.ztps-test.com eosplus
ejabberdctl register veos-dc1-pod1-spine2 im.ztps-test.com eosplus
ejabberdctl register veos-dc1-pod1-spine3 im.ztps-test.com eosplus
ejabberdctl register veos-dc1-pod1-spine4 im.ztps-test.com eosplus
service ejabberd restart
sleep 6
ejabberdctl status

######################################
# CONFIGURE APACHE
######################################
mv /etc/apache2/ports.conf /etc/apache2/ports.conf.bak
cp /tmp/packer/ports.conf /etc/apache2/ports.conf

rm /etc/apache2/sites-enabled/000-default
cp /tmp/packer/001-ztpserver /etc/apache2/sites-enabled/001-ztpserver

service apache2 restart
# stopping apache since ZTPServer will run in standalone mode on port 8080
service apache2 stop
update-rc.d -f apache2 remove
service apache2 status

######################################
# CONFIGURE BIND
######################################
mv /etc/bind/named.conf.default-zones /etc/bind/named.conf.default-zones.bak
touch /etc/bind/named.conf.default-zones
cp /tmp/packer/named.conf.local /etc/bind/named.conf.local
mkdir /etc/bind/zones
cp /tmp/packer/db.ztps-test.com /etc/bind/zones/db.ztps-test.com

service bind9 restart
named-checkconf -z

######################################
# CONFIGURE DHCP
######################################
mv /etc/dhcp/dhcpd.conf /etc/dhcp/dhcpd.conf.bak
cp /tmp/packer/dhcpd.conf /etc/dhcp/dhcpd.conf
service isc-dhcp-server start

######################################
# INSTALL ZTPSERVER
######################################
cd /home/ztpsadmin

# clone from GitHub
git clone https://github.com/arista-eosplus/ztpserver.git
cd ztpserver
git checkout v1.2.0

# build/install
python setup.py build
python setup.py install

mkdir /home/ztpsadmin/ztps-sampleconfig
cd /home/ztpsadmin/ztps-sampleconfig
git clone https://github.com/arista-eosplus/ztpserver-demo.git

cd ztpserver-demo/
cp -R ./definitions /usr/share/ztpserver/
cp -R ./files /usr/share/ztpserver/
cp -R ./nodes /usr/share/ztpserver/
cp -R ./resources /usr/share/ztpserver/
cp -R ./neighbordb /usr/share/ztpserver/
cp ztpserver.conf /etc/ztpserver/ztpserver.conf
cp bootstrap.conf /usr/share/ztpserver/bootstrap/bootstrap.conf

cd /usr/share/ztpserver/files
mkdir images
cp -R /tmp/packer/files/images .
mkdir puppet
cp -R /tmp/packer/files/puppet .

echo "auto lo
iface lo inet loopback

auto eth0
iface eth0 inet dhcp

auto eth1
iface eth1 inet static
address 172.16.130.10
netmask 255.255.255.0
" > /etc/network/interfaces

######################################
# Prepare ZTPServer for WSGI
######################################
# modify SELinux policy
chown -R www-data:www-data /usr/share/ztpserver
chcon -R -h system_u:object_r:httpd_sys_script_rw_t /usr/share/ztpserver
