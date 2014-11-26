#!/bin/bash

####################################
# Automatically setup a ZTPServer VM
# Author: eosplus-dev@arista.com
# Date: 20141124
####################################

usage="usage:create-ztpserver.sh [vmware|virtualbox] [fedora|ubuntu]\n"

# if less than two arguments supplied, display usage
    if [ $# -lt 2 ];then
        echo "Not enough arguments"
        echo -e $usage
        exit 1
    fi

# check whether user had supplied -h or --help . If yes display usage
    if [[ ( $# == "--help") ||  $# == "-h" ]];then
        echo "Help:"
        echo -e $usage
        exit 0
    fi

# check hypervisor is vmware or virtualbox
    if [[ $1 != "vmware" && $1 != "virtualbox" ]];then
        echo "Error: hypervisor argument incorrect"
        echo -e $usage
        exit 1
    fi

# check os is fedora or ubuntu
    if [[ $2 != "fedora" && $2 != "ubuntu" ]];then
        echo "Error: os argument incorrect"
        echo -e $usage
        exit 1
    fi

# Installation Variables
HYPER=$1
DIST=$2
PACKER_URL=https://dl.bintray.com/mitchellh/packer
PACKER_VERSION=0.7.2
FUSION_LIB=/Applications/VMware\ Fusion.app/Contents/Librar/


# Set Environment
OS=$(uname | awk '{print tolower($0)}')
OS_ARCH=$(getconf LONG_BIT)
if [ ${OS_ARCH} -eq "64" ];then
    OS_ARCH=amd64
else
    OS_ARCH=386
fi
echo "Tailoring install for "${OS}_${OS_ARCH}

# Install Packer if needed
echo "Checking if packer is already installed."

if $(hash packer);then
    echo "Packer found. Skipping installation"
else
    echo "Installing Packer"
    cd ~
    URL=${PACKER_URL}/packer_${PACKER_VERSION}_${OS}_${OS_ARCH}.zip
    #echo ${URL}
    #curl -Lo ~/packer.zip ${URL}
    mkdir -p ~/packer-bin
    echo "Unzipping packer binaries to ~/packer-bin/"
    tar -xf ~/packer.zip -C ~/packer-bin

    if [ -r ~/.profile ];then
        echo "PATH=$PATH:~/packer-bin" >> ~/.profile
    elif [ -r ~/.bash_profile ];then
        echo "PATH=$PATH:~/packer-bin" >> ~/.bash_profile
    else
        echo "PATH=$PATH:~/packer-bin" >> ~/.bashrc
    fi
    PATH=$PATH:~/packer-bin

    # Confirm Packer is installed
    echo "Packer is running with version "$(packer -v)
fi


# Modify/create vmnets for specified hypervisor

if [ $HYPER == "vmware" ];then
    if [[ $OS == "darwin" && -d "$FUSION_LIB" ]];then
        echo "Found the Fusion Library files in default location"
    else
        # Use find to see if we can locate the right directory
        FUSION_LIB=$(sudo find /Applications -name vmnet-cli)
        echo "Found new directory: "$FUSION_LIB
        echo "ERROR:Cannot find Fusion library files"
        exit 0
    fi
fi
