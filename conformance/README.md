
### Sonobuoy conformance testing

SONOGZIP=https://github.com/vmware-tanzu/sonobuoy/releases/download/v0.20.0/sonobuoy_0.20.0_linux_386.tar.gz
[[ -f conformance/sonobuoy ]] || curl -sL $SONOGZIP | tar zxvf - -C conformance sonobuoy

# image: k8s.gcr.io/conformance:v1.20.1

# smoke test - should run one test successfully

conformance/sonobuoy run\
 --sonobuoy-image projects.registry.vmware.com/sonobuoy/sonobuoy:v0.20.0\
 --mode=quick

# run all e2e conformance tests

conformance/sonobuoy run\
 --plugin=e2e\
 --sonobuoy-image=projects.registry.vmware.com/sonobuoy/sonobuoy:v0.20.0\
 --mode=certified-conformance\
 --timeout=30000

# watch the tests run in one console window

watch 'sonobuoy status --json | json_pp'

# watch the logs as the tests run in another console window

conformance/sonobuoy logs -f

# get the test results upon completion

results=$(conformance/sonobuoy retrieve)
mv $results conformance
conformance/sonobuoy results conformance/$results
tar -zxvf conformance/$results --strip-components 2 -C conformance plugins/e2e/sonobuoy_results.yaml

# clean up the cluster

sonobuoy delete --wait

# get failures

./getfails sonobuoy_results.yaml
NAME: [sig-scheduling] SchedulerPredicates [Serial] validates that there is no conflict between pods with same hostPort but different hostIP and protocol [Conformance]
NAME: [sig-network] Services should have session affinity timeout work for service with type clusterIP [LinuxOnly] [Conformance]
NAME: [sig-network] Services should have session affinity timeout work for NodePort service [LinuxOnly] [Conformance]

# run only failures

sonobuoy run --e2e-focus "validates that there is no conflict between pods with same hostPort but different hostIP and protocol"
sonobuoy run --e2e-focus "should have session affinity timeout work for service with type clusterIP"
sonobuoy run --e2e-focus "should have session affinity timeout work for NodePort service"
