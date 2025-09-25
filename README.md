# Desktop Kubernetes

<img src="resources/desktop-kubernetes-no-text.jpg" width="150"/>

_Desktop Kubernetes_ is a Linux Bash CLI that provisions a Kubernetes cluster right on your desktop using KVM or VirtualBox - with each cluster node consisting of a guest VM running any of: Alma, CentOS, or Rocky Linux. The goal is to create a local development and testing environment that is 100% compatible with a production-grade Kubernetes environment.

_Desktop Kubernetes_ is the _57 Chevy_ of Kubernetes distros: you can take it apart and put it back together with just a few Linux console tools: `bash`, `curl`, `ssh`, `scp`, `tar`, `openssl`, `helm`, `yq`, kvm tools (`virsh`, `virt-install`, `qemu-img`), and `kubectl`. That being said, **v1.33.1** of this distribution is Kubernetes Certified. See: [CNCF Landscape](https://landscape.cncf.io/?group=certified-partners-and-providers&view-mode=grid&item=platform--certified-kubernetes-distribution--desktop-kubernetes).

[<img src="https://www.cncf.io/wp-content/uploads/2020/07/certified_kubernetes_color-1.png" width="90"/>](https://github.com/cncf/k8s-conformance/tree/master/v1.33/desktop-kubernetes)

This project started as a way to automate the steps in **Kelsey Hightower's** [Kubernetes The Hard Way](https://github.com/kelseyhightower/kubernetes-the-hard-way) - just to see if I could. But at this point I pretty much rely on it for all my local Kubernetes development. I use it on a couple of different Ubuntu 24.04.X systems with 64 gigs of RAM and 6+ hyper-threaded processors.

## Quick Start

The `dtk` script in the repo root is the _Desktop Kubernetes_ CLI.

The first time, run with just the `--check-compatibility` option to check the installed versions of the tools used by _Desktop Kubernetes_ (curl, etc.) against the tested versions. E.g.:

```
./dtk --check-compatibility
```

There will likely be differences and you have to decide whether the differences are material. Slight version differences may not matter, but for sure you need all the listed tools. In keeping with the project philosophy of not modifying your desktop - you need to install the tools listed in order to use this project. **_Desktop Kubernetes_ will not alter your desktop.**

> See the full documentation (link below) to know which tools are specific to KVM vs VirtualBox.

The `dtk` script in the repo root is what you run. If you supply no arguments, the script will configure the cluster based on the `config.yaml` file in the repo root resulting in a three node Alma Linux cluster consisting of one controller and two workers.

Once the cluster comes up, the script will display a message telling you how to set your `KUBECONFIG` environment variable in order to access the cluster. It will also display a message showing how to SSH into each node. (There's also a helper script `sshto` that you can use for that.)

## Full Documentation

Please see [https://aceeric.github.io/desktop-kubernetes](https://aceeric.github.io/desktop-kubernetes) for the full documentation.
