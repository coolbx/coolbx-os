# ADR-0029: Generieke kiosk-apps uit config; Focus als kiosk-app in een aparte feature

- **Status:** Aanvaard
- **Datum:** 2026-09-14
- **Beslissers:** Johan, Claude

## Context
De kiosk (sway + waybar + browser op een eigen VT, VT-vergrendeld, ADR-0006/0016) is gebouwd en getest,
maar kende één hardgecodeerde app: Focus. Scholen willen "maak de toets in app X" voor willekeurige
web-apps (Bingel, Smartschool-toets, …). ChromeOS biedt kiosk-apps in het aanmeldscherm; wij overwogen
dat, maar de leerling werkt meestal gewoon in de sessie en wordt dán gevraagd te wisselen.

## Beslissing
- De kiosk start **alleen vanuit een lopende GNOME-sessie**, via één launcher per app. Niet vanuit GDM.
- **sway + waybar blijven** (balk bovenaan: wifi, batterij, klok, "Sessie afsluiten" met bevestiging).
  gnome-kiosk werd overwogen maar heeft geen balk en geen VT-vergrendeling.
- Apps zijn **data**: YAML-bestanden in `/usr/share/coolbx/kiosk/apps.d/` (image-defaults) en
  `/etc/coolbx/kiosk-apps.d/` (config, root-only, via ansible). Velden: `id`, `name`, `icon`, `url`,
  optioneel `allow_domains` (→ URLBlocklist `*` + allowlist tijdens de sessie) en `policy` (extra
  Chromium-policies tijdens de sessie). `coolbx-kiosk-apps apply` genereert de launchers.
- De launcher geeft **enkel de app-id** door aan `coolbx-kiosk-start`; URL en policy komen uit het
  root-bestand. Een leerling kan geen eigen URL injecteren.
- Per-app-policy leeft als `coolbx-kiosk-app.json` in de Chromium-policy-dir **alleen zolang de kiosk
  draait** (opgeruimd door kiosk-return en een boot-cleanup) — zelfde patroon als de exam-policy.
- **Focus** = de `focus`-feature: force-install + managed-storage, attestatie/exam-policy (voormalige
  `attest`), native-messaging-host, en één kiosk-app `focus` ("Toetsmodus") met `allow_domains` op de
  Focus-infra. De daemon-gestuurde per-examen-allowlist blijft ongewijzigd.

## Gevolgen
`kiosk` is Focus-vrij en browser-agnostisch (Chrome of Chromium). Tests/greenboot/status mogen geen
Focus-bestanden meer als OS-invariant nemen. Dev-e2e gebruikt een `test`-app met de placeholder.

## Alternatieven
- Kiosk-apps in GDM als wachtwoordloze gebruikers per app: verworpen, past niet bij "leerling werkt in sessie".
- gnome-kiosk: verworpen (geen balk, geen VT-lock, geen bewezen escape-tests).
