## OpenEBS test

Verifies the proper functioning of the OpenEBS installation. OpenEBS is the dynamic storage provisioner used by this project. See the main README for more details. The OpenEBS operator that this project installs is the lite version that supports dynamic local HostPath provisioning. This enables testing workloads that use PVs and PVCs. The lite operator is a  dynamic provisioner that creates and binds PVs to PVCs. For each PV the provisioner creates a subdirectory under `/var/openebs/local/` on the node that is running the pod. All the files created on that PV are located in that subdirectory. When the PV is deleted, the directory is removed. Only ReadWriteOnce is supported. 

## Steps

Create a `test-openebs` namespace, a PVC, and a Pod that uses the PVC:

```shell
$ kubectl apply -f test-workloads/openebs 

$ kubectl -n test-openebs wait po hello-local-hostpath-pod --for condition=ready
pod/hello-local-hostpath-pod condition met

$ kubectl -n test-openebs get po -owide
NAME                       READY   STATUS    RESTARTS   AGE   IP              NODE  ...
hello-local-hostpath-pod   1/1     Running   0          55s   22.200.224.66   ham   ...
```

Notice that - in this case - the pod is running in the `ham` node. After a few seconds:

```shell
$ scripts/sshto ham
Activate the web console with: systemctl enable --now cockpit.socket

Last login: Sat Mar 20 22:14:55 2021 from 192.168.0.49
[root@ham ~]# cat /var/openebs/local/pvc-9a86f84d-042e-4027-8c8a-b631c27f3eee/greet.txt 
Sun Mar 21 02:53:31 UTC 2021 hello-local-hostpath-pod hello from OpenEBS Local PV
Sun Mar 21 02:53:36 UTC 2021 hello-local-hostpath-pod hello from OpenEBS Local PV
Sun Mar 21 02:53:41 UTC 2021 hello-local-hostpath-pod hello from OpenEBS Local PV
Sun Mar 21 02:53:46 UTC 2021 hello-local-hostpath-pod hello from OpenEBS Local PV
...
```
(remainder redacted for brevity)

Clean up:

```shell
[root@ham ~]# exit
logout
Connection to 192.168.0.46 closed.
$ kubectl delete ns test-openebs
namespace "test-openebs" deleted
```
