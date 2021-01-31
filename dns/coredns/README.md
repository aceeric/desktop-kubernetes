## CoreDNS

CoreDNS for this project was obtained by `curl`ing the following upstreams into the `binaries` directory:

1. https://github.com/coredns/deployment/raw/coredns-1.14.0/kubernetes/deploy.sh
2. https://github.com/coredns/deployment/raw/coredns-1.14.0/kubernetes/coredns.yaml.sed

Then:

```shell
source binaries/deploy.sh -i 10.32.0.10 -s > coredns.yaml
```

The `deploy.sh` script looks for `coredns.yaml.sed` in it's execution directory and emanates the yaml to the console.

Then I made mods that aligned with other sources (e.g. Hightower) etc. My original attempt was to generate it on the fly directly from original sources to make the traceability clear, but that just proved to be a lot of `sed` scripting for limited value. So if you want to change the CoreDNS configuration, just edit the yaml in this directory. If you want a different version, grab it and make whatever tweaks you need.
