FROM debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-client nmap hydra iputils-ping dnsutils netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY docker/attacker/check-lab.sh /usr/local/bin/check-lab.sh
COPY docker/attacker/hydra-bruteforce.sh /usr/local/bin/hydra-bruteforce.sh
COPY docker/attacker/nmap-recon.sh /usr/local/bin/nmap-recon.sh
RUN printf 'password\n123456\nsentinel\n' > /usr/share/wordlists/sentinel-passwords.txt \
    && chmod 0755 /usr/local/bin/check-lab.sh /usr/local/bin/hydra-bruteforce.sh /usr/local/bin/nmap-recon.sh

CMD ["sleep", "infinity"]
