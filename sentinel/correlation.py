"""Streaming correlation rules for distributed authentication failures."""

from collections import defaultdict, deque
from datetime import datetime
from typing import Any, Iterable

MITRE_T1110 = "T1110"


def _seconds(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def detect_distributed_bruteforce(
    events: Iterable[dict[str, Any]], window_seconds: int = 60,
    host_threshold: int = 3,
) -> list[dict[str, Any]]:
    """Return alerts for an IP observed on at least N distinct hosts in a window."""
    by_ip: dict[str, deque[tuple[float, str]]] = defaultdict(deque)
    alerts: list[dict[str, Any]] = []
    for event in sorted(events, key=lambda item: _seconds(item["timestamp"])):
        ip = event["source_ip"]
        timestamp = _seconds(event["timestamp"])
        window = by_ip[ip]
        window.append((timestamp, event["host"]))
        while window and timestamp - window[0][0] > window_seconds:
            window.popleft()
        hosts = sorted({host for _, host in window})
        if len(hosts) >= host_threshold:
            alerts.append({
                "alert": "distributed_ssh_bruteforce",
                "source_ip": ip,
                "hosts": hosts,
                "host_count": len(hosts),
                "window_seconds": window_seconds,
                "mitre_technique": MITRE_T1110,
                "timestamp": event["timestamp"],
            })
    return alerts
