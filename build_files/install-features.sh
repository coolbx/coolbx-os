#!/usr/bin/env bash
set -ouex pipefail

# Modulair feature-mechanisme (ADR-0012). FEATURES = spatie-gescheiden lijst.
# Een Containerfile kan niet loopen → dit script doet het in bash.
FEATURES="${1:-${FEATURES:-}}"
FEATURES_DIR="/ctx/features"

for feat in $FEATURES; do
  fdir="${FEATURES_DIR}/${feat}"
  if [[ ! -d "$fdir" ]]; then
    # Hard falen (F-02-051): een typo in FEATURES mag geen stil featureloos
    # image opleveren (een kale build zonder kiosk/attest slaagt anders en de
    # e2e-suite valt pas veel later om). Beschikbare features tonen.
    echo "::error::feature '${feat}' niet gevonden in ${FEATURES_DIR}" >&2
    echo "Beschikbare features: $(cd "${FEATURES_DIR}" && ls -d */ 2>/dev/null | tr -d '/' | tr '\n' ' ')" >&2
    exit 1
  fi
  echo "== feature: ${feat} =="
  # Self-contained: kopieer eventuele system_files en draai install.sh.
  if [[ -d "${fdir}/system_files" ]]; then
    cp -r "${fdir}/system_files/." /
  fi
  if [[ -f "${fdir}/install.sh" ]]; then
    bash "${fdir}/install.sh"
  fi
done

# Icon-cache NA alle features (een feature die na 'branding' komt — bv. focus — voegt anders iconen toe
# aan een al gebouwde cache; GTK vertrouwt die cache en vindt het icoon dan niet → generiek fallback-icoon).
if command -v gtk-update-icon-cache >/dev/null 2>&1 && [ -d /usr/share/icons/hicolor ]; then
  gtk-update-icon-cache -f -q /usr/share/icons/hicolor || echo "warn: icon-cache update mislukt"
fi
