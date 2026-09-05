# Sentinel

Sentinel is a local, isolated container lab for authorized network and SSH
testing. It starts five Ubuntu SSH victims, a Debian-based attacker toolbox,
and a Kafka/Zookeeper pair on one private Docker network. Authentication
events flow through a versioned JSON schema to Kafka, are persisted by the
consumer in PostgreSQL, and are correlated across the fleet.

> Use this lab only on systems and accounts you own or are explicitly
> authorized to test. The credentials below are intentionally weak for local
> training and must not be reused outside this lab.

## Requirements

- Docker Engine with Docker Compose
- Python 3.10+ (for the optional virtual environment)

## Start the lab

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

docker compose up -d --build
docker compose ps
```

The services use the private `sentinel_net` bridge network and are addressable
by service name:

| Service | Hostname | Purpose |
| --- | --- | --- |
| `victim1`-`victim5` | matching service name | Ubuntu SSH targets |
| `attacker` | `attacker` | Debian toolbox with `nmap`, `hydra`, and SSH client |
| `zookeeper` | `zookeeper` | Kafka coordination |
| `kafka` | `kafka` | Kafka broker on port `9092` inside the network |
| `postgres` | `postgres` | PostgreSQL event and alert store |
| `consumer` | `consumer` | Kafka-to-PostgreSQL consumer and correlation service |

## Verify connectivity and SSH

Run the included checks from the attacker container:

```bash
docker compose exec attacker /usr/local/bin/check-lab.sh
docker compose exec attacker ssh -o StrictHostKeyChecking=no \
  -o PreferredAuthentications=password -o PubkeyAuthentication=no \
  labuser@victim1 'hostname && id'
```

  Each victim also runs `/usr/local/bin/auth-agent.py`. It checks for a usable
  systemd journal first and otherwise tails `/var/log/auth.log`, emitting JSON
  events for failed SSH logins. Five failures from one source IP within 30
  seconds produce a local `repeated_ssh_failures` alert in the victim's
  container logs:

  ```bash
  docker compose logs -f victim1
  ```

## Detection components

`sentinel/event_schema.py` is the shared version-1 event contract. The victim
agent continues to print local JSON and, when `KAFKA_BOOTSTRAP_SERVERS` is set,
publishes the same event to `security-events`. The consumer validates events,
stores them in `security_events`, and stores correlation alerts in
`security_alerts`. A distributed brute-force alert is emitted when one source
IP reaches at least three distinct hosts within 60 seconds and is tagged with
MITRE ATT&CK `T1110` (Brute Force).

`sentinel/anomaly.py` provides an optional scikit-learn Isolation Forest
training/scoring API for downstream analysis; it is deliberately separate from
the streaming consumer so a model can be trained with an operator-selected
baseline.

The attacker toolbox includes authorized lab-only demonstrations:

```bash
docker compose exec attacker /usr/local/bin/hydra-bruteforce.sh victim1
docker compose exec attacker /usr/local/bin/nmap-recon.sh victim1
```

Run unit tests with `pytest -q`. Bring up the full pipeline with
`docker compose up -d --build`, inspect events with
`docker compose exec postgres psql -U sentinel -d sentinel`, and tear it down
with `docker compose down -v`.

### Design decisions

- JSON over Kafka keeps the agent lightweight and makes events inspectable.
- PostgreSQL JSONB preserves the raw event while identity columns support
  future dashboards and queries.
- Correlation is deterministic and timestamp-based, making it testable without
  Kafka or a database. Isolation Forest remains an opt-in batch module.
- All services use the existing private bridge network; no victim SSH ports
  are published to the host.

  The lab credentials are `labuser` / `sentinel-lab`. Stop and remove the lab
  with:

```bash
docker compose down
```

## Files

- `docker-compose.yml` defines the complete fleet and private network.
- `docker/victim/Dockerfile` builds the SSH-enabled victim image.
- `docker/attacker/Dockerfile` builds the network-testing toolbox.
- `requirements.txt` contains optional Python tooling dependencies.
