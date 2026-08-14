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
      patch \
      python3 \
      tmux \
      ttyd \
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

WORKDIR /config

COPY run.sh /run.sh
COPY init_codex.py /usr/local/libexec/init_codex.py
COPY codex-ha /usr/local/bin/codex-ha
COPY codex-cleanup /usr/local/bin/codex-cleanup
COPY ttyd-run /etc/services.d/ttyd/run
COPY tests/container-smoke.sh /usr/local/libexec/container-smoke.sh
COPY tests/tooling-integration.sh /usr/local/libexec/codex-tooling-integration.sh
COPY tests/test_codex_cleanup.py /usr/local/libexec/test_codex_cleanup.py
RUN chmod 755 \
      /run.sh \
      /usr/local/libexec/init_codex.py \
      /usr/local/bin/codex-ha \
      /usr/local/bin/codex-cleanup \
      /etc/services.d/ttyd/run \
      /usr/local/libexec/container-smoke.sh \
      /usr/local/libexec/codex-tooling-integration.sh \
      /usr/local/libexec/test_codex_cleanup.py \
    && /usr/local/libexec/container-smoke.sh \
    && CODEX_CLEANUP_BIN=/usr/local/bin/codex-cleanup \
      python3 /usr/local/libexec/test_codex_cleanup.py

EXPOSE 22 8099
CMD [ "/run.sh" ]
