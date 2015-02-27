#!/usr/bin/python

####################################
# Automatically setup a ZTPServer VM
# Author: eosplus-dev@arista.com
# Date: 20150113
####################################

import sys
import os
newPath = os.path.join(os.getcwd(), "lib")
sys.path.append(newPath)
from eosplusvnets import *


def createVM(hyper, hostOS, vmOS, vmName, user, packerCmd, **kwargs):

    d = datetime.datetime.now()
    time = d.strftime("%Y%m%d_%H%M%S")

    # Set packer logging variable
    os.environ['PACKER_LOG'] = "enable"
    os.environ['PACKER_LOG_PATH'] = "./packer-debug.log"

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

    if (hostOS == "windows" and hyper == "virtualbox"):
        build = "--only=%s-windows-iso" % hyper
    elif vmOS == "eos":
        build = "--only=%s-iso-eos" % hyper
    else:
        build = "--only=%s-iso" % hyper

    nameVar = "name=%s" % vmName

    try:
        if vmOS == "fedora":
            wkd = os.path.join(os.getcwd(), "Fedora")
            builder_file = "ztps-fedora_20_x86_64.json"
            if hyper == "esxi":
                esxi = kwargs["esxi_info"]
                opts = "-var name='%s' -var esxi-user='%s' -var esxi-passwd='%s' \
                        -var esxi-host='%s' -var esxi-path='%s' \
                        -var esxi-network='%s'" % (vmName, esxi['user'],
                                                   esxi['passwd'], esxi['host'],
                                                   esxi['datastore'],
                                                   esxi['network'])
            else:
                opts = "-var name='%s'" % vmName

        elif vmOS == "eos":
            wkd = os.path.join(os.getcwd(), "Fedora")
            builder_file = "ztps-fedora_20_i386.json"
            if hyper == "esxi":
                esxi = kwargs["esxi_info"]
                opts = "-var name='%s' -var esxi-user='%s' -var esxi-passwd='%s' \
                        -var esxi-host='%s' -var esxi-path='%s' \
                        -var esxi-network='%s'" % (vmName, esxi['user'],
                                                   esxi['passwd'], esxi['host'],
                                                   esxi['datastore'],
                                                   esxi['network'])
            else:
                opts = "-var name='%s'" % vmName

        elif vmOS == "ubuntu":
            wkd = os.path.join(os.getcwd(), "Ubuntu")
            builder_file = "ztps-ubuntu-12.04.4_amd64.json"
            if hyper == "esxi":
                esxi = kwargs["esxi_info"]
                opts = "-var name='%s' -var esxi-user='%s' -var esxi-passwd='%s' \
                        -var esxi-host='%s' -var esxi-path='%s' \
                        -var esxi-network='%s'" % (vmName, esxi['user'],
                                                   esxi['passwd'], esxi['host'],
                                                   esxi['datastore'],
                                                   esxi['network'])
            else:
                opts = "-var name='%s'" % vmName

        rc = subprocess.call("%s build %s %s %s" % (packerCmd, build, opts, builder_file),
                             shell=True, cwd=wkd)

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
        print "Please copy error ouput and raise an issue at https://github.com/arista-eosplus/packer-ztpserver/issues with your console output."
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

        subprocess.call([cmd, "import", "--options", "keepallmacs", vmPath], cwd=path)

        return True


def main():

    # Argument Variables
    hypervisors = ["vmware", "esxi", "virtualbox"]
    oses = ["fedora", "ubuntu", "eos"]

    parser = argparse.ArgumentParser(description="Automatically install the ZTPServer Demo")
    parser.add_argument("-H", "--hypervisor", required=True, choices=hypervisors, help="Hypervisor to create VM in")
    parser.add_argument("-o", "--os", required=True, choices=oses, help="Desired OS to use for VM")
    parser.add_argument("-n", "--vmname", help="The Virtual Machine name")
    parser.add_argument("-u", "--esxi-user", help="The ESXi username")
    parser.add_argument("-e", "--esxi-host", help="The IP or hostname of the ESXi host")
    parser.add_argument("-p", "--datastore-path", help="The ESXi path to save the VM")
    parser.add_argument("-i", "--esxi-network", help="vSphere network assigned to VM \
                                                      that allows communication with local \
                                                      builder")
    args = parser.parse_args()

    # Set install variables
    user = getpass.getuser()
    if user == "root" and os.getenv("SUDO_USER") != "root":
        print bcolors.FAIL, "ERROR: DO NOT RUN THIS SCRIPT WITH SUDO", bcolors.ENDC
        exit()

    hyper = args.hypervisor
    vmOS = args.os
    if args.vmname:
        vmName = args.vmname
    else:
        vmName = ""

    if hyper == "esxi":
        if not args.esxi_user or not args.esxi_host or not args.esxi_network or not args.datastore_path:
            parser.error('esxi-host, datastore-path and esxi-network are all \
                         required when using the esxi hypervisor')
        try:
            print "Parsing arguments for ESXi installation:"
            print " - Host:%s\n - Datastore Path:%s\n - VM Network:%s" % (args.esxi_host, args.datastore_path, args.esxi_network)
            esxi = dict()
            esxi["passwd"] = getpass.getpass("Enter ESXi host password:")
            esxi["user"] = args.esxi_user
            esxi["host"] = args.esxi_host
            esxi["datastore"] = args.datastore_path
            esxi["network"] = args.esxi_network
        except:
            raise Exception("Unable to get ESXi password from user")

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
    packerCmd = which("packer")
    if not packerCmd:
        print "Packer not found - install it"
        packerCmd = installPacker(hostOS, hostArch)

    # Setup Virtual Networks
    if hyper == "virtualbox":
        if createVBoxNets(hostOS, hostArch, libDir):
            # Create the Virtual Machine
            vmName = createVM(hyper, hostOS, vmOS, vmName, user, packerCmd)
            if vmName:
                if registerVbox(hyper, libDir, vmName, vmOS):
                    print "Successfully created VM %s!" % vmName
                    exit(0)

    elif hyper == "vmware":
        if createVmNets(hostOS, hostArch, libDir):
            # Create the Virtual Machine
            vmName = createVM(hyper, hostOS, vmOS, vmName, user, packerCmd)
            if vmName:
                print "Successfully created VM %s!" % vmName
                exit(0)

    elif hyper == "esxi":
        vmName = createVM(hyper, hostOS, vmOS, vmName, user, packerCmd,
                          esxi_info=esxi)
        if vmName:
            print "Successfully created VM %s!" % vmName
            exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print "Exiting script..."
