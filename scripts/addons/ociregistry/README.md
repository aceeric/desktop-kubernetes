# Ociregistry

This add-on installs my pull-through registry. The configuration supports two values in the configuration yaml:

|Value|Default|Description|
|-|-|-|
|`image-path`|blank|Specifies a path on the local host for the Ociregistry image tarball. If non-blank then this file will be copied to each cluster host and loaded into the `containerd` image cache. If the path starts with `/` then it is absolute, otherwise it is relative to the project directory. You are responsible to place the image tarball at the specified location (e.g. using `docker pull` and `docker save`...)|
|`containerd-mirror-enabled`|`false`|If `true` then configures `containerd` on each host to mirror to the in-cluster registry pod. If you set this to `true` then you almost certainly need to provide an image path because the Ociregistry pod can't be started without an image and if `containerd` is configured to mirror, it won't be able to start the Ociregistry pod without the image already in `containerd` cache. |

Example:

```yaml
addons:
  - name: ociregistry
    enabled: true
    image-path: binaries/ociregistry-image-1.12.3.tar
    containerd-mirror-enabled: true
```

## Ingress

At this time, only the Kubernetes Gateway API is supported for ingress. The helm values specify an `HTTPRoute` with a host name of `ociregistry.io`. The registry serves on `/`. The reason is that some tools (the Docker CLI) have trouble with a registry serving on anything other than `/`. Ingress is optional. If you're installing the registry exclusively as an in-cluster mirror then you don't need access to the registry externally but its installed with external access anyway.

With the ingress so configured you can test the registry by pulling through it: `docker pull ociregistry.io/docker.io/hello-world:latest`.
