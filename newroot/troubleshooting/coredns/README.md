
https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution

```shell
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: dnsutils
  namespace: default
spec:
  containers:
    - name: dnsutils
      image: gcr.io/kubernetes-e2e-test-images/dnsutils:1.3
      command:
        - sleep
        - "60000"
      imagePullPolicy: IfNotPresent
  restartPolicy: Always
EOF
```

kubectl exec -i -t dnsutils -- nslookup kubernetes.default
kubectl exec -ti dnsutils -- cat /etc/resolv.confn
kubectl exec -i -t dnsutils -- nslookup kubernetes.default
kubectl get pods --namespace=kube-system -l k8s-app=kube-dns
kubectl get svc --namespace=kube-system
kubectl get endpoints kube-dns --namespace=kube-system
