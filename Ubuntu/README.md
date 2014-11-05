#Create an Ubuntu ZTPServer VM

##Introduction
You can use [Packer](https://packer.io) to automate the creation of the ZTPServer VM.
By using this method, you can be sure that all of the required packages and dependencies are installed right out of the gate. This setup will include some extra services like XMPP, Syslog, NTP, DHCP, DNS, LLDPAD and others (with complementary [configs](https://github.com/arista-eosplus/packer-ztpserver/tree/master/Ubuntu/conf)) to help you get a complete testing environment running quickly.

(All of the minor [details](#the-minor-details))



##1. Install Packer
First things first; we need Packer. Follow the steps below if you don't already have Packer installed.

###Manually
1. Download the appropriate binaries http://www.packer.io/downloads.html
2. Unzip and move to desired location eg ~/packer or /usr/local/share/ or /usr/local/bin/
3. Set ENV variable (or just put Packer somewhere the ```PATH``` is already pointing - ```echo $PATH```)
    * EG: in ~/.bash_login, add ```EXPORT PATH=$PATH:/path/to/packer/files```

###Automatically (MacOSX)
<pre>
$ brew tap homebrew/binary
$ brew install packer
</pre>

###Verify Installation
Run ```packer -v``` to make sure Packer is properly installed.



##2a. Creating a VM for use with VMware Fusion/Workstation
[I want to build a ZTPServer on VirtualBox - skip to section](#2b-creating-a-vm-for-use-with-virtualbox)

> **Note:** The following procedure was tested using VMWare Fusion 6.0.3/4 and Workstation 10

> **IMPORTANT:** Regarding VMware virtual networks: The default setup places eth1 on vmnet2. This might not be created in your VMware environment. Therefore, you may wish to run the [setup-fusion.sh](https://github.com/arista-eosplus/packer-veos/blob/master/VMware/setup-fusion.sh) script to help create this virtual network for you (VMware Fusion only). Once you have downloaded the script, ensure that is is executable, ```chmod +x setup-fusion.sh``` and then run it using ```sudo setup-fusion.sh```

1. Retrieve the ZTPServer Packer Config files [here](https://github.com/arista-eosplus/packer-ztpserver/archive/master.zip) or run from a shell on your local machine.
<pre>
git clone https://github.com/arista-eosplus/packer-ztpserver.git
</pre>
2. Move into position
<pre>
cd packer-ztpserver/Ubuntu
</pre>
3. Let Packer loose to create your VM
<pre>
packer build --only=vmware-iso ztps-ubuntu-12.04.4_amd64.json
</pre>
    Some logs worth noting
    <pre>
    Arista$ packer build --only=vmware-iso ztps-ubuntu-12.04.4_amd64.json
    vmware-iso output will be in this color.
    ==> vmware-iso: Downloading or copying ISO
        vmware-iso: Downloading or copying: http://releases.ubuntu.com/12.04/ubuntu-12.04.4-server-amd64.iso
    </pre>
    Once the ISO is downloaded, packer brings up a VMWare VM. The Anaconda installation will proceed without any user input.
    After 10 minutes the OS installation will be complete, the VM will reboot, and you will be presented with a login prompt.  **Resist the urge to log in and tinker** - the [setup.sh](https://github.com/arista-eosplus/packer-ztpserver/blob/master/Ubuntu/scripts/setup.sh) script is about to be kicked off.
    You'll notice the packer builder ```ssh``` into the VM and begin working on updating, installing and configuring new services.

    <pre>
    ==> vmware-iso: Connecting to VM via VNC
    ==> vmware-iso: Typing the boot command over VNC
    ==> vmware-iso: Waiting for SSH to become available
    ==> vmware-iso: Connected to SSH!
    ==> vmware-iso: Uploading conf => /tmp/packer
    ==> vmware-iso: Uploading files => /tmp/packer
    ==> vmware-iso: Provisioning with shell script: scripts/setup.sh
        vmware-iso: + apt-get -y update
    ... (shell script output)
    </pre>

    After some extensive apt-getting (~5minutes), you will see:
    <pre>
    ==> vmware-iso: Gracefully halting virtual machine
        vmware-iso: Waiting for VMware to clean up after itself
    ==> vmware-iso: Deleting unnecessary VMware files
        vmware-iso: Deleting: output-vmware-iso/startMenu.plist
        vmware-iso: Deleting: output-vmware-iso/vmware.log
        vmware-iso: Deleting: output-vmware-iso/ztps.plist
        vmware-iso: Deleting: output-vmware-iso/ztps.vmx.lck/M62713.lck
    ==> vmware-iso: Cleaning VMX prior to finishing up
        vmware-iso: Detaching ISO from CD-ROM device
    ==> vmware-iso: Compacting the disk image
    Build 'vmware-iso' finished.
    ==> Builds finished. The artifacts of successful builds are:
    --> vmware-iso: VM files in directory: output-vmware-iso
    </pre>

    You now have a full-featured ZTPServer.  We've gone ahead and placed some demo files from [GitHub](https://github.com/arista-eosplus/ztpserver-demo) to make life a little easier. All of the interesting files are in ```/usr/share/ztpserver``` and ```/etc/ztpserver/```.
4. Log into the server with user ```root``` and password ```eosplus```. Simply type to start the standalone ztpserver:
<pre>
ztps
</pre>
or to send all console output to a file:
<pre>
ztps --debug </dev/null >/var/log/ztps-console.log 2>&1 &
</pre>
You can stop the ztps process anytime by typing
<pre>
pkill ztps
</pre>
Refer to the [ZTPServer Documentation](http://ztpserver.readthedocs.org/en/develop/) to learn how to customize your ZTPServer. You can create some [vEOS](https://github.com/arista-eosplus/packer-veos) nodes using Packer to help get your demo working even faster.





##2b. Creating a VM for use with VirtualBox
> **Note:** The following procedure was tested using VirtualBox 4.3.12. **This does not work on Windows with 4.3.14.**

> **IMPORTANT:** Regarding VirtualBox networks: The default setup places eth1 on vboxnet2. This might not be created in your Virtual Box environment.  
Therefore, open Vbox and open the **General Settings/Preferences** menu. Click on the **Network** tab. Click on **Host-only Networks.**
Add or Modify vboxnet2.  Configure the IP Address for 172.16.130.1, the Netmask 255.255.255.0 and turn off the DHCP server.

1. Retrieve the ZTPServer Packer Config files [here](https://github.com/arista-eosplus/packer-ztpserver/archive/master.zip) or run from a shell on your local machine.
<pre>
git clone https://github.com/arista-eosplus/packer-ztpserver.git
</pre>
2. Move into position
<pre>
cd packer-ztpserver/Ubuntu
</pre
3. Let Packer loose to create your VM
  1. For VirtualBox on MacOSX or Linux
<pre>
packer build --only=virtualbox-iso ztps-ubuntu-12.04.4_amd64.json
</pre>
  2. For VirtualBox on Windows
<pre>
packer build --only=virtualbox-windows-iso ztps-ubuntu-12.04.4_amd64.json
</pre>
    Some logs worth noting:
    <pre>
    Arista$ packer build --only=virtualbox-iso ztps-ubuntu-12.04.4_amd64.json
    virtualbox-iso output will be in this color.
    ==> virtualbox-iso: Downloading or copying Guest additions checksums
        virtualbox-iso: Downloading or copying: http://download.virtualbox.org/virtualbox/4.3.12/SHA256SUMS
    ==> virtualbox-iso: Downloading or copying Guest additions
        virtualbox-iso: Downloading or copying: http://download.virtualbox.org/virtualbox/4.3.12/VBoxGuestAdditions_4.3.12.iso
    ==> virtualbox-iso: Downloading or copying ISO
        virtualbox-iso: Downloading or copying: http://releases.ubuntu.com/12.04/ubuntu-12.04.4-server-amd64.iso
    </pre>

    Once the ISO is downloaded, packer brings up a VBox VM. The installation will proceed without any user input.
    After a few minutes the OS installation will be complete, the VM will reboot, and you will be presented with a login prompt.  **Resist the urge to log in and tinker** - the setup.sh script is about to be kicked off.
    You'll notice the packer builder ```ssh``` into the VM and begin working on updating, installing and configuring new services.

    <pre>
    ==> virtualbox-iso: Waiting for SSH to become available...
    ==> virtualbox-iso: Connected to SSH!
    ==> virtualbox-iso: Uploading VirtualBox version info (4.3.12)
    ==> virtualbox-iso: Uploading VirtualBox guest additions ISO...
    ==> virtualbox-iso: Uploading conf => /tmp/packer
    ==> virtualbox-iso: Uploading files => /tmp/packer
    ==> virtualbox-iso: Provisioning with shell script: scripts/setup.sh
    ... (shell script output)
    </pre>
    After some extensive apt-getting (<5minutes), you will see:

    <pre>
    ==> virtualbox-iso: Gracefully halting virtual machine
        virtualbox-iso: Broadcast message from root@ztps.ztps-test.com on pts/0 (Tue 2014-06-17 08:44:25 EDT):
        virtualbox-iso: The system is going down for power-off NOW!
    ==> virtualbox-iso: Preparing to export machine...
        virtualbox-iso: Deleting forwarded port mapping for SSH (host port 3213)
    ==> virtualbox-iso: Exporting virtual machine
        virtualbox-iso: Executing: export ztps-ubuntu-12.04.4_amd64-2014-06-17T12:29:58Z --output output-virtualbox-iso/ztps-ubuntu-12.04.4_amd64-2014-06-17T12:29:58Z.ovf
    ==> virtualbox-iso: Unregistering and deleting virtual machine
    Build 'virtualbox-iso' finished.
    ==> Builds finished. The artifacts of successful builds are:
    --> virtualbox-iso: VM files in directory: output-virtualbox-iso
    Build 'vmware-iso' finished.
    </pre>
    You now have a full-featured ZTPServer. We've gone ahead and placed some demo files from [GitHub](https://github.com/arista-eosplus/ztpserver-demo) to make life a little easier. All of the interesting files are in ```/usr/share/ztpserver``` and ```/etc/ztpserver/```.
4. Log into the server with user ```root``` and password ```eosplus```. Simply type to start the standalone ztpserver:
<pre>
ztps
</pre>
or to send all console output to a file:
<pre>
ztps --debug </dev/null >/var/log/ztps-console.log 2>&1 &
</pre>
You can stop the ztps process anytime by typing
<pre>
pkill ztps
</pre>
Refer to the [ZTPServer Documentation](http://ztpserver.readthedocs.org/en/develop/) to learn how to customize your ZTPServer. You can create some [vEOS](https://github.com/arista-eosplus/packer-veos) nodes using Packer to help get your demo working even faster.

> **Note**: If you created the VM with VBox, you will have to navigate to the output folder and double-click on the .ovf file to import it into Virtual Box.

##Setting up a Quick Demo
As part of the installation above, sample files were copied from the ztpserver-demo repo and placed into the necessary locations ( /etc/ztpserver/ and /usr/share/ztpserver/). If you used [packer-veos](https://github.com/arista-eosplus/packer-veos) to create vEOS nodes, then you can just start the ZTPserver by typing ```ztps``` and watch the nodes retrieve their configuration.  If you have existing vEOS nodes that you would like to use follow the steps below.

1. Type ```show version``` in your vEOS node to get it's MAC address.
2. Log into the ZTPserver with username ```root``` and password ```eosplus```.
3. Type ```cd /usr/share/ztpserver/nodes```.
4. Copy the default spine-1 config (001122334455) to a new node that has the MAC address of your local vEOS instance. ```mv 001122334455 <local spine MAC>```. Repeat this procedure for the 001122334456 node.  This will become spine-2.
5. start ztpserver ```ztps``` and watch the two nodes retrieve their configuration from ZTP mode.



##The Minor Details
* Create a VM with 7GB Hard Drive
* 2GB RAM
* Ubuntu Server 12.04 Standard Install
* Python 2.7.x with PIP
* Hostname ztps.ztps-test.com
    * eth0 (NAT) VBox DHCP
    * eth1 (vboxnet2/vmnet2) Runs ZTPServer services
* UFW Firewall disabled.
* Users
    * root/eosplus and ztpsadmin/eosplus
* DHCP installed with Option 67 configured (eth1 only)
* BIND DNS server installed with zone ztps-test.com
    * wildcard forward rule to 8.8.8.8 for all other queries
    * XMPP SRV RR for im.ztps-test.com
* rsyslog-ng installed; Listening on UDP and TCP (port 514)
* XMPP server configured for im.ztps-test.com
    * XMPP admin user ztpsadmin@im.ztps-test.com, passwd eosplus
* Apache2 installed and configured for ZTPServer (mod_wsgi) running on port 8080
* ZTPServer installed (with [sample files](https://github.com/arista-eosplus/ztpserver-demo) to get you up and running)




##Troubleshooting
###Gathering Diags
To gather a log file, just pre-pend ```PACKER_LOG=true PACKER_LOG_PATH=./debug.log```.  For example, ```PACKER_LOG=true PACKER_LOG_PATH=./debug.log packer build ztps-fedora_20_x86_64.json```.

###Potential Issues

####References
http://www.packer.io/docs/builders/virtualbox-iso.html
