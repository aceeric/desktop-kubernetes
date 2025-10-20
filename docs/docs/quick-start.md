# Quick Start

Run the `dtk` script in the repo root. If you supply no arguments, the script will use KVM to provision and configure a cluster based on the `config.yaml` file in the project root resulting in a three node Alma Linux cluster consisting of one controller and two workers. See the [Configuration](configuration.md) section for details.

I recommend you run first with just the `check-tools` command to check the versions of the CLIs used by the scripts (curl, etc.) against the tested versions. E.g.:

```
./dtk check-tools
```

The tools / components checked by the script are:

| Component | Purpose | Only for Virtual Box? | Only for KVM? |
|-|-|:-:|:-:|
| `openssl` | SSL Connectivity to guests. | - | - |
| `openssh` |  SSL Connectivity to guests. | - | - |
| `genisoimage` | Builds an ISO to configure VirtualBox. | Yes | - |
| Virtual Box (vboxmanage) | Provisions VirtualBox VMs. | Yes | - |
| Host operating system | I run Ubuntu but there's really nothing specific to any given Linux as long as Bash is available. |  - | - |
| `kubectl` | Connect to the provisioned cluster to run clustr commands. | - | - |
| `curl` | Download binaries. | - | - |
| `helm` | Install Add-Ons (e.g.: CoreDNS.) | - | - |
| `yq` | Parse the configuration yaml file. | - | - |
| `virt-install` | Provision KVM VMs. | - | Yes |
| `virsh` |  Provision KVM VMs. | - | Yes |
| `qemu-img` |  Provision KVM VMs. | - | Yes |


You may need to install tools and there will likely be differences between the versions tested by the project, and what you've installed. You have to decide whether the differences are material. Slight version differences may not matter, but for sure you need all the listed tools. In keeping with the project philosophy of not modifying your desktop - **you** must install the tools listed in order to use this project - the project seeks to not alter your desktop OS.

Once the cluster comes up, the script will display a message telling you how to set your `KUBECONFIG` environment variable in order to access the cluster. It will also display a message showing how to SSH into each node. (There's also a helper script `sshto` that you can use for that.)
