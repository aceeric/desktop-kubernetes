### Strimzi Kafka

A simple Strimzi Kafka deployment with persistent storage for Kafka and Zookeeper. Requires the Kubernetes
cluster to have been provisioned with the `--storage` option: in this case, the OpenEBS local HostPath provisioner.
See the help for the `--storage` option of the `dtk` script for info on OpenEBS.

#### Steps

Get `strimzi.io-install-latest.yaml` (in this case, 0.25.0, as of 14-Aug-2021):
```shell
curl -L https://strimzi.io/install/latest?namespace=kafka -o test-workloads/strimzi/strimzi.io-install-latest.yaml
```

Deploy the Strimzi Cluster Operator and CRDs and wait for the Strimzi Operator pod to be ready:
```shell
$ kubectl create ns kafka &&\
  kubectl -n kafka create -f test-workloads/strimzi/strimzi.io-install-latest.yaml &&\
  kubectl -n kafka wait pod -lname=strimzi-cluster-operator --for=condition=ready 
pod/strimzi-cluster-operator-68c6747bc6-w8gkr condition met
```

Deploy the Kafka CR to create the single-node Kafka/Zookeeper cluster. This example also configures an external listener so we can connect to Kafka from outside the cluster:
```shell
$ kubectl -n kafka apply -f test-workloads/strimzi/kafka-persistent-single.yaml
```

Wait for all the pods to reach the running state, and for the PVCs to be created and bound, and the PVs to be created.
```shell
$ watch kubectl -n kafka get po,pv,pvc
NAME                                              READY   STATUS    RESTARTS   AGE
pod/my-cluster-entity-operator-549cd74978-vpgg7   3/3     Running   0          2m59s
pod/my-cluster-kafka-0                            1/1     Running   0          3m25s
pod/my-cluster-kafka-exporter-898b887bf-jkdj9     1/1     Running   0          2m39s
pod/my-cluster-zookeeper-0                        1/1     Running   0          4m4s
pod/strimzi-cluster-operator-799b7d7596-p7cvb     1/1     Running   0          11m

NAME                                CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                               STORAGECLASS       REASON   AGE
persistentvolume/pvc-12461d97-...   2Gi        RWO            Delete           Bound    kafka/data-my-cluster-zookeeper-0   openebs-hostpath            4m
persistentvolume/pvc-72996c16-...   2Gi        RWO            Delete           Bound    kafka/data-my-cluster-kafka-0       openebs-hostpath            3m24s

NAME                                                STATUS   VOLUME             CAPACITY   ACCESS MODES   STORAGECLASS       AGE
persistentvolumeclaim/data-my-cluster-kafka-0       Bound    pvc-72996c16-...   2Gi        RWO            openebs-hostpath   3m25s
persistentvolumeclaim/data-my-cluster-zookeeper-0   Bound    pvc-12461d97-...   2Gi        RWO            openebs-hostpath   4m4s
```
