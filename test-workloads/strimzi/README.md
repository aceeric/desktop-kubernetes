### Strimzi Kafka

A simple Strimzi Kafka deployment. This example uses static local persistent volumes for Kakfa and Zookeeper.

#### Steps

Create a directory in the monk node for the Kafka volume storage, and a directory in the ham node for Zookeeper volume storage:
```shell
$ ip=$(scripts/get-vm-ip monk) && ssh -i kickstart/id_ed25519 root@$ip mkdir -p /pv/pv1
$ ip=$(scripts/get-vm-ip ham) && ssh -i kickstart/id_ed25519 root@$ip mkdir -p /pv/pv1
```

Create two PVs, each of which maps to one of the nodes referenced above:
```shell
$ kubectl apply -f\
  test-workloads/strimzi/default-storage-class.yaml\
  test-workloads/strimzi/pvs.yaml
```

Get `strimzi.io-install-latest.yaml`:
```shell
curl -L https://strimzi.io/install/latest?namespace=kafka -o test-workloads/strimzi/strimzi.io-install-latest.yaml
```

Deploy the Strimzi Cluster Operator and CRDs and wait for the Strimzi Operator pod to be ready:
```shell
$ kubectl create ns kafka &&\
  kubectl -n kafka apply -f test-workloads/strimzi/strimzi.io-install-latest.yaml &&\
  kubectl -n kafka wait pod -lname=strimzi-cluster-operator --for=condition=ready 
pod/strimzi-cluster-operator-68c6747bc6-w8gkr condition met
```

Deploy the Kafka CR to create the single-node Kafka/Zookeeper cluster:
```shell
$ kubectl apply -f test-workloads/strimzi/kafka-persistent-single.yaml
```

Wait for all the pods to reach the running state:
```shell
$ watch kubectl get po -nkafka
NAME                                          READY   STATUS    RESTARTS   AGE
my-cluster-entity-operator-5fd974964d-2qvzp   3/3     Running   0          13m
my-cluster-kafka-0                            1/1     Running   0          13m
my-cluster-zookeeper-0                        1/1     Running   0          14m
strimzi-cluster-operator-68c6747bc6-w8gkr     1/1     Running   0          22m
```
