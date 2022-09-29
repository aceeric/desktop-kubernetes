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

https://computingforgeeks.com/manually-pull-container-images-used-by-kubernetes-kubeadm/
[config/images] Pulled k8s.gcr.io/kube-apiserver:v1.25.0
[config/images] Pulled k8s.gcr.io/kube-controller-manager:v1.25.0
[config/images] Pulled k8s.gcr.io/kube-scheduler:v1.25.0
[config/images] Pulled k8s.gcr.io/kube-proxy:v1.25.0
[config/images] Pulled k8s.gcr.io/etcd:v3.5.4
