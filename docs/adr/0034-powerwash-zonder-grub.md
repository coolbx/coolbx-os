# ADR-0034: Powerwash zonder GRUB-ingang; fysieke beveiliging bewust uitgesteld

- **Status:** Aanvaard
- **Datum:** 2026-09-14
- **Beslissers:** Johan, Claude

## Context
Een toestel moet op het toestel zelf "gewist/gereset" kunnen worden (Chromebook-powerwash). Een GRUB-
menu-item zou dat voor iedereen met fysieke toegang mogelijk maken. Johan wil fysieke hardening
(firmware-/GRUB-wachtwoord) voorlopig niet inplannen.

## Beslissing
- **Twee ingangen**: (1) aanmelden als beheerder `coolbx` → launcher "Toestel wissen" (bevestiging);
  (2) op afstand via een vlag in `devices.yml` (ansible-pull zet de marker). **Geen GRUB-item.**
- **Mechanisme**: marker `/var/lib/coolbx/powerwash` + herstart; een vroege-boot-unit (vóór GDM) wist
  homes, SSSD-cache, AccountsService, NetworkManager-verbindingen, Coolbx-toestelstaat (`device.yaml`,
  ansible-state, vault-pass, enrollment-token), Flatpak-userdata en journal. Systeemkritieke `/etc`-
  bestanden (fstab, machine-id, crypttab) blijven. Het image blijft. `bootc install reset` blijft een
  optie zodra stabiel (ADR-0017).
- **Fysieke beveiliging** (firmware-wachtwoord, GRUB-wachtwoord, Secure-Boot-afdwinging) is **bewust
  uitgesteld**; de uitrolgids benoemt het als aanbeveling, niet als stap.

## Gevolgen
Het lokale `coolbx`-account is de enige on-device reset-weg en werkt zonder LDAP. Na powerwash is het
toestel "net geïnstalleerd" maar niet meer ingeschreven (device.yaml weg) → herinstallatie of handmatig
`device.yaml` + vault-pass terugzetten. Overweeg later: enrollment-staat bewaren bij powerwash.

## Alternatieven
GRUB-item met wachtwoord: verworpen zolang er geen GRUB-wachtwoordbeleid is.
