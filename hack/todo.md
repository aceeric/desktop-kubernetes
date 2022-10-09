# TODO list

## In Progress

- Test kube-prometheus tweaks are benign if containerized

## Next

- Remove all download/filesys refs and source `artifacts` to reduce number of script args
- Don't install kernel-devel in ks.cfg because we just uninstall it in desktop-kubernetes.sh
- K8s production-grade containerd runtimes systemd cgroup driver:
    https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/configure-cgroup-driver/
- Network service vs. NetworkManager service - clarify

## Done
- Separate dashboard install - always install Kubernetes dash
- Support containerized control plane