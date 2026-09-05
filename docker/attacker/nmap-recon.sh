#!/bin/sh
set -eu

target="${1:-victim1}"
nmap -sV -Pn -T2 "$target"
