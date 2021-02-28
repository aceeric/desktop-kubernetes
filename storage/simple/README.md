### Storage

A simple storage test.

Creates a storage class and two static `local` persistent volumes. Then two claims for the volumes, then two pods referencing the claims.

Steps:

Create directories in the doc pod for the volume storage
```shell
$ docip=$(scripts/get-vm-ip doc)
$ ssh -i kickstart/id_ed25519 root@$docip mkdir -p /pv/pv1 /pv/pv1
```
Then:
```shell
$ kubectl apply -f\
  default-storage-class.yaml\
  test-pv-1.yaml\
  test-pv-2.yaml\
  test-pvc1.yaml\
  test-pvc2.yaml\  
  test-pod-1.yaml\
  test-pod-2.yaml
```

Then:
```shell
$ kubectl exec -it test-pod-1 -- sh -c 'echo from pod 1 > /tmp/foo/from-pod-1'
$ kubectl exec -it test-pod-2 -- sh -c 'echo from pod 2 > /tmp/foo/from-pod-2'
```

And verify:
```shell
$ ssh -i kickstart/id_ed25519 root@$docip find /pv
/pv
/pv/pv1
/pv/pv1/from-pod-1
/pv/pv2
/pv/pv2/from-pod-2
```
