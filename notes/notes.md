### Getting the latest version of a GitHub release artifact

The following link is a nice recipe for getting the latest release of something from GitHub:

https://gist.github.com/lukechilds/a83e1d7127b78fef38c2914c4ececc3c

Example for getting etcd:

```shell
TAG=$(curl -s https://api.github.com/repos/etcd-io/etcd/releases/latest | \
      grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/') &&\
 RELEASE=etcd-$TAG-linux-amd64.tar.gz &&\
 curl -sL https://github.com/etcd-io/etcd/releases/download/$TAG/$RELEASE -o $RELEASE
```
