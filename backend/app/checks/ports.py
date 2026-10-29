"""Active TCP port check. Kept to a short, well-known list rather than a
full 1-65535 sweep: this is a posture check, not a reconnaissance tool."""
from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor
from typing import Any

CONNECT_TIMEOUT_SECONDS = 1.5

COMMON_PORTS: dict[int, str] = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    6379: "Redis",
    8080: "HTTP-alt",
    27017: "MongoDB",
}

# Ports that are fine to expose on a normal web server.
EXPECTED_OPEN = {80, 443}


def _probe(ip: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(CONNECT_TIMEOUT_SECONDS)
        return sock.connect_ex((ip, port)) == 0


def check_ports(ip: str) -> dict[str, Any]:
    with ThreadPoolExecutor(max_workers=len(COMMON_PORTS)) as pool:
        open_flags = list(pool.map(lambda p: _probe(ip, p), COMMON_PORTS.keys()))

    open_ports = [
        {"port": port, "service": service, "unexpected": port not in EXPECTED_OPEN}
        for (port, service), is_open in zip(COMMON_PORTS.items(), open_flags)
        if is_open
    ]
    return {
        "scanned_ports": list(COMMON_PORTS.keys()),
        "open_ports": open_ports,
        "unexpected_open_count": sum(1 for p in open_ports if p["unexpected"]),
    }
