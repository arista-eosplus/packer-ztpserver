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

########################
# Functions
########################
function findLibrary {
  echo "######################################"
  echo "Searching for ${HYPER} Libraries..."
  echo "######################################"

  LIB_DIR=$(find $1 -name $2 -print0 | xargs -0 dirname)

  if [[ ! $LIB_DIR ]];then
    echo "ERROR:Cannot find ${HYPER} library files - is it installed?"
    exit 0
  fi

  #LIB_DIR=$(dirname ${LIB_PATH})
  echo "Library files found here: "$LIB_DIR
}

function elementExists() {
  name=$1[@]
  elements=("${!name}")
  element=${2}
  for i in ${elements[@]} ; do
    if [ $i == $element ] ; then
      echo " - virtual network ${i} interface is up"
      return 1
    fi
  done
  echo "ERROR: There was a problem configuring your vmnets."
  echo "ERROR: vmnet${i} was not found using ifconfig. Check logs above for info."
  exit 0
}

########################
# Installation Variables
########################
RED='\033[0;31m'
NC='\033[0m'
HYPER=$1
DIST=$2
PACKER_URL=https://dl.bintray.com/mitchellh/packer
PACKER_VERSION=0.7.5
#FUSION_LIB=/Applications/VMware\ Fusion.app/Contents/Librar/


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
        source ~/.profile
    elif [ -r ~/.bash_profile ];then
        echo "PATH=$PATH:~/packer-bin" >> ~/.bash_profile
        source ~/.bash_profile
    else
        echo "PATH=$PATH:~/packer-bin" >> ~/.bashrc
        source ~/.bash_rc
    fi
    export PATH=$PATH:~/packer-bin

    # Confirm Packer is installed
    echo "Packer is installed with version "$(packer -v)
fi


# Modify/create vmnets for specified hypervisor

