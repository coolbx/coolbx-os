#!/usr/bin/env bash
# Coolbx OS — focus-feature (ADR-0012/0029): ALLE Coolbx-Focus-binding in één optionele laag.
#  - force-install van de productie student-extensie + managed-storage (coolbx-managed.json, ADR-0021)
#  - kiosk-app 'focus' ("Toetsmodus") + lobby-/examen-policy-hooks (B3.c)
#  - toestel-attestatie: per-toestel-secret (TPM2-sealed, ADR-0027) + signing-daemon + native-messaging-host
# Vereist de kiosk-feature (eerder in FEATURES). Een kale Coolbx OS zonder deze feature kent geen Focus.
set -ouex pipefail

[ -x /usr/bin/coolbx-kiosk-apps ] || { echo "::error::focus vereist de kiosk-feature (zet 'kiosk' vóór 'focus')"; exit 1; }

echo "::group:: focus: TPM2-tooling (B3.e — sealed device-secret)"
dnf5 install -y --setopt=install_weak_deps=False tpm2-tools tpm2-tss || \
  echo "warn: tpm2-tooling niet beschikbaar — sealing valt terug op file-secret"
echo "::endgroup::"

chmod 0755 /usr/libexec/coolbx-gen-device-secret \
           /usr/libexec/coolbx-attestd \
           /usr/libexec/coolbx-attest-host \
           /usr/libexec/coolbx-exam-policy \
           /usr/bin/coolbx-enroll-info

systemctl enable coolbx-device-secret.service
systemctl enable coolbx-attestd.service
systemctl enable coolbx-exam-policy-cleanup.service

# Kiosk-app-launcher "Toetsmodus" + dock-favoriet.
/usr/bin/coolbx-kiosk-apps apply --image

echo "focus feature installed"
