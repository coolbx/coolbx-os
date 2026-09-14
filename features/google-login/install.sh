#!/usr/bin/env bash
# Coolbx OS — google-login-feature (ADR-0031): SSSD tegen Google Secure LDAP, home bij eerste
# aanmelding, toegang per Google-groep, offline-cache. Config + geheimen komen op het toestel via de
# config-repo; tot dan blijft sssd uit (alleen lokale accounts).
set -ouex pipefail

dnf5 install -y --setopt=install_weak_deps=False \
  sssd sssd-ldap sssd-tools oddjob oddjob-mkhomedir authselect python3-pyyaml
chmod 0755 /usr/libexec/coolbx-google-login-apply
# PAM/NSS: sssd + mkhomedir + faillock (brute-force-rem). Idempotent.
authselect select sssd with-mkhomedir with-faillock --force
# oddjobd maakt de home aan bij eerste aanmelding (pam_oddjob_mkhomedir).
systemctl enable oddjobd.service
# sssd pas actief na coolbx-google-login-apply (config aanwezig); zonder config faalt sssd anders bij boot.
systemctl disable sssd.service 2>/dev/null || true
install -d -m0755 /etc/coolbx/google-login
command -v dconf >/dev/null && dconf update || true
echo "google-login feature installed"
