#!/usr/bin/bash
#
# Configures the host only network adapter. Installs VirtualBox Guest Additions in
# two steps with a reboot in between. Note - the Guest Additions install seems sensitive
# to the Linux version. I got this working with Centos Stream / Rocky 9 then happened
# to test w/ Centos 7 and it didn't work any more. It seems too much trouble to support
# multiple versions.
#

set -e

touch /root/desktop-kubernetes.log

function msg() {
  echo "$(date '+%Y-%m-%d %H:%M:%S.%3N') [$(hostname)] -- $1"\
  | tee -a /root/desktop-kubernetes.log
}

# If host only networking, the project mounts a config ISO to the cloned VM to
# configure enp0s8 (the host-only interface.) Label CFGENP0S8 is assigned to this
# ISO by 'scripts/virtualbox/gen-hostonly-ifcfg-iso'. If mounted, then copy the enp0s8
# config file from the CD to the network config directory. This is how we configure the
# network in each VM in the cluster with a different IPv4 address for host only
# networking. If bridge networking, then the CD is not mounted to the clone and
# so this if block is never entered. And - we never mount the ISO in the template
# VM, only in a clone.

if blkid | grep 'LABEL="CFGENP0S8"'; then
  msg "begin network configuration"
  msg "copying host only network config file"
  mkdir -p /mnt/cdrom
  mount -r /dev/cdrom /mnt/cdrom
  yes | /bin/cp /mnt/cdrom/ifcfg-enp0s8 /etc/sysconfig/network-scripts/ifcfg-enp0s8
  umount /mnt/cdrom
  rm -rf /mnt/cdrom
  msg "host only network config file copied"
  msg "before restart enp0s8 interface"
  nmcli connection reload
  nmcli connection up enp0s8 || :
  msg "after restart enp0s8 interface"
  msg "completed network configuration - exiting"
  exit 0
fi

# Guest Additions install is done in the template when it is created. Thereafter,
# the template is cloned to create each cluster VM and so each clone automatically
# has guest additions. Guest Additions install logic was adapted from:
# https://www.tecmint.com/install-virtualbox-guest-additions-on-centos-8/

if ! grep -q 'completed guest additions step 1' /root/desktop-kubernetes.log; then
  if grep -q 'begin guest additions step 1' /root/desktop-kubernetes.log; then
    msg "error - guest additions step 1 failed"
    exit 1
  fi
  msg "begin guest additions step 1"

  dnf -y install epel-release && dnf -y update --refresh
  dnf -y remove kernel-devel
  dnf -y install gcc make perl kernel-devel kernel-headers bzip2 dkms elfutils-libelf-devel
  dnf -y update kernel-*
  msg "completed guest additions step 1 - rebooting"
  reboot -f
fi

if ! grep -q 'completed guest additions step 2' /root/desktop-kubernetes.log; then
  if grep -q 'begin guest additions step 2' /root/desktop-kubernetes.log; then
    msg "error - guest additions step 2 failed"
    exit 1
  fi
  msg "begin guest additions step 2"
  mkdir -p /mnt/cdrom
  mount -r /dev/cdrom /mnt/cdrom
  /mnt/cdrom/VBoxLinuxAdditions.run
  umount /mnt/cdrom
  rm -rf /mnt/cdrom
  msg "completed guest additions step 2 - shutting down"
  shutdown now
fi