if [ $HYPER == "vmware" ];then
  if [[ $OS == "darwin" ]];then
    findLibrary "/Applications" "vmnet-cli"

    #Run VMware
    find /Applications -name "VMware Fusion.app" -print0 | xargs -0 open

    #Create an array with the vmnets we want to create/modify
    declare -a VMNETS
    VMNETS=(2 3 4 5 6 7 9 10 11)

    echo "###########################"
    echo "Creating VMware virtualnets"
    echo "###########################"
    for i in "${VMNETS[@]}"; do
      echo "###########################"
      echo "Creating/Modifying vmnet$i"
      echo "###########################"
      NET=$(($i+128))
      "${LIB_DIR}"/vmnet-cfgcli vnetcfgadd VNET_${i}_DHCP no
      "${LIB_DIR}"/vmnet-cfgcli vnetcfgadd VNET_${i}_HOSTONLY_SUBNET 172.16.${NET}.0
      "${LIB_DIR}"/vmnet-cfgcli vnetcfgadd VNET_${i}_HOSTONLY_NETMASK 255.255.255.0
      "${LIB_DIR}"/vmnet-cfgcli vnetcfgadd VNET_${i}_VIRTUAL_ADAPTER yes
    done
    echo "#############################################"
    echo "Running vmnet-cli --configure to save changes"
    echo "#############################################"
    "${LIB_DIR}"/vmnet-cli --configure
    echo "########################"
    echo "Running vmnet-cli --stop"
    echo "########################"
    "${LIB_DIR}"/vmnet-cli --stop
    echo "##########################"
    echo "Running vmnet-cli --start"
    echo "##########################"
    "${LIB_DIR}"/vmnet-cli --start

    #Check to make sure vmnets are active
    echo "##################################"
    echo "Confirming new vmnet ifs are up..."
    echo "##################################"

    # Run ifconfig to grab vmnet ifs, then strip all text and leave vmnet number
    IFCONFIG=$(ifconfig | grep 'vmnet' | cut -d: -f1 | awk '{print $0}' | sed -e s/vmnet//g)
    read -a INSTALLED_NETS <<<$IFCONFIG
    #echo ${#INSTALLED_NETS[@]}
    for i in "${VMNETS[@]}"; do
      # Confirm each configured vmnets is in ifconfig array
      elementExists INSTALLED_NETS ${i}
    done

    # Now let's create a ZTPServer VM
    echo "###############################"
    echo "Creating Fusion ZTPServer VM..."
    echo "###############################"

    echo -e "${RED}##############################################"
    echo -e "WARNING: DO NOT TYPE IN VIRTUAL MACHINE WINDOW"
    echo -e "##############################################${NC}"

    if [[ $DIST == "fedora" ]];then
      cd Fedora
      VMNAME="ztps-fedora_20_x86_64_$(date +"%Y%m%d_%H%M%S")"
      sudo -u ${SUDO_USER} packer build --only=vmware-iso -var "name=${VMNAME}" ztps-fedora_20_x86_64.json
    elif [[ $DIST == "ubuntu" ]];then
      cd Ubuntu
      VMNAME="ztps-ubuntu-12.04_amd64_$(date +"%Y%m%d_%H%M%S")"
      sudo -u ${SUDO_USER} packer build --only=vmware-iso -var "name=${VMNAME}" ztps-ubuntu-12.04.4_amd64.json
    fi

  elif [[ $OS == "Linux" ]];then
    findLibrary "/" "vmware-networks"
  fi
elif [ $HYPER == "virtualbox" ];then
  if [[ $OS == "darwin" ]];then
    findLibrary "/usr" "VBoxManage"

    #Run VMware
    find /Applications -name "VirtualBox.app" -print0 | xargs -0 open

    #Create an array with the vmnets we want to create/modify
    declare -a VMNETS
    VMNETS=(0 1 2 3 4 5 6 7 8 9 10)

    #Check to see which networks already exist and then augment/modify
    # Run ifconfig to grab vmnet ifs, then strip all text and leave vmnet number
    VBOXNETS=$("${LIB_DIR}"/vboxmanage list hostonlyifs | grep 'Name:' | grep -v 'HostInterface' | cut -d: -f2 | sed -e s/vboxnet//g)
    read -a INSTALLED_NETS <<<$VBOXNETS
    #echo ${#INSTALLED_NETS[@]}
    if [[ ${#INSTALLED_NETS[@]} -ge ${#VMNETS[@]} ]];then
      echo Enough vboxnets installed - lets just configure them.
    else
      NUM_CREATE=$((${#VMNETS[@]}-${#INSTALLED_NETS[@]}))
      echo We need to create ${NUM_CREATE} hostonlyifs
      for ((i = 0 ; i < $NUM_CREATE ; i++ )); do
        "${LIB_DIR}"/vboxmanage hostonlyif create
      done
    fi

    #Now configure them with correct IP info
    for ((i = 0 ; i < ${#VMNETS[@]} ; i++ )); do
      NET=$(($i+128))
      echo "Assigning vboxnet${i} to 172.16.${NET}.1/24"
      "${LIB_DIR}"/vboxmanage hostonlyif ipconfig vboxnet${i} -ip 172.16.${NET}.1 -netmask 255.255.255.0
    done

    #Check to make sure vboxnets are active
    echo "####################################"
    echo "Confirming new vboxnet ifs are up..."
    echo "####################################"

    # Run ifconfig to grab vmnet ifs, then strip all text and leave vmnet number
    IFCONFIG=$(ifconfig | grep 'vboxnet' | cut -d: -f1 | awk '{print $0}' | sed -e s/vboxnet//g)
    read -a INSTALLED_NETS <<<$IFCONFIG
    #echo ${#INSTALLED_NETS[@]}
    for i in "${VMNETS[@]}"; do
      # Confirm each configured vmnets is in ifconfig array
      elementExists INSTALLED_NETS ${i}
    done

    # Now let's create a ZTPServer VM
    echo "###################################"
    echo "Creating VirtualBox ZTPServer VM..."
    echo "###################################"

    echo -e "${RED}##############################################"
    echo -e "WARNING: DO NOT TYPE IN VIRTUAL MACHINE WINDOW"
    echo -e "##############################################${NC}"

    if [[ $DIST == "fedora" ]];then
      cd Fedora
      VMNAME="ztps-fedora_20_x86_64_$(date +"%Y%m%d_%H%M%S")"
      sudo -u ${SUDO_USER} packer build --only=virtualbox-iso -var "name=${VMNAME}" ztps-fedora_20_x86_64.json
    elif [[ $DIST == "ubuntu" ]];then
      cd Ubuntu
      VMNAME="ztps-ubuntu-12.04_amd64_$(date +"%Y%m%d_%H%M%S")"
      sudo -u ${SUDO_USER} packer build --only=virtualbox-iso -var "name=${VMNAME}" ztps-ubuntu-12.04.4_amd64.json
    fi

    #Import the VM into Vbox
    "${LIB_DIR}"/vboxmanage import */${VMNAME}.ovf 

  elif [[ $OS == "Linux" ]];then
    findLibrary "/" "vmware-networks"
  fi
fi
