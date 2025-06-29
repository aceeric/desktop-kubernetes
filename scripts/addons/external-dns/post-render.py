#!/usr/bin/env python3
#
# Removes the webhook sidecar which is not needed because the webhook runs on the
# desktop, not in the cluster.
#

import sys
import yaml

def remove_sidecar(manifests_yaml):
    modified_manifests = []
    for manifest in yaml.safe_load_all(manifests_yaml):
        if manifest and manifest.get("kind") == "Deployment":
            containers = manifest["spec"]["template"]["spec"]["containers"]
            manifest["spec"]["template"]["spec"]["containers"] = [
                c for c in containers if c.get("name") != "webhook"
            ]
        modified_manifests.append(manifest)
    return yaml.dump_all(modified_manifests, default_flow_style=False)

if __name__ == "__main__":
    input_yaml = sys.stdin.read()
    output_yaml = remove_sidecar(input_yaml)
    sys.stdout.write(output_yaml)
