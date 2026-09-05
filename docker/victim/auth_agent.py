#!/usr/bin/env python3
"""Emit structured SSH failures and detect bursts from one source IP."""

import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict, deque
from datetime import datetime

WINDOW_SECONDS = 30
FAILURE_THRESHOLD = 5

FAILED_LOGIN_RE = re.compile(
    r"(?P<message>Failed password for (?:(?:invalid user) )?(?P<user>\S+)"
    r"|Invalid user (?P<invalid_user>\S+)) from (?P<ip>[0-9a-fA-F:.]+)"
)
SYSLOG_RE = re.compile(
    r"^(?P<stamp>[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})"
)
ISO_RE = re.compile(r"^(?P<stamp>\d{4}-\d{2}-\d{2}T[^ ]+)")


def timestamp_for(line):
    match = ISO_RE.search(line) or SYSLOG_RE.search(line)
    if not match:
        return datetime.now().astimezone().isoformat()
    stamp = match.group("stamp")
    if "T" in stamp:
        return stamp
    return datetime.strptime(
        f"{datetime.now().year} {stamp}", "%Y %b %d %H:%M:%S"
    ).astimezone().isoformat()


def event_from(line):
    match = FAILED_LOGIN_RE.search(line)
    if not match:
        return None
    username = match.group("user") or match.group("invalid_user")
    return {
        "timestamp": timestamp_for(line),
        "source_ip": match.group("ip"),
        "username": username,
    }


def journal_available():
    """Prefer journald when this image has a usable systemd journal."""
    if not os.path.exists("/run/systemd/journal/socket"):
        return False
    try:
        subprocess.run(
            ["journalctl", "--no-pager", "-n", "0"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except (OSError, subprocess.SubprocessError):
        return False
    return True


def lines_from_journal():
    return subprocess.Popen(
        ["journalctl", "--no-pager", "-f", "-o", "short-iso", "-u", "ssh"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )


def lines_from_auth_log():
    path = "/var/log/auth.log"
    while not os.path.exists(path):
        time.sleep(0.5)
    with open(path, encoding="utf-8", errors="replace") as log:
        log.seek(0, os.SEEK_END)
        while True:
            line = log.readline()
            if line:
                yield line
            else:
                time.sleep(0.25)


def main():
    failures = defaultdict(deque)
    alerted = set()
    journal_process = None
    if journal_available():
        journal_process = lines_from_journal()
        lines = journal_process.stdout
        source = "journald"
    else:
        lines = lines_from_auth_log()
        source = "/var/log/auth.log"
    print(json.dumps({"agent": "ssh-auth-baseline", "log_source": source}), flush=True)

    try:
        for line in lines:
            event = event_from(line)
            if event is None:
                continue
            now = time.monotonic()
            source_ip = event["source_ip"]
            recent = failures[source_ip]
            recent.append(now)
            while recent and now - recent[0] > WINDOW_SECONDS:
                recent.popleft()
            print(json.dumps({"event": "ssh_login_failure", **event}), flush=True)
            if len(recent) >= FAILURE_THRESHOLD and source_ip not in alerted:
                alerted.add(source_ip)
                print(
                    json.dumps(
                        {
                            "alert": "repeated_ssh_failures",
                            "source_ip": source_ip,
                            "failure_count": len(recent),
                            "window_seconds": WINDOW_SECONDS,
                        }
                    ),
                    flush=True,
                )
            if len(recent) < FAILURE_THRESHOLD:
                alerted.discard(source_ip)
    finally:
        if journal_process is not None:
            journal_process.terminate()


if __name__ == "__main__":
    main()
