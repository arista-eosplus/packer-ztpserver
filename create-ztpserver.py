#!/usr/bin/python

####################################
# Automatically setup a ZTPServer VM
# Author: eosplus-dev@arista.com
# Date: 20150113
####################################

import sys
import os
import re
import ssl
import platform
import argparse
import subprocess
import datetime
import urllib
import zipfile
import getpass


packerURL = "http://dl.bintray.com/mitchellh/packer"
packerVersion = "0.7.5"

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def getHostOS():
    return platform.system().lower()

def getHostArch():
    is_64bits = sys.maxsize > 2**32
    return 64 if is_64bits else 32

def find(path, name):
    print "Searching %s for %s..." % (path, name)
    # Look recursively through OS for files
    for root, dirs, files in os.walk(path):
        #print files
        if name in files:
            print "Found file here:%s" % root
            return root
        if name in dirs:
            print "Found file here:%s" % root
            return os.path.join(root, name)

def getUnzipped(url, dest, fn):
    name = os.path.join(dest, fn)
    try:
        print "Downloading Packer binaries to %s" % name
        print "This may take a few minutes (~85MB)..."
        #name, hdrs = urllib.urlretrieve(url, name)
    except IOError, e:
        print "Can't retrieve %r to %r: %s" % (url, name, e)
        raise
    print "Download successful!"
    try:
        print "Unzipping %s..." % name
        with zipfile.ZipFile(name, "r") as z:
            bin = os.path.join(dest, "packer-bin")
            z.extractall(bin)
    except zipfile.error, e:
        print "Bad zipfile (from %r): %s" % (url, e)
        raise
    print "Unzipped successfully to %s" % bin
    return bin

def installPacker(hostOS, hostArch):
    if hostArch == 64:
        arch = "amd64"
    else:
        arch = "386"

    url = "%s/packer_%s_%s_%s.zip" % (packerURL, packerVersion, hostOS, arch)

    installPath = os.path.expanduser('~')
    packerDir = getUnzipped(url, installPath, "packer-bin.zip")
    packerDir = os.path.join(installPath, "packer-bin")

    # Add packer-bin to path
    os.environ["PATH"] += os.pathsep + packerDir
    print "Updated path to be:%s" % os.environ["PATH"]
    try:
        print "Checking if install was successful by running 'packer -v'"
        subprocess.call(["packer", "-v"])
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print "Packer installation failed"
            raise
        else:
            print "Something else went wrong"
            raise

    print "Packer installed!"

def getActiveNets(cmd, regex):
    # Get existing networks and return array of numbers
    try:
        ifconfig = subprocess.check_output(cmd)
        return re.findall(r"%s" % regex, ifconfig)
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print "vboxnet creation failed. Check output above"
            raise
        else:
            print "Something else went wrong"
            raise

