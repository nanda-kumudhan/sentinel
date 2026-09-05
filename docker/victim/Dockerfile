FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server iproute2 iputils-ping python3 \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash labuser \
    && echo 'labuser:sentinel-lab' | chpasswd \
    && mkdir -p /run/sshd \
    && touch /var/log/auth.log \
    && sed -ri 's/^#?PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -ri 's/^#?PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config

COPY auth_agent.py /usr/local/bin/auth-agent.py
COPY entrypoint.sh /usr/local/bin/victim-entrypoint.sh
RUN chmod 0755 /usr/local/bin/auth-agent.py /usr/local/bin/victim-entrypoint.sh

EXPOSE 22

ENTRYPOINT ["/usr/local/bin/victim-entrypoint.sh"]
