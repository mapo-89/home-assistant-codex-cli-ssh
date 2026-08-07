FROM ghcr.io/home-assistant/base:latest

ARG BUILD_VERSION
ARG BUILD_ARCH

LABEL \
  io.hass.name="Codex CLI SSH" \
  io.hass.description="Privileged SSH/CLI workspace with persistent Codex state" \
  io.hass.version="${BUILD_VERSION}" \
  io.hass.type="app" \
  io.hass.arch="${BUILD_ARCH}"

ENV CODEX_HOME=/data/codex \
    HOME=/root \
    PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

RUN apk add --no-cache \
      bash \
      ca-certificates \
      git \
      nodejs \
      npm \
      openssh-server \
      python3 \
    && npm install --global @openai/codex@latest \
    && npm cache clean --force \
    && mkdir -p /run/sshd /root/.ssh /data/codex \
    && chmod 700 /root/.ssh /data/codex \
    && printf '%s\n' \
      'export CODEX_HOME=/data/codex' \
      'export HOME=/root' \
      'export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' \
      > /etc/profile.d/codex.sh \
    && chmod 644 /etc/profile.d/codex.sh

COPY run.sh /run.sh
COPY init_codex.py /usr/local/libexec/init_codex.py
COPY codex-ha /usr/local/bin/codex-ha
RUN chmod 755 /run.sh /usr/local/libexec/init_codex.py /usr/local/bin/codex-ha

WORKDIR /homeassistant
EXPOSE 22
CMD [ "/run.sh" ]