def createVBoxNets(hostOS, hostArch, libDir):
    print "Creating virtual networks for Virtual Box"

    if hostOS == "darwin":
        # Open VirtualBox App
        print "Opening VirtualBox application..."
        cmd = ["open", "-a", "VirtualBox"]
        process = subprocess.Popen(cmd)

        #Get list of current networks
        cmd = ["ifconfig", "-a"]
        regex = "vboxnet(\d+)"
        activeNets = getActiveNets(cmd, regex)
        print activeNets

        # Create vmnets
        vmnets = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10)
        if len(activeNets) < len(vmnets):
            numCreate = len(vmnets) - len(activeNets)
            for i in range(0, numCreate):
                try:
                    cmd = "%s/vboxmanage" % libDir
                    subprocess.call([cmd, "hostonlyif", "create"])
                except OSError as e:
                    if e.errno == os.errno.ENOENT:
                        print "vboxnet creation failed. Check output above"
                        raise
                    else:
                        print "Something else went wrong"
                        raise
        else:
            print "Enough existing virtual networks exist. Let's just reconfigure them."

        try:
            for net in vmnets:

                print "###############################"
                print "Creating/modifying vboxnet%s" % net
                print "###############################"
                network = int(net) + 128
                print "Assigning vboxnet%s to 172.16.%s.1/24" % (net, network)

                cmd = "%s/vboxmanage" % libDir
                vboxnet = "vboxnet%s" % net
                ip = "172.16.%s.1" % network
                subprocess.call([cmd, "hostonlyif", "ipconfig", vboxnet,
                                 "-ip", ip, "-netmask", "255.255.255.0"])
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                print "vboxnet creation failed. Check output above"
                raise
            else:
                print "Something else went wrong"
                raise

        # Remove any DHCP Servers from virtual networks
        try:
            cmd = "%s/vboxmanage" % libDir
            dhcpList = subprocess.check_output([cmd, "list", "dhcpservers"])
            regex = "NetworkName:\s+(\S+)"
            hostOnlyDHCPSrvs = re.findall(r"%s" % regex, dhcpList)

            for srv in hostOnlyDHCPSrvs:
                print "Disabling HostOnlyIf DHCP Server %s" % srv
                subprocess.call([cmd, "dhcpserver", "remove", "--netname", srv])

            return True

        except OSError as e:
            if e.errno == os.errno.ENOENT:
                print "vboxnet creation failed. Check output above"
                raise
            else:
                print "Something else went wrong"
                raise

    elif hostOS == "windows":
        # Open VirtualBox App
        print "Opening VirtualBox application..."
        cmd = ["%s/VirtualBox.exe" % libDir]
        process = subprocess.Popen(cmd)

        #Get list of current networks
        cmd = ["ipconfig"]
        regex = "Ethernet.*(VirtualBox Host-Only.*):"
        activeNets = getActiveNets(cmd, regex)

        print "\n\nAnalyzing Host-Only Networks..."

        # Create vmnets
        vmnets = ("", " #2", " #3", " #4", " #5", " #6", " #7", " #8", " #9", " #10")
        if len(activeNets) < len(vmnets):
            if len(activeNets) > 0:
                print "Existing Host-Only networks found:"
                for n in activeNets:
                    print " - %s" % n
            else:
                print "No existing Host-Only networks found."

            numCreate = len(vmnets) - len(activeNets)
            print "Creating %s new Host-Only Networks" % numCreate
            for i in range(0, numCreate):
                try:
                    cmd = "%s/vboxmanage" % libDir
                    subprocess.call([cmd, "hostonlyif", "create"])
                except OSError as e:
                    if e.errno == os.errno.ENOENT:
                        print "vboxnet creation failed. Check output above"
                        raise
                    else:
                        print "Something else went wrong"
                        raise
        else:
            print "Enough existing virtual networks exist. Let's just reconfigure them."
            print "Existing Host-Only networks found:"
            for n in activeNets:
                print " - %s" % n

        try:
            network = 128
            for net in vmnets:

                print "Modifying VirtualBox Host-Only Ethernet Adapter%s" % net
                print " - Assigning VirtualBox Host-Only Ethernet Adapter%s to 172.16.%s.1/24\n" % (net, network)

                cmd = "%s/vboxmanage" % libDir
                vboxnet = "VirtualBox Host-Only Ethernet Adapter%s" % net
                ip = "172.16.%s.1" % network
                subprocess.call([cmd, "hostonlyif", "ipconfig", vboxnet,
                                 "-ip", ip, "-netmask", "255.255.255.0"])
                network += 1

        except OSError as e:
            if e.errno == os.errno.ENOENT:
                print "vboxnet creation failed. Check output above"
                raise
            else:
                print "Something else went wrong"
                raise

        # Remove any DHCP Servers from virtual networks
        try:
            cmd = "%s/vboxmanage" % libDir
            dhcpList = subprocess.check_output([cmd, "list", "dhcpservers"])
            regex = "NetworkName:\s+(\S+.*)"
            hostOnlyDHCPSrvs = re.findall(r"%s" % regex, dhcpList)

            print "######################"
            print "Disabling DHCP Servers"
            print "######################"
            for srv in hostOnlyDHCPSrvs:
                print " - Disabling DHCP Server %s" % srv
                subprocess.call([cmd, "dhcpserver", "remove", "--netname", "%s" % srv], shell=True)
        except OSError as e:
            if e.errno == os.errno.ENOENT:
                print "vboxnet creation failed. Check output above"
                raise
            else:
                print "Something else went wrong"
                raise
        return True

def createVmNets(hostOS, hostArch, libDir):
    print "Creating virtual networks for VMware"

    if hostOS == "darwin":
        # Open VMware Fusion App
        cmd = ["open", "-a", "VMware Fusion"]
        process = subprocess.Popen(cmd)

        # Create/modify vmnets
        vmnets = (2, 3, 4, 5, 6, 7, 9, 10, 11)
        try:
            print "Creating/modifying vmnets"
            for net in vmnets:

                print "###############################"
                print "Creating/modifying vmnet%s" % net
                print "###############################"

                network = int(net) + 128
                netcfgCmd = r"%s/vmnet-cfgcli" % libDir
                cfgCmd = r"%s/vmnet-cli" % libDir
                dhcpCmd = "VNET_%s_DHCP" % net
                subnetCmd = "VNET_%s_HOSTONLY_SUBNET" % net
                subnet = "172.16.%s.0" % network
                netmaskCmd = "VNET_%s_HOSTONLY_NETMASK" % net
                virtualCmd = "VNET_%s_VIRTUAL_ADAPTER" % net
                subprocess.call(["sudo", netcfgCmd, "vnetcfgadd", dhcpCmd, "no"])
                subprocess.call(["sudo", netcfgCmd, "vnetcfgadd", subnetCmd, subnet])
                subprocess.call(["sudo", netcfgCmd, "vnetcfgadd", netmaskCmd, "255.255.255.0"])
                subprocess.call(["sudo", netcfgCmd, "vnetcfgadd", virtualCmd, "yes"])

            # Configure and restart to take effect
            print "##################################"
            print "Committing vmware network services"
            print "##################################"
            subprocess.call(["sudo", cfgCmd, "--configure"])

            print "##################################"
            print "Stopping vmware network services"
            print "##################################"
            subprocess.call(["sudo", cfgCmd, "--stop"])

            print "##################################"
            print "Starting vmware network services"
            print "##################################"
            subprocess.call(["sudo", cfgCmd, "--start"])

            print "VMNets Installed!"

        except OSError as e:
            if e.errno == os.errno.ENOENT:
                print "vmnet creation failed. Check output above"
                raise
            else:
                print "Something else went wrong"
                raise

        return True

