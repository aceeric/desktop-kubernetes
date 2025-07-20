#!/usr/bin/env python3
#
# Parses a config.yaml file like the one included in the project root. Emanates
# a series of bash variable assigment statements. To understand what this script
# does, just run this from the repo root:
#
# scripts/helpers/parse-config.py ./config.yaml
#
# This script is intended to be sourced by the 'dtk' script to set script variables.
# For example, if 'config.yaml' has:
#
# kvm:
#   kickstart: kvm.text.ks.cfg
#
# then this script emanates a line:
#
# kvm_kickstart=kvm.text.ks.cfg
#
# Not all keys in the config file are processed. Only certain ones that the 'dtk'
# script cares about.
#

import yaml, sys, os

valid_configs = [
    "k8s.containerized-cplane",
    "k8s.cluster-cidr",
    "k8s.cluster-dns",
    "k8s.kube-proxy",
    "kvm.network",
    "kvm.kickstart",
    "kvm.os-variant",
    "vbox.host-network-interface",
    "vbox.host-only-network",
    "vbox.kickstart",
    "vbox.vboxdir",
    "vm.linux",
    "vm.create-template",
    "vm.template-vmname"
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
    # virt is a top level key
    if key == "virt":
        vars = vars + "%svirt=%s" % (newline, cfg[key])
        newline = "\n"
    elif key not in ["k8s", "kvm", "vbox", "vm"]:
        continue
    else:
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
