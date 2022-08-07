#!/usr/bin/bash
#
# Does two things:
#
# 1 - Installs VirtualBox Guest Additions in two steps
# 2 - Configures the host only network adapter
#
# Guest Additions install is done in the template when it is created. Thereafter - the template is cloned to
# create each cluster VM and so each clone automatically has guest additions. The network config is only
# done in the cloned VMs, and only if host-only networking is selected.
#
# Guest Additions install logic is adapted from: https://www.tecmint.com/install-virtualbox-guest-additions-on-centos-8/
#

# If host only networking, the project mounts a config ISO to the cloned VM to configure enp0s8 (the host-only
# interface.) Label CFGENP0S8 is assigned to this ISO by scripts/gen-hostonly-ifcfg-iso. If mounted, then copy
# the enp0s8 config file from the CD to the network config directory. This is how we configure the network in
# each VM in the cluster with a different IPv4 address for host only networking. If bridge networking, then the
# CD is not mounted to the clone and so this if block is never entered. And - we never mount the ISO in the
# template VM, only when we clone the template. Note that the desktop-kubernetes service is configured to run
# before any networking services so - placing the configuration file into /etc/sysconfig/network-scripts
# causes networking to pick it up.

if blkid | grep 'LABEL="CFGENP0S8"'; then
  touch /root/network-setup.started
  echo "$(date '+%Y-%m-%d %H:%M:%S.%3N') [$(hostname)] -- copying host only network config file" | tee -a /root/desktop-kubernetes.log
  mkdir -p /mnt/cdrom &&\
    mount -r /dev/cdrom /mnt/cdrom &&\
    yes | /bin/cp /mnt/cdrom/ifcfg-enp0s8 /etc/sysconfig/network-scripts/ifcfg-enp0s8 &&\
    umount /mnt/cdrom &&\
    rm -rf /mnt/cdrom
  echo "$(date '+%Y-%m-%d %H:%M:%S.%3N') [$(hostname)] -- host only network config file copied" | tee -a /root/desktop-kubernetes.log
  touch /root/network-setup.succeeded
  exit 0
fi

if [[ ! -f /root/guest-additions-step1.succeeded ]]; then
  if [[ -f /root/guest-additions-step1.started ]]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S.%3N') [$(hostname)] -- error - guest additions step 1 failed" | tee -a /root/desktop-kubernetes.log
    exit 1
  fi
  touch /root/guest-additions-step1.started
  echo "$(date '+%Y-%m-%d %H:%M:%S.%3N') [$(hostname)] -- begin guest additions step 1" | tee -a /root/desktop-kubernetes.log
  dnf -y install epel-release &&\
    dnf -y install gcc make perl kernel-devel kernel-headers bzip2 dkms &&\
    dnf -y update kernel-* &&\
    touch /root/guest-additions-step1.succeeded &&\
    echo "$(date '+%Y-%m-%d %H:%M:%S.%3N') [$(hostname)] -- completed guest additions step 1 - rebooting" | tee -a /root/desktop-kubernetes.log &&\
    reboot -f
fi

if [[ ! -f /root/guest-additions-step2.succeeded ]]; then
  if [[ -f /root/guest-additions-step2.started ]]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S.%3N') [$(hostname)] -- error - guest additions step 2 failed" | tee -a /root/desktop-kubernetes.log
    exit 1
  fi
  touch /root/guest-additions-step2.started
  echo "$(date '+%Y-%m-%d %H:%M:%S.%3N') [$(hostname)] -- begin guest additions step 2" | tee -a /root/desktop-kubernetes.log
  mkdir -p /mnt/cdrom &&\
    mount -r /dev/cdrom /mnt/cdrom &&\
    /mnt/cdrom/VBoxLinuxAdditions.run &&\
    umount /mnt/cdrom &&\
    rm -rf /mnt/cdrom &&\
    touch /root/guest-additions-step2.succeeded &&\
    echo "$(date '+%Y-%m-%d %H:%M:%S.%3N') [$(hostname)] -- completed guest additions step 2 - shutting down" | tee -a /root/desktop-kubernetes.log &&\
    shutdown now
fi
