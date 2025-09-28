#!/usr/bin/env python3
#
# Based on:
# https://kubernetes-sigs.github.io/external-dns/v0.18.0/docs/tutorials/webhook-provider/
#

import re
import sys
import signal
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# the Version of this webhook
version = "1.12.0"

# The server
httpd = None

# If true, then don't update /etc/hosts, only log updates
dry_run = False

# If true, log more detailed info
debug = False

# Port to serve on
port = 5000

# This is the control plane node VM IP address - this will go into /etc/hosts
cluster_ip = ""

# Used by external DNS to know which domains are handled by this webhook. We also use
# it to ignore all /adjustendpoints calls when we are passed records that don't match
# these domains.
filters = {
    "domains": [
    ]
}

# Documentation. This is what we might get from External DNS. Note that the target is a
# service IP address in the Kubernetes cluster which doesn't help us here outside the
# cluster so its simply ignored.
example_record =  {
    "dnsName": "dtk.io",
    "targets": [
      "10.32.0.197"
    ],
    "recordType": "A",
    "labels": {
      "resource": "ingress/kubernetes-dashboard/kubernetes-dashboard"
    }
  }

# Array of records like 'example_record' above. Provided by the external DNS webhook
# provider running in the cluster. We don't interpret then we just store what we receive
# so we can give them back when requested.
records = []

# Per external-dns guidance
mime_type = "application/external.dns.webhook+json;version=1"

class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    """
    The Webhook.
    """
    def do_GET(self):
        """
        Handle GET
        """
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == "/":
            self.handle_get_root()
        elif path == "/records":
            self.handle_get_records()
        elif path == "/domains":
            self.handle_get_domains()
        elif path == "/clusterip":
            self.handle_get_clusterip()
        else:
            self._send_response(404, mime_type, {"error": "Not Found"})
    
    def do_POST(self):
        """
        Handle POST
        """
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == "/records":
            self.handle_post_records()
        elif path == "/adjustendpoints":
            self.handle_post_adjustendpoints()
        elif path == "/domains":
            self.handle_post_domains()
        elif path == "/clusterip":
            self.handle_post_clusterip()
        else:
            self._send_response(404, mime_type, {"error": "Not Found"})

    def handle_get_root(self):
        """
        GET /
        """
        self._send_response(200, mime_type, filters)
    
    def handle_get_records(self):
        """
        GET /records
        """
        self._send_response(200, mime_type, records)

    def handle_get_clusterip(self):
        """
        GET /clusterip
        """
        self._send_response(200, mime_type, cluster_ip)

    def handle_get_domains(self):
        """
        GET /domains
        """
        self._send_response(200, mime_type, filters["domains"])

    def handle_post_adjustendpoints(self):
        """
        POST /adjustendpoints
        """
        post_data = self.get_post_data()
        if not post_data:
            self._send_response(400, mime_type, {"error": "No adjustment data provided"})
            return
        global records
        records = post_data
        self.log_message("updating hosts file")
        self.update_etc_hosts(post_data)
        self._send_response(200, mime_type, [])

    def handle_post_domains(self):
        """
        POST /domains
        """
        post_data = self.get_post_data()
        if not post_data:
            self._send_response(400, mime_type, {"error": "No domain data provided"})
            return
        global filters
        filters["domains"].append(post_data)
        self._send_response(200)

    def handle_post_clusterip(self):
        """
        POST /clusterip
        """
        post_data = self.get_post_data()
        if not post_data:
            self._send_response(400, mime_type, {"error": "No cluster ip data provided"})
            return
        global cluster_ip
        cluster_ip = post_data
        self._send_response(200)

    def handle_post_records(self):
        """
        Unused
        """
        self._send_response(200)

    def _send_response(self, status_code, content_type=mime_type, data=None):
        """
        Helper that sends a response
        """
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        
        if data is not None:
            if content_type == mime_type:
                self.wfile.write(json.dumps(data).encode())
            else:
                self.wfile.write(data.encode())

    def get_post_data(self):
        """
        Get the post data
        """
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length:
            post_data = self.rfile.read(content_length).decode()
            try:
                return json.loads(post_data)
            except json.JSONDecodeError:
                return post_data
        return None
    
    def log_message(self, format, *args):
        """
        Logs a message
        """
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

    def is_managed_domain(self, hostname):
        """
        Checks the filters and returns true if the passed host name is part of a
        managed domain, else false.
        """
        global filters
        for domain in filters["domains"]:
            if hostname.endswith(domain):
                return True
        return False

    def update_etc_hosts(self, recs):
        """
        Updates /etc/hosts
        """
        etc_hosts = "/etc/hosts"
        for rec in recs:
            if debug:
                print(f"DEBUG: {rec}")
            if not self.is_managed_domain(f"{rec['dnsName']}"):
                print(f"domain is not managed: {rec['dnsName']}")
                return

            new_entry = f"{cluster_ip} {rec['dnsName']}"
            found = False
            expr = r"(^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s]+" + rec["dnsName"] + "$"

            with open(etc_hosts, "r") as file:
                lines = file.readlines()
            for idx, line in enumerate(lines):
                result = re.match(expr, line)
                if result is not None:
                    found = True
                    if result.groups()[0] != cluster_ip:
                        self.log_message("updating entry: %s", new_entry)
                        lines[idx] = f"{new_entry}\n"
                    else:
                        self.log_message("entry matches for %s - no changes made", rec["dnsName"])
                    break
            if not found:
                self.log_message("adding entry: %s", new_entry)
                lines.extend([f"{new_entry}\n"])

        if not dry_run:
            with open(etc_hosts, "w") as file:
                file.writelines(lines)

