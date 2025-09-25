# Command Line Options

The following command-line options are supported for the `dtk` script:

| Option | Description |
|-|-|
| `--config` | Specifies the path to a `yaml` file that provides cluster configuration. If omitted, then the CLI looks for a file named `config.yaml` in the project root. Example: `--config ~/cluster_one.yaml`. |
| `--create-template` | Accepts `true` or `false`. Overrides the `vm.create-template` setting in the `config.yaml` file. Example: `--create-template=false`. |
| `--no-create-vms` | Do not create VMs. If this option is specified, then the VMs in the `config.yaml` file must be up and running, and the installer will simply install k8s on them. The CLI will get the IP addresses for each cluster VM from the virtual machine manager. |
| `--install-addon` | Once a cluster is up and running, Installs the specified add-on into a running cluster. Example: `--install-addon openebs`. (The add-on sub-directory has to exist in the `addons` directory.) Typically you bring a cluster up with all the add-ons you want, by enabling them (un-commenting them) in the `config.yaml` file. But this option supports ad-hoc add-on installation. |
| `--verify` | Looks for all the upstreams or filesystem objects used by the CLI to build the core k8s cluster. Valid options are `upstreams` and `files`. If `upstreams`, then the CLI does a curl HEAD request for each upstream (e.g. OS ISO, Kubernetes binaries, etc.). If `files`, then the same check is performed for the downloaded filesystem objects. This is a useful option to see all the objects that are required to provision a cluster. Example: `--verify upstreams`. Note that this excludes the add-on Helm binaries. Each add-on has the URL and version for it's Helm tarball. |
| `--check-compatibility` {: .nowrap-column } | Checks the installed versions of various desktop tools used by the project (`curl`, `kubectl`, etc) against what the project has been tested on - and then exits, taking no further action. You should do this at least once. Note - there will likely be differences between your desktop and what I tested with - you will have to determine whether the differences are relevant. |
| `--up`,<br/>`--down`,<br/>`--delete` | Takes a comma-separated list of VM names, and starts (`--up`), stops (`--down`), or deletes (`--delete`) them all. The `--down` option is a graceful shutdown. The `--delete` is a fast shutdown and also removes the VM files from the file system. E.g.: `--up vm1,vm2,vm3`. |
| `--help` | Displays help and exits. |
