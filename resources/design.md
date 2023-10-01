# Design

This project might seem like a lot of bash code but it's actually pretty simple. There are about 30-odd primary shell scripts, and a number of *helper* scripts. The helpers aren't shown below - they do minor things like download files, etc. (See `scripts/helpers`.) Only the primary scripts are shown in this README.

## Directory structure

The script directory structure is organized around related areas of functionality. E.g. `scripts/virtualbox` has all the scripts that interact with Virtual Box. The scripts generate numerous files as part of provisioning a cluster. These generated files are all placed into the `generated` directory in the project root. Most of these are purely transitory, **except:**

| File | Purpose |
| ---- | ------- |
| generated/kickstart/id_ed25519 | This is the private key corresponding to the public key that Desktop Kubernetes adds to the template VM `authorized_keys` file. As long as the template VM is used to provision new Desktop Kubernetes clusters, this private key must be retained for ssh'ing into the cluster VMs. Desktop Kubernetes only generates the SSH keys when a template is created using the `--create-template` arg. |
| generated/kubeconfig/admin.kubeconfig | This is the admin kubeconfig that is generated each time a new cluster is created. You need this kubeconfig to run `kubectl` commands against the cluster. |

## Call structure

All of the scripts except for `dtk` are in the `scripts` directory. All of the scripts are invoked by `dtk`. The tree below shows the scripts as they are called to 1) create a template VM, and then 2) provision a three-node cluster using the template.

See the _Narrative_ section that follows for a description of each numeric annotation:

```shell
dtk
├─ scripts/virtualbox/create-template-vm (1)
│  ├─ scripts/vm/gen-ssh-keyfiles
│  ├─ scripts/os/gen-kickstart-iso
│  ├─ scripts/virtualbox/create-vm
│  └─ scripts/virtualbox/install-guest-additions
│
├─ scripts/cluster/gen-root-ca (2)
│
├─ scripts/cluster/gen-core-k8s (3)
│  ├─ scripts/virtualbox/clone-vm
│  ├─ scripts/cluster/gen-admin-kubeconfig
│  ├─ scripts/worker/configure-worker (4)
│  │  ├─ scripts/os/configure-firewall
│  │  ├─ scripts/worker/kubelet/gen-worker-tls
│  │  ├─ scripts/worker/misc/install-misc-bins
│  │  ├─ scripts/worker/containerd/install-containerd
│  │  └─ scripts/worker/kubelet/install-kubelet
|  └─ scripts/control-plane/configure-controller (5)
│     ├─ scripts/os/configure-firewall
│     ├─ scripts/cluster/gen-cluster-tls
│     ├─ scripts/control-plane/etcd/install-etcd
│     ├─ scripts/control-plane/kube-apiserver/install-kube-apiserver
│     ├─ scripts/control-plane/kube-controller-manager/install-kube-controller-manager
│     └─ scripts/control-plane/kube-scheduler/install-kube-scheduler
│
├─ scripts/vm/configure-etc-hosts (6)
├─ scripts/networking/kube-proxy/install-kube-proxy
├─ scripts/networking/calico/install-calico-networking
├─ scripts/dns/coredns/install-coredns
├─ scripts/monitoring/kube-prometheus/install-kube-prometheus
└─ scripts/storage/openebs/install-openebs
```

## Narrative

1. If the `--create-template` arg is provided then ssh keys are generated, and a template VM is created using Kickstart and a CentOS/Alma/Rocky ISO depending on the `--linux` option. This ssh public key is copied into the VM in the `authorized-keys` file, and Virtual Box Guest Additions is installed. This template VM is cloned in subsequent steps to create the VM(s) that comprise the Kubernetes cluster, so each VM has an identical configuration. Guest Additions is used because it enables getting the IP address of a VirtualBox VM.
2. A root CA is generated for the cluster. This CA is used to sign certs throughout the remainder of the cluster provisioning process.
3. The core Kubernetes cluster is created. This is done by creating one (or three) clones depending on whether `--single-node` was specified. Then, the canonical Kubernetes components are installed on each VM.
4. Each worker gets a unique TLS cert/key for its `kubelet`, a few binaries: `crictl`, `runc`, and `cni plugins`, and of course the `kubelet` and `containerd`.
5. The controller is provisioned with cluster TLS, `etcd`, the `api server`, `controller manager`, and `scheduler`. (This project runs with a single controller to minimize the desktop footprint.)
6. The remainder of the scripts are: Configure `/etc/hosts` on each VM with all the cluster IP addresses. Then, assuming command line arg `--networking=calico`, Kube Proxy and Calico networking are installed. Following that, Core DNS, the Kube Prometheus stack for monitoring, and assuming `--storage=openebs`, the Open EBS storage provisioner is installed to support workloads with persistent volumes and claims.

On completion, you have a functional Kubernetes cluster consisting of three physical VMs, one of which is a controller, and all three of which are workers.
