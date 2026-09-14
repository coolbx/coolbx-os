#!/usr/bin/env bash
# Coolbx OS — role-gedeeld (ADR-0030/0031): lokale wachtwoordloze gebruiker 'leerling', autologin bij
# boot, home gewist bij afmelden en bij opstart; leerling-dconf-locks; toestel-default rol=gedeeld.
set -ouex pipefail
chmod 0755 /usr/bin/coolbx-gedeeld-reset /etc/gdm/PostSession/Default
systemctl enable coolbx-gedeeld-reset.service

# Wachtwoordloos aanmelden in GDM: pam_succeed_if vóór de gewone stack (alleen deze gebruiker).
PAMF=/etc/pam.d/gdm-password
if [ -f "$PAMF" ] && ! grep -q 'coolbx-gedeeld' "$PAMF"; then
  sed -i '0,/^auth/s//auth        sufficient    pam_succeed_if.so user = leerling quiet_success  # coolbx-gedeeld\nauth/' "$PAMF"
fi

# Autologin bij boot (prod). In een DEV-build blijft de tester-autologin (02-config.sh) staan.
if [[ "${ENABLE_FIRSTBOOT_USER:-0}" != "1" ]]; then
  install -d /etc/gdm
  cat > /etc/gdm/custom.conf <<'CONF'
[daemon]
AutomaticLoginEnable=True
AutomaticLogin=leerling
CONF
fi

# Zelfde leerling-vergrendeling als role-leerling (één bron).
install -D -m0644 /ctx/features/role-leerling/system_files/etc/dconf/db/local.d/30-coolbx-leerling \
  /etc/dconf/db/local.d/30-coolbx-leerling
install -D -m0644 /ctx/features/role-leerling/system_files/etc/dconf/db/local.d/locks/30-coolbx-leerling \
  /etc/dconf/db/local.d/locks/30-coolbx-leerling
install -d /etc/coolbx
printf 'C /etc/coolbx/device.yaml 0644 root root - /usr/share/coolbx/device.yaml\n' > /usr/lib/tmpfiles.d/coolbx-device.conf
command -v dconf >/dev/null && dconf update || true
echo "role-gedeeld installed"
