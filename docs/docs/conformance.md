# Conformance

This section documents the process of running _Desktop Kubernetes_ through the Kubernetes conformance tests and getting it certified. This guide assumes you have git cloned the repo and the repo root is the current working directory. The first part of this guide assumes you've git cloned this repo and your current working directory is the root of the cloned repo.

> This is presented purely as background information since the certification request can only come from the project fork. But you may wish to run the conformance tests on your own cluster provisioned by _Desktop Kubernetes_.

## Get Hydrophone

The project uses [Hydrophone](https://www.kubernetes.dev/blog/2024/05/23/introducing-hydrophone/) to run the conformance tests.

```shell
go install sigs.k8s.io/hydrophone@latest
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

1. This document.
1. The Project README.
1. The `PRODUCT.yaml` and `README.md` files in `conformance/conformance-submission`.
1. Git commit and push.
1. Tag `desktop-kubernetes` with a tag matching the Kubernetes version. E.g.:
   `git tag -a v1.35.0 -m "Kubernetes 1.35.0 passes conformance using Hydrophone v0.7.0"`.
1. Git push the tag: `git push origin v1.35.0`.

## Conformance fork

This section assumes you've forked the conformance repo per their guidance. E.g., my fork is [https://github.com/aceeric/k8s-conformance.git](https://github.com/aceeric/k8s-conformance.git). Set the working directory to where the repo is cloned on the file system.

1. Sync the fork with the upstream (in the GitHub UI) so you're starting from the latest.
1. Do a `git pull`.
1. Create branch, e.g.: `git checkout -b v1.35-desktop-kubernetes`.
1. Create directory, e.g.: `mkdir ./v1.35/desktop-kubernetes`.
1. Populate the directory: `cp ~/projects/desktop-kubernetes/conformance/conformance-submission/* ./v1.35/desktop-kubernetes`.
1. Verify:
   ```shell
   $ ls -l ./v1.35/desktop-kubernetes
   total 2312
   -rw-rw-r-- 1 eace eace    7957 Jun  3 18:19 e2e.log
   -rw-rw-r-- 1 eace eace 2348748 Jun  3 18:19 junit_01.xml
   -rw-rw-r-- 1 eace eace     549 Jun  3 18:19 PRODUCT.yaml
   -rw-rw-r-- 1 eace eace    4037 Jun  3 18:19 README.md
   ```
1. Git add and commit to the branch with message AND signoff:
   ```shell
   git commit -m 'Conformance results for v1.35/desktop-kubernetes
   Signed-off-by: Eric Ace <24485843+aceeric@users.noreply.github.com>'
   ```
1. Push to GitHub.
1. Create a Pull Request to https://github.com/cncf/k8s-conformance from the branch in the fork. For detailed instructions, see [creating-a-pull-request-from-a-fork](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request-from-a-fork) on the GitHub _Collaborating with pull requests_ documentation page.