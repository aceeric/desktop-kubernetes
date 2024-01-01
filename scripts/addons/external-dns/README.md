# External DNS

This is a toy. This directory contains a simple Flask app that runs a webhook for External DNS to talk to. The way External DNS recommends to implement a webhook is as a sidecar - but this approach instead just runs the webhook on the desktop and has External DNS talk to it from inside the cluster.

When you create an Ingress, External DNS will call the webook, and the webhook will add the Ingress host into the `/etc/hosts` file on your desktop. Then you can access the hostname as though it had been provisioned by an actual DNS server. (So basically this just saves hand-editing `/etc/hosts`.) Here's how you use it with Desktop Kubernetes:

1. Make sure ingress-nginx is installed in the cluster.
1. Pip install Flask.
1. Get your desktop IP address and put it into the `values.yaml` in the `--webhook-provider-url` arg. (Leave the port as `5000`.)
1. Run the webhook: `sudo -E ./webhook --ip-address 192.168.56.200` in a separate terminal window. The `--ip-address` is the address of any Desktop Kubernetes node running the ingress controller.
1. Install External DNS: `./dtk --install-addon external-dns`.
1. Create a Deployment running Nginx, a Service, and an Ingress. Annotate the Ingress with `external-dns.alpha.kubernetes.io/target: <hostname>` matching the host name of the Ingress. (You have to do this becuase of how External DNS parses the Ingress resource to determine whether to send the webbook new hosts. See the example below.)
1. External DNS will call the webhook which will append the host name from the Ingress annotation to `/etc/hosts` on your desktop, with the IP address of your cluster VM.
1. Then you can curl that host or access it from your browser.

## Example Ingress

Observe that the annotation below has the same hostname as the `host` in the `rules` list - `frobozz.dtk.io`:

```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  annotations:
    external-dns.alpha.kubernetes.io/target: frobozz.dtk.io
  name: test
spec:
  ingressClassName: nginx
  rules:
  - host: frobozz.dtk.io
    http:
      paths:
      - backend:
          service:
            name: test
            port:
              number: 80
        path: /
        pathType: Prefix
```

Once Nginx configures the Ingress and External DNS calls the webhook you can observe that the host has been added to your `/etc/hosts` file. When you're done with the cluster, just CTRL-C the webhook script. (You have to clean up `/etc/hosts` yourself.)

Result in `/etc/hosts`:
```
...
192.168.56.200 frobozz.dtk.io
```

Curl the endpoint: `curl http://frobozz.dtk.io`. Observe the Nginx response:
```
...
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>
...
```