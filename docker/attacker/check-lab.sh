#!/bin/sh
set -eu

for victim in victim1 victim2 victim3 victim4 victim5; do
    printf '%s: ' "$victim"
    getent hosts "$victim" >/dev/null
    nc -z -w 5 "$victim" 22
    printf 'DNS and SSH reachable\n'
done

printf 'kafka: '
nc -z -w 5 kafka 9092
printf 'Kafka reachable\n'

printf 'zookeeper: '
nc -z -w 5 zookeeper 2181
printf 'Zookeeper reachable\n'