def createVM(hyper, hostOS, vmOS, vmName, user):
    d = datetime.datetime.now()
    time = d.strftime("%Y%m%d_%H%M%S")
    if vmName:
        vmName = "%s-%s_%s" % (vmName, vmOS, time)
    else:
        vmName = "ztps-%s_%s" % (vmOS, time)

    print "Using VM name %s" % vmName
    print "Creating VM with user %s" % user

    print bcolors.WARNING
    print "##############################################"
    print "WARNING: DO NOT TYPE IN VIRTUAL MACHINE WINDOW"
    print "##############################################"
    print bcolors.ENDC

    if hostOS == "windows":
        build = "--only=%s-windows-iso" % hyper
    else:
        build = "--only=%s-iso" % hyper

    nameVar = "name=%s" % vmName

    try:
        if vmOS == "fedora":
                rc = subprocess.call(["packer", "build", build, "-var", nameVar,
                                 "ztps-fedora_20_x86_64.json" ], cwd="Fedora")
        elif vmOS == "ubuntu":
                rc = subprocess.call(["packer", "build", build, "-var", nameVar,
                                 "ztps-ubuntu-12.04.4_amd64.json" ], cwd="Ubuntu")
        print "Return code:%s" % rc
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print "Unable to create Virtual Machine"
            raise
        else:
            print "Something else went wrong"
            raise

    if rc == 0:
        return vmName
    elif rc > 0:
        print "Packer install failed!!!"
        print "Please copy raise an issue at https://github.com/arista-eosplus/packer-ztpserver/issues with your console output."
        exit(rc)

def registerVbox(hyper, libDir, vmName, vmOS):
    #Import the VM into Vbox
    if hyper == "virtualbox":
        cmd = "%s/vboxmanage" % libDir
        vmPath = "%s-vbox/%s.ovf" % (vmName, vmName)
        if vmOS == "fedora":
            path = "Fedora/"
        else:
            path = "Ubuntu/"

        print "Path: %s" % path
        print "VM: %s" % vmPath

        subprocess.call([ cmd, "import", vmPath ], cwd=path)

def main():

    # Argument Variables
    hypervisors = ["vmware", "virtualbox"]
    oses = ["fedora", "ubuntu"]

    parser = argparse.ArgumentParser(description="Automatically install the ZTPServer Demo")
    parser.add_argument("hypervisor", choices=hypervisors, help="Hypervisor to create VM in")
    parser.add_argument("os", choices=oses, help="Desired OS to use for VM")
    parser.add_argument("-N", "--vmname", help="The Virtual Machine name")
    args = parser.parse_args()

    # Set install variables
    user = getpass.getuser()
    hyper = args.hypervisor
    vmOS = args.os
    if args.vmname:
        vmName = args.vmname
    else:
        vmName = ""

    # Get host machine information
    hostOS = getHostOS()
    hostArch = getHostArch()
    print "Tailoring install for a %s bit %s environment" % (hostArch, hostOS)

    print "Looking for hypervisor libraries"
    if hyper == "vmware":
        if hostOS == "darwin":
            libDir = find("/Applications", "vmnet-cli")
        elif hostOS == "windows":
            libDir = find("C:\\", "vmnetcfg")
    elif hyper == "virtualbox":
        if hostOS == "darwin":
            libDir = find("/usr", "VBoxManage")
        elif hostOS == "windows":
            libDir = find("C:\\", "VBoxManage.exe")

    # Test to see if Packer is installed
    try:
        subprocess.call(["packer", "-v"])
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print "Packer not found - install it"
            installPacker(hostOS, hostArch)
        else:
            print "Something else went wrong"
            raise

    # Setup Virtual Networks
    if hyper == "virtualbox":
        if createVBoxNets(hostOS, hostArch, libDir):
            # Create the Virtual Machine
            vmName = createVM(hyper, hostOS, vmOS, vmName, user)
            if vmName:
                if registerVbox(hyper, libDir, vmName, vmOS):
                    print "Successfully created VM %s!" % vmName
                    exit(0)

    elif hyper == "vmware":
        if createVmNets(hostOS, hostArch, libDir):
            # Create the Virtual Machine
            vmName = createVM(hyper, hostOS, vmOS, vmName, user)
            if vmName:
                print "Successfully created VM %s!" % vmName
                exit(0)


if __name__ == "__main__":
   main()
