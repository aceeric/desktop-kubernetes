# Images

If you place `.tar.` and `.tgz` files here, the installer will copy them to each host as the cluster is bring provisioned and then load the images into the containerd cache on each host to help minimize the impact of Docker rate limiting. See `scripts/worker/containerd/install-containerd` and `hack/create-image-archive` for additional information.
