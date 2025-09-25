# Addons

The Add-ons are Helm workloads that are generally considered useful to a wide audience.

_Desktop Kubernetes_ supports Add-ons as follows:

1. The `config.yaml` specifies an Add-On name.
2. That Add-On name has to exactly match a subdirectory under the `scripts/addons` directory.
3. The CLI loops through all enabled add-ons and simply runs a script named `install` in each such directory matching the name of the enabled Add-On.

## Add-On install scripts

Each Add-On install script does the same things:

1. Downloads the Add-On tarball using a hard-coded version in the Add-On `install` script.
2. Helm-installs the Add-On.

Some Add-Ons are more complex because because the Add-On might require:

1. Templating Helm values
2. Manipulating the guest VMs. (E.g.: Calico requires copying a config file to each host and restarting NetworkManager)

For those you will see more logic in the Add-On `install` script. In general, the approach is for the main CLI `dtk` to know nothing about the Add-Ons except how to find the `install` script.

See the [Components and Versions](components-and-versions.md) Section for a list of the Add-Ons and versions.
