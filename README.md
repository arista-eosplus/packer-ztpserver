#Automatically Create a Full-Featured ZTPServer

##Introduction
You can use [Packer](https://packer.io) to automate the creation of the ZTPServer VM.
By using this method, you can be sure that all of the required packages and dependencies are installed right out of the gate. This setup will include some extra services like XMPP, Syslog, NTP, DHCP, DNS, LLDPAD and others to help you get a complete testing environment running quickly.

You can also use Packer to automate the setup of [vEOS nodes](https://github.com/arista-eosplus/packer-veos).

###What's Supported
* **ZTPServer**
  * Ubuntu 12.04 on Virtual Box
  * Ubuntu 12.04 on VMWare
  * Fedora 20 on VMWare
  * Fedora 20 on Virtual Box


##Getting Started
 * [Create Fedora ZTPServer VM](https://github.com/arista-eosplus/packer-ztpserver/tree/master/Fedora)
 * [Create Ubuntu ZTPServer VM](https://github.com/arista-eosplus/packer-ztpserver/tree/master/Ubuntu)

Feel free to raise an issue and attach logs if you run into any problems.
