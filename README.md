# Sentinel

Sentinel is a local, isolated container lab for authorized network and SSH
testing. It starts five Ubuntu SSH victims, a Debian-based attacker toolbox,
and a Kafka/Zookeeper pair on one private Docker network.

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

## Verify connectivity and SSH

Run the included checks from the attacker container:

```bash
docker compose exec attacker /usr/local/bin/check-lab.sh
docker compose exec attacker ssh -o StrictHostKeyChecking=no \
  -o PreferredAuthentications=password -o PubkeyAuthentication=no \
  labuser@victim1 'hostname && id'
```

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
