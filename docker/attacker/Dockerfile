FROM debian:12-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-client nmap hydra iputils-ping dnsutils netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

COPY check-lab.sh /usr/local/bin/check-lab.sh
RUN chmod 0755 /usr/local/bin/check-lab.sh

CMD ["sleep", "infinity"]
