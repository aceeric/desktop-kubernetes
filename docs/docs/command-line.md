# The Command Line

The `dtk` CLI takes one mandatory command, and then an optional sub-command or operand, and flags. As stated elsewhere in the documentation, most cluster configuration is read from a configuration yaml file. See the [configuration](configuration.md) section for more information on that.

## Usage

```
dtk command [sub-command] [flags]
```

## Commands

| Command | Sub-cmd / Operand | Description |
|-|-|-|
| cluster | create | Creates a cluster per the configuration yaml file. |
| | up | Starts all the VMs in configuration yaml. |
| | down | Stops all the VMs in configuration yaml. |
| | delete | Deletes a cluster by deleting all the VMs in configuration yaml. |
| verify | upstreams | Does a curl HEAD request on all core k8s components, ISOs. |
| | files | Reports on which core k8s components have already been downloaded to the file system. |
| install-addon | The addon name | Install an add-on from the scripts/addons directory. |
| check-tools | n/a | Reports on the presence or absence, and version, of the tools used by the CLI to provision a cluster. |
| version | n/a | Displays this CLI version. |
| help | n/a | Displays this help. |


## Options

| Option | Description |
|-|-|
| `--config` | The path to a configuration yaml file that specifies the cluster options. If not provided, uses the configuration yaml file in the same directory as the CLI. |
| `--create-template` {: .nowrap-column } | Overrides the setting specified in the configuration yaml. Allowed values are "true" and "false". |
| `--create-vms` | Create VMs. Allowed values are "true" and "false". Default is true. If false, then the VMs in the configuration yaml file must be up and running, and the installer will simply install Kubernetes on them. |
| `--help` | Same as the help command. |

## Examples

```
./dtk cluster create --config mycluster.yaml
```

Creates a cluster as defined in the `mycluster.yaml` file.

```
./dtk cluster create --create-template=false
```

Like above except re-uses the existing template from a prior cluster creation, and uses the configuration yaml in the CLI dir. (The configuration yaml specifies the name of the template VM.)

```
./dtk cluster up
```

Starts the VMs listed in the configuration yaml in the CLI dir.

```
./dtk install-addon external-dns
```

Installs the external-dns add-on from scripts/addons.
