#!/usr/bin/env python3
"""CloudNotes production service bootstrap.

Simulates service startup, DNS resolution, and TLS validation using the
configuration files under config/. Diagnostic output is written to
logs/application.log so the deployment can be investigated post-incident.

Python standard library only. Runs completely offline.
"""

import os
import socket
import sys
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_CONF = os.path.join(BASE_DIR, "config", "app.conf")
DNS_CONF = os.path.join(BASE_DIR, "config", "dns.conf")
TLS_CONF = os.path.join(BASE_DIR, "config", "tls.conf")
LOG_FILE = os.path.join(BASE_DIR, "logs", "application.log")


def load_conf(path):
    """Parse a simple KEY=VALUE configuration file, ignoring comments."""
    values = {}
    if not os.path.exists(path):
        return values
    with open(path, "r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            values[key.strip()] = value.strip()
    return values


class Logger:
    """Minimal logger that mirrors records to stdout and the log file."""

    def __init__(self, path):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        # Start each run with a fresh log for clean investigation.
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("")

    def _write(self, level, message):
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        line = "{stamp} {level} {message}".format(
            stamp=stamp, level=level, message=message
        )
        print(line)
        with open(self.path, "a", encoding="utf-8") as handle:
            handle.write(line + "\n")

    def info(self, message):
        self._write("INFO", message)

    def warning(self, message):
        self._write("WARNING", message)

    def error(self, message):
        self._write("ERROR", message)


def check_dns(log, dns_conf):
    """Attempt to resolve the configured service host."""
    host = dns_conf.get("SERVICE_HOST", "")
    port = dns_conf.get("SERVICE_PORT", "")
    log.info("resolving service host {host}:{port}".format(host=host, port=port))

    try:
        socket.gethostbyname(host)
        log.info("host {host} resolved successfully".format(host=host))
        return True
    except socket.gaierror:
        log.error("unable to resolve host {host}".format(host=host))
        log.error("service unavailable")
        return False


def check_tls(log, tls_conf):
    """Validate that TLS is enabled and certificate material is present."""
    enabled = tls_conf.get("TLS_ENABLED", "false").strip().lower() == "true"
    cert = os.path.join(BASE_DIR, tls_conf.get("CERTIFICATE", ""))
    key = os.path.join(BASE_DIR, tls_conf.get("PRIVATE_KEY", ""))

    log.info("validating TLS configuration")

    if not enabled:
        log.warning("TLS is disabled")
        log.warning("deployment does not meet security requirements")
        return False

    if not os.path.exists(cert) or not os.path.exists(key):
        log.warning("TLS certificate or private key not found")
        log.warning("deployment does not meet security requirements")
        return False

    log.info("TLS enabled with valid certificate material")
    return True


def main():
    app_conf = load_conf(APP_CONF)
    dns_conf = load_conf(DNS_CONF)
    tls_conf = load_conf(TLS_CONF)

    log = Logger(LOG_FILE)
    app_name = app_conf.get("APP_NAME", "CloudNotes")
    app_env = app_conf.get("APP_ENV", "unknown")

    log.info("starting {name} service in {env} environment".format(
        name=app_name, env=app_env))

    dns_ok = check_dns(log, dns_conf)
    tls_ok = check_tls(log, tls_conf)

    if dns_ok and tls_ok:
        log.info("service startup complete")
        log.info("cloudnotes is ready to accept traffic")
        return 0

    log.error("service startup failed")
    log.error("review configuration and logs to diagnose the incident")
    return 1


if __name__ == "__main__":
    sys.exit(main())
