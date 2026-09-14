# ADR-0032: Config-naad — `device.yaml` op het toestel, git-profielen, platte serienummerlijst

- **Status:** Aanvaard (vervangt de OU-boom uit `coolbx-ansible/DESIGN.md`, 29 jun 2026)
- **Datum:** 2026-09-14
- **Beslissers:** Johan, Claude

## Context
Johan wil (nog) geen directory/OU-boom voor configuratie, wel iets git-gebaseerds waarbij **het toestel
zelf** bepaalt welk type config het krijgt. De identiteits-directory bestaat al (Google Workspace) en
wordt niet gerepliceerd.

## Beslissing
Drie lagen, elk met een eigen bron (zie ROADMAP §3):
1. **Image** = software/hardening/rol-standaard (`FEATURES`).
2. **Toestel**: `/etc/coolbx/device.yaml` met `role`, `profile`, `channel` (default uit de rol-feature;
   ingevuld door de installer). De **config-repo** (`github.com/coolbx/coolbx-ansible`) bevat
   `profiles/<naam>.yml` (basis + specifieke lagen: kiosk-apps, dconf, Chrome-policies, flatpaks,
   printers, google-login-groepen) en een **platte `devices.yml`** met per serienummer: naam, profiel,
   eventueel kanaal/powerwash-vlag. Resolutie (in deze volgorde, eerste treffer wint): (1) `devices.yml`-
   match op serienummer (BIOS; hostnaam via veld `name` als fallback in VM's), (2) een expliciet
   `profile` in het lokale `device.yaml`, (3) `<rol>-standaard`. Een toestel dat in `devices.yml` staat,
   volgt dus altijd git; "lokaal overschrijven" geldt voor toestellen die (nog) niet in de lijst staan.
3. **Gebruiker**: Chrome-beleid uit de Google Admin-console; Google-groep → dconf-profiel-mapping in git.

Motor: de bestaande `coolbx-ansible-pull` (fleet-feature), uitgebreid: leest `device.yaml` + serienummer,
kanaal → git-branch, vault-wachtwoord uit `/etc/coolbx/vault-pass` (root-only, door de installer gezet).
Geheimen (LDAP-cert/key/toegangsgegevens, Chrome-token, beheerderswachtwoord-hash) in **ansible-vault**.
De repo is vandaag publiek; vault maakt dat draaglijk, **advies: privé zetten**.

Installer: school-specifieke Anaconda-ISO (BIB) waarvan de kickstart `device.yaml`, `ansible.conf`,
`vault-pass` en het beheerderswachtwoord zet uit een lokaal, git-genegeerd `school.env`. Installeren = ingeschreven.

## Gevolgen
Geen registry/UI nodig; later kan een UI enkel `devices.yml`/`device.yaml` schrijven. Alles reviewbaar in git.

## Alternatieven
OU-boom (DESIGN.md jun 2026): uitgesteld — de platte lijst dekt de behoefte; Google levert groepen.
