#!/usr/bin/env bash
# Coolbx OS — chromium-feature (ADR-0011/0033): Fedora-Chromium als browser (fallback / dev-harnas).
# Leest de gedeelde Coolbx-policy-dir /etc/chromium/policies/managed. Zonder Chrome Enterprise Core.
set -ouex pipefail

dnf5 install -y --setopt=install_weak_deps=False chromium

# Camera via PipeWire/portal (libcamera/IPU6-camera's; UVC blijft werken). Standaard UIT in Chromium;
# Fedora-chromium sourcet /etc/chromium/chromium.conf → idempotent appenden.
CONF=/etc/chromium/chromium.conf
if [ -f "$CONF" ] && ! grep -q 'WebRtcPipeWireCamera' "$CONF"; then
  printf '\n# Coolbx OS: camera via PipeWire/portal (libcamera)\nCHROMIUM_FLAGS="${CHROMIUM_FLAGS} --enable-features=WebRtcPipeWireCamera"\n' >> "$CONF"
fi

echo "chromium feature installed"
