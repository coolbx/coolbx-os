# ADR-0030: Drie rol-images — leerling, leerkracht, gedeeld

- **Status:** Aanvaard
- **Datum:** 2026-09-14
- **Beslissers:** Johan, Claude

## Context
Toestellen verschillen per rol in standaardapps, Flatpak-zichtbaarheid en accountmodel. Eén image met
runtime-rol vraagt een muteerbare rol-schakelaar; meerdere images passen bij bootc (rol = artefact).

## Beslissing
Eén `Containerfile`, **drie tags** via een CI-matrix: `ghcr.io/coolbx/coolbx-os:leerling`, `:leerkracht`,
`:gedeeld` (+ gedateerde tags, later `:testing-<rol>`). Rol wisselen = `bootc switch`; homes, accounts en
`/etc/coolbx/device.yaml` blijven daarbij bewaard. Verschil per rol (samenstelling in `docs/ROADMAP.md`):

| | leerling | leerkracht | gedeeld |
|---|---|---|---|
| Login | Google (SSSD) | Google (SSSD) | lokale gebruiker `leerling`, wachtwoordloos |
| Home | blijvend, per gebruiker | blijvend, per gebruiker | gewist bij afmelden en bij opstart |
| Flatpak | in image (ansible system-wide); GNOME Software **niet** zichtbaar, geen terminal | GNOME Software + terminal, eigen user-installs | als leerling |
| Kiosk | ja | ja | ja |

"Verbergen, niet verbieden": Flatpak zit in elk image zodat ansible software kan bijzetten; leerlingen
missen enkel de ingangen (Software, terminal).

## Gevolgen
Justfile-recepten en CI bouwen per rol; rechunk per rol; `role-*`-features houden de verschillen klein.
Een school kan met `FEATURES` eigen combinaties bouwen.

## Alternatieven
Eén image + `coolbx-role set …`: verworpen (muteerbare staat, meer machinerie, minder bootc-idiomatisch).
