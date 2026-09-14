#!/usr/bin/env bash
# Coolbx OS — admin-feature (ADR-0031/0034): verborgen lokale beheerder `coolbx` (wheel/sudo) +
# powerwash (marker + vroege-boot-wipe + launcher die alleen beheerders zien).
set -ouex pipefail

dnf5 install -y --setopt=install_weak_deps=False zenity
chmod 0755 /usr/bin/coolbx-powerwash
# TryExec-truc: alleen leden van wheel mogen dit uitvoeren → alleen zij zien de launcher.
chown root:wheel /usr/bin/coolbx-powerwash-gui && chmod 0750 /usr/bin/coolbx-powerwash-gui
systemctl enable coolbx-powerwash.service
echo "admin feature installed"
