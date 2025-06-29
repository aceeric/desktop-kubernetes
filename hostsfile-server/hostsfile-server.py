#!/usr/bin/env python3
# https://kubernetes-sigs.github.io/external-dns/v0.18.0/docs/tutorials/webhook-provider/

import re
import sys
import signal
import json
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime

# The server
httpd = None

# If true, then don't update /etc/hosts, only log updates
dry_run = False

# Port to serve on
port = 5000

# This is the control plane node VM IP address - this will go into /etc/hosts
cluster_ip = ""

# Used by external DNS to know which domains are handled by this webhook (I think)
filters = {
    "domains": [
    ]
}

# Documentation
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

mime_type = "application/external.dns.webhook+json;version=1"

class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        
        if path == "/":
            self.handle_get_root()
        elif path == "/records":
            self.handle_get_records()
        elif path == "/domains":
            self.handle_get_domains()
        else:
            self._send_response(404, mime_type, {"error": "Not Found"})
    
    def do_POST(self):
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
        self._send_response(200, mime_type, filters)
    
    def handle_get_records(self):
        self._send_response(200, mime_type, records)

    def handle_get_domains(self):
        self._send_response(200, mime_type, filters["domains"])

    def handle_post_adjustendpoints(self):
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
        post_data = self.get_post_data()
        if not post_data:
            self._send_response(400, mime_type, {"error": "No domain data provided"})
            return
        global filters
        filters["domains"].append(post_data)
        self._send_response(200)

    def handle_post_clusterip(self):
        post_data = self.get_post_data()
        if not post_data:
            self._send_response(400, mime_type, {"error": "No cluster ip data provided"})
            return
        global cluster_ip
        cluster_ip = post_data
        self._send_response(200)

    def handle_post_records(self):
        """NOP"""
        self._send_response(200)

    def _send_response(self, status_code, content_type=mime_type, data=None):
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
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length:
            post_data = self.rfile.read(content_length).decode()
            try:
                return json.loads(post_data)
            except json.JSONDecodeError:
                return post_data
        return None
    
    def log_message(self, format, *args):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")

    def update_etc_hosts(self, recs):
        etc_hosts = "/etc/hosts"
        for rec in recs:
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
    print(f"Received signal {signum}: shutting down server...")
    httpd.shutdown()
    print("Server was shut down")
    sys.exit(0)

def run_server(host, port):
    global httpd

    server_address = (host, port)
    httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
    print(f"Starting HTTP server on http://{host}:{port}")

    signal.signal(signal.SIGTERM, shutdown_handler)    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nCTRL-C was pressed: shutting down server...")
        httpd.shutdown()
        print("Server was shut down")

def parse_arg(idx, arg, isbool=False):
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
    global cluster_ip, port, filters,dry_run
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
        return False
    return True

if __name__ == "__main__":
    if not parse_args():
        print("error parsing args")
        sys.exit(1)
    run_server("0.0.0.0", port)
