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
  * EOS (run as a 32-bit Fedora 20 VM on EOS)
* **Host Hypervisors**
  * VirtualBox
  * VMware Fusion
  * VMware Workstation
  * VMware [ESXi](#how-the-esxi-builder-works)
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
arista:packer-ztpserver arista$ ./create-ztpserver.py -h
usage: create-ztpserver.py [-h] -H {vmware,esxi,virtualbox} -o
                           {fedora,ubuntu,eos} [-n VMNAME] [-d DISK_SIZE]
                           [-u ESXI_USER] [-e ESXI_HOST] [-p DATASTORE_PATH]
                           [-i ESXI_NETWORK]

Automatically install the ZTPServer Demo

optional arguments:
  -h, --help            show this help message and exit
  -H {vmware,esxi,virtualbox}, --hypervisor {vmware,esxi,virtualbox}
                        Hypervisor to create VM in
  -o {fedora,ubuntu,eos}, --os {fedora,ubuntu,eos}
                        Desired OS to use for VM
  -n VMNAME, --vmname VMNAME
                        The Virtual Machine name
  -d DISK_SIZE, --disk-size DISK_SIZE
                        VM Disk size in MB
  -u ESXI_USER, --esxi-user ESXI_USER
                        The ESXi username
  -e ESXI_HOST, --esxi-host ESXI_HOST
                        The IP or hostname of the ESXi host
  -p DATASTORE_PATH, --datastore-path DATASTORE_PATH
                        The ESXi path to save the VM
  -i ESXI_NETWORK, --esxi-network ESXI_NETWORK
                        vSphere network assigned to VM that allows
                        communication with local builder
</pre>

1. Retrieve the ZTPServer Packer files [here](https://github.com/arista-eosplus/packer-ztpserver/archive/master.zip) or run from a shell on your local machine.
  <pre>
  git clone https://github.com/arista-eosplus/packer-ztpserver.git
  cd packer-ztpserver
  </pre>
2. Fire in the hole

  **NIX-based Terminal**
  <pre>
  python ./create-ztpserver.py -H [vmware|virtualbox|esxi] -o [fedora|ubuntu|eos] --vmname VMNAME-PREFIX
  </pre>
  > **IMPORTANT:** You will have to enter your sudo password so keep an eye on it.

  **Windows-based Command-Prompt**
  > **IMPORTANT:** Open the command prompt as an Administrator so you don't have to authorize every command

  <pre>
  C:\> C:\Python27\python.exe ./create-ztpserver.py -H [vmware|virtualbox|esxi] -o  [fedora|ubuntu|eos] --vmname VMNAME-PREFIX
  </pre>
  > **Note:** Your Python executable might be somewhere else, or part of your
    %PATH% in which case you could just type ```python```, but this is just
    meant to be a general idea.

  **Examples:**

  Create an Ubuntu ZTPServer VM for Fusion with VM name prefix "my-demo"
  <pre>
  create-ztpserver.py -H vmware -o ubuntu --vmname my-demo
  </pre>
  Create a Fedora ZTPServer VM for Workstation with VM name prefix "my-demo"
  <pre>
  create-ztpserver.py -H vmware -o fedora --vmname my-demo
  </pre>
  Create a Fedora ZTPServer VM for Fusion with 10GB disk
  <pre>
  create-ztpserver.py -H vmware -o fedora -d 10000
  </pre>
  Create a ZTPServer VM that runs on an EOS device
  <pre>
  create-ztpserver.py -H vmware -o eos
  </pre>
  Create a Fedora ZTPServer VM that runs on an ESXi host
  <pre>
  create-ztpserver.py -H esxi -o fedora -u esxiUser -e esxi-host.example.com -p Datastore1/ztpservers -i net_vlan100
  </pre>

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

###Post-Installation Tips
####Set the PATH Variable
If Packer is installed via the script above, the packer binary path wasn't permanently
added to your system ```PATH``` variable.  If you intend on using Packer again, you might consider
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

####Upload the EOS VM to an Arista Switch
**Step 1:** First SCP the resulting .vmdk file to your Arista switch
```
scp disk.vmdk admin@eos-switch-1:/mnt/dst/path
```
**Step 2:** Create Virtual-Machine entry.  Log into your EOS switch:
```
eos-switch-1#conf
eos-switch-1(config)#virtual-machine ztps
eos-switch-1(config-ztps)#disk-image usb1:/path/disk.vmdk image-format vmdk
eos-switch-1(config-ztps)#memory-size 1024 ! Choose a desired size
eos-switch-1(config-ztps)#enable
```
**Step 3:** Confirm the VM is running
```
eos-switch-1#show virtual-machine
VM Name              Enabled    State
-------              -------    -----
ztps                 Yes        Running
```
**Step 4:** Console into the ZTPServer VM
```
eos-switch-1#bash
[admin@eos-switch-1 ~]$ sudo virsh
virsh # list
Id Name                 State
----------------------------------
1 ztps                  running

virsh # console 1
error: Failed to get local hostname
error: Failed to get connection hostname
Connected to domain ztps
Escape character is ^]

[root@ztps ~]# echo hello world
```

##The Minor Details
###How the ESXi Builder Works
Packer provides built-in support for VM creation on VMware ESXi. In this case,
you still execute the ```create-ztpserver``` script on your local machine, but
you provide details for Packer to upload and create the VM on your ESXi host.

####Require Parameters
* ```-u``` ESXi Username: This is the username used to log into your ESXi host
* ```-e``` ESXi Host: The IP or resolvable hostname of your ESXi host
* ```-p``` ESXi Datastore path: This is where the script will copy your VM to. Typically it looks something like ```Datastore-1/path/to/dir```
* ```-i``` ESXi Network Name: Your local machine and the VM must be able to communicate.  So this must be the network that provides that network connectivity.

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
* 7GB Hard Drive
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
* rsyslog-ng installed; Listening on UDP and TCP (port 514)
* XMPP server configured for im.ztps-test.com
* XMPP admin user ztpsadmin@im.ztps-test.com, passwd eosplus
* httpd installed and configured for ZTPServer (mod_wsgi).  The configuration files are in place, but httpd is not running by default.
* ZTPServer installed (with [sample files](https://github.com/arista-eosplus/ztpserver-demo) to get you up and running)

If you run into any snags, please feel free to raise an issue and attach the
logs.
