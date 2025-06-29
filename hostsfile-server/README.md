# External DNS Integration

The main goal of _Desktop Kubernetes_ (DTK) is to enable multi-VM Kubernetes development on a single machine so that at home (for example) the development and troubleshooting experience is very close to what it's like at work. In this environment, there is a need for Ingresses that specify host names to be name-resolvable (e.g. by `nslookup`.)

The easiest way to do this is by updating `/etc/hosts`. But - that's tedious to do by hand all the time whenever a new Ingress resources is deployed. So the project has the ability to automate updating `/etc/hosts` when new Ingress resources are created in the cluster. Since everything is running right on your desktop, this is a completely reasonable approach, despite being low-tech.

The project supports this feature using two components:

1. The [External DNS](https://github.com/kubernetes-sigs/external-dns) add-on.
2. A Python HTTP server included in this directory that implements the External DNS webhook provider interface (and a couple additional methods.)

> For details on External DNS's webhook design, have a look at [their documentation](https://kubernetes-sigs.github.io/external-dns/v0.18.0/docs/tutorials/webhook-provider/#exposed-endpoints).

## Important

The steps described here assume you are running the Python HTTP server found in this directory either as a systemd service (which is how I run it) or just from the command line while you're provisioning and running your cluster. Since the External DNS workload running inside the Kubernetes cluster within a VM on your desktop will be making HTTP calls to the Python HTTP server running outside the VM on your desktop you **might** need to configure firewall rules on your desktop to allow that traffic in to your host from the guest(s).

On my Ubuntu desktop, for example, I use Gufw and I have a global rule to allow traffic into my desktop from the same network. When KVM creates the VMs, it uses DHCP on my home network to assign an IP address in same CIDR block as my desktop. Your environment might differ.

## How it works

The sequence diagram illustrates the design:

```mermaid
sequenceDiagram
    developer->>desktop-kubernetes: 1: Create cluster
    desktop-kubernetes->>hostsfile-server.py: 2: Manage domain 'dtk.io'
    desktop-kubernetes->>kubernetes: 3: Install external-dns with webhook provider
    kubernetes->>external-dns: 4: Install
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

1. When you create a new Kubernetes cluster you specify External DNS integration using the `dns` section of the `config.yaml`. Example:
   ```
   dns:
     enabled: true
     domain: dtk.io
     host-ip: 192.168.0.12
     webhook-port: 5000
   ```
   The yaml entries are: `enabled: true` turns the feature on. (It is off by default.) The `domain: dtk.io` entry tells the DTK scripts to send that domain to the Python HTTP server which will add it to the server's internal list of managed domains. The `host-ip: 192.168.0.12` entry is your desktop IP address. The `webhook-port: 5000` is the port you're running the Python HTTP server on. Both the IP address and port are templated into the External DNS Helm values when it is installed by DTK. That's how External DNS inside the cluster can call the Python HTTP server running on your desktop.
2. DTK sends the specified domain (`dtk.io` in this case) to the Python HTTP server. The server stores it.
3. DTK installs `external-dns`, either because you uncommented it in the `addons` list in `config.yaml`, or you explicitly installed it with `./dtk --install-addon external-dns`. As part of this step, your host IP and webhook port are templated into the `external-dns` Helm values.
4. Kubernetes creates the `external-dns` workload.
5. When `external-dns` starts it sees that it is configured to integrate with the `webhook` provider so it calls the webhook (the Python HTTP server) to get a list of managed domains.
6. The Python HTTP server replies with `dtk.io`.
7. You (the developer) create an Ingress with one of the rules specifying host `foo.dtk.io` **and** with an annotation that External DNS understands. (There is an example ingress below.)
8. External DNS is watching Ingresses.
9. External DNS reads the host name from the Ingress annotation.
10. External DNS sends the host name as a CNAME record to the webhook (the Python HTTP server.)
11. The Python HTTP server updates `/etc/hosts`
12. You can now curl https://foo.dtk.io (or `http` depending on how you configured the Ingress)

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

## Running the server by hand

hostsfile-server/hostsfile-server.py\
  --cluster-ip=192.168.122.167\
  --port=5000\
  --domains=dtk.io

## Install script

sets the domain from config..
