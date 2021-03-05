
## Cilium

The two yamls in this directory are from:

1. https://raw.githubusercontent.com/cilium/cilium/1.9.4/install/kubernetes/quick-install.yaml
2. https://raw.githubusercontent.com/cilium/cilium/1.9.4/install/kubernetes/quick-hubble-install.yaml

It is possible to run Cilium *without* kube-proxy. See: https://docs.cilium.io/en/v1.9/gettingstarted/kubeproxy-free/

In order to run Cilium without kube-proxy (which I was interested in trying) it requires the quick-install manifest to be patched in such a way as to require `kustomize`. (It can't reasonably be done with `sed`.)

I didn't want to introduce `kustomize` as a requirement just for this, so I elected to place the Cilium manifests into this install directory as static files and incorporate the necessary edits by hand.

This makes the Cilium install a little different from others because the manifests aren't downloaded like so many others.

The modifications to the manifests are noted by *ESACE* in the YAMLs.

TODO: Review: https://docs.cilium.io/en/v1.9/gettingstarted/kubeproxy-free/