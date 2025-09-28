# External DNS Integration

In a typical corporate environment, when a Kubernetes cluster is provisioned using IaC for example, DNS is usually configured as part of cluster provisioning.

On the desktop we can't modify DNS to route `abc.com` to the Kubernetes cluster VMs running on your local host. But a simple way to accomplish this is to update `/etc/hosts` with such an entry. But it's tedious to do that by hand whenever a new Ingress resources is deployed. So DTK has the ability to automate updating `/etc/hosts` to add Ingress host names when a new Ingress resource is created in the cluster. Since everything is running right on your desktop, this is a completely reasonable approach, despite being low-tech.

DTK implements this using two components:

1. The [External DNS](https://github.com/kubernetes-sigs/external-dns) add-on.
2. A Python HTTP server included in the project repo that implements the External DNS **webhook provider** interface (and a couple additional methods.) The External DNS Add-On installer will configure the External DNS workload in the cluster to call out to this Python server.

> For details on External DNS's webhook design, see [their documentation](https://kubernetes-sigs.github.io/external-dns/v0.18.0/docs/tutorials/webhook-provider/#exposed-endpoints).


The steps described in this guide assume you are running the Python HTTP server found in the `hostsfile-server` directory of DTK - either as a `systemd` service (which is how I run it) or just from the command line while you're provisioning and running your cluster. Details on this are provided further down in this document.

!!! Important
    Since the External DNS workload running inside the Kubernetes cluster within a VM on your desktop will be making HTTP calls to the Python HTTP server running outside the VM on your desktop you **might** need to configure firewall rules on your desktop to allow that traffic in to your host from the guest(s).

    On my Ubuntu desktop, for example, I use _Gufw_ and I have a global rule to allow traffic into my desktop from the same network. When KVM creates the VMs, it uses DHCP on my home network to assign an IP address in same CIDR block as my desktop. Your environment might differ.

## How it works

The sequence diagram illustrates the design:

```mermaid
sequenceDiagram
    developer->>desktop-kubernetes: 1: Create cluster
    desktop-kubernetes->>hostsfile-server.py: 2: Manage domain 'dtk.io'
    desktop-kubernetes->>kubernetes: 3: Install external-dns with webhook provider
    kubernetes->>external-dns: 4: Create workload
    external-dns->>hostsfile-server.py: 5: Get domains
    hostsfile-server.py->>external-dns: 6: 'dtk.io'
    developer->>kubernetes: 7: Create Ingress with host 'foo.dtk.io'
    external-dns->>kubernetes: 8: Watch Ingress
    external-dns->>external-dns: 9: Read Ingress domain
    external-dns->>hostsfile-server.py: 10: 'foo.dtk.io' was added
    hostsfile-server.py->>/etc/hosts: 11: Update
    developer->>kubernetes: 12: curl https://foo.dtk.io
```

Narrative:

1. When you create a new Kubernetes cluster you enable the `external-dns` Add-On, and you configure External DNS integration using the `dns` section of the `config.yaml`. Example:
   ```
   dns:
     domain: dtk.io
     host-ip: 192.168.0.12
     webhook-port: 5000
   ```
   The yaml entries are:
    1. `domain: dtk.io`: Defines the list of managed domains. Only those domains will be managed in `/etc/hosts` by the Python HTTP server. All other domains will be ignored.
    1. `host-ip: 192.168.0.12`: Your desktop IP address.
    1. `webhook-port: 5000`: The port you're running the Python HTTP server on. The desktop IP address and this port are templated into the External DNS Helm values when it is installed by DTK. That's how External DNS inside the cluster can call the Python HTTP server running on your desktop.
2. DTK sends the specified domain (`dtk.io` in this case) and the IP address of the Kubernetes controller VM to the Python HTTP server. The server stores these.
3. DTK installs `external-dns`, either because you uncommented it in the `addons` list in `config.yaml`, or you explicitly installed it with `./dtk --install-addon external-dns`. As part of this step, your host IP and webhook port are templated into the `external-dns` Helm values.
4. Kubernetes creates the `external-dns` workload.
5. When `external-dns` starts it sees that it is configured to integrate with the `webhook` provider so it calls the webhook (the Python HTTP server) to get a list of managed domains.
6. The Python HTTP server replies with `dtk.io`.
7. You (the developer) create an Ingress with one of the rules specifying host `foo.dtk.io` **and** with an annotation that External DNS understands. (There is an example ingress below showing the annotation.)
8. External DNS watches Ingresses.
9. External DNS reads the host name from the Ingress annotation.
10. External DNS sends the host name to the webhook (the Python HTTP server.)
11. The Python HTTP server updates `/etc/hosts`.
12. You can now curl https://foo.dtk.io (or `http` depending on how you configured the Ingress.)

## Example Ingress

Observe that the annotation below has the same host name as the `host` in the `rules` list:  `foo.dtk.io`:

```
cat <<EOF | kubectl -n default apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    external-dns.alpha.kubernetes.io/target: foo.dtk.io
  name: test
spec:
  ingressClassName: nginx
  rules:
  - host: foo.dtk.io
    http:
      paths:
      - backend:
          service:
            name: test
            port:
              number: 80
        path: /
        pathType: Prefix
EOF
```

## Running the Webook Server by hand

If you don't want to install the webook as a `systemd` service you can just run it while you're running the Kubernetes cluster that is running the External DNS Add-On. The `external-dns` install script initializes the webhook server from the `config.yaml` when it installs the Add-On. So you can run the server manually before installing the Add-On. Run as `sudo` because the process updates `/etc/hosts`:

```
sudo hostsfile-server/hostsfile-server.py
```

## Restarting the Webook Server

If you stop the server, it loses all its state. You can restart it with the configuration that it would normally receive from the `external-dns` Add-On install script. E.g.:

```
sudo hostsfile-server/hostsfile-server.py\
  --cluster-ip=192.168.122.167\
  --port=5000\
  --domains=dtk.io,mydomain.io
```

In the example above, the `192.168.122.167` ip address is the address of the controller node VM. This is the IP address that gets interpolated into `/etc/hosts` whenever a new host name is received by the webhook from External DNS.

## Install script

When you install the `external-dns` Add-On either by enabling it in the `config.yaml` or manually via `--install-addon external-dns` the install script does the following:

1. Reads `dns.host-ip` and `dns.webhook-port` from configuration.
1. Configures the External DNS Helm chart with these values.
1. Reads `dns.domain` from configuration and gets the IP address of the cluster control plane VM.
1. Configures the running webhook server with these values using REST calls.

Therefore you must edit the `config.yaml` before installing the Add-On with values that make sense for your environment.
