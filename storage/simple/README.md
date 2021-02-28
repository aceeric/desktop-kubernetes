### Storage

A simple storage test.

Creates a storage class and two static `local` persistent volumes. Then two claims for the volumes, then two pods referencing the claims. Adds some data into the mounted volumes in the pods, and verifies the data was added.

#### Steps

Create directories in the doc pod for the volume storage:
```shell
$ docip=$(scripts/get-vm-ip doc)
$ ssh -i kickstart/id_ed25519 root@$docip mkdir -p /pv/pv1 /pv/pv1
```
Create a storage class, two persistent volumes, two PVCs that bind to the PVs, and two Pods that use the PVCs:
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

Write some data to the persistent volumes:
```shell
$ kubectl exec -it test-pod-1 -- sh -c 'echo from pod 1 > /tmp/foo/from-pod-1'
$ kubectl exec -it test-pod-2 -- sh -c 'echo from pod 2 > /tmp/foo/from-pod-2'
```

Verify the data was created in the VM:
```shell
$ ssh -i kickstart/id_ed25519 root@$docip find /pv
/pv
/pv/pv1
/pv/pv1/from-pod-1
/pv/pv2
/pv/pv2/from-pod-2
```
