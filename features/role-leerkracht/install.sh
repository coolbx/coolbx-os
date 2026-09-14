#!/usr/bin/env bash
# Coolbx OS — role-leerkracht (ADR-0030): GNOME Software (Flatpak-installs voor het eigen account),
# terminal (Ptyxis), toestel-default rol=leerkracht. Geen sudo (beheer = `coolbx`).
set -ouex pipefail
dnf5 install -y --setopt=install_weak_deps=False gnome-software ptyxis
install -d /etc/coolbx
printf 'C /etc/coolbx/device.yaml 0644 root root - /usr/share/coolbx/device.yaml\n' > /usr/lib/tmpfiles.d/coolbx-device.conf
command -v dconf >/dev/null && dconf update || true
echo "role-leerkracht installed"
