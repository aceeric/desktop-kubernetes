# Design

This project might seem like a lot of bash code but it's actually pretty simple. There are about 30 main shell scripts, and a number of *helper* scripts. The helpers aren't shown below - they do minor things like download files, etc. Only the main scripts are shown.

## Script structure

Everything is invoked by the `new-cluster` script. See the _Narrative_ section that follows for a description of each numeric annotation:

```shell
new-cluster
├─ scripts/create-template-vm (1)
│  ├─ scripts/gen-ssh-keyfiles
│  ├─ scripts/gen-kickstart-iso
│  ├─ scripts/create-vm
│  └─ scripts/install-guest-additions
│
├─ scripts/gen-root-ca (2)
│
├─ toplevel-scripts/provision-controller (3)
│  ├─ scripts/clone-vm
│  ├─ scripts/configure-controller
│  │  ├─ scripts/configure-firewall
│  │  ├─ scripts/gen-cluster-tls
│  │  ├─ control-plane/etcd/install-etcd
│  │  ├─ control-plane/kube-apiserver/install-kube-apiserver
│  │  ├─ control-plane/kube-controller-manager/install-kube-controller-manager
│  │  └─ control-plane/kube-scheduler/install-kube-scheduler
│  └─ admin/gen-admin-kubeconfig
│   
├─ scripts/configure-worker (4)
│  ├─ scripts/configure-firewall
│  ├─ scripts/gen-worker-tls
│  ├─ worker/misc/install-misc-bins
│  ├─ worker/containerd/install-containerd
│  └─ worker/kubelet/install-kubelet
│
├─ toplevel-scripts/provision-workers (5)
│  └─ toplevel-scripts/provision-worker
│     ├─ scripts/clone-vm
│     └─ scripts/configure-worker
│        (same scripts, same order, as under #4 above)
│
├─ scripts/configure-etc-hosts (6)
├─ networking/kube-proxy/install-kube-proxy
├─ networking/calico/install-calico-networking
├─ dns/coredns/install-coredns
├─ monitoring/kube-prometheus/install-kube-prometheus
└─ features/storage/openebs/install-openebs
```

## Narrative

1. If the `--create-template` arg is provided then ssh keys are generated, and a template VM is created using Kickstart and a CentOS ISO. This ssh public key is copied into the VM in the `authorized-keys` file, and Virtual Box guest additions is installed. This template VM is cloned in subsequent steps to create the three VMs that comprise the Kubernetes cluster, so each VM has an identical configuration. Guest additions is used because it enables getting the IP address of a VM.
2. A root CA is generated for the cluster. This CA is used to sign and verify certs throughout the remainder of the cluster provisioning process.
3. A controller is provisioned with: cluster TLS, `etcd`, the `api server`, `controller manager`, and `scheduler`. (This project runs with a single controller to minimize the desktop footprint.)
4. Because the controller is also a worker, the controller is configured as a worker node. (See next item below.)
5. If the `--single-node` flag is **not** specified, then two dedicated workers are provisioned. A worker gets a unique TLS cert/key for its `kubelet`, a few binaries: `crictl`, `runc`, and `cni plugins`, and of course the `kubelet` and `containerd`.
6. The remainder of the scripts are: Configure `/etc/hosts` on each VM with all the cluster IP addresses. Then, assuming command line arg `--networking=calico`, Kube Proxy and Calico networking are installed. Following that, Core DNS, the Kube Prometheus stack for monitoring, and assuming `--storage=openebs`, The Open EBS storage provisioner is installed to support workloads with persistent volumes and claims.

On completion, you have a functional Kubernetes cluster consisting of three VMs, one controller, and three worker nodes.