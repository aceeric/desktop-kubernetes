# Design

This project might seem like a lot of bash code but it's actually pretty simple. There are about 30-odd primary shell scripts, and a number of *helper* scripts. This README focuses on the *primary* scripts.

## Directory structure

The script directory structure is organized around related areas of functionality. The scripts generate numerous files as part of provisioning a cluster. These generated files are all placed into the `generated` directory in the project root. Most of these are purely transitory, **except:**

| File | Purpose |
| ---- | ------- |
| generated/kickstart/id_ed25519 | This is the private key corresponding to the public key that Desktop Kubernetes adds to the template VM `authorized_keys` file. As long as the template VM is used to provision new Desktop Kubernetes clusters, this private key must be retained for ssh'ing into the cluster VMs. Desktop Kubernetes only generates the SSH keys when a template is created - and only if the keypair does not already exist. |
| generated/kubeconfig/admin.kubeconfig | This is the admin kubeconfig. It is regenerated for each new cluster you provision. You need this kubeconfig to run `kubectl` commands against the cluster. |

## Call structure

All of the scripts in the call tree except for `dtk` and `artifacts` are in the `scripts` directory. All of the scripts are invoked by `dtk`. The tree below shows the scripts as they are called to create a template VM, and then provision a cluster using the template. See the _Narrative_ section that follows for a description of each numeric annotation:

```
dtk
├─ source artifacts (1)
│
├─ scripts/helpers/download-objects (2)
│  └─ scripts/helpers/download-obj
│
├─ scripts/kvm/provision-vms (3) (if kvm)
│  ├─ scripts/kvm/create-template-vm
│  │  └─ scripts/vm/gen-ssh-keyfiles
│  ├─ scripts/kvm/clone-vm
│  └─ scripts/vm/configure-etc-hosts
│
├─ scripts/virtualbox/provision-vms (3) (if vbox)
│  ├─ scripts/virtualbox/create-template-vm
│  │  ├─ scripts/vm/gen-ssh-keyfiles
│  │  ├─ scripts/os/gen-kickstart-iso
│  │  ├─ scripts/virtualbox/create-vm
│  │  └─ scripts/virtualbox/install-guest-additions
│  ├─ scripts/virtualbox/clone-vm
│  │  └─ scripts/virtualbox/configure-hostonly-networking
│  │     └─ scripts/virtualbox/gen-hostonly-ifcfg-iso
│  └─ scripts/vm/configure-etc-hosts
│
├─ scripts/cluster/gen-root-ca (4)
│
├─ scripts/cluster/gen-core-k8s (5)
│  ├─ scripts/worker/configure-worker (5a)
│  │  ├─ scripts/os/configure-firewall
│  │  ├─ scripts/worker/misc/install-misc-bins
│  │  ├─ scripts/worker/containerd/install-containerd
│  │  ├─ scripts/worker/kubelet/install-kubelet
│  │  └─ scripts/networking/kube-proxy/install-kube-proxy
│  └─ scripts/control-plane/configure-controller (5b)
│     ├─ scripts/os/configure-firewall
│     ├─ scripts/cluster/gen-kubernetes-certs
│     ├─ scripts/control-plane/etcd/install-etcd
│     ├─ scripts/control-plane/kube-apiserver/install-kube-apiserver
│     ├─ scripts/control-plane/kube-controller-manager/install-kube-controller-manager
│     └─ scripts/control-plane/kube-scheduler/install-kube-scheduler
|
└─ scripts/addons/install-addons (6)
```

## Narrative

1. The `artifacts` file is sourced, which defines all the upstream URLs and local filesystem locations for the core objects needed to provision the cluster.
2. All the binaries, ISOs, manifests, and tarballs needed to provision the core cluster are downloaded into the `binaries` directory based on configuration options. E.g. if config specifies `linux: rocky` then `Rocky-X.X-x86_64-dvd.iso` (X.X based on whatever is hard-coded in the `artifacts` file.)
3. All the VMs are created:
    - If config specifies `create-template: true` then ssh keys are generated, and a template VM is created using Kickstart and a CentOS / Alma / Rocky ISO depending on the `linux` selection. The ssh public key is copied into the VM in the `authorized-keys` file.
    - The template VM (the one created in the prior step, or one that was already there identified by the `template-vmname` config) is cloned to create the VM(s) that comprise the Kubernetes cluster, so each VM has an identical configuration.
4. A root CA is generated for the cluster if one does not already exist. This CA is used to sign cluster certs throughout the remainder of the cluster provisioning process.
5. The core Kubernetes cluster is created by installing the canonical Kubernetes components on each VM:
    - 5a: Each worker gets a unique TLS cert/key for its `kubelet`, a few binaries: `crictl`, `runc`, and `cni plugins`, and of course the `kubelet` and `containerd`.
    - 5b: The controller is provisioned with cluster TLS, `etcd`, the `api server`, `controller manager`, and `scheduler`. This project runs with a single controller to minimize the desktop footprint.
6. The `install-addons` script is called. It walks its own directory and for each subdirectory that matches an entry in the `addons` section of the `config.yaml`, it looks for and invokes an `install` script in that directory to install the add-on.

On completion, you have a functional Kubernetes cluster consisting of one or one or more physical VMs, the first of which is always a controller, and the remainder of which are workers.
