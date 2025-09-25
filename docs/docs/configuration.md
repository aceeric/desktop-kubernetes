# Configuration

The project includes a `config.yaml` file in the repo root that specifies the cluster configuration. The file is structured into the following sections:

| Section | Description |
|-|-|
| `addons` | A list of cluster add-ons to install, e.g.: CNI, CoreDNS, etc. |
| `k8s` | Kubernetes cluster configuration. |
| `kvm` | KVM configuration. |
| `vbox` | VirtualBox configuration. |
| `vm` | VM configuration (common to KVM & VirtualBox.) |
| `vms` | A list of VMs to create for the cluster, and their characteristics. |
| `cluster` | Populated by _Desktop Kubernetes_ when a new cluster is provisioned. |

There is one top-level key with no subkeys: `virt`. This key determines whether KVM or VirtualBox will be used to provision and manage the VMs. The options are `virtualbox` and `kvm`. The default value is `kvm`. The reason is that KVM is significantly faster (and simpler) to provision VMs than VirtualBox.

## The `addons` Section

This section enables or disables the addons included with the CLI. See the [Addons](add-ons.md) section for more details. These are the default values:

| Key | Enabled by default? |
|-|-|
| `calico` | false |
| `cert-manager` | true |
| `cilium` | true |
| `coredns` | true |
| `external-dns` | false |
| `ingress-nginx` | true |
| `kube-prometheus-stack` | true |
| `kubernetes-dashboard` | true |
| `metrics-server` | true |
| `openebs` | true |
| `vcluster` | false |

## The `k8s` Section

The `k8s` section has configuration settings that configure Kubernetes, independent of the virtualization that you choose.

