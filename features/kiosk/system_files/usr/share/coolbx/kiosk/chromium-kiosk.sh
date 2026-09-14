#!/usr/bin/env bash
# Start de browser in kiosk-modus (--app, één venster); herstart bij crash met een limiet.
# Browser-agnostisch: Google Chrome (chrome-feature) of Fedora-Chromium (chromium-feature) — beide
# lezen de gedeelde Coolbx-policy-dir. Flags bewezen in de kiosk-sessie (ADR-0015 + S3).
set -uo pipefail

URL="${COOLBX_KIOSK_URL:?COOLBX_KIOSK_URL ontbreekt}"
BIN="$(command -v google-chrome-stable || command -v google-chrome || command -v chromium-browser || command -v chromium || true)"
[ -n "$BIN" ] || { echo "geen browser gevonden (chrome/chromium)" >&2; exit 1; }
PROFILE="${XDG_RUNTIME_DIR:-$HOME}/coolbx-chrome"

# DEV-ONLY (ADR-0020): CDP-debugpoort voor de e2e-harness. NOOIT in productie — de prod-image zet
# COOLBX_KIOSK_DEBUG nooit. user-data-dir is sowieso gezet (Chrome 136+ vereist dat).
DEBUG_FLAGS=()
if [ "${COOLBX_KIOSK_DEBUG:-0}" = "1" ]; then
  echo "WAARSCHUWING: CDP-debugpoort 9222 actief (COOLBX_KIOSK_DEBUG=1) — DEV ONLY" >&2
  DEBUG_FLAGS=(
    --remote-debugging-port=9222
    --remote-allow-origins=http://127.0.0.1:9222
  )
fi
# DEV-ONLY: laad een extensie UNPACKED (test van managed-storage zonder force-install).
if [ -n "${COOLBX_KIOSK_LOAD_EXT:-}" ] && [ -d "${COOLBX_KIOSK_LOAD_EXT}" ]; then
  echo "DEV: unpacked extensie laden uit ${COOLBX_KIOSK_LOAD_EXT}" >&2
  DEBUG_FLAGS+=(
    "--load-extension=${COOLBX_KIOSK_LOAD_EXT}"
    "--disable-extensions-except=${COOLBX_KIOSK_LOAD_EXT}"
  )
fi

n=0
while [ "$n" -lt 10 ]; do
  # Singleton afdwingen: een nieuwe start zou anders z'n URL aan de bestaande instance overdragen
  # (handoff) en meteen terugkeren → stapels vensters. Eerst opruimen.
  pkill -f -- "--user-data-dir=$PROFILE" 2>/dev/null && sleep 1 || true

  GPU_FLAGS=()
  [ "${COOLBX_KIOSK_SW_RENDER:-0}" = "1" ] && GPU_FLAGS+=(--disable-gpu)

  start=$SECONDS
  "$BIN" \
    --ozone-platform=wayland \
    --user-data-dir="$PROFILE" \
    --password-store=basic \
    "${GPU_FLAGS[@]}" \
    --disable-dev-shm-usage \
    --no-first-run --no-default-browser-check \
    --disable-session-crashed-bubble --disable-infobars \
    --start-maximized \
    "${DEBUG_FLAGS[@]}" \
    --app="$URL" || true

  # Te snel terug (<5s) = handoff of directe crash → tel als faal (anti-spin).
  if [ $(( SECONDS - start )) -lt 5 ]; then n=$((n + 1)); else n=0; fi
  sleep 1
done

# Te veel crashes → sessie netjes beëindigen (terug naar GNOME via ExecStopPost).
swaymsg exit 2>/dev/null || true
