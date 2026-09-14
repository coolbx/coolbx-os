#!/usr/bin/env bash
# Coolbx OS — kiosk-feature (ADR-0006/0016/0029): generieke, vergrendelde sway-sessie voor één
# kiosk-app (browser --app). Apps zijn data (apps.d/*.yaml); Focus is er één van (focus-feature).
set -ouex pipefail

# sway + waybar = de kiosk-compositor; dbus-x11 levert dbus-launch (waybar zonder user-dbus);
# python3-pyyaml voor de app-registry.
dnf5 install -y --setopt=install_weak_deps=False sway waybar dbus-x11 python3-pyyaml

chmod 0755 /usr/bin/coolbx-kiosk-start /usr/bin/coolbx-kiosk-exit /usr/bin/coolbx-kiosk-apps \
           /usr/bin/coolbx-vt-lock /usr/bin/coolbx-kiosk-return \
           /usr/share/coolbx/kiosk/chromium-kiosk.sh /usr/share/coolbx/kiosk/apply-scale.sh
systemctl enable coolbx-kiosk-cleanup.service

# DEV/PROD-gate (ADR-0022): de prod-only browser-hardening (DeveloperToolsAvailability:2, file://-blok)
# breekt de e2e-harness (CDP) en de dev-placeholder. In een DEV-build weg; prod behoudt 'm.
if [[ "${ENABLE_FIRSTBOOT_USER:-0}" == "1" ]]; then
  echo "DEV-build: prod-only browser-hardening verwijderen + test-kiosk-app toevoegen"
  rm -f /etc/chromium/policies/managed/coolbx-hardening-prod.json
  cat > /usr/share/coolbx/kiosk/apps.d/test.yaml <<'YAML'
# DEV-ONLY test-app (bestaat niet in prod-builds): de lokale placeholder-pagina.
name: Testmodus
url: file:///usr/share/coolbx/kiosk/placeholder.html
icon: coolbx-kiosk
YAML
fi

# Launchers + dock-favorieten voor de image-default apps (features die ná kiosk komen — bv. focus —
# draaien 'apply --image' opnieuw).
/usr/bin/coolbx-kiosk-apps apply --image

echo "kiosk feature installed"