| Key | Description |
|-|-|
| `k8s.containerized-cplane` {: .nowrap-column } | If specified, creates the control plane components as static pods on the controller VM like kubeadm, RKE2, et. al. (By default, Desktop Kubermetes creates the control plane components as as systemd units.) Allowed values: `all`, or any of: `etcd`, `kube-apiserver`, `kube-proxy`, `kube-scheduler`, `kube-controller-manager` (comma-separated.) E.g.: `etcd,kube-apiserver` |
| `k8s.cluster-cidr` | Configures CIDR range for Pods. This is applied to the `kube-controller-manager`. (Be aware of `--node-cidr-mask-size...` args which you can't override at this time.) |
| `k8s.cluster-dns` | Ignored - not yet implemented. |
| `k8s.kube-proxy` | If true, you can run the cluster without Calico or Cilium (or other CNI) using the default CNI configuration that is established by `scripts/worker/containerd/install-containerd`. |
| `k8s.containerd-mirror` | Supports configuring `containerd` to mirror to a different registry. The example in the yaml (commented out) has all images mirrored to a distribution server on 192.168.0.49:8080. Background: I use my own caching pull-only, pull-through OCI distribution server https://github.com/aceeric/ociregistry running as a systemd service on my desktop to mitigate DockerHub rate limiting. See the example immediately below. |

> Static pod container images for the containerized control plane per: https://kubernetes.io/releases/download/

### Configuring `containerd`

You can configure containerd to mirror with the following in the `config.yaml` file. In the example, **all** images are mirrored (`name: _default`) and the mirror is http://http://192.168.0.49:8080.

```
k8s:
  containerd-mirror:
    name: _default
    config: |
      [host."http://192.168.0.49:8080"]
        capabilities = ["pull", "resolve"]
        skip_verify = true
```


## The `vbox` Section

This section is only used if `virt = virtualbox`

| Key | Description |
|-|-|
| `vbox.host-network-interface` {: .nowrap-column } | The name of the primary network interface on your machine. The scripts use this to configure the VirtualBox bridge network for each guest VM. **Important**: you must specify this consistently when creating the template, and when creating a cluster from the template. The reason is that the option configures settings at the VM level that then propagate into the guest OS. Since guests are cloned from the template, the guest networking has to be defined consistently with the template. This config is mutually exclusive with `vbox.host-only-network`. |
| `vbox.host-only-network` | The left three octets of the network. E.g. `192.168.56`. (*For some additional information on this address, see*: [the VirtualBox docs](https://www.virtualbox.org/manual/ch06.html) *section on "Host-Only Networking"*.) This option configures NAT + host only networking mode. The scripts will create a new host only network and configure the cluster to use it for intra-cluster networking, and will configure NAT for the cluster to access the internet. *See important note in the table entry immediately above regarding VBox networking type.* This config is mutually exclusive with `vbox.host-network-interface`. |
| `vbox.vboxdir` | The directory where you keep your VirtualBox VM files. The script uses the `VBoxManage` utility to create the VMs, which will in turn create a sub-directory under this directory for each VM. If empty, the script will get the value from VirtualBox. The directory must exist. The script will not create it. |
| `vbox.kickstart` | Specifies the name of the kickstart file to configure the OS. The file has to be in the `kickstarts` directory. The default is `vbox.text.ks.cfg` which is a non-graphical install. |

## The `kvm` Section

This section is only used if `virt = kvm`

| Key | Description |
|-|-|
| `kvm.network` | This is set to `nat` in the configuration file. This setting is actually ignored because NAT is the only KVM networking option currently implemented but stating that in the configuration makes it more self-documenting. |
| `kvm.kickstart` | The kickstart file used when creating a template VM. Kickstart files are in the `kickstarts` directory of the project. The default is `kvm.text.ks.cfg`. |
| `kvm.os-variant` {: .nowrap-column } | Has to align with OS ISO. (Values from `virt-install --os-variant list`.) Default is `almalinux9`. |

## The `vm` Section

| Key | Description |
|-|-|
| `vm.linux` | Determines the Linux variant.  Valid values are `alma9` for Alma 9.6 (the default), `alma8` for Alma 8.10, `centos9` for CentOS 9 Stream, and `rocky` for Rocky Linux. Ignored unless `vm.create-template` is specified. **CentOS and Rocky are un-tested.** (It's on the to-do list.) |
| `vm.create-template` | Values are `true` (the  default) or `false`. Causes the script to create a template VM to clone all the cluster nodes from before bringing up the cluster. (This step by far takes the longest.) If not specified, the script expects to find an existing VM to clone from per the `vm.template-vmname` setting. This option installs the OS using Kickstart. **You must set this to true for the very first cluster you create.** |
| `vm.template-vmname` {: .nowrap-column } | Specifies the template VM name to create - or clone from. |

## The `vms` Section

This section has a list of dictionaries.

| Key | Description |
|-|-|
| `vms` | This is a list of VMs to create. Each VM in the list specifies the following keys: |
| `vms[n].name` | The VM Name. |
| `vms[n].cpu` | Number of CPUs. |
| `vms[n].mem` | Memory in MB. E.g.: `8192` = 8 gig. |
| `vms[n].ip` | The rightmost octet of the IP address for the host. Ignored unless `virt=virtualbox` and `vbox.host-only-network` is configured. So, for example, if `vbox.host-only-network` is `192.168.56` and this `ip` value is `200`. then the IP address assigned to the host-only interface in the VM is `192.168.56.200`. |
| `vms[n].disk` | Only supported if `virt=kvm` at this time. Resizes the disk to the specified number which is interpreted as Gi. **Note:** the script will use `sudo` to issue the resize command because libvirt makes `root` the owner of the VM `qcow2` files and I have not been able to figure out how to overcome that. |
| `vms[n].pod-cidr` {: .nowrap-column } | Used to configure CNI for containerd. **As soon as Cilium or Calico are installed then this configuration is rendered unused.** |

## The `cluster` Section

| Key | Description |
|-|-|
| `cluster` | Contains cluster information for the add-ons. Populated (overwritten) by `scripts/addons/install-addons`. Avoid editing this as it will be overwritten whenever a cluster is provisioned. |
