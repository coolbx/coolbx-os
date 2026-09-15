#!/usr/bin/env bash
# Coolbx OS — chrome-feature (ADR-0033): Google Chrome (stable) + Chrome Enterprise Core-gereedheid.
#  - Chrome uit Google's RPM-repo in het image (updates via de dagelijkse image-build).
#  - /etc/opt/chrome/policies/managed → symlink naar de gedeelde Coolbx-policy-dir zodat kiosk-/
#    hardening-policies browser-agnostisch blijven (ADR-0029).
#  - /etc/opt/chrome/policies/enrollment/ bestaat; het CloudManagementEnrollmentToken komt via de
#    config-repo (vault) op het toestel — nooit in het publieke image.
#  - Chrome = standaardbrowser (mimeapps).
set -ouex pipefail

echo "::group:: chrome: Google Chrome stable"
cat > /etc/yum.repos.d/google-chrome.repo <<'REPO'
[google-chrome]
name=google-chrome
baseurl=https://dl.google.com/linux/chrome/rpm/stable/x86_64
enabled=1
gpgcheck=1
gpgkey=https://dl.google.com/linux/linux_signing_key.pub
REPO
dnf5 install -y --setopt=install_weak_deps=False google-chrome-stable
# De RPM plant een cron-job + eigen repo-file voor zelf-updates; op bootc komen updates via het image.
rm -f /etc/cron.daily/google-chrome /etc/yum.repos.d/google-chrome.repo
echo "::endgroup::"

echo "::group:: chrome: gedeelde policy-dir + enrollment-pad"
install -d -m0755 /etc/chromium/policies/managed /etc/opt/chrome/policies/enrollment
if [ -d /etc/opt/chrome/policies/managed ] && [ ! -L /etc/opt/chrome/policies/managed ]; then
  # Eventuele bestaande bestanden meenemen naar de gedeelde dir.
  cp -an /etc/opt/chrome/policies/managed/. /etc/chromium/policies/managed/ 2>/dev/null || true
  rm -rf /etc/opt/chrome/policies/managed
fi
ln -sfn /etc/chromium/policies/managed /etc/opt/chrome/policies/managed
echo "::endgroup::"

echo "::group:: chrome: standaardbrowser"
install -d /etc/xdg
cat > /etc/xdg/mimeapps.list <<'MIME'
[Default Applications]
text/html=google-chrome.desktop
application/xhtml+xml=google-chrome.desktop
x-scheme-handler/http=google-chrome.desktop
x-scheme-handler/https=google-chrome.desktop
MIME
echo "::endgroup::"

chmod 0755 /usr/libexec/coolbx-chrome-first-run
echo "chrome feature installed"
