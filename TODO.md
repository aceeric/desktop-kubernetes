# TODO list

## In Progress

- Support containerized control plane
  - Don't tweak kube-prometheus if containerized

## Next

- Once containerized CP done, remove all download/filesys refs and source `artifacts`
- Don't install kernel-devel in ks.cfg because we just uninstall it in desktop-kubernetes.sh
- K8s production-grade containerd runtimes systemd cgroup driver:
    https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/configure-cgroup-driver/
- Network service vs. NetworkManager service - confused

## Done
- Separate dashboard install - always install Kubernetes dash

## Background
