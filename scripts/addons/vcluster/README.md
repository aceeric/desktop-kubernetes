# After installing

So far, I cannot get this working in Nginx using instructions here: https://www.vcluster.com/docs/using-vclusters/access without also creating a hostname in `/etc/hosts` and using that host name in the ingress. (In other words a host-less rule does not work in the ingress and I don't know why.)

So this example uses `NodePort` for now based on the same link above jsut a little further down the page.

As a result, this is a little more complicated than the `Ingress` approach but doesn't require dealing with `/etc/hosts`. The key thing to understand is that vcluster stores the kube config for the virtual cluster in a secret in the vcluster namespace. If you look through the [vclusterctl](https://github.com/loft-sh/vcluster/tree/main/cmd/vclusterctl) code you will see that when their documentation says to do this:
```
vcluster connect my-vcluster -n my-vcluster --update-current=false --server=https://x.x.x.x
```

...all it does is go get the kubeconfig from the secret, and replace the `server` value with what you specify as the `--server=` on the command line. This is what is accomplished by this snippet. (This snippet requires `yq`):

## Get the NodePort service port num
```
port=$(kubectl -n vcluster get svc vcluster-nodeport -oyaml -ojsonpath='{.spec.ports[0].nodePort}')
```

## Get the secret that has the kubeconfig
```
kubectl -n vcluster get secret vc-vcluster -oyaml >| ./vc-kubeconfig.yaml
```

## Get the kubeconfig from the secret
```
kcfg=$(yq '.data.config' vc-kubeconfig.yaml)
```

## Base 64 decode the kubeconfig to the file system
```
echo $kcfg | base64 -d >| ./vc-kubeconfig.yaml
```

## Get the IP address of the k8s controller
```
controller_ip=$(kubectl get nodes -l node-role.kubernetes.io/controller=\
  -o jsonpath={.items[*].status.addresses[?\(@.type==\"InternalIP\"\)].address})
```

## Patch in the Controller IP and NodePort port num
```
yq -i '.clusters[0].cluster.server = "https://'$controller_ip:$port'"' ./vc-kubeconfig.yaml
```

## Select the vcluster kubeconfig
```
export KUBECONFIG=./vc-kubeconfig.yaml
```

## Then
```
kubectl get nodes -owide
```

## Output
```
NAME   STATUS   ROLES    AGE   VERSION        INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                KERNEL-VERSION      CONTAINER-RUNTIME
vm1    Ready    <none>   22h   v1.29.1+k3s2   10.32.0.34    <none>        Fake Kubernetes Image   4.19.76-fakelinux   docker://19.3.12
```
