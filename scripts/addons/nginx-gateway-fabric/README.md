# Nginx Gateway Fabric

This addon installs Nginx Gateway Fabric (NGF) and configures one `Gateway` resource called `dtk-gateway` for all cluster workloads. This causes NGF to create a proxy pod on the control plane that listens on **host port 80**. This means that in order to access your workloads, you go through the control plane node.

> It is possible to configure NGF to create gateway proxies as `DaemonSets` which enables network traffic on all cluster nodes. This add-on elected to create the proxies as `Deployments` bound to the control plane since that's a lighter weight approach and doesn't impact the ability to access workloads running on other nodes.

## Details

After installing this add-on, you can test it by deploying the example. To set the stage, say you are testing in a four-node cluster, so `kubectl get node -owide` shows the following output:

```shell
NAME      STATUS  ROLES              VERSION  INTERNAL-IP
atlas     Ready   worker             v1.35.0  192.168.122.107
hyperion  Ready   worker             v1.35.0  192.168.122.20
kronos    Ready   controller,worker  v1.35.0  192.168.122.24
perses    Ready   worker             v1.35.0  192.168.122.231
```

Observe that `kronos` is the control plane node.

## Verifying the add-on

After installing the add-on then `kubectl -n nginx-gateway get po -owide` should show:

```shell
NAME                                  READY  STATUS   RESTARTS  AGE    IP            NODE
dtk-gateway-nginx-76bf8f7d87-qsfbp    1/1    Running  0         7m47s  10.200.0.185  kronos
nginx-gateway-fabric-d494f6498-c7npx  1/1    Running  0         7m48s  10.200.0.106  kronos
```

The `nginx-gateway-fabric-d494f6498-c7npx` pod is the Nginx control plane, and the `dtk-gateway-nginx-76bf8f7d87-qsfbp` is the gateway proxy pod that is bound to port 80. Nginx creates the gateway pod (i.e. _proxy_) with affinity to the control plane node because of the addon value in `nginx.pod.nodeSelector` in `values.yaml`.

## Create the example workload

The example workload runs a simple Python server, and creates an `HTTPRoute` to receive traffic from the gateway. The Python server prints `hello, world` when accessed on path `/gw-test`:

```shell
kubectl apply -f scripts/addons/nginx-gateway-fabric/example.yaml
```

Observe the pods using `kubectl -n gw-test get po -owide`:

```shell
NAME                     READY   STATUS    RESTARTS   AGE   IP             NODE
gw-test-c69b4b49-d9h5m   1/1     Running   0          9s    10.200.2.191   hyperion
```

The `gw-test-c69b4b49-d9h5m` pod is the Python server. Assume `/etc/hosts` has an entry for the control plane node on `192.168.122.24`:

```
192.168.122.24 dtk.io
```

Then `curl dtk.io/gw-test` responds with:

```shell
hello, world
```

Observe the Python server logs using `kubectl -n gw-test logs gw-test-c69b4b49-d9h5m`:
```shell
Starting gw-test server on port 8080...
10.200.0.185 - "GET /gw-test HTTP/1.1" 200 -
```

## How it works

When you create a `Gateway` as this add-on installer does, NGF creates a proxy pod on the control plane that listens on port 80. Then the `HTTPRoute` resources configure the  gateway proxy to forward packets to the workload service referenced by the `HTTPRoute`. You can inspect these components as follows:

First, ssh into the `kronos` node.

### Find the process listening on host port 80

Since the proxy will running as a pod you won't be able to see the listening process using a simple `netstat` command. The pod will be running in a Linux namespace so search all the container namespaces to find it:

```shell
(
  echo "NETID STATUS RECV-Q SEND-Q LOCAL-ADDR:PORT PEER-ADDR:PORT PROCESS"
  ip netns list | awk '{print $1}' |\
    xargs -I% ip netns exec % ss -tulpn | grep '0\.0\.0\.0:80\b'
) | column -t
```

You should see something like:
```shell
NETID  STATUS  RECV-Q  SEND-Q  LOCAL-ADDR:PORT  PEER-ADDR:PORT  PROCESS
tcp    LISTEN  0       511     0.0.0.0:80       0.0.0.0:*       users:(("nginx",pid=44696,fd=13),("nginx",pid=44695,fd=13),("nginx",pid=44476,fd=13))
```

There are multuple `nginx` process IDs because each sub-process within the pod is listed. Take the right-most (highest level) Nginx pid, which is `44476` in the example, and find it's ultimate parent:

```shell
cat <<'EOF' | bash -s
ppid=0
pid=44476
while true; do
  ppid=$(ps -o ppid= -p $pid | tr -d  '[[:space:]]')
  if [[ $ppid -eq 1 ]]; then
    echo "PID=$pid"
    break
  else
    pid=$ppid
  fi
done
EOF
```

Example output:

```shell
PID=44368
```

Now print the process tree for `44368` using the `pstree` command: `pstree -aTp 44368`. Output:

```shell
containerd-shim,44368 -namespace k8s.io -id 4a15ddeaca0865e6e4751d432e1b167515408ef55e54cbc04e99bae3ee2980f1 -address /run/containerd/containerd.sock
  ├─entrypoint.sh,44463 /agent/entrypoint.sh
  │   ├─nginx,44476
  │   │   ├─nginx,44695
  │   │   └─nginx,44696
  │   └─nginx-agent,44480
  └─pause,44391
```

You can see the containerd shim running pod ID `4a15ddea`. Examine the pod using the `crictl ps --pod 4a15ddea` command. Output:

```shell
CONTAINER      IMAGE          CREATED         STATE    NAME   ATTEMPT  POD ID         POD                                  NAMESPACE
48cf4b7c49ae2  697846c37ce04  20 minutes ago  Running  nginx  0        4a15ddeaca086  dtk-gateway-nginx-76bf8f7d87-qsfbp   nginx-gateway
```

This pod - `dtk-gateway-nginx-76bf8f7d87-qsfbp` in the gateway proxy. You can inspect its logs with `k -n gw-test logs dtk-gateway-nginx-76bf8f7d87-qsfbp`.

So by following these steps, you've proved that the gateway proxy pod is bound to host port 80.
