### NodePort test

A simple test to verify that a pod can be accessed from outside the cluster using a NodePort service.

This project uses VirtualBox bridged networking. So all the VMs are accessible by IP directly from the desktop without requiring any ingress infrastructure.

This test simply proves that each node proxies traffic through a NodePort service to the pod selected by the service.

Based on: https://kubernetes.io/docs/tutorials/stateless-application/expose-external-ip-address/

```shell
$ kubectl create ns nodeport-test

$ cat <<EOF | kubectl -n nodeport-test apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app.kubernetes.io/name: load-balancer-example
  name: hello-world
spec:
  replicas: 3
  selector:
    matchLabels:
      app.kubernetes.io/name: load-balancer-example
  template:
    metadata:
      labels:
        app.kubernetes.io/name: load-balancer-example
    spec:
      containers:
      - image: gcr.io/google-samples/node-hello:1.0
        name: hello-world
        ports:
        - containerPort: 8080
EOF

$ kubectl -n nodeport-test expose deployment hello-world\
  --type=LoadBalancer --name=my-service

$ kubectl -n nodeport-test get svc/my-service -oyaml
apiVersion: v1
kind: Service
metadata:
  labels:
    app.kubernetes.io/name: load-balancer-example
  name: my-service
  namespace: nodeport-test
spec:
  clusterIP: 10.32.0.103
  clusterIPs:
  - 10.32.0.103
  externalTrafficPolicy: Cluster
  ports:
  - nodePort: 31960
    port: 8080
    protocol: TCP
    targetPort: 8080
  selector:
    app.kubernetes.io/name: load-balancer-example
  sessionAffinity: None
  type: LoadBalancer

$ kubectl get po -lapp.kubernetes.io/name=load-balancer-example --all-namespaces -owide
NAME                           READY   STATUS    RESTARTS   AGE   IP             NODE
hello-world-6df5659cb7-8nbwh   1/1     Running   0          10m   11.200.2.214   monk
hello-world-6df5659cb7-b4b6x   1/1     Running   0          10m   11.200.1.144   ham
hello-world-6df5659cb7-g8vrn   1/1     Running   0          10m   11.200.0.156   doc

$ for vm in doc ham monk; do\
  ip=$(scripts/get-vm-ip $vm);\
  port=$(kubectl -n nodeport-test get svc my-service\
         -ojsonpath='{.spec.ports[0].nodePort}');\
  echo accessing the service on VM $vm;\
  curl http://$ip:$port;\
  echo;\
done

accessing the service on VM doc
Hello Kubernetes!
accessing the service on VM ham
Hello Kubernetes!
accessing the service on VM monk
Hello Kubernetes!
```


