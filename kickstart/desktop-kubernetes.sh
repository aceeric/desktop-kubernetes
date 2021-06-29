#!/usr/bin/bash

# This install logic is adapted from:
# https://www.tecmint.com/install-virtualbox-guest-additions-on-centos-8/

# The output of 'rpm -q kernel-devel' and 'uname -r' have to match or the guest
# additions install will fail
kdvl=$(which rpm &>/dev/null && rpm -q kernel-devel)
unam=kernel-devel-$(uname -r)

step=prepandreboot
if [[ ! -z "$kdvl" ]] && [[ "$kdvl" == "$unam" ]]; then
  # values match - check if we are on step 2 of the install, or already completed the install
  modcnt=$(lsmod | grep vboxguest | wc -l)
  if [[ $modcnt -ne 0 ]]; then
    # guest additions install complete - the service will continue to run on every startup
    # if the enp0s8 config CD is mounted and no file /etc/sysconfig/network-scripts/ifconfig-enp0s8 exists
    # then copy that file from the CD to the directory and shutdown. This is how we configure the network in
    # each VM in the cluster with a different IPv4 address for host-only networking. If bridge networking, then
    # the CD is not mounted by the caller.
    if [[ -f /root/did-network-setup ]]; then
      exit 0
    fi
    touch /root/did-network-setup
    # TODO CHANGE TO ENP0S8 !!!!!
    if [[ $(blkid | grep 'LABEL="CFGENP0S8"') -eq 0 ]] && [[ ! -f /etc/sysconfig/network-scripts/ifconfig-enp0s8 ]]; then
      echo "copying host-only network config file"
      mount -r /dev/cdrom /mnt/cdrom &&\
      cp /mnt/cdrom/ifconfig-enp0s8 /etc/sysconfig/network-scripts/ifconfig-enp0s8 &&\
      umount /mnt/cdrom &&\
      rm -rf /mnt/cdrom
      echo "host-only network config file copied - shutting down"
      # other scripts may be waiting for this VM to come up using loops and sleeps so don't outrun them
      sleep 5s
      shutdown now
    fi
    exit 0
  else
    # we completed step one and rebooted - next need to do step 2
    step=doinstall
  fi
fi

if [[ $step == prepandreboot ]]; then
  # guard against infinite reboot
  if [[ -f /root/did-prepandreboot ]]; then
    echo "ERROR prepandreboot failed last boot - did not install guest additions"
    exit 1
  fi
  echo "step one - updating kernel params and reboot for them to take effect"
  touch /root/did-prepandreboot
  dnf -y install epel-release &&\
    dnf -y install gcc make perl kernel-devel kernel-headers bzip2 dkms &&\
    dnf -y update kernel-* &&\
    reboot -f
elif [[ $step == doinstall ]]; then
  # guard against infinite failed re-install
  if [[ -f /root/did-install ]]; then
    echo "ERROR doinstall failed last boot - did not install guest additions"
    exit 1
  fi
  echo "step two - installing guest additions"
  touch /root/did-install
  mkdir -p /mnt/cdrom &&\
    mount -r /dev/cdrom /mnt/cdrom &&\
    /mnt/cdrom/VBoxLinuxAdditions.run &&\
    umount /mnt/cdrom &&\
    rm -rf /mnt/cdrom
    echo "finished installing virtual box guest additions - shutting down"
    shutdown now
fi