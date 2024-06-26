# Kubernetes Dashboard

To access the UI, use the provided NodePort service. E.g., say your cluster is like this:

```
NAME       STATUS  ROLES              AGE  VERSION  INTERNAL-IP     etc.
host-one   Ready   controller,worker  70m  v1.28.1  192.168.56.200  etc.
```
Then, in your browser: https://192.168.56.200:30443

Create a token:

```
k -n kubernetes-dashboard create token kubernetes-dashboard
```
