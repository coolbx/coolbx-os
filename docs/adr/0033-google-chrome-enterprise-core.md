# ADR-0033: Google Chrome + Chrome Enterprise Core als `chrome`-feature (Chromium blijft fallback)

- **Status:** Aanvaard (verfijnt ADR-0011)
- **Datum:** 2026-09-14
- **Beslissers:** Johan, Claude

## Context
De Chromebook-ervaring komt grotendeels van centraal browserbeheer. **Chrome Enterprise Core** is gratis
($0, geverifieerd 14 sep 2026), werkt op Linux via een tokenbestand
(`/etc/opt/chrome/policies/enrollment/CloudManagementEnrollmentToken`) en beheert de browser vanuit de
Google Admin-console (per OU/groep; per gebruiker zodra die inlogt). Het vereist Google Chrome; Fedora-
Chromium mist de API-sleutels voor de inschrijving. De `media-nonfree`-feature haalde Widevine al uit de
Chrome-RPM. Token voor OU `/coolbx-sandbox` staat klaar.

## Beslissing
- **`chrome`-feature**: Google Chrome (stable) uit Google's RPM-repo in het image (updates via de dagelijkse
  image-build). `/etc/opt/chrome/policies/managed` wordt een symlink naar de gedeelde Coolbx-policy-dir
  (`/etc/chromium/policies/managed`), zodat kiosk-/hardening-policies browser-agnostisch blijven.
  Het enrollment-token komt via de config-repo (vault) op het toestel.
- **`chromium`-feature** = de Fedora-Chromium (fallback en dev-harnas). Kiosk en policies werken met beide.
- Twee lagen beleid: het **OS** bepaalt de harde kant (kiosk-lockdown, DevTools/file://, per-app-allowlist);
  de **Admin-console** bepaalt de inhoud (bladwijzers, extensies, startpagina, sign-in).

## Gevolgen
Eén extra externe repo in de build (dl.google.com). Widevine-extractie kan vervallen wanneer Chrome zelf in
het image zit. ADR-0011's "RPM in het image, geen Flatpak" blijft gelden.

## Alternatieven
Chromium + lokale JSON alleen: blijft mogelijk (fallback) maar zonder centraal beheer.
