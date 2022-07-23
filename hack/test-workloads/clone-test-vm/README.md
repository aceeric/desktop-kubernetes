# Create a scratch VM from the "bingo" template

Create a scratch VM for testing CentOS configuration changes and manual Kubernetes component installs.

## Ensure you are in the repo root

E.g.:
```
$ cd ~/projects/desktop-kubernetes
```

## Define vars and functions needed by the scripts

```
export DTKBASE=$(pwd)
function xec() { f=$(find $DTKBASE/scripts -name $1) && $f "${@:2}"; }
export -f xec
```

## Clone template VM "bingo" into scratch VM "scratch"

Use the private key created when the template VM _bingi_ was provisioned

```
xec clone-vm\
 --priv-key=./generated/kickstart/id_ed25519\
 --template-vmname=bingo\
 --clone-vmname=scratch\
 --clone-ram=4096\
 --clone-cpu=2\
 --host-only-network=192.168.56\
 --host-only-octet=100\
 --vboxdir=/sdb1/virtualboxvms\
 --shutdown=false
```

## Configure etc hosts in the VM

```
xec configure-etc-hosts ./generated/kickstart/id_ed25519 scratch
```

## Display how to ssh into the VM

```
xec show-ssh ./generated/kickstart/id_ed25519 scratch
```