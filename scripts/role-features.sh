#!/usr/bin/env bash
# Eén bron van waarheid voor de rol-samenstellingen (ADR-0030, ROADMAP v3 §3).
#   scripts/role-features.sh leerling|leerkracht|gedeeld|dev
set -euo pipefail
COMMON="chrome kiosk branding hardware fleet managed apps media-nonfree admin"
case "${1:-}" in
  leerling)   echo "$COMMON google-login role-leerling" ;;
  leerkracht) echo "$COMMON google-login role-leerkracht" ;;
  gedeeld)    echo "$COMMON role-gedeeld" ;;
  dev)        echo "$COMMON chromium focus" ;;
  *) echo "gebruik: $0 leerling|leerkracht|gedeeld|dev" >&2; exit 2 ;;
esac
