FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
    && apt-get install -y --no-install-recommends openssh-server iproute2 iputils-ping \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --shell /bin/bash labuser \
    && echo 'labuser:sentinel-lab' | chpasswd \
    && mkdir -p /run/sshd \
    && sed -ri 's/^#?PasswordAuthentication .*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && sed -ri 's/^#?PermitRootLogin .*/PermitRootLogin no/' /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D", "-e"]
