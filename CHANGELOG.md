# Change Log

## 28-Sep-2025
Commit: `e1e9771`

1. Implement External DNS Webhook to manage /etc/hosts so Ingresses can accessed by host name.
1. Change `config.yaml` to use an `enabled` flag rather than commenting configuration out
1. Update `.gitignore` - remove sonobuoy (not used any more) and add ability to ignore multiple configs

---
## 27-Sep-2025
Commit: `ba8e110`

1. Added documentation, published via GitHub pages to https://aceeric.github.io/desktop-kubernetes.

---
## 19-Sep-2025
Commit: `84b73db`

1. Kubernetes 1.34.1, etcd v3.6.5, crictl v1.34.0, runc v1.3.1, cni plugins v1.8.0, containerd 2.1.4.

---

## 26-July-2025
Commit: `85b2626`

1. Update check-compatibility script to reflect version that were updated as part of Ubuntu upgrade to 24.04.2 LTS.

---

## 02-July-2025
Commit: `7f6d561f`

1. Update README to reflect current 1.33.1 is formally certified.

---

## 28-June-2025
Commit: `4ddd2e63`

1. Corrected an omission in the prior commit: Re-add ` annotations-risk-level: Critical` to Nginx so it will accept the Kubernetes Dashboard bearer token as a snippet.

---

## 25-June-2025
Commit: `132e3f62` to `12c78912` (inclusive)

1. Kubernetes Dashboard: Expose via Ingress. Pass static admin token in auth header to bypass login. Note - The ingress needs a host so I went with host `dtk.io` which unfortunately at present requires hand-editing `/etc/hosts`. (I don't have a DNS solution yet to make newly provisioned clusters DNS-addressable.)
2. Ingress-Nginx: Allow snippet annotations by default.
3. Cert-Manager: Create a `ClusterIssuer`.

---

## 22-June-2025
Commit: `cceb1762`

1. Alma to 9.6

---

## 03-June-2025
Tag: `v1.33.1`

1. Kubernetes 1.33.1 passes conformance using Hydrophone v0.7.0

---

## 26-May-2025
Commit: `87afc243`

1. Addons: Calico 3.30.0

---

## 26-May-2025
Commit: `c538b600`

1. Addons: Cilium 1.17.4

---

## 25-May-2025
Commit: `04428cee`

1. Addons: coredns 1.42.1, ingress-nginx 4.12.2, kube-prometheus-stack 72.6.2, kubernetes-dashboard 7.12.0, metrics-server 3.12.2, openebs 4.2.0

---

## 25-May-2025
Commit: `a1699e16`

1. Kubernetes v1.33.1, runc v1.3.0, etcd v3.6.0, crictl v1.33.0, containerd 2.1.1, cni plugins v1.7.1

---

## 24-May-2025
Commit: `e7faa4e4`

1. Renamed `master` branch to `main`
2. Support both Alma 8.10 and Alma 9.5
3. Configure Alma 9.5 as the default
