# Sentinel

Sentinel is a small, local security lab. It creates five Linux containers to
act as SSH targets, an attacker container with Hydra and Nmap, and a Kafka +
PostgreSQL pipeline for collecting and correlating login failures.

Use it only on systems you own or are allowed to test. Everything runs on a
private Docker network. The lab username is `labuser` and the password is
`sentinel-lab`.

## Start it

You need Docker Compose and Python 3.

```bash
cd ~/Github/sentinel
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
docker compose up -d --build
docker compose ps
```

## Try it

Check that the containers can see each other and that SSH works:

```bash
docker compose exec attacker /usr/local/bin/check-lab.sh
docker compose exec attacker ssh -o StrictHostKeyChecking=no \
  -o PreferredAuthentications=password -o PubkeyAuthentication=no \
  labuser@victim1 'hostname && id'
```

Each victim watches its SSH log. Five failures from the same IP within
30 seconds produce a local alert:

```bash
docker compose logs -f victim1
```

The agents also send JSON events to Kafka. The consumer stores them in
PostgreSQL and raises a distributed brute-force alert when one IP reaches
three victims within 60 seconds. Those alerts are tagged with MITRE ATT&CK
technique `T1110` (Brute Force).

The attacker container includes two lab demonstrations:

```bash
docker compose exec attacker /usr/local/bin/hydra-bruteforce.sh victim1
docker compose exec attacker /usr/local/bin/nmap-recon.sh victim1
```

The project also includes an optional Isolation Forest model in
`sentinel/anomaly.py`. It gives unusual events a lower anomaly score, but it
is currently a separate batch experiment rather than part of the live
consumer.

## Development

Run the tests with:

```bash
pytest -q
```

Stop the lab and remove its database volume with:

```bash
docker compose down -v
```
