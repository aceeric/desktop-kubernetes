# Sonobuoy conformance testing
03-September-2024

This README assumes you're in the repo root. E.g.:

```
$ pwd
~/projects/desktop-kubernetes
```

# Get Sonobuoy
```
SONOVER=0.57.2
SONOGZIP=https://github.com/vmware-tanzu/sonobuoy/releases/download/v$SONOVER/sonobuoy_${SONOVER}_linux_amd64.tar.gz
rm -f conformance/sonobuoy
curl -sL $SONOGZIP | tar zxvf - -C conformance sonobuoy
```

## Smoke test - should run one test successfully

```
conformance/sonobuoy run --mode=quick --dns-namespace coredns
watch 'conformance/sonobuoy status --json | jq'
conformance/sonobuoy delete --wait
```

## Run conformance tests

```
conformance/sonobuoy run --mode=certified-conformance --timeout=30000 --dns-namespace coredns
```

## Watch the tests run in one console window

```
watch 'conformance/sonobuoy status --json | jq'
```

## Watch the logs in another console window

```
conformance/sonobuoy logs -f
```

## Get the test results upon completion

```
outfile=$(conformance/sonobuoy retrieve) &&\
 mv $outfile conformance &&\
 rm -rf conformance/results &&\
 mkdir -p conformance/results &&\
 tar xzf conformance/$outfile -C conformance/results
```

## Clean up the cluster

```
conformance/sonobuoy delete --wait
```

## Certification submission process

### This repo

1. Download Sono / Update Sono version in main README / Run Sono per above. If PASS:
2. Copy two Sono result files to a staging dir in this project:
   ```
   find conformance/results \( -name e2e.log -o -name junit_01.xml \) | xargs -I% cp % conformance/conformance-submission
   ```
3. Hand edit this README, plus `PRODUCT.yaml` and `README.md` in `conformance/conformance-submission` as needed
4. Git commit and push
5. Tag `desktop-kubernetes` with a tag matching the Kubernetes version: `git tag -a v1.31.0 -m "Kubernetes 1.31.0 passes Sonobuoy conformance v0.57.2"`
6. Git push the tag: `git push origin v1.31.0`

## Conformance fork

E.g.: `~/projects/k8s-conformance-esace-fork`

1. Sync fork https://github.com/aceeric/k8s-conformance/tree/master
2. Do a `git pull`
3. Create branch: `git checkout -b v1.31-desktop-kubernetes`
4. Create directory: `mkdir ./v1.31/desktop-kubernetes`
5. Populate the directory: `cp ~/projects/desktop-kubernetes/conformance/conformance-submission/* ./v1.31/desktop-kubernetes`
6. Verify
   ```
   $ ls -l ./v1.31/desktop-kubernetes
   total 2264
   -rw-r--r-- 1 eace eace    7883 Sep  3 19:45 e2e.log
   -rw-r--r-- 1 eace eace 2296506 Sep  3 19:45 junit_01.xml
   -rw-rw-r-- 1 eace eace     549 Sep  3 19:45 PRODUCT.yaml
   -rw-rw-r-- 1 eace eace    4253 Sep  3 19:45 README.md
   ```
7. Git add and commit to the branch with message AND signoff:
   ```
   git commit -m 'Conformance results for v1.31/desktop-kubernetes
   Signed-off-by: Eric Ace <24485843+aceeric@users.noreply.github.com>'
   ```
8. Push to GitHub
9. Create a Pull Request to https://github.com/cncf/k8s-conformance from the branch in the fork per https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork

