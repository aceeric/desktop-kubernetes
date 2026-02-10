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
| Host | Linux desktop | Ubuntu 22.04.5 LTS | - | - |
| Host | openssl | 3.0.2 | - | - |
| Host | openssh | OpenSSH_8.9p1 | - | - |
| Host | genisoimage (used to create a VirtualBox kickstart ISO) | 1.1.11 | Yes | - |
| Host | Virtual Box / VBoxManage | 7.0.10 | Yes | - |
| Host | helm | v4.1.1 | - | - |
| Host | kubectl (client only) | v1.35.0 | - | - |
| Host | curl | 7.81.0 | - | - |
| Host | yq | 4.40.5 | - | - |
| Host | virt-install / virt-clone | 4.0.0 | - | Yes |
| Host | virsh | 8.0.0 | - | Yes |
| Host | Hydrophone | v0.7.0 | - | - |
| Guest VM | Centos ISO | Stream-9-latest-x86_64 | - | - |
| Guest VM | Rocky Linux ISO | 8.10 | - | - |
| Guest VM | Alma Linux ISO | 8.10 and 9.7 _(9.7 is the default)_ | - | - |
| Guest VM | Virtual Box Guest Additions ISO | 7.0.18 | Yes | - |
| Kubernetes | kube-apiserver | 1.35.0 | - | - |
| Kubernetes | kube-controller-manager | 1.35.0 | - | - |
| Kubernetes | kube-scheduler | 1.35.0 | - | - |
| Kubernetes | kubelet | 1.35.0 | - | - |
| Kubernetes | kube-proxy (if installed) | 1.35.0 | - | - |
| Kubernetes | etcd | v3.6.7 | - | - |
| Kubernetes | crictl | v1.35.0 | - | - |
| Kubernetes | runc | v1.4.0 | - | - |
| Kubernetes | cni plugins | v1.9.0 | - | - |
| Kubernetes | containerd | 2.1.4 | - | - |

> The Virtual Box Guest Additions ISO enables getting the IP address of a VM.

## Add-ons

To install different add-on versions change the version in the `scripts/addons` directory. (Version updates sometimes require `values.yaml` changes and other tweaks to the install logic.)

| Add-on                              | Chart Version |
|-|-|
| Calico networking (Tigera Operator) | v3.31.3 |
| Cert Manager                        | v1.19.2 |
| Cilium networking                   | 1.18.5  |
| CoreDNS                             | 1.45.0  |
| External DNS                        | 1.19.0  |
| Ingress NGINX Controller            | 4.14.1  |
| Kube Prometheus Stack               | 80.6.0  |
| Kubernetes Dashboard                | 7.14.0  |
| Metrics Server                      | 3.13.0  |
| NFS Subdir External Provisioner     | 4.0.18  |
| Nginx Gateway Fabric                | 2.4.1   |
| OpenEBS Local PV Provisioner        | 4.4.0   |
| Vcluster                            | 0.30.4  |
