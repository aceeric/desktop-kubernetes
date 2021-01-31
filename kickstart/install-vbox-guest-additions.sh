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
    # the service will run this on every startup so if already installed, just exit
    # todo: disable the service since it has served its purpose?
    exit 0
  else
    # we completed step one and rebooted - next need to do step 2
    step=doinstall
  fi
fi

if [[ $step == prepandreboot ]]; then
  # guard against infinite reboot
  if [[ -f /root/did_prepandreboot ]]; then
    echo "ERROR prepandreboot failed last boot - did not install guest additions"
    exit 1
  fi
  # step one - update kernel params and reboot for them to take effect
  touch /root/did_prepandreboot
  dnf -y install epel-release &&\
    dnf -y install gcc make perl kernel-devel kernel-headers bzip2 dkms &&\
    dnf -y update kernel-* &&\
    reboot -f
elif [[ $step == doinstall ]]; then
  # guard against infinite failed re-install
  if [[ -f /root/did_install ]]; then
    echo "ERROR doinstall failed last boot - did not install guest additions"
    exit 1
  fi
  # step two - install guest additions
  touch /root/did_install
  mkdir -p /mnt/cdrom &&\
    mount -r /dev/cdrom /mnt/cdrom &&\
    /mnt/cdrom/VBoxLinuxAdditions.run &&\
    umount /mnt/cdrom &&\
    rm -rf /mnt/cdrom
    echo "finished installing virtual box guest additions"
    shutdown now
fi