# Kubernetes Dashboard

To access the UI, youy have two options:

## Ingress

The add-on creates a path-based ingress with hostname `dtk.io` and path `/dashboard`. So: https://dtk.io/dashboard. This requires you to hand-edit your `/etc/hosts` file and add one or all the VM IPs. (I don't have a good DNS solution at this time to auto-configure DNS for new clusters.) Example `/etc/hosts`:

```
...
192.168.122.24  dtk.io
...
```

The ingress is configured to pass an auth header with a bearer token consisting of a static token that is configured into the kube-apiserver so you don't have to log in to the dashboard if accessed via the ingress.

## NodePort service

Say your cluster is like this:

```
NAME  STATUS  ROLES              AGE  VERSION  INTERNAL-IP     etc.
vm1   Ready   controller,worker  70m  v1.33.1  192.168.122.24  etc.
```
Then, in your browser: https://192.168.122.24:30443

Create a token:

```
k -n kubernetes-dashboard create token kubernetes-dashboard-kong
```

Copy/paste the token into the UI.
