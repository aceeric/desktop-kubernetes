#!/usr/bin/env python3

import yaml, sys, os

valid_configs = [
    "k8s.containerized-cplane",
    "k8s.cluster-cidr",
    "k8s.cluster-dns",
    "k8s.kube-proxy",
    "vbox.host-network-interface",
    "vbox.host-only-network",
    "vbox.vboxdir",
    "vm.linux",
    "vm.create-template",
    "vm.template-vmname",
    "vm.kickstart"
]

skip_configs = [
    "k8s.containerd-mirror"
]

quiet = False
config_file = sys.argv[1]
if len(sys.argv) == 3:
    quiet = True

with open(config_file, "r") as file:
    cfg = yaml.safe_load(file)

vars = ""
newline = ""

for key in list(cfg.keys()):
   if not key in ["k8s", "vbox", "vm"]:
        continue
   for subkey in list(cfg[key].keys()):
        config = "%s.%s" % (key, subkey)
        if config in skip_configs:
            continue
        if not config in valid_configs:
            print("error: unsupported configuration: " + config)
            os._exit(1)
        val = "" if cfg[key][subkey] is None else cfg[key][subkey]
        if str(val) == "True":
            val = "1"
        elif str(val) == "False":
            val = "0"
        var = (key + "-" + subkey).replace("-", "_")
        vars = vars + "%s%s=%s" % (newline, var, val)
        newline = "\n"

if not quiet:
    print(vars)
