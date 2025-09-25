# Components and Versions

This project has been tested with the tools, components and versions shown in the tables below. Where the _Category_ column says _host_ - you are responsible to install those. This project tries not to alter your environment and so this project will use whatever is present and will not mutate your system. Everything else in the table is downloaded by the project but is only installed into the VMs created by the project.

To install with different Kubernetes component versions, change the corresponding version variable (e.g. `K8S_VER` or `GUEST_ADDITIONS_VER`) in the `artifacts` file. The install different Add-On versions, modify the version constant in the relevant Add-On `install` script. (More on that below.)

> This shows what I've tested with. Most likely, minor version differences will still work with _Desktop Kubernetes_.

## Components

The categories are:

1. **Host:** These tools must be installed on your desktop (by you.)
2. **Guest VM:**  These are installed in the Guest VMs that make up the cluster.
3. **Kubernetes:** These run Kubernetes in the Guest VMs.

| Category | Component | Version | VirtualBox Only | KVM Only |
|-|-|-|-|-|
| Host | Linux desktop | Ubuntu 22.04.5 LTS | - | - |
| Host | openssl | 3.0.2 | - | - |
| Host | openssh | OpenSSH_8.9p1 | - | - |
| Host | genisoimage (used to create a VirtualBox kickstart ISO) | 1.1.11 | Yes | - |
| Host | Virtual Box / VBoxManage | 7.0.10 | Yes | - |
| Host | helm | v3.18.0 | - | - |
| Host | kubectl (client only) | v1.33.1 | - | - |
| Host | curl | 7.81.0 | - | - |
| Host | yq | 4.40.5 | - | - |
| Host | virt-install / virt-clone | 4.0.0 | - | Yes |
| Host | virsh | 8.0.0 | - | Yes |
| Host | qemu-img | 6.2.0 | - | Yes |
| Host | Hydrophone | v0.7.0 | - | - |
| Guest VM | Centos ISO | Stream-9-latest-x86_64 | - | - |
| Guest VM | Rocky Linux ISO | 8.10 | - | - |
| Guest VM | Alma Linux ISO | 8.10 and 9.6 _(9.6 is the default)_ | - | - |
| Guest VM | Virtual Box Guest Additions ISO | 7.0.18 | Yes | - |
| Kubernetes | kube-apiserver | 1.34.1 | - | - |
| Kubernetes | kube-controller-manager | 1.34.1 | - | - |
| Kubernetes | kube-scheduler | 1.34.1 | - | - |
| Kubernetes | kubelet | 1.34.1 | - | - |
| Kubernetes | kube-proxy (if installed) | 1.34.1 | - | - |
| Kubernetes | etcd | v3.6.5 | - | - |
| Kubernetes | crictl | v1.34.0 | - | - |
| Kubernetes | runc | v1.3.1 | - | - |
| Kubernetes | cni plugins | v1.8.0 | - | - |
| Kubernetes | containerd | 2.1.4 | - | - |

## Add-ons

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