def shutdown_handler(signum, frame):
    """
    Shuts down the webhook server
    """
    print(f"Received signal {signum}: shutting down server...")
    httpd.shutdown()
    print("Server was shut down")
    sys.exit(0)

def run_server(host, port):
    """
    Runs the webhook server
    """
    global httpd, version

    server_address = (host, port)
    httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
    now = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
    print(f"Desktop Kubernetes External-DNS webhook, version {version}")
    print("Configuration settings:")
    print(f"  dry_run: {dry_run}")
    print(f"  debug: {debug}")
    print(f"  port: {port}")
    print(f"  cluster_ip: {cluster_ip}")
    print(f"  managed domains: {filters['domains']}")
    print(f"  records: {records}")
    print(f"Starting HTTP server at {now} on http://{host}:{port}")

    signal.signal(signal.SIGTERM, shutdown_handler)    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nCTRL-C was pressed: shutting down server...")
        httpd.shutdown()
        print("Server was shut down")

def parse_arg(idx, arg, isbool=False):
    """
    Parses one arg
    """
    if sys.argv[idx].startswith(f"--{arg}="):
        val = sys.argv[idx].split("=")[1]
    elif sys.argv[idx] == f"--{arg}":
        if isbool:
            val = True
        else:
            idx += 1
            val = sys.argv[idx]
    else:
        return idx, None
    return idx + 1, val

def parse_args():
    """
    Parses all command line args
    """
    global cluster_ip, port, filters, dry_run, debug
    i = 1
    while i < len(sys.argv):
        i, val = parse_arg(i, "cluster-ip")
        if val is not None:
            cluster_ip = val
            continue
        i, val = parse_arg(i, "port")
        if val is not None:
            port = int(val)
            continue
        i, val = parse_arg(i, "domains")
        if val is not None:
            domains = val.split(",")
            for domain in domains:
                filters["domains"].append(domain)
            continue
        i, val = parse_arg(i, "dry-run", True)
        if val is not None:
            dry_run = val
            continue
        i, val = parse_arg(i, "debug", True)
        if val is not None:
            debug = val
            continue
        return False
    return True

if __name__ == "__main__":
    if not parse_args():
        print("error parsing args")
        sys.exit(1)
    run_server("0.0.0.0", port)
