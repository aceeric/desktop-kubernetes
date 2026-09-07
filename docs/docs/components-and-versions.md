# Components and Versions

This project has been tested with the tools, components and versions shown in the tables below. Where the _Category_ column says _host_ - you are responsible to install those. This project tries not to alter your environment and so this project will use whatever is present and will not mutate your system. Everything else in the table is downloaded by the project but is only installed into the VMs created by the project.

To install with different Kubernetes component versions, change the corresponding version variable (e.g. `K8S_VER` or `GUEST_ADDITIONS_VER`) in the `artifacts` file. The install different Add-On versions, modify the version constant in the relevant Add-On `install` script. (More on that below.)

> This shows what I've tested with. Most likely, minor version differences will still work with _Desktop Kubernetes_.

## Components

The categories are:

1. **Host:** These tools must be installed on your desktop (by you.)
2. **Guest VM:**  These are installed by _Desktop Kubernetes_ into the Guest VMs that make up the cluster.
3. **Kubernetes:** These run Kubernetes in the Guest VMs.

| Category | Component | Version | VirtualBox Only | KVM Only |
|-|-|-|-|-|
| Host | Linux desktop | Ubuntu 24.04.4 | - | - |
| Host | openssl | 3.0.13 | - | - |
| Host | openssh | OpenSSH_9.6p1 | - | - |
| Host | genisoimage (used to create a VirtualBox kickstart ISO) | 1.1.11 | Yes | - |
| Host | Virtual Box / VBoxManage | 7.0.10 | Yes | - |
| Host | helm | v4.1.1 | - | - |
| Host | kubectl (client only) | v1.37.0 | - | - |
| Host | curl | 8.5.0 | - | - |
| Host | yq | 4.40.5 | - | - |
| Host | virt-install / virt-clone | 4.1.0 | - | Yes |
| Host | virsh | 10.0.0 | - | Yes |
| Host | Hydrophone | v0.7.0 | - | - |
| Guest VM | Centos ISO | Stream-9-latest-x86_64 | - | - |
| Guest VM | Rocky Linux ISO | 8.10 | - | - |
| Guest VM | Alma Linux ISO | 8.10, 9.7, 10.2 _(10.2 is the default)_ | - | - |
| Guest VM | Virtual Box Guest Additions ISO | 7.0.18 | Yes | - |
| Kubernetes | kube-apiserver | 1.37.0 | - | - |
| Kubernetes | kube-controller-manager | 1.37.0 | - | - |
| Kubernetes | kube-scheduler | 1.37.0 | - | - |
| Kubernetes | kubelet | 1.37.0 | - | - |
| Kubernetes | kube-proxy (if installed) | 1.37.0 | - | - |
| Kubernetes | etcd | v3.7.1 | - | - |
| Kubernetes | crictl | v1.36.0 | - | - |
| Kubernetes | runc | v1.5.1 | - | - |
| Kubernetes | cni plugins | v1.9.1 | - | - |
| Kubernetes | containerd | 2.3.5 | - | - |

> The Virtual Box Guest Additions ISO enables getting the IP address of a VM.

## Add-ons

To install different add-on versions change the version in the `scripts/addons` directory. (Version updates sometimes require `values.yaml` changes and other tweaks to the install logic.)

| Add-on                              | Chart Version | Note |
|-|-|-|
| Calico networking (Tigera Operator) | v3.32.1 ||
| Cert Manager                        | v1.21.1 ||
| Cilium networking                   | 1.19.6  ||
| CoreDNS                             | 1.47.0  ||
| External DNS                        | 1.20.0  ||
| Headlamp                            | 0.44.0  |(2)|
| Ingress NGINX Controller            | 4.14.1  |(1)|
| Kube Prometheus Stack               | 88.3.0 ||
| Kubernetes Dashboard                | 7.14.0  |(1)|
| Metrics Server                      | 3.13.1  ||
| NFS Subdir External Provisioner     | 4.0.18  ||
| Nginx Gateway Fabric                | 2.6.7   ||
| Ociregistry                         | 1.16.0  |(2)|
| OpenEBS Local PV Provisioner        | 4.5.1   ||
| Vcluster                            | 0.36.1  ||

Notes:
1. Deprecated
2. Requires Gateway API CRDs (installed by Nginx Gateway Fabric add-on)
