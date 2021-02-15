
https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution

```shell
kubectl create ns dnstest

cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: dnsutils
  namespace: dnstest
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

Then:
```shell
kubectl -n dnstest exec -it dnsutils -- nslookup kubernetes.default
kubectl -n dnstest exec -ti dnsutils -- cat /etc/resolv.conf
kubectl -n dnstest exec -it dnsutils -- nslookup kubernetes.default
kubectl get pods --namespace=kube-system -l k8s-app=kube-dns
kubectl get svc --namespace=kube-system
kubectl get endpoints kube-dns --namespace=kube-system
```

Also, per:
https://kubernetes.io/docs/tasks/administer-cluster/dns-debugging-resolution/

```shell
kubectl apply -f https://k8s.io/examples/admin/dns/dnsutils.yaml
kubectl get po -A

NAMESPACE  NAME      READY   STATUS    RESTARTS   AGE
default    dnsutils  1/1     Running   0          2m6s

kubectl exec -it dnsutils -- nslookup kubernetes.default
Server:		10.32.0.10
Address:	10.32.0.10#53

Name:	kubernetes.default.svc.cluster.local
Address: 10.32.0.1

```