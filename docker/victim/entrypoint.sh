#!/bin/sh
set -eu

mkdir -p /run/sshd
touch /var/log/auth.log

/usr/local/bin/auth-agent.py &
agent_pid=$!

cleanup() {
    kill "$agent_pid" 2>/dev/null || true
}
trap cleanup INT TERM EXIT

exec /usr/sbin/sshd -D -E /var/log/auth.log
