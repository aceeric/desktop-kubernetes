# kuvboxctl

**Ku**bernetes **V**irtual**Box** **Ctl**

This project provisions a desktop Kubernetes cluster using VirtualBox and CentOS. This project is derivative of the well-known Kelsey Hightower's [Kubernetes The Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way) and also incorporates elements of a variant of the Hightower repo [Bare Metal Edition](https://github.com/bserdar/kubernetes-the-hard-way) by Burak Serdar. The differences between the upstream projects and this project are as follows:

| Upstream | Feature | This project |
| :-- | :-- | --- |
| Hightower | Presents a series of manual labs to get hands-on experience with Kubernetes installation as a learning exercise | Is automated - brings up a desktop Kubernetes cluster with one controller and multiple workers with a single Bash shell script invocation |
| Hightower | Uses [Google Cloud Platform](https://cloud.google.com/) to provision the compute resources | Provisions VMs on the desktop using VirtualBox |
| Hightower | Uses Ubuntu for the cluster nodes | Uses CentOS 8 (for now) |
| Hightower | Structures the installation and configuration tasks by related activities, e.g. creates all the certs, then generates configuration files, etc. | Structures the tasks more around the individual Kubernetes components where possible, because I was interested in delineating the specific dependencies and requirements for each component |
| Hightower | Hand-generates the intra-node routing | Just uses the built-in routing that comes free with a VirtualBox bridged network - which is the network type I selected for this project because it provides host-to-guest, guest-to-guest, and guest-to-internet right out of the box |
| Hightower | Implements Pod networking via the bridge network plugin from [containernetworking](https://github.com/containernetworking) | Per the *Bare Metal* variant, uses the kube-router from [cloudnativelabs](https://github.com/cloudnativelabs). I couldn't get the containernetworking plugin working on CentOS VMs. (Due to my limited understanding of Linux networking.) The Kube Router says it "just works" and that was indeed my experience |
| Hightower | Uses Cloudflare [cfssl](https://github.com/cloudflare/cfssl) to generate the cluster certs | Uses `openssl` since it is almost universally available - I was interested to see if openssl introduced any issues as compared to cfssl - and I had no issues with openssl |
| Serdar | Leaves provisioning the VMs to you | Automates VM provisioning. I was interested to get some experience with the `VBoxManage` utility and CentOS [Kickstart](https://docs.centos.org/en-US/centos/install-guide/Kickstart2/) for unattended OS installation. The script creates a template VM, and then clones it for each of the the cluster nodes. I also needed the VirtualBox Guest Additions, and came up with a way to automate that installation. Guest Additions provides the ability to get the IP address from a VM. In VirtualBox bridged networking, the IP is assigned by your desktop's DHCP so Guest Additions helps with the automation |
| Serdar | Disables the firewall on CentOS | Leaves the firewall running in the OS and configures the rules to support the requirements of the Kubernetes components. After some troubleshooting I found one additional port that is required on the workers with the firewall enabled |


TODO LICENCING / ATTRIBUTION ETC.!!!


another variant: https://github.com/bserdar/kubernetes-the-hard-way/blob/master/docs/02-client-tools.md

TODO document versions of all utils used

download iso
create vm 'model'
  - bridged network
installl vboc client extensions ?
install OS
  - passwordless root
ssh config
then set root password
- these may not be needed for the control plane!
  - firewall (maynot not needed if ubuntu)
  - networking
    - netfilter
    - ip forwarding
      sysctl net.ipv4.ip_forward
      if not 1 already out of the box then:
      sysctl -w net.ipv4.ip_forward=1
docker ??
 - ubuntu containerd
   - https://kubernetes.io/docs/setup/production-environment/container-runtimes/
   

clone to node1, node2
  - change hostname(s)
  - change MAC address to pick up a new IP!
gen tls - CA, apiserver controller-manager, scheduler
gen config files
data encryption keys
etcd
controllers
    kube-apiserver            DONE
    kube-controller-manager   << HERE!
    kube-scheduler

<< HERE NOW TIME FOR WORKERS



Interesting
https://github.com/kelseyhightower/kubernetes-the-hard-way/issues/248


READ THIS:
https://kubernetes.io/docs/reference/command-line-tools-reference/kubelet-tls-bootstrapping/

Monitor kube controller manager
https://sysdig.com/blog/how-to-monitor-kube-controller-manager/
curl  http://localhost:10252/metrics

Ubuntu auto-install
https://ubuntu.com/server/docs/install/autoinstall-quickstart

