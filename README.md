# Desktop Kubernetes

This is a Bash shell project that provisions a desktop Kubernetes cluster using VirtualBox - with each cluster node consisting of a CentOS 8 guest VM. The cluster consists of one VM in functioning with a dual role  of control plane node and worker node, and two dedicated worker nodes.

This has been tested on a Ubuntu 20.04.1 desktop host with 64 gig of RAM and 6 hyper-threaded processors that Ubuntu sees as 12 CPUs.

This project is derivative of **Kelsey Hightower's** [Kubernetes The Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way). The differences between the Hightower project and this project are listed below:

| Hightower | This project |
| :-- | --- |
| Presents a series of manual labs to get hands-on experience with Kubernetes installation as a learning exercise | Is automated - brings up a desktop Kubernetes cluster with one controller and multiple workers with a single Bash shell script invocation (see the *Quick Start*). |
| Uses [Google Cloud Platform](https://cloud.google.com/) to provision the compute resources | Provisions VMs on the desktop using [VirtualBox](https://www.virtualbox.org/). I was interested to get some experience with the `VBoxManage` utility and CentOS [Kickstart](https://docs.centos.org/en-US/centos/install-guide/Kickstart2/) for hands-free OS installation. The script creates a template VM, and then clones the template for each of the cluster nodes. I also needed the VirtualBox Guest Additions, and came up with a way to automate that installation. Guest Additions provides the ability to get the IP address from a VM. In VirtualBox bridged networking, the IP is assigned by the desktop's DHCP so Guest Additions helps with the automation. This was an interesting side-effort that resulted in the ability to create a CentOS VM just by running a single script command |
| Uses Ubuntu for the cluster node OS | Uses [CentOS 8](https://www.centos.org/download/) |
| Structures the installation and configuration tasks by related activities, e.g. creates all the certs, copies binaries, generates configuration files, etc. | Structures the tasks more around the individual Kubernetes components where possible, because I was interested in delineating the specific dependencies and requirements for each component |
| Hand-generates the node routing | Uses the built-in routing that comes with a VirtualBox bridge network - which is the network type I selected for this project because it provides host-to-guest, guest-to-guest, and guest-to-internet right out of the box |
| Implements Pod networking via the bridge network plugin from [containernetworking](https://github.com/containernetworking) | Performs a kube-proxyless install of [Cilium](https://docs.cilium.io/en/stable/gettingstarted/k8s-install-default) for cluster networking, and [Hubble](https://cilium.io/blog/2019/11/19/announcing-hubble) for network monitoring |
| Uses Cloudflare [cfssl](https://github.com/cloudflare/cfssl) to generate the cluster certs | Uses [openssl](https://www.openssl.org/) since it is almost universally available on Linux. I was interested to see what the scripting would look like using openssl, especially for things like creating CSRs and so on |
| Is nicely terse and compact | Is verbose by virtue of using scripts with lots of options, and separating the component installs into separate scripts, thus requiring a lot of option passing and parsing |
| Does not include monitoring | Installs [Kubernetes Metrics Server](https://github.com/kubernetes-sigs/metrics-server) and [Kubernetes Dashboard](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/) |

## Quick Start

The `new-cluster` script in the repo root is what you run.

> Before running the first time, you need to do three things: 1) Run `ifconfig` and get the name of your primary network interface. 2) Determine where on the filesystem you store VirtualBox VM files. Each VM will be about 6 gigs, and there will be four VMs: one template, and three nodes. So you need 24 gigabytes. 3) Check the CentOS mirror in the `new-cluster` script and make sure it makes sense for your geography.
>
> I also recommend you run once with just the `--check-compatibility` option to check the versions of the utilities used by the scripts (curl, etc.) against the tested versions. E.g.: `./new-cluster --check-compatibility`. I'm sure there will be differences and you have to decide whether the differences are material. Most probably aren't.

To create a cluster for the first time, run the script as shown below (using your unique values for the network interface name and VirtualBox directory). This is what works on my desktop:

```shell
$ ./new-cluster --host-network-interface=enp0s31f6 --from-scratch\
  --vboxdir=/sdb1/virtualbox --networking=cilium
```

The `--from-scratch` option is important. It tells the script to `curl` all the upstream objects, such as the CentOS ISO, the Virtual Box Guest Additions ISO, and the Kubernetes binaries and other manifests. I've coded the script with specific versions of everything in the interests of repeatability. The `--networking` option installs cluster networking. I initially went with `kube-router` but most recently switched to  Cilium.

> Please Note: URLs are perishable. Just in the time that I was developing this project, the CentOS version and URL changed slightly so - don't be surprised if you have to tweak the URLs. The script will test each URL before it begins provisioning the cluster and will tell you which ones it couldn't access. Then you will have to modify the `new-cluster` script accordingly.

Once the cluster comes up, the script will display a message telling you how to set your `KUBECONFIG` in order to access the cluster. It will also display a message showing how to SSH into each node. (The `scripts` directory has a script `sshto` that takes a VM name as an arg and SSHs into the VM.)

To see a list of all supported options:

```shell
$ ./new-cluster --help
```



## ToDos

| Task                           | Description                                                  |
| ------------------------------ | ------------------------------------------------------------ |
| Volume Provisioning            | Implement the [Local Static Provisioner](https://github.com/kubernetes-sigs/sig-storage-local-static-provisioner). Currently, persistent volumes have to be hand-managed by generating directories in the VMs, and creating PVs that ref those VMs. |
| Monitoring                     | Support Prometheus and Grafana. Currently, the project configures the [Metrics Server](https://github.com/kubernetes-sigs/metrics-server) and the [Web UI Dashboard](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/) and requires you to `kubectl proxy` and get a token from a cluster secret to log in to the dashboard. |
| Sonobuoy                       | See if it is possible for this cluster to pass the Kubernetes certification tests using [Sonobuoy](https://github.com/vmware-tanzu/sonobuoy) |
| Firewall                       | There are plenty of posts discussing how to configure the firewall settings for Kubernetes. The documented settings do not appear to work with CoreDNS on CentOS 8. (In fact, many posters recommend to disable `firewalld` on CentOS.) So presently, the firewall is disabled but my goal is to run the cluster with the firewall enabled and the correct rules defined |
| Ubuntu                         | Support Ubuntu Server as the Guest OS - presently only CentOS is supported |
| Virtual Box Networking         | This version of the script uses VBox bridge networking for each of the VMs. As stated earlier, this provides guest-to-guest, host-to-guest, and guest-to-internet. However - with this networking solution the IP addresses are assigned by the host DHCP software. So Guest Additions are required to introspect the VMs to get their IP addresses. A better solution would be to use a VBox networking model that allows assignment of static IPs to guest VMs. Then the Guest Additions installation step could be omitted |
| Headless                       | Support running the VMs headless. At present, each VM comes up on the desktop, which can be somewhat intrusive it you're doing other work. (OTOH it does provide positive feedback on what's happening) |
| Nodes                          | Consider making the number of controllers configurable, as well as node characteristics such as storage, RAM, and CPU. Right now, only one controller and two workers are supported, their names are hard-coded, etc. |
| Hands-free install improvement | The current version builds a Kickstart ISO, and mounts the ISO on the VM to do the hands-free CentOS install. Unfortunately, this method does not allow you to change the boot menu timeout on the *initial* startup of the VM. So, unless you intervene, the boot menu takes 60 seconds to time out before the Kickstart installation begins. The alternate way to do this is to break apart the ISO, modify the boot menu timeout, and then re-build the ISO. I may consider this at some future point, although that would not easily lend itself to automation |
| CoreOS?                        | Consider [Fedora CoreOS](https://getfedora.org/en/coreos?stream=stable) as a VM OS |

## Versions

This project has been testing with the following tools, components and versions. The Kubernetes component versions and CentOS and VirtualBox Guest Addition versions are hard-coded into the `new-cluster` script. So any changes only need to be made one time in that script. *If you decide to use later (or earlier) Kubernetes components, be aware that the supported options can change between versions which may require additional script changes.*

| Where    | Component                                       | Version            |
| -------- | ----------------------------------------------- | ------------------ |
| host     | Linux desktop                                   | Ubuntu 20.04.2 LTS |
| host     | openssl                                         | 1.1.1f             |
| host     | openssh                                         | OpenSSH_8.2p1      |
| host     | genisoimage (used to create the Kickstart ISO)  | 1.1.11             |
| host     | Virtual Box / VBoxManage                        | 6.1.18r142142      |
| host     | kubectl (client only)                           | v1.18.0            |
| host     | curl                                            | 7.68.0             |
| guest VM | Centos ISO                                      | 8.3.2011-x86_64    |
| guest VM | Virtual Box Guest Additions ISO                 | 6.1.18             |
| k8s      | etcd                                            | v3.4.14            |
| k8s      | kube-apiserver                                  | v1.20.1            |
| k8s      | kube-controller-manager                         | v1.20.1            |
| k8s      | kube-scheduler                                  | v1.20.1            |
| k8s      | kubelet                                         | v1.20.1            |
| k8s      | crictl                                          | v1.19.0            |
| k8s      | runc                                            | v1.0.0-rc92        |
| k8s      | cni plugins                                     | v0.9.0             |
| k8s      | containerd                                      | v1.4.3             |
| k8s      | kube-router                                     | v1.1.1             |
| k8s      | CoreDNS                                         | 1.8.0              |
| k8s      | Metrics Server                                  | 0.4.2              |
| k8s      | Kubernetes Dashboard                            | 2.0.0              |
| k8s      | Cilium networking and Hubble network monitoring | 1.9.4              |

