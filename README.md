# Desktop Kubernetes

<img src="resources/desktop-kubernetes-no-text.jpg" width="100"/>

Desktop Kubernetes is a Linux *Bash* project that provisions a desktop Kubernetes cluster using VirtualBox - with each cluster node consisting of a CentOS Stream, Alma, or Rocky Linux guest VM. The purpose is to create a local development and testing environment that is 100% compatible with a production-grade Kubernetes environment.

Desktop Kubernetes is the *57 Chevy* of Kubernetes distros: you can take it apart and put it back together with just a few Linux console tools: bash, curl, genisoimage, ssh, scp, tar, openssl, vboxmanage, and kubectl. That being said, **v1.28.0** of this distribution is Kubernetes Certified. See: [CNCF Interactive Landscape](https://landscape.cncf.io/card-mode?category=platform&amp;grouping=category&amp;selected=desktop-kubernetes).

[<img src="https://www.cncf.io/wp-content/uploads/2020/07/certified_kubernetes_color-1.png" width="90"/>](https://github.com/cncf/k8s-conformance/tree/master/v1.28/desktop-kubernetes)

The project consists of a number of bash scripts and supporting manifests / config files. The design is documented [here](https://github.com/aceeric/desktop-kubernetes/blob/master/resources/design.md).

One of the premises of the project is transparency. Every single binary or manifest used to create the cluster is pulled from an official upstream, including the OS itself.

The cluster provisioned by the project consists of one VM functioning in a dual role of control plane server and worker node, plus two dedicated worker node VMs - a total of three VMs. The cluster is provisioned by running one script - `dtk` - with a few command line options. The script makes no changes to your desktop's environment - other than the files it downloads, and the VirtualBox VMs it creates. (Of course, VirtualBox may create various virtual network interfaces but these are cleaned up by VirtualBox if you remove the cluster.)

This has been tested on Ubuntu 20.04.X systems with 64 gigs of RAM and 6+ hyper-threaded processors.

This project started as a way to automate the steps in **Kelsey Hightower's** [Kubernetes The Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way) - just to see if I could. But at this point I pretty much rely on it for all my local Kubernetes development.

## Quick Start

The `dtk` script in the repo root is what you run.

> Before running the first time: 1) Determine where on the filesystem you store VirtualBox VM files. Each VM will be about 6 gigs, and there will be four VMs: one template, and three nodes. So you need 24 gigabytes. 2) For Centos check the mirror in the `artifacts` script and make sure it makes sense for your geography. (Rocky has automatic redirect.)
>
> I also recommend you run once with just the `--check-compatibility` option to check the versions of the utilities used by the scripts (curl, etc.) against the tested versions. E.g.: `./dtk --check-compatibility`. There will likely be differences and you have to decide whether the differences are material. Most probably aren't.

To create a cluster for the first time, run the script as shown below (using your unique values).

**Host only + NAT networking:** This option enables the cluster to run on different networks. It's good for a laptop installation where you want to run the cluster in various locations. Any IP address is fine for the host network (subject to constraints imposed by VirtualBox.) Supply the left three octets - the script will assign the rightmost octet:

```bash
$ ./dtk --host-only-network=192.168.56 --vboxdir=/sdb1/virtualboxvms --create-template\
  --networking=calico --monitoring=kube-prometheus
```

**Bridged networking:** This is good for a desktop install since you can't run the cluster on a different network once the cluster is created. For this approach, first run `ifconfig` and get the name of your primary network interface. You use that in the `--host-network-interface` option (mine is shown below):

```shell
$ ./dtk --host-network-interface=enp0s31f6 --create-template\
  --vboxdir=/sdb1/virtualboxvms --networking=calico --monitoring=kube-prometheus
```

The `--networking` option installs cluster networking. In the example: Calico (and kube-proxy.)

The `--monitoring` option installs monitoring. In the example: Kube Prometheus. (The kube-prometheus param also creates a NodePort service on port 30300 which you can access directly using any one of the VM IPs to access the Grafana dashboard using credentials admin/admin.)

The `--create-template` option is **required** the first time: it creates a template VM which is used to clone the cluster VMs.

> Please Note: URLs are perishable. The script provides an option to test each URL and tell you which ones it couldn't access.

Once the cluster comes up, the script will display a message telling you how to set your `KUBECONFIG` environment variable in order to access the cluster. It will also display a message showing how to SSH into each node.

## Command Line Options

The following command-line options are supported for the `dtk` script:

### Cluster creation options

| Option | Required? | Description |
| --- | --- |--- |
| `--host-network-interface` | or `--host-only-network` | The name of the primary network interface on your machine. The scripts use this to configure the VirtualBox bridge network for each guest VM. **Important**: you must specify this consistently when creating the template, and when creating a cluster from the template. The reason is that the option configures settings at the VM level that then propagate into the guest OS. Since guests are cloned from the template, the guest networking has to be defined consistently with the template. |
| `--host-only-network`| or `--host-network-interface` | The left three octets of the network. E.g. `192.168.56`. (*For some additional information on this address, see*: [the VirtualBox docs](https://www.virtualbox.org/manual/ch06.html) *section on "Host-Only Networking"*.) This option configures NAT + host only networking mode. The scripts will create a new host only network and configure the cluster to use it for intra-cluster networking, and will configure NAT for the cluster to access the internet. *See important note in the table entry immediately above regarding VBox networking type.* |
| `--vboxdir` | Required | The directory where you keep your VirtualBox VM files. The script uses the `VBoxManage` utility to create the VMs, which will in turn create a sub-directory under this directory for each VM. The directory must exist. The script will not create it. |
| `--networking` | Optional | Installs Pod networking. Current valid values are `calico` (which also installs kube-proxy), and `cilium`. E.g.: `--networking=calico`. I use calico. And: calico is the pod networking that I used to get the k8s conformance tests passing. |
| `--containerized-cplane` | Optional | If specified, creates the control plane components as static pods on the controller VM like Kubeadm, RKE2, et. al. (By default, creates the control plane components as as systemd units.) Allowed values: `all`, or any of: `etcd`, `kube-apiserver`, `kube-proxy`, `kube-scheduler`, `kube-controller-manager` (comma-separated.) E.g.: `--containerized-cplane=etcd,kube-proxy` |
| `--create-template` | Optional | First creates a template VM to clone all the cluster nodes from before bringing up the cluster. (This step by far takes the longest.) If not specified, the script expects to find an existing VM to clone from. This option installs the OS using Kickstart, then installs Guest Additions. **You must provide this option for the very first cluster you create.** |
| `--template-name` | Optional | Specifies the template name to create - or clone from. Default is *bingo* if not provided. |
| `--linux` | Optional | Valid values are *centos8* and *centos9* for CentOS Stream (the default), *alma* for Alma Linux, and *rocky* for Rocky Linux. Ignored unless `--create-template` is specified. |
| `--monitoring` | Optional | Installs monitoring. Allowed values are `metrics.k8s.io`, and `kube-prometheus`. The `metrics.k8s.io` value installs the [Resource metrics pipeline](https://kubernetes.io/docs/tasks/debug-application-cluster/resource-usage-monitoring/). The `kube-prometheus` value installs Prometheus and Grafana using the [kube-prometheus](https://github.com/prometheus-operator/kube-prometheus) stack. This option creates a `NodePort` service on port 30300 so you can access Grafana without port-forwarding. Once the cluster is up, the script will display the IP addresses of each of the nodes, and you can access Grafana on any one of those IP addresses on port 30300. (Remember to allow cookies for this site.) |
| `--storage` | Optional | Installs dynamic storage provisioning to support running workloads that use Persistent Volumes and Persistent Volume Claims. Currently, the only supported value is `openebs`, which installs the [OpenEBS](https://docs.openebs.io/docs/next/uglocalpv-hostpath.html) *Local HostPath* provisioner. This controller provides dynamic provisioning of HostPath volumes. This is a light-weight provisioner that supports desktop testing. OpenEBS creates directories inside the cluster VMs for each PV. For this feature to be reasonably stable, you have to be cognizant of the amount of storage in the VMs you provision as compared the the storage consumed by the workloads you're testing. The script internals contain resizing logic but this isn't exposed via the script API at present. |
| `--single-node` | Optional | Creates a single node cluster. The default is to create three nodes: one control plane node, and two workers. This option is useful to quickly test changes since it is faster to provision a single node. |

### Other (optional) options

| Option | Description |
| ------ | ----------- |
| `--verify` | Looks for all the upstreams or filesystem objects used by the script. Valid options are `upstreams` and `files`. If `upstreams`, then the script does a curl HEAD request for each upstream (e.g. OS ISO, Kubernetes binaries, etc.). If `files`, then the same check is performed for the downloaded filesystem objects. This is a useful option to see all the objects that are required to provision a cluster. |
| `--check-compatibility` | Checks the installed versions of various desktop tools used by the project (curl, kubectl, etc) against what the project has been tested on - and then exits, taking no further action. You should do this at least once. Note - there will likely be differences between your desktop and what I tested with - you will have to determine whether the differences are relevant. |
| `--up`, `--down`, `--delete` | Takes a comma-separated list of VM names, and starts (`--up`), stops (`--down`), or deletes (`--delete`) them all. The `--down` option is a graceful shutdown. The `--delete` is a fast shutdown and also removes the Virtual Box VM files from the file system. |
| `--help` | Displays this help and exits. |

## Examples

**Example 1**

`./dtk --create-template --host-only-network=192.168.56 --vboxdir=/sdb1/virtualboxvms --networking=calico --monitoring=kube-prometheus --storage=openebs`

Creates a template VM configured with host-only networking and NAT. The host network is 192.168.56. The script will create a host-only network in VirtualBox for the template. For the k8s cluster, it installs Calico networking, Kube-Prometheus monitoring, and the OpenEBS HostPath Provisioner. Each VM gets a sequential IP address (192.168.56.200, 192.168.56.201, 192.168.56.202). This is what you run (i.e. with `--create-template`) the very first time.

**Example 2**

`./dtk --host-only-network=192.168.56 --vboxdir=/sdb1/virtualboxvms --networking=calico --monitoring=kube-prometheus --storage=openebs`

Creates a k8s cluster exactly as above, except uses the template created by the prior invocation. **Notice** that the `--host-only-network` option matches the option that was specified when the template was created. This is what you run if you're happy with the template: you just keep tearing down your cluster and re-creating it from the template. If ever you change something about the template generation, then you would delete the template, and go back to the first form of the script invocation.

The value you choose for the octets is up to you but - once you pick those values you have to use them consistently when creating new clusters from the same VM, because they are used to configure the NIC in the guest, and the octets have to match a Host-Only network configured in VirtualBox. (E.g. in the VBox UI: File > Host Network Manager > Properties.)

## TODOs

| Task | Description |
|-|-|
| Network config        | For Rocky 9, configure networking the new way vs network scripts |
| Graceful shutdown     | Configure graceful shutdown |
| Management Cluster    | Support the ability to configure as a management cluster |
| Minimal OS            | Provision with minimal (text-only, least packages) OS |
| Kube Bench            | https://github.com/aquasecurity/kube-bench |
| Load Balancer         | [MetalLB](https://github.com/google/metallb)? [Kube VIP](https://kube-vip.io/)?|
| Firewall              | Get it working with nftables rules and all ports locked down |
| SELinux               | Enable SELinux |
| Nodes                 | Make number/names/config of cluster fully configurable |
| Linux                 | Consider other Linux variants (Currently supports CentOS Stream and Rocky) |
| Other VM provisioning | Consider Packer |
| Virtualization        | Consider KVM |

## Versions

This project has been tested with the tools, components and versions shown in the table below. Where the _Category_ column says _host_ - you are responsible to install those. This project tries not to alter your environment and so this project will use whatever is there and will not mutate your system. Everything else in the table is downloaded by the project but is only installed into the VMs created by the project. To install with different versions, all you have to do is change the corresponding version variable (e.g. `K8S_VER` or `GUEST_ADDITIONS_VER`) in the `artifacts` file.

| Category | Component                                              | Version                |
| -------- | ------------------------------------------------------ | ---------------------- |
| host     | Linux desktop                                          | Ubuntu 22.04.3 LTS     |
| host     | openssl                                                | 3.0.2                  |
| host     | openssh                                                | OpenSSH_8.9p1          |
| host     | genisoimage (used to create the Kickstart ISO)         | 1.1.11                 |
| host     | Virtual Box / VBoxManage                               | 7.0.10_Ubuntur158379   |
| host     | kubectl (client only)                                  | v1.28.0                |
| host     | curl                                                   | 7.81.0                 |
| guest VM | Centos ISO (X= 8 or 9)                                 | Stream-X-x86_64-latest |
| guest VM | Rocky Linux ISO                                        | Rocky-9.2-x86_64-dvd   |
| guest VM | Virtual Box Guest Additions ISO                        | 7.0.8                  |
| k8s      | etcd                                                   | v3.5.9                 |
| k8s      | kube-apiserver                                         | v1.28.1                |
| k8s      | kube-controller-manager                                | v1.28.1                |
| k8s      | kube-scheduler                                         | v1.28.1                |
| k8s      | kubelet                                                | v1.28.1                |
| k8s      | crictl                                                 | v1.28.0                |
| k8s      | runc                                                   | v1.1.9                 |
| k8s      | cni plugins                                            | v1.3.0                 |
| k8s      | containerd                                             | v1.7.6                 |
| k8s      | CoreDNS                                                | 1.11.1                 |
| k8s      | Kubernetes Dashboard                                   | v2.7.0                 |
| k8s      | kube-proxy (if installed)                              | v1.28.1                |
| k8s      | Metrics Server (if installed)                          | v0.6.4                 |
| k8s      | Calico networking (if installed)                       | v3.26.1                |
| k8s      | Cilium networking and Hubble monitoring (if installed) | 1.9.4                  |
| k8s      | kube-prometheus stack (if installed)                   | v0.12.0                |
| k8s      | OpenEBS (if installed)                                 | 3.9.0                  |
| k8s      | Sonobuoy conformance                                   | v0.56.16               |

> Static pod container images per: https://kubernetes.io/releases/download/
