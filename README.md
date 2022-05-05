# Desktop Kubernetes

<img src="resources/desktop-kubernetes-no-text.jpg" width="100"/>

Desktop Kubernetes is a Linux *Bash* project that provisions a desktop Kubernetes cluster using VirtualBox - with each cluster node consisting of a CentOS 8 guest VM. Desktop Kubernetes is the *57 Chevy* of Kubernetes distros: you can take it apart and put it back together with just a few Linux console tools: bash, curl, genisoimage, ssh, scp, openssl, vboxmanage, and kubectl. That being said, v1.0.0 of this distribution is Kubernetes Certified. See: [CNCF Interactive Landscape](https://landscape.cncf.io/card-mode?category=platform&amp;grouping=category&amp;selected=desktop-kubernetes). 

<img src="https://www.cncf.io/wp-content/uploads/2020/07/certified_kubernetes_color-1.png" width="90"/>

The cluster provisioned by the project consists of one VM functioning in a dual role of control plane server and worker node, plus two dedicated worker nodes. The cluster is provisioned by running one script - `new-cluster` - with a few command line options. The script makes no changes to your desktop's environment - the only changes it makes to your desktop are the files it downloads, and the VirtualBox VMs it creates. (Of course, VirtualBox may create various network interfaces but these are cleaned up by VirtualBox if you remove the cluster.)

This has been tested on Ubuntu 20.04.X systems with 64 gig of RAM and 6+ hyper-threaded processors.

This project is derivative of **Kelsey Hightower's** [Kubernetes The Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way). The differences between the Hightower project and this project are listed below:

| Hightower | This project |
| :-------- | ------------ |
| Presents a series of manual labs to get hands-on experience with Kubernetes installation as a learning exercise | Is automated - brings up a desktop Kubernetes cluster with one controller and multiple workers with a single Bash shell script invocation (see the *Quick Start* further on down.) |
| Uses [Google Cloud Platform](https://cloud.google.com/) to provision the compute resources | Provisions VMs on the desktop using [VirtualBox](https://www.virtualbox.org/). I was interested to get some experience with the `VBoxManage` utility and CentOS [Kickstart](https://docs.centos.org/en-US/centos/install-guide/Kickstart2/) for hands-free OS installation. The script creates a template VM, and then clones the template for each of the cluster nodes. I also needed the VirtualBox Guest Additions, and came up with a way to automate that installation. Guest Additions provides the ability to get the IP address from a VM. This was an interesting side-effort that resulted in the ability to create a CentOS VM just by running a single script command. |
| Uses Ubuntu for the cluster node OS | Uses [CentOS 8 Stream](https://www.centos.org/download/) |
| Structures the installation and configuration tasks by related activities, e.g. creates all the certs, copies binaries, generates configuration files, etc. | Structures the tasks (and associated script filesystem hierarchy) more around the individual Kubernetes components where possible, because I was interested in delineating the specific dependencies and requirements for each component. |
| Hand-generates the node routing | Uses the built-in VirtualBox routing that comes with either a bridged network - or host only + NAT. Both options provide host-to-guest, guest-to-guest, and guest-to-internet. |
| Implements Pod networking via the bridge network plugin from [containernetworking](https://github.com/containernetworking) | Supports cluster networking using one of three networking solutions based on a command-line option: a) [Calico](https://docs.projectcalico.org) + [kube-proxy](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-proxy/), or b) [kube-router](https://github.com/cloudnativelabs/kube-router), or c) [Cilium](https://docs.cilium.io/en/stable/gettingstarted/k8s-install-default). |
| Uses Cloudflare [cfssl](https://github.com/cloudflare/cfssl) to generate the cluster certs | Uses [openssl](https://www.openssl.org/) since it is almost universally available on Linux. I was interested to see what the scripting would look like using openssl, especially for things like creating CSRs and so on. |
| Is nicely terse and compact | Is verbose by virtue of using scripts with lots of options, and separating the component installs into separate scripts, thus requiring a lot of option passing and parsing. |
| Does not include monitoring | Installs either [Kubernetes Metrics Server](https://github.com/kubernetes-sigs/metrics-server) with the [Kubernetes Dashboard](https://kubernetes.io/docs/tasks/access-application-cluster/web-ui-dashboard/) - or - the [kube-prometheus](https://github.com/prometheus-operator/kube-prometheus) stack. |
| Does not include additional features since it is focused on Kubernetes itself | Supports OpenEBS volume provisioner |

## Quick Start

The `new-cluster` script in the repo root is what you run.

> Before running the first time: 1) Determine where on the filesystem you store VirtualBox VM files. Each VM will be about 6 gigs, and there will be four VMs: one template, and three nodes. So you need 24 gigabytes. 2) Check the CentOS mirror in the `new-cluster` script and make sure it makes sense for your geography.
>
> I also recommend you run once with just the `--check-compatibility` option to check the versions of the utilities used by the scripts (curl, etc.) against the tested versions. E.g.: `./new-cluster --check-compatibility`. There will likely be differences and you have to decide whether the differences are material. Most probably aren't.

To create a cluster for the first time, run the script as shown below (using your unique values).

**Host only + NAT networking:** This option enables the cluster to run on different networks. It's good for a laptop installation where you want to run the cluster in various locations. Any IP address is fine for the host network (subject to constraints imposed by VirtualBox.) Supply the left three octets - the script will assign the rightmost octet:

```bash
$ ./new-cluster --host-only-network=192.168.56 --vboxdir=/sdb1/virtualbox --create-template\
  --networking=calico --monitoring=kube-prometheus
```

**Bridged networking:** This is good for a desktop install since you can't run the cluster on a different network once the cluster is created. For this approach, first run `ifconfig` and get the name of your primary network interface. You use that in the `--host-network-interface` option (mine is shown below):

```shell
$ ./new-cluster --host-network-interface=enp0s31f6 --create-template\
  --vboxdir=/sdb1/virtualbox --networking=calico --monitoring=kube-prometheus
```

The `--networking` option installs cluster networking. In the example: Calico (and kube-proxy.)

The `--monitoring` option installs monitoring. In the example: Kube Prometheus. (The kube-prometheus param also creates a NodePort service on port 30300 which you can access directly using any one of the VM IPs to access the Grafana dashboard using credentials admin/admin.)

The `--create-template` option is required the first time: it creates a template VM which is used to clone the cluster VMs.

> Please Note: URLs are perishable. The script provides an option to test each URL and tell you which ones it couldn't access. Then you will have to modify the `new-cluster` script accordingly.

Once the cluster comes up, the script will display a message telling you how to set your `KUBECONFIG` in order to access the cluster. It will also display a message showing how to SSH into each node. The `scripts` directory also has a helper script `sshto` that takes a VM name as an arg and SSHs into the VM. E.g.: `scripts/sshto doc`.

## Command Line Options

The following command-line options are supported for the `new-cluster` script:

### Cluster creation options

| Option | Type | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------ | ---- |--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `--host-network-interface` | Required | Specify this, or the `--host-only-network` option. If this, then the parameter is the name of the primary network interface on your machine. The scripts use this to configure the VirtualBox bridge network for each guest VM. **Important**: you must specify this consistently when creating the template, and when creating a cluster from the template. The reason is that the option configures settings at the VM level that then propagate into the guest OS. Since guests are cloned from the template, the guest networking has to be defined consistently with the template.                                                                                                                                                                                                                                                                      |
| `--host-only-network`      | Required | Specify this, or the `--host-network-interface` option. If this, then the parameter is the left three octets of the network. E.g. `192.168.56`. (*For some additional information on this address, see*: [the VirtualBox docs](https://www.virtualbox.org/manual/ch06.html).) This option configures NAT + host only networking mode. The scripts will create a new host only network and configure the cluster to use it for intra-cluster networking, and will configure NAT for the cluster to access the internet. *See important note in the table entry immediately above regarding VBox networking type.*                                                                                                                                                                                                                                         |
| `--vboxdir`                | Required | The directory where you keep your VirtualBox VM files. The script uses the `VBoxManage` utility to create the VMs, which will in turn create a sub-directory under this directory for each VM. The directory must exist. The script will not create it.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `--networking`             | Optional | Installs Pod networking. Current valid values are `calico` (which also installs kube-proxy), `kube-router` and `cilium`. E.g.: `--networking=calico`. I use calico. And: calico is the pod networking that I used to get the k8s conformance tests passing.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `--create-template`        | Optional | First creates a template VM to clone all the cluster nodes from before bringing up the cluster. (This step by far takes the longest.) If not specified, the script expects to find an existing VM to clone from. This option installs the OS using Kickstart, then installs Guest Additions. You must provide this option for the very first cluster you create.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| `--monitoring`             | Optional | Installs monitoring. Allowed values are `metrics.k8s.io`, and `kube-prometheus`. The `metrics.k8s.io` value installs the [Resource metrics pipeline](https://kubernetes.io/docs/tasks/debug-application-cluster/resource-usage-monitoring/) and it also installs [Kubernetes Dashboard](https://github.com/kubernetes/dashboard), which can be accessed using `kubectl proxy`. The `kube-prometheus` value installs Prometheus and Grafana using the [kube-prometheus](https://github.com/prometheus-operator/kube-prometheus) stack. This option creates a `NodePort` service on port 30300 so you can access Grafana without port-forwarding. Once the cluster is up, the script will display the IP addresses of each of the nodes, and you can access Grafana on any one of those IP addresses on port 30300. (Remember to allow cookies for this site.) |
| `--storage`                | Optional | Installs dynamic storage provisioning to support running workloads that use Persistent Volumes and Persistent Volume Claims. Currently, the only supported value is `openebs`, which installs the [OpenEBS](https://docs.openebs.io/docs/next/uglocalpv-hostpath.html) *Local HostPath* provisioner. This controller provides dynamic provisioning of HostPath volumes. This is a light-weight provisioner that supports desktop testing. OpenEBS creates directories inside the cluster VMs for each PV. For this feature to be reasonably stable, you have to be cognizant of the amount of storage in the VMs you provision as compared the the storage consumed by the workloads you're testing. The script internals contain resizing logic but this isn't exposed via the script API at present.                                                       |
| `--single-node`            | Optional | Creates a single node cluster. The default is to create three nodes: one control plane node, named *doc*, and two workers, named *ham* and *monk*. This option is useful to quickly test changes since it is faster to provision a single node.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |

### Other (optional) options

| Option | Description |
| ------ | ----------- |
| `--verify` | Looks for all the upstreams or filesystem objects used by the script. Valid options are `upstreams` and `files`. If `upstreams`, then the script does a curl HEAD request for each upstream (e.g. CentOS ISO, Kubernetes binaries, etc.). If `files`, then the same check is performed for the downloaded filesystem objects. This is a useful option to see all the objects that are required to provision a cluster. The list is influenced by some other options. E.g. if you specify `--monitoring=kube-prometheus`, then that will add to the list of objects to be checked. |
| `--check-compatibility`      | Checks the installed versions of various desktop tools used by the project (curl, kubectl, etc) against what the project has been tested on - and then exits, taking no further action. You should do this at least once. Or just run `verify-prereqs` in the `scripts` directory. Note - there will likely be differences between your desktop and what I tested with - you will have to determine whether the differences are relevant. |
| `--up`, `--down`, `--delete` | Takes a comma-separated list of VM names, and starts (`--up`), stops (`--down`), or deletes (`--delete`) them all. The `--down` option is a graceful shutdown. The `--delete` is a fast shutdown and also removes the Virtual Box VM files from the file system. |
| `--help`                     | Displays this help and exits. |

## Examples

**Example 1**

`./new-cluster --create-template --host-only-network=192.168.56 --vboxdir=/sdb1/virtualbox/ --networking=calico --monitoring=kube-prometheus --storage=openebs`

Creates a template VM configured with host-only networking and NAT. The host network is 192.168.56. The script will create a host-only network in VirtualBox for the template. For the k8s cluster, it installs Calico networking, Kube-Prometheus monitoring, and the OpenEBS HostPath Provisioner. Each VM gets a sequential IP address (192.168.56.200, 192.168.56.201, 192.168.56.202). This is what you run - with `--create-template` - the very first time.

**Example 2**

`./new-cluster --host-only-network=192.168.56 --vboxdir=/sdb1/virtualbox/ --networking=calico --monitoring=kube-prometheus --storage=openebs`

Creates a k8s cluster exactly as above, except uses the template created by the prior invocation. **Notice** that the `--host-only-network` option matches the option that was specified when the template was created. This is what you run if you're happy with the template: you just keep tearing down your cluster and re-creating it from the template. If ever you change something about the template generation, then you would delete the template, and go back to the first form of the script invocation. The value you choose for the octets is up to you but - once you pick those values you have to use them consistently because they are used to configure the NIC in the guest, and the octets have to match a Host-Only network configured in VirtualBox. (E.g. in the VBox UI: File > Host Network Manager > Properties.)

**Example 3**

```shell
$ ./new-cluster --verify=upstreams --create-template --monitoring=kube-prometheus --networking=calico --storage=openebs
OK: https://github.com/etcd-io/etcd/releases/download/v3.5.2/etcd-v3.5.2-linux-amd64.tar.gz
OK: https://dl.k8s.io/v1.23.4/bin/linux/amd64/kube-apiserver
OK: https://dl.k8s.io/v1.23.4/bin/linux/amd64/kube-controller-manager
OK: https://dl.k8s.io/v1.23.4/bin/linux/amd64/kube-scheduler
OK: https://github.com/kubernetes-sigs/cri-tools/releases/download/v1.23.0/crictl-v1.23.0-linux-amd64.tar.gz
OK: https://github.com/opencontainers/runc/releases/download/v1.1.0/runc.amd64
OK: https://github.com/containernetworking/plugins/releases/download/v1.1.0/cni-plugins-linux-amd64-v1.1.0.tgz
OK: https://github.com/containerd/containerd/releases/download/v1.6.0/containerd-1.6.0-linux-amd64.tar.gz
OK: https://dl.k8s.io/v1.23.4/bin/linux/amd64/kubelet
OK: https://mirror.umd.edu/centos/8-stream/isos/x86_64/CentOS-Stream-8-x86_64-latest-dvd1.iso
OK: https://download.virtualbox.org/virtualbox/6.1.30/VBoxGuestAdditions_6.1.30.iso
OK: https://github.com/prometheus-operator/kube-prometheus/archive/v0.10.0.tar.gz
OK: https://dl.k8s.io/v1.23.4/bin/linux/amd64//kube-proxy
OK: https://docs.projectcalico.org/manifests/calico.yaml
OK: https://raw.githubusercontent.com/openebs/charts/gh-pages/hostpath-operator.yaml
OK: https://openebs.github.io/charts/openebs-lite-sc.yaml
```

Using the cluster creation options, checks the upstream URLS with a HEAD request to make sure all those resources are presently available matching the hard-coded versions. Doesn't actually create a cluster. Note - some upstreams don't have versioned URLs, which unfortunately makes it impossible to achieve a completely deterministic install...   

## ToDos

| Task                           | Description                                                  |
| ------------------------------ | ------------------------------------------------------------ |
| Aggregation                    | Remove patch and incorporate into main api-server setup      |
| Kubernetes binaries            | For these, encode the version into the downloaded binary and strip it when copied into the VM for better documentation |
| Graceful shutdown              | Configure graceful shutdown                                  |
| Management Cluster             | Support the ability to configure as a management cluster     |
| Centos minimal                 | Provision with CentOS minimal                                |
| Load Balancer                  | Implement [MetalLB](https://github.com/google/metallb) ?     |
| Firewall                       | There are plenty of posts discussing how to configure the firewall settings for Kubernetes. The documented settings do not appear to work with CoreDNS on CentOS 8. (In fact, many posters recommend to disable `firewalld` on CentOS.) So presently, the firewall is disabled but my goal is to run the cluster with the firewall enabled and the correct rules defined |
| Ubuntu                         | Support Ubuntu Server as the Guest OS - presently only CentOS is supported |
| Headless                       | Support running the VMs headless. At present, each VM comes up on the desktop, which can be somewhat intrusive it you're doing other work. (OTOH it does provide positive feedback on what's happening) |
| Nodes                          | Consider making the number of controllers configurable, as well as node characteristics such as storage, RAM, and CPU. Right now, only one controller and two workers are supported, their names are hard-coded, etc. |
| Hands-free install improvement | The current version builds a Kickstart ISO, and mounts the ISO on the VM to do the hands-free CentOS install. Unfortunately, this method does not allow you to change the boot menu timeout on the *initial* startup of the VM. So, unless you intervene, the boot menu takes 60 seconds to time out before the Kickstart installation begins. The alternate way to do this is to break apart the ISO, modify the boot menu timeout, and then re-build the ISO. I may consider this at some future point, although that would not easily lend itself to automation |
| Flatcar Linux                  | Consider [Flatcar Linux](https://kinvolk.io/blog/2020/02/flatcar-container-linux-enters-new-era-after-coreos-end-of-life-announcement/) as a VM OS |
| Static Pods                    | Consider running the Kubernetes core components as static pods |
| Other VM provisioning          | Experiment with other VM provisioning tooling (Terraform? Vagrant? CloudInit?) |

## Versions

This project has been tested with the following tools, components and versions. I've tried to make this as comprehensive and accurate as possible. The Kubernetes component versions and CentOS and VirtualBox Guest Addition versions are hard-coded into the `new-cluster` script where possible. (Some manifests, like OpenEBS for example, don't have versioned URLs. So in those cases, the versions reflect the testing at the point in time indicated in the table.)

For explicitly versioned components, changes only need to be made one time in the `new-cluster` script. *If you decide to use later (or earlier) Kubernetes components, be aware that the supported options can change between versions which may require additional script changes.*

| Where    | Component                                                      | Version                | Updated    |
| -------- | -------------------------------------------------------------- |------------------------| ---------- |
| host     | Linux desktop                                                  | Ubuntu 20.04.4 LTS     | 2022-02-26 |
| host     | openssl                                                        | 1.1.1f                 |            |
| host     | openssh                                                        | OpenSSH_8.2p1          |            |
| host     | genisoimage (used to create the Kickstart ISO)                 | 1.1.11                 |            |
| host     | Virtual Box / VBoxManage                                       | 6.1.30                 | 2022-02-26 |
| host     | kubectl (client only)                                          | v1.24.0                | 2022-05-05 |
| host     | curl                                                           | 7.68.0                 |            |
| guest VM | Centos ISO                                                     | Stream-8-x86_64-latest | 2022-02-26 |
| guest VM | Virtual Box Guest Additions ISO                                | 6.1.30                 | 2021-11-27 |
| k8s      | etcd                                                           | v3.5.2                 | 2022-02-26 |
| k8s      | kube-apiserver                                                 | v1.23.4                | 2022-02-26 |
| k8s      | kube-controller-manager                                        | v1.23.4                | 2022-02-26 |
| k8s      | kube-scheduler                                                 | v1.23.4                | 2022-02-26 |
| k8s      | kubelet                                                        | v1.23.4                | 2022-02-26 |
| k8s      | crictl                                                         | v1.23.0                | 2022-02-26 |
| k8s      | runc                                                           | v1.1.0                 | 2022-02-26 |
| k8s      | cni plugins                                                    | v1.1.0                 | 2022-02-26 |
| k8s      | containerd                                                     | v1.6.0                 | 2022-02-26 |
| k8s      | CoreDNS                                                        | 1.9.0                  | 2022-02-26 |
| k8s      | kube-proxy (if installed)                                      | v1.23.4                | 2022-02-26 |
| k8s      | kube-router (if installed)                                     | v1.3.1                 | 2021-08-14 |
| k8s      | Metrics Server (if installed)                                  | 0.4.2                  |            |
| k8s      | Kubernetes Dashboard (if installed)                            | 2.0.0                  |            |
| k8s      | Calico networking (if installed)                               | 3.22.0                 | 2022-02-26 |
| k8s      | Cilium networking and Hubble network monitoring (if installed) | 1.9.4                  |            |
| k8s      | kube-prometheus stack (if installed)                           | 0.10.0                 | 2022-02-26 |
| k8s      | OpenEBS (if installed)                                         | 2.11.1                 | 2022-02-26 |
| k8s      | Sonobuoy conformance (passed)                                  | v0.53.2                | 2021-08-18 |
