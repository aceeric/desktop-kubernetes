
### Sonobuoy conformance testing

proj_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SONOGZIP=https://github.com/vmware-tanzu/sonobuoy/releases/download/v0.20.0/sonobuoy_0.20.0_linux_386.tar.gz
[[ -f $proj_root/conformance/sonobuoy ]] || curl -sL $SONOGZIP | tar zxvf - -C $proj_root/conformance sonobuoy

# smoke test - should run one test successfully

$proj_root/conformance/sonobuoy run\
 --sonobuoy-image projects.registry.vmware.com/sonobuoy/sonobuoy:v0.20.0\
 --mode=quick

# run all e2e conformance tests

$proj_root/conformance/sonobuoy run\
 --plugin=e2e\
 --sonobuoy-image=projects.registry.vmware.com/sonobuoy/sonobuoy:v0.20.0\
 --mode=certified-conformance\
 --timeout=30000

# watch the tests run in one console window

watch 'sonobuoy status --json | json_pp'

# watch the logs as the tests run in another console window

$proj_root/conformance/sonobuoy logs -f

# get the test results upon completion

results=$($proj_root/conformance/sonobuoy retrieve)
$proj_root/conformance/sonobuoy results $proj_root/conformance/sonobuoy/$results

# clean up the cluster

sonobuoy delete --wait