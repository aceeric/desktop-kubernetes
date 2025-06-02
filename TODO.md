# TODO

1. conformance is failing:
     WORKS: `dig +notcp +noall +answer +search kubernetes.default.svc.cluster.local A`
     DOES NOT WORK: `dig +tcp +noall +answer +search kubernetes.default.svc.cluster.local A`
     Something interfering with DNS over TCP??
2. Support https://github.com/flannel-io/flannel#deploying-flannel-with-helm
3. Add auth side-car to kube dash
4. Alma 9.5 no longer available - now its 9.6
