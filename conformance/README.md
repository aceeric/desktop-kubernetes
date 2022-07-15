### Sonobuoy conformance testing

13-July-2022

SONOGZIP=https://github.com/vmware-tanzu/sonobuoy/releases/download/v0.56.8/sonobuoy_0.56.8_linux_amd64.tar.gz
[[ -f conformance/sonobuoy ]] || curl -sL $SONOGZIP | tar zxvf - -C conformance sonobuoy

#### smoke test - should run one test successfully

conformance/sonobuoy run --mode=quick
watch 'conformance/sonobuoy status --json | json_pp'

#### run conformance tests

conformance/sonobuoy run --mode=certified-conformance --timeout=30000

####  watch the tests run in one console window

watch 'conformance/sonobuoy status --json | json_pp'

####  watch the logs as the tests run in another console window

conformance/sonobuoy logs -f

####  get the test results upon completion

outfile=$(conformance/sonobuoy retrieve) &&\
 mv $outfile conformance &&\
 mkdir -p conformance/results; tar xzf conformance/$outfile -C conformance/results

#### clean up the cluster

conformance/sonobuoy delete --wait
