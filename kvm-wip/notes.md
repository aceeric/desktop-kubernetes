# Notes

virsh list --all

virsh net-list --all

virsh net-info default

brctl show

virt-install --os-variant list

virsh net-autostart default

virsh net-start default

virsh pool-list --all

virsh shutdown kvmtest (graceful)
virsh destroy kvmtest (force)
virsh destroy kvmtest --graceful
virsh undefine kvmtest

## show bridges
brctl show


## adding a network

### TOPLINE
1) bridge on host
2) 


https://amoldighe.github.io/2017/12/20/kvm-networking/

https://unix.stackexchange.com/questions/671992/how-to-add-an-additional-network-interface-on-a-kvm-vm
virsh attach-interface --type bridge --source $YOUR_HOST_BRIDGE --model virtio $YOUR_VM

https://documentation.suse.com/sles/15-SP2/html/SLES-all/cha-libvirt-networks.html

> bridged with static IP

https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/virtualization_deployment_and_administration_guide/sect-guest_virtual_machine_installation_overview-creating_guests_with_virt_install#sect-Guest_virtual_machine_installation_overview-virt_install-Kickstart

SIMILAR TO ABOVE?
https://www.ibm.com/docs/en/linux-on-z?topic=choices-using-linux-bridge


## this has the storage location
virsh pool-dumpxml default

## Changing the storage pool location
https://gist.github.com/plembo/5e108dc8000850442d756fc3747d31a3

virsh pool-dumpxml default >| ./default-pool.xml
virsh pool-destroy default
virsh pool-undefine default
virsh pool-define ./default-pool.xml
virsh pool-start default
virsh pool-autostart default

## how to initialize authorized_keys?


SSH in as root with password!!!

https://unix.stackexchange.com/questions/207012/how-to-send-upload-a-file-from-host-os-to-guest-os-in-kvmnot-folder-sharing


https://adam.younglogic.com/2018/11/ssh-keys-cloud-image/




16-MAR HAD NO EFFECT:


Virtual Machine Manager wants to inhibit shortcuts.
You can restore shortcuts by pressing Super+Escape. 


https://askubuntu.com/questions/1488341/how-do-i-inhibit-shortcuts-for-virtual-machines


flatpak permission-set gnome shortcuts-inhibitor virt-manager.desktop GRANTED
flatpak permission-set gnome shortcuts-inhibitor virt-viewer.desktop GRANTED
