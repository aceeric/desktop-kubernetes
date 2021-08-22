## remove kube-prometheus as part of repetitive re-install testing

```shell
kubectl api-resources -oname --api-group monitoring.coreos.com | xargs -r kubectl delete crd &
kubectl delete clusterrole prometheus-adapter &
kubectl delete clusterrole system:aggregated-metrics-reader &
kubectl delete clusterrolebinding prometheus-adapter &
kubectl delete clusterrolebinding resource-metrics:system:auth-delegator &
kubectl delete clusterrole resource-metrics-server-resources &
kubectl delete clusterrole prometheus-k8s &
kubectl delete clusterrolebinding prometheus-k8s &
kubectl delete clusterrole prometheus-operator &
kubectl delete clusterrolebinding prometheus-operator &
kubectl delete clusterroles blackbox-exporter &
kubectl delete clusterrolebinding blackbox-exporter &
kubectl delete clusterroles kube-state-metrics &
kubectl delete clusterrolebinding kube-state-metrics &
kubectl delete clusterrole node-exporter &
kubectl delete clusterrolebinding node-exporter &
kubectl get rolebinding -A | grep  resource-metrics-auth-reader | awk '{print $1" "$2}' | xargs -l bash -c 'kubectl -n $0 delete rolebinding $1' &
kubectl get role -A | grep  prometheus-k8s | awk '{print $1" "$2}' | xargs -l bash -c 'kubectl -n $0 delete role $1' &
kubectl delete namespace monitoring &
```