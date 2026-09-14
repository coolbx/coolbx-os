# ADR-0031: Accountmodel — Google Secure LDAP via SSSD, gedeelde lokale gebruiker, beheerder `coolbx`

- **Status:** Aanvaard (vervangt ADR-0008)
- **Datum:** 2026-09-14
- **Beslissers:** Johan, Claude

## Context
ADR-0008 koos voor een autologin-gastprofiel in de pilot. De heropname wil Chromebook-gedrag: elke
leerling/leerkracht meldt aan met het school-Google-account en krijgt een eigen, blijvende home; een
ander account op hetzelfde toestel = nieuwe home. De school heeft Workspace for Education Fundamentals,
waarin **Secure LDAP** gratis zit. Alternatieven (Canonical **authd** met Google-broker, OpenID Connect)
zijn Ubuntu-only; Fedora heeft vandaag geen volwassen OIDC-login voor GDM.

Geverifieerd op 14 sep 2026 tegen de sandbox (`docs/WORKSPACE.md`): TLS-clientcert + toegangsgegevens
werken; gebruikers zijn `posixAccount` (uidNumber/gidNumber/homeDirectory/loginShell/memberOf), groepen
`posixGroup`+`groupOfNames`; bind met volledige DN én met e-mail werkt; **secundaire domeinen zijn aparte
subbomen** (`dc=lln,dc=edugolo,dc=be` naast `dc=edugolo,dc=be`), een sub-search vanaf de hoofdboom vindt
ze niet.

## Beslissing
1. **`google-login`-feature**: SSSD (`id_provider = ldap`, `ldap_schema = rfc2307bis`, `ldaps://ldap.google.com`,
   clientcert), `cache_credentials = true` (offline aanmelden na één online login), oddjob-mkhomedir,
   authselect `sssd with-mkhomedir`, GDM zonder gebruikerslijst. **Meerdere zoekbases** (per domein),
   login by e-mail én by uid; het profiel geeft een `domain` op dat het OS op het aanmeldscherm aanvult.
2. **Toegang per toestel op Google-groep** (`access_provider = simple`, `simple_allow_groups`): de groepen
   komen uit het toestelprofiel. Leerling-laptop: leerlingen + ict; leerkracht-laptop: personeel. De grens
   is de groep, het domein is gemak; alles is config, niets school-specifieks in het image.
3. **Gedeeld toestel**: lokale gebruiker `leerling`, wachtwoordloos in GDM (PAM `pam_succeed_if` op die
   gebruiker in `gdm-password`), autologin bij boot, home gewist bij afmelden (GDM PostSession) en bij boot.
4. **Verborgen beheerder `coolbx`** op elk toestel: lokaal, uid < 1000 (niet in GDM-lijst), lid van wheel
   (sudo). Wachtwoord komt uit de installer/config-repo (vault), nooit uit het publieke image. Geen enkele
   gewone gebruiker (ook de leerkracht niet) is beheerder.
5. **Geen welkomstwizard** (gnome-initial-setup) — identiteit komt van Google.
6. Tweestapsverificatie: LDAP is wachtwoord-only; **bewust zo gelaten** (Johan, 14 sep). PAM-faillock
   tegen brute force wél.

## Gevolgen
Certificaat verloopt **13 sep 2029** — runbook-item. Geheimen (cert/key/toegangsgegevens) via ansible-vault
naar `/etc/sssd/` (root-only). Bij powerwash verdwijnen homes + SSSD-cache; identiteit blijft in Google.

## Alternatieven
- authd/OIDC: later, zodra op Fedora beschikbaar; zelfde feature-naad.
- Lokale accounts + welkomstwizard: verworpen (wachtwoordbeheer over de vloot, geen Chromebook-gedrag).
