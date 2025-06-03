# Conformance testing
_03-Jun-2025_

This README assumes you have git cloned the repo and the repo root is the current working directory. This article documents the conformance submission process.

## Get Hydrophone

The project uses [Hydrophone](https://www.kubernetes.dev/blog/2024/05/23/introducing-hydrophone/) to run the conformance tests.

```shell
go install sigs.k8s.io/hydrophone@v0.7.0
```

## Run conformance tests

```shell
hydrophone --conformance --parallel 5
```

The test results are generated into the current working directory.

## Move test results to submission folder

```shell
rm conformance/conformance-submission/{e2e.log,junit_01.xml}
mv e2e.log junit_01.xml conformance/conformance-submission
```

## Clean up the cluster

```shell
hydrophone --cleanup
```

## Edit documents

Update any new version numbers, etc.:

1. This README
2. The Project README
3. `PRODUCT.yaml` and `README.md` in `conformance/conformance-submission`
4. Git commit and push
5. Tag `desktop-kubernetes` with a tag matching the Kubernetes version. E.g.:
   `git tag -a v1.33.1 -m "Kubernetes 1.33.1 passes conformance using Hydrophone v0.7.0"`
6. Git push the tag: `git push origin v1.33.1`

## Conformance fork

E.g.: `~/projects/k8s-conformance-esace-fork`

1. Sync fork https://github.com/aceeric/k8s-conformance/tree/master
2. Do a `git pull`
3. Create branch: `git checkout -b v1.33-desktop-kubernetes`
4. Create directory: `mkdir ./v1.33/desktop-kubernetes`
5. Populate the directory: `cp ~/projects/desktop-kubernetes/conformance/conformance-submission/* ./v1.33/desktop-kubernetes`
6. Verify
   ```shell
   $ ls -l ./v1.33/desktop-kubernetes
   total 2312
   -rw-rw-r-- 1 eace eace    7957 Jun  3 18:19 e2e.log
   -rw-rw-r-- 1 eace eace 2348748 Jun  3 18:19 junit_01.xml
   -rw-rw-r-- 1 eace eace     549 Jun  3 18:19 PRODUCT.yaml
   -rw-rw-r-- 1 eace eace    4037 Jun  3 18:19 README.md
   ```
7. Git add and commit to the branch with message AND signoff:
   ```shell
   git commit -m 'Conformance results for v1.33/desktop-kubernetes
   Signed-off-by: Eric Ace <24485843+aceeric@users.noreply.github.com>'
   ```
8. Push to GitHub
9. Create a Pull Request to https://github.com/cncf/k8s-conformance from the branch in the fork per https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork
