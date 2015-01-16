#Automatically Create a Full-Featured ZTPServer

##Introduction
This project uses [Packer](https://packer.io) to automatically create a
full-featured ZTPServer VM.
By using this method, you can be sure that all of the required packages and
dependencies are installed right out of the gate.
This setup will include some extra services like XMPP, Syslog, NTP, DHCP, DNS,
LLDPAD and others to help you get a complete testing environment running quickly.

You can also use Packer to automate the setup of [vEOS nodes](https://github.com/arista-eosplus/packer-veos).

###What's Supported
* **Host Operating Systems**
  * Windows
  * Mac Osx
* **Host Hypervisors**
  * VirtualBox
  * VMware Fusion
  * VMware Workstation
* **VM Remote Operating Systems**
  * Fedora 20
  * Ubuntu 12.04

##Getting Started
There is a nice, shiny [python script](https://github.com/arista-eosplus/packer-ztpserver/blob/master/create-ztpserver.py)
that will make your life very easy!

Here's what it's going to do:
* Download and install [Packer](https://packer.io) to ~/packer-bin (~80MB)
* Create some virtual networks. It might also change existing settings,
but we'll create a backup just in case you want to revert. Check out the
[details](#the-minor-details) for more information. We won't disturb **vmnet0**(Workstation),  **vmnet1** and **vmnet8** in VMware which are
the default networks.
* Create a ZTPServer VM with the hypervisor you choose.

###Requirements
* Python (this has been tested on Python 2.7.x)
 * [Get Python 2.7.x for Windows](https://www.python.org/downloads/windows/)
* Git (technically optional but makes life easier)
 * [Get Git](http://git-scm.com/downloads)
* User running script has sudo privileges (NIX-based)

###Go Time
####Script Arguments
<pre>
arista:packer-ztpserver arista$ ./create-ztpserver.py --help
usage: create-ztpserver.py [-h] [-N VMNAME]
{vmware,virtualbox} {fedora,ubuntu}

Automatically install the ZTPServer Demo

positional arguments:
{vmware,virtualbox}   Hypervisor to create VM in
{fedora,ubuntu}       Desired OS to use for VM

optional arguments:
-h, --help                  show this help message and exit
-N VMNAME, --vmname VMNAME  The Virtual Machine name Prefix
</pre>

1. Retrieve the ZTPServer Packer files [here](https://github.com/arista-eosplus/packer-ztpserver/archive/master.zip) or run from a shell on your local machine.
  <pre>
  git clone https://github.com/arista-eosplus/packer-ztpserver.git
  cd packer-ztpserver
  </pre>
2. Fire in the hole

  **NIX-based Terminal**
  <pre>
  python ./create-ztpserver.py [vmware|virtualbox] [fedora|ubuntu] --vmname VMNAME-PREFIX
  </pre>
  > **IMPORTANT:** You may have to enter your sudo password so keep an eye on it.

  **Windows-based Command-Prompt**
  > **IMPORTANT:** Open the command prompt as an Administrator so you don't have to authorize every command

  <pre>
  C:\> C:\Python27\python.exe ./create-ztpserver.py [vmware|virtualbox] [fedora|ubuntu] --vmname VMNAME-PREFIX
  </pre>
  > **Note:** Your Python executable might be somewhere else, or part of your
    %PATH% in which case you could just type ```python```, but this is just
    meant to be a general idea.

3. When the script exits successfully you will have a full-featured ZTPServer.  We've gone ahead and placed some demo files from [GitHub](https://github.com/arista-eosplus/ztpserver-demo) to make life a little easier. All of the interesting files are in ```/usr/share/ztpserver``` and ```/etc/ztpserver/```.
4. Log into the server with user ```ztpsadmin``` and password ```eosplus```. Simply type the following to start the standalone ztpserver:
<pre>
ztps
</pre>
  or to send all console output to a file:
  ```
  ztps --debug </dev/null >~/ztps-console.log 2>&1 &
  ```
  You can stop the ztps process anytime by typing
  <pre>
  pkill ztps
  </pre>
  You can also run the ZTPServer as an Apache Web Server Gateway Interface.  All of  the necessary config is already in place.  Just start Apache:
  > **Note:** The ZTPServer can only run in Standalone mode OR as an WSGI App. Kill the ztps process first if you would like to run the WSGI App.

  <pre>
  systemctl start httpd
  systemctl enable httpd
  </pre>
  WSGI related logs will be in ```/var/log/messages``` and ```/var/log/httpd/error.log```
  Refer to the [ZTPServer Documentation](http://ztpserver.readthedocs.org/en/develop/) to learn how to customize your ZTPServer. You can create some [vEOS](https://github.com/arista-eosplus/packer-veos) nodes using Packer to help get your demo working even faster.

###Post-Installation
If Packer is installed via the script above, the packer binary wasn't permanently
added to your ```PATH```.  If you intend on using Packer again, you might consider
updating your ```PATH``` variable.

**NIX-Based Terminal**
<pre>
echo "export PATH=$PATH:~/packer-bin" >> ~/.bash_profile
</pre>
and then restart your bash.

**Windows-Based Command Prompt**
<pre>
setx PATH "%PATH%;%USERPROFILE%\packer-bin"
</pre>
and then restart your ```cmd.exe```.

##The Minor Details
###Virtual Networks
Host-only virtual networks will be created:
* vboxnet2/vmnet2
  * Used for Eth1 on the ZTPServer.  This is the internal management network
  * DHCP off
  * NAT off
* vboxnet3/vmnet3
  * Proactively created for use with vEOS demo - data network
  * DHCP off
  * NAT off
* vboxnet4/vmnet4
  * Proactively created for use with vEOS demo - data network
  * DHCP off
  * NAT off
* vboxnet5/vmnet5
  * Proactively created for use with vEOS demo - data network
  * DHCP off
  * NAT off
* vboxnet6/vmnet6
  * Proactively created for use with vEOS demo - data network
  * DHCP off
  * NAT off
* vboxnet7/vmnet7
  * Proactively created for use with vEOS demo - data network
  * DHCP off
  * NAT off
* vboxnet9/vmnet9
  * Proactively created for use with vEOS demo - data network
  * DHCP off
  * NAT off
* vboxnet10/vmnet10
  * Proactively created for use with vEOS demo - data network
  * DHCP off
  * NAT off

###The ZTPServer VM
* Create a VM with 7GB Hard Drive
* 2GB RAM
* Python 2.7.x with Pip
* Hostname ztps.ztps-test.com
* eth0 (NAT) DHCP
* eth1 (vboxnet2/vmnet2) 172.16.130.10/24
* Firewall disabled.
* Users
  * root/eosplus and ztpsadmin/eosplus
* DHCP installed with Option 67 configured (eth1 only)
* BIND DNS server installed with zone ztps-test.com
* wildcard forward rule to 8.8.8.8 for all other queries
* XMPP SRV RR for im.ztps-test.com
* rsyslog-ng installed; Listening on UDP and TCP (port 514)
* XMPP server configured for im.ztps-test.com
* XMPP admin user ztpsadmin@im.ztps-test.com, passwd eosplus
* httpd installed and configured for ZTPServer (mod_wsgi).  The configuration files are in place, but httpd is not running by default.
* ZTPServer installed (with [sample files](https://github.com/arista-eosplus/ztpserver-demo) to get you up and running)

If you run into any snags, please feel free to raise an issue and attach the
logs.
