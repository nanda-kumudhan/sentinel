FROM debian:13

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server iproute2 iputils-ping python3 python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash labuser \
    && echo 'labuser:sentinel-lab' | chpasswd \
    && mkdir -p /run/sshd \
    && touch /var/log/auth.log \
    && sed -ri 's/^#?PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -ri 's/^#?PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config
RUN python3 -m venv /opt/venv \
    && /opt/venv/bin/pip install --no-cache-dir 'kafka-python>=2.0,<3.0'

COPY docker/victim/auth_agent.py /usr/local/bin/auth-agent.py
COPY sentinel /opt/sentinel/sentinel
COPY docker/victim/entrypoint.sh /usr/local/bin/victim-entrypoint.sh
RUN chmod 0755 /usr/local/bin/auth-agent.py /usr/local/bin/victim-entrypoint.sh
ENV PYTHONPATH=/opt/sentinel
ENV PATH=/opt/venv/bin:$PATH

EXPOSE 22

ENTRYPOINT ["/usr/local/bin/victim-entrypoint.sh"]
