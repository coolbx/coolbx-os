#!/usr/bin/env bash
# Coolbx OS — role-leerling (ADR-0030): dconf-vergrendeling leerling + toestel-default rol=leerling.
set -ouex pipefail
install -d /etc/coolbx
printf 'C /etc/coolbx/device.yaml 0644 root root - /usr/share/coolbx/device.yaml\n' > /usr/lib/tmpfiles.d/coolbx-device.conf
command -v dconf >/dev/null && dconf update || true
echo "role-leerling installed"
