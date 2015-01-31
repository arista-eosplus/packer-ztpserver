#!/usr/bin/python

####################################
# Automatically setup a ZTPServer VM
# Author: eosplus-dev@arista.com
# Date: 20150113
####################################

import sys
import os
newPath = os.path.join( os.getcwd(), "lib")
sys.path.append(newPath)
from eosplusvnets import *

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

    if (hostOS == "windows" and hyper=="virtualbox"):
        build = "--only=%s-windows-iso" % hyper
    elif vmOS == "eos":
        build = "--only=%s-iso-eos" % hyper
    else:
        build = "--only=%s-iso" % hyper

    nameVar = "name=%s" % vmName

    try:
        if vmOS == "fedora":
            rc = subprocess.call(["packer", "build", build, "-var", nameVar,
                                 "ztps-fedora_20_x86_64.json" ], cwd="Fedora")
        elif vmOS == "eos":
            rc = subprocess.call(["packer", "build", build, "-var", nameVar,
                                 "ztps-fedora_20_i386.json" ], cwd="Fedora")
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
        if (vmOS == "fedora" or vmOS == "eos"):
            path = "Fedora/"
        else:
            path = "Ubuntu/"

        print "Path: %s" % path
        print "VM: %s" % vmPath

        subprocess.call([ cmd, "import", "--options", "keepallmacs", vmPath ], cwd=path)

        return True

def main():

    # Argument Variables
    hypervisors = ["vmware", "virtualbox"]
    oses = ["fedora", "ubuntu", "eos"]

    parser = argparse.ArgumentParser(description="Automatically install the ZTPServer Demo")
    parser.add_argument("-H", "--hypervisor", required=True, choices=hypervisors, help="Hypervisor to create VM in")
    parser.add_argument("-o", "--os", required=True, choices=oses, help="Desired OS to use for VM")
    parser.add_argument("-n", "--vmname", help="The Virtual Machine name")
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
            libDir = find("C:\\", "vmware.exe")
    elif hyper == "virtualbox":
        if hostOS == "darwin":
            libDir = find("/usr", "VBoxManage")
        elif hostOS == "windows":
            libDir = find("C:\\", "VBoxManage.exe")

    # Test to see if Packer is installed
    try:
        subprocess.call(["packer -v"], shell=True)
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
