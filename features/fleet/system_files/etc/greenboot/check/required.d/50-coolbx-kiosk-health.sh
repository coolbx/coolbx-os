#!/usr/bin/env bash
# Coolbx OS — greenboot required health-check (Fase 5). Bij N gefaalde boots rolt bootc/ostree
# automatisch terug naar de vorige deployment. LOKAAL ONLY: nooit een externe dienst checken —
# een externe outage zou anders de hele vloot doen terugrollen (ADR-0017, roadmap §Updates).
# Feature-bewust (ADR-0012/0029): kiosk-checks alleen als de kiosk-feature aanwezig is.
set -uo pipefail

fail=0
chk() { if eval "$2" >/dev/null 2>&1; then echo "OK   $1"; else echo "FAIL $1"; fail=1; fi; }

chk "gdm actief"                 'systemctl is-active --quiet gdm'
chk "browser aanwezig"           'command -v google-chrome-stable || command -v chromium-browser || command -v chromium'
if [ -e /usr/share/coolbx/kiosk/sway.conf ]; then
  chk "kiosk-launcher aanwezig"  'test -x /usr/bin/coolbx-kiosk-start'
  chk "sway aanwezig"            'command -v sway'
fi
chk "geen kritieke failed units" 'test "$(systemctl --failed --no-legend --plain | wc -l)" -lt 3'

[ "$fail" -eq 0 ] && echo "coolbx-health: GROEN" || echo "coolbx-health: ROOD"
exit "$fail"
