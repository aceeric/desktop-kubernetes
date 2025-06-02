# Desktop Kubernetes

<img src="resources/desktop-kubernetes-no-text.jpg" width="100"/>

Desktop Kubernetes is a Linux *Bash* project that provisions a desktop Kubernetes cluster using KVM or VirtualBox - with each cluster node consisting of an Alma, CentOS, or Rocky Linux guest VM. The purpose is to create a local development and testing environment that is 100% compatible with a production-grade Kubernetes environment.

Desktop Kubernetes is the *57 Chevy* of Kubernetes distros: you can take it apart and put it back together with just a few Linux console tools: bash, curl, ssh, scp, tar, openssl, helm, yq, kvm tools (virsh, virt-install, qemu-img), and kubectl. That being said, **v1.31.0** of this distribution is Kubernetes Certified. See: [CNCF Landscape](https://landscape.cncf.io/?group=certified-partners-and-providers&view-mode=grid&item=platform--certified-kubernetes-distribution--desktop-kubernetes).

[<img src="https://www.cncf.io/wp-content/uploads/2020/07/certified_kubernetes_color-1.png" width="90"/>](https://github.com/cncf/k8s-conformance/tree/master/v1.28/desktop-kubernetes)

The project consists of a number of bash scripts and supporting manifests / config files. The design is documented [here](https://github.com/aceeric/desktop-kubernetes/blob/master/resources/design.md).

This project started as a way to automate the steps in **Kelsey Hightower's** [Kubernetes The Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way) - just to see if I could. But at this point I pretty much rely on it for all my local Kubernetes development. I use it on Ubuntu 20.04.X systems with 64 gigs of RAM and 6+ hyper-threaded processors.

> **NOTE: In May 2025 the `master` branch was renamed to `main` and `main` is now the default branch.**

## Contents

  * [Quick Start](#quick-start)
  * [Command Line Options](#command-line-options)
  * [The `config.yaml` configuration file](#the-configyaml-configuration-file)
  * [Versions](#versions)
  * [Change Log](#change-log)

## Quick Start

The `dtk` script in the repo root is what you run. If you supply no arguments, the script will configure the cluster based on the `config.yaml` file in the project root resulting in a three node Alma Linux cluster consisting of one controller and two workers.

> I recommend you run once with just the `--check-compatibility` option to check the versions of the CLIs used by the scripts (curl, etc.) against the tested versions. E.g.: `./dtk --check-compatibility`. There will likely be differences and you have to decide whether the differences are material. Slight version differences may not matter, but for sure you need all the listed tools. In keeping with the project philosophy of not modifying your desktop - you need to install the tools listed in order to use this project.

Once the cluster comes up, the script will display a message telling you how to set your `KUBECONFIG` environment variable in order to access the cluster. It will also display a message showing how to SSH into each node. (There's also a helper script `sshto` that you can use for that.)

## Command Line Options

The following command-line options are supported for the `dtk` script:

| Option | Description |
| ------ | ----------- |
| `--config` | Specifies the path to a `yaml` file that provides cluster configuration. If omitted, then the script uses the `config.yaml` file in the project root. Example: `--config ~/myconfig.yaml`. |
| `--verify` | Looks for all the upstreams or filesystem objects used by the script to build the core k8s cluster. Valid options are `upstreams` and `files`. If `upstreams`, then the script does a curl HEAD request for each upstream (e.g. OS ISO, Kubernetes binaries, etc.). If `files`, then the same check is performed for the downloaded filesystem objects. This is a useful option to see all the objects that are required to provision a cluster. Example: `--verify upstreams`. |
| `--check-compatibility` | Checks the installed versions of various desktop tools used by the project (curl, kubectl, etc) against what the project has been tested on - and then exits, taking no further action. You should do this at least once. Note - there will likely be differences between your desktop and what I tested with - you will have to determine whether the differences are relevant. |
| `--up`, `--down`, `--delete` | Takes a comma-separated list of VM names, and starts (`--up`), stops (`--down`), or deletes (`--delete`) them all. The `--down` option is a graceful shutdown. The `--delete` is a fast shutdown and also removes the VM files from the file system. |
| `--create-template` | Accepts `true` or `false`. Overrides the `vm.create-template` setting in the `config.yaml` file. Example: `--create-template=false`. |
| `--no-create-vms` | Do not create VMs. If this option is specified, then the VMs in the `config.yaml` file must be up and running, and the installer will simply install k8s on them. |
| `--install-addon` | Installs the specified add-on into a running cluster. Example: `--install-addon openebs`. (The add-on has to exist in the `addons` directory.) |
| `--help` | Displays help and exits. |

## The `config.yaml` configuration file

The project has a `config.yaml` file in the repo root that specifies the cluster configuration. The file is structured into the following sections:

1. **k8s:** Kubernetes cluster configuration.
2. **vbox:** VirtualBox configuration.
3. **kvm:** KVM configuration.
4. **vm:** VM configuration (common to KVM & VBox)
5. **vms:** A list of VMs to create for the cluster, and their characteristics.
6. **addons:** A list of cluster add-ons to install, e.g.: CNI, CoreDNS, etc.
7. **config:** Populated by the installer.

| Key | Description |
|-|-|
| `virt` | Options are `virtualbox` and `kvm`. The default value is `kvm`. The reason is that kvm is significantly faster (and simpler) to provision VMs than VirtualBox. |
| `k8s.containerized-cplane` | If specified, creates the control plane components as static pods on the controller VM like kubeadm, RKE2, et. al. (By default, creates the control plane components as as systemd units.) Allowed values: `all`, or any of: `etcd`, `kube-apiserver`, `kube-proxy`, `kube-scheduler`, `kube-controller-manager` (comma-separated.) E.g.: `etcd,kube-apiserver` |
| `k8s.cluster-cidr` | Configures CIDR range for Pods. This is applied to the `kube-controller-manager`. (Be aware of `--node-cidr-mask-size...` args which you can't override at this time.) |
| `k8s.cluster-dns` | Ignored - not yet implemented. |
| `k8s.kube-proxy` | If true, you can run the cluster without Calico or Cilium (or other CNI) using the default CNI configuration that is established by `scripts/worker/containerd/install-containerd`. |
| `k8s.containerd-mirror` | Supports configuring `containerd` to mirror to a different registry. The example in the yaml (commented out) has all images mirrored to a distribution server on 192.168.0.49:8080. Background: I use my own caching pull-only, pull-through OCI distribution server https://github.com/aceeric/ociregistry running as a systemd service on my desktop to mitigate DockerHub rate limiting. |
| `vbox.host-network-interface` | The name of the primary network interface on your machine. The scripts use this to configure the VirtualBox bridge network for each guest VM. **Important**: you must specify this consistently when creating the template, and when creating a cluster from the template. The reason is that the option configures settings at the VM level that then propagate into the guest OS. Since guests are cloned from the template, the guest networking has to be defined consistently with the template. This config is mutually exclusive with `vbox.host-only-network`. |
| `vbox.host-only-network` | The left three octets of the network. E.g. `192.168.56`. (*For some additional information on this address, see*: [the VirtualBox docs](https://www.virtualbox.org/manual/ch06.html) *section on "Host-Only Networking"*.) This option configures NAT + host only networking mode. The scripts will create a new host only network and configure the cluster to use it for intra-cluster networking, and will configure NAT for the cluster to access the internet. *See important note in the table entry immediately above regarding VBox networking type.* This config is mutually exclusive with `vbox.host-network-interface`. |
| `vbox.vboxdir` | The directory where you keep your VirtualBox VM files. The script uses the `VBoxManage` utility to create the VMs, which will in turn create a sub-directory under this directory for each VM. If empty, the script will get the value from VirtualBox. The directory must exist. The script will not create it. |
| `vbox.kickstart` | Specifies the name of the kickstart file to configure the OS. The file has to be in the `kickstarts` directory. The default is `vbox.text.ks.cfg` which is a non-graphical install. |
| `kvm.network` | This is set to `nat` in the configuration file. This setting is actually ignored because NAT is the only KVM networking option currently implemented but stating that in the configuration makes it more self-documenting. |
| `kvm.kickstart` | The kickstart file used when creating a template VM. Kickstart files are in the `kickstarts` directory. The default is `kvm.text.ks.cfg`. |
| `kvm.os-variant` | Has to align with OS ISO. (Values from `virt-install --os-variant list`.) Default is `almalinux9`. |
| `vm.linux` | Valid values are `alma9` for Alma 9.5 (the default), `alma8` for Alma 8.10, `centos9` for CentOS 9 Stream, and `rocky` for Rocky Linux. Ignored unless `vm.create-template` is specified. **CentOS and Rocky are un-tested.** (It's on the to-do list.) |
| `vm.create-template` | True (the  default)/False. Causes the script to create a template VM to clone all the cluster nodes from before bringing up the cluster. (This step by far takes the longest.) If not specified, the script expects to find an existing VM to clone from per the `vm.template-vmname` setting. This option installs the OS using Kickstart. **You must set this to true for the very first cluster you create.** |
| `vm.template-vmname` | Specifies the template VM name to create - or clone from. |
| `vms` | This is a list of VMs to create. Each VM in the list specifies the following keys: |
| `vms[n].name` | The VM Name. |
| `vms[n].cpu` | Number of CPUs. |
| `vms[n].mem` | RAM in MB. E.g.: `8192` = 8 gig. |
| `vms[n].ip` | The rightmost octet of the IP address for the host. Ignored unless `virt=virtualbox` and `vbox.host-only-network` is configured. So, for example, if `vbox.host-only-network` is `192.168.56` and this `ip` value is `200`. then the IP address assigned to the host-only interface in the VM is `192.168.56.200`. |
| `vms[n].disk` | Only supported if `virt=kvm` at this time. Resizes the disk to the specified number which is interpreted as Gi. **Note:** the script will use `sudo` to issue the resize command because libvirt makes `root` the owner of the VM `qcow2` files and I have not been able to figure out how to overcome that. |
| `vms[n].pod-cidr` | Used to configure CNI for containerd. As soon as Cilium or Calico are installed then this configuration is superseded. |
| `addons` | Installs the listed add-ons in the `scripts/addons` directory. E.g. Calico, Cilium, Kube Prometheus Stack, etc. Add-ons are installed in the order listed in the yaml. _CNI needs to be first!_ |
| `cluster` | Contains cluster information for the add-ons. Populated (overwritten) by `scripts/addons/install-addons`. |

## Versions

This project has been tested with the tools, components and versions shown in the table below. Where the _Category_ column says _host_ - you are responsible to install those. This project tries not to alter your environment and so this project will use whatever is present and will not mutate your system. Everything else in the table is downloaded by the project but is only installed into the VMs created by the project. To install with different k8s versions, change the corresponding version variable (e.g. `K8S_VER` or `GUEST_ADDITIONS_VER`) in the `artifacts` file.

| Category | Component | Version |
|-|-|-|
| host | Linux desktop | Ubuntu 22.04.5 LTS |
| host | openssl | 3.0.2 |
| host | openssh | OpenSSH_8.9p1 |
| host (vbox) | genisoimage (used to create a kickstart ISO) | 1.1.11 |
| host (vbox) | Virtual Box / VBoxManage | 7.0.10 |
| host | helm | v3.18.0 |
| host | kubectl (client only) | v1.33.1 |
| host | curl | 7.81.0 |
| host | yq | 4.40.5 |
| host (kvm) | virt-install / virt-clone | 4.0.0 |
| host (kvm) | virsh | 8.0.0 |
| host (kvm) | qemu-img | 6.2.0 |
| guest VM | Centos ISO | Stream-9-latest-x86_64 |
| guest VM | Rocky Linux ISO | 8.10 |
| guest VM | Alma Linux ISO | 8.10 and 9.5 _(9.5 is the defaut)_ |
| guest VM (vbox) | Virtual Box Guest Additions ISO | 7.0.18 |
| k8s | kube-apiserver | v1.33.1 |
| k8s | kube-controller-manager | v1.33.1 |
| k8s | kube-scheduler | v1.33.1 |
| k8s | kubelet | v1.33.1 |
| k8s | kube-proxy (if installed) | v1.33.1 |
| k8s | etcd | v3.6.0 |
| k8s | crictl | v1.33.0 |
| k8s | runc | v1.3.0 |
| k8s | cni plugins | v1.7.1 |
| k8s | containerd | 2.1.1 |
| conformance | Sonobuoy conformance | v0.57.2 |

### Add-ons

To install different add-on versions change the version in the `scripts/addons` directory. (Version updates sometimes require `values.yaml` changes and other tweaks to the install logic.)

| Add-on                              | App Version  | Chart Version |
|-|-|-|
| Calico networking (Tigera Operator) | v3.30.0      | v3.30.0 |
| Cert Manager                        | v1.17.2      | v1.17.2 |
| Cilium networking                   | 1.17.4       | 1.17.4  |
| CoreDNS                             | 1.12.0       | 1.42.2  |
| External DNS                        | v0.14.0      | 1.13.1  |
| Ingress NGINX Controller            | 1.12.2       | 4.12.2  |
| Kube Prometheus Stack               | v0.82.2      | 72.6.0  |
| Kubernetes Dashboard                | (multiple)   | 7.12.0  |
| Metrics Server                      | 0.7.2        | 3.12.2  |
| OpenEBS Local PV Provisioner        | 4.2.0        | 4.2.0   |

> Static pod container images per: https://kubernetes.io/releases/download/

## Change Log

Date: 26-May-2025
Commit: `87afc243`

Significant changes:

1. Addons: Calico 3.30.0

---

Date: 26-May-2025
Commit: `c538b600`

Significant changes:

1. Addons: Cilium 1.17.4

---

Date: 25-May-2025
Commit: `04428cee`

Significant changes:

1. Addons: coredns 1.42.1, ingress-nginx 4.12.2, kube-prometheus-stack 72.6.2, kubernetes-dashboard 7.12.0, metrics-server 3.12.2, openebs 4.2.0

---

Date: 25-May-2025
Commit: `a1699e16`

Significant changes:

1. Kubernetes v1.33.1, runc v1.3.0, etcd v3.6.0, crictl v1.33.0, containerd 2.1.1, cni plugins v1.7.1

---

Date: 24-May-2025
Commit: `e7faa4e4`

Significant changes:

1. Renamed `master` branch to `main`
2. Support both Alma 8.10 and Alma 9.5
3. Configure Alma 9.5 as the default

