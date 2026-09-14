# ADR-0035: Design — "papier & inkt", vector-eerst, schaalt met het scherm

- **Status:** Aanvaard (carte blanche van Johan, 14 sep 2026; verfijnt ADR-0010)
- **Datum:** 2026-09-14
- **Beslissers:** Claude (ontwerp), Johan (opdracht: "echt mooi, origineel, niet ChromeOS")

## Context
De juni-branding was "alles donker" met een tekst-wordmark die op sommige resoluties "lomp" oogde
(vaste pixels). ADR-0010 vraagt de play↔focus-dualiteit zonder schild-metafoor, binnen de coolbx-
familie (inkt/papier, Inter, amber gereserveerd voor Focus).

## Beslissing
**Papier & inkt.** Play en focus zijn twee kanten van één vel:
- het **bureaublad is licht papier** (`#FAF8F3`, zwakke schrijflijnen, één mint kantlijn, een dot met
  zachte gloed) — daar werk je vrij;
- **opstart, aanmelden en kiosk zijn nacht** (`#141210`) — het kader dat je opent; de kiosk-balk toont de
  app-naam in mint, bij Toetsmodus in amber.
- **Eén glyph**: het vel met de dot (tegel / lichte tegel / kale glyph). **Eén accent**: mint `#50CE96`.
  Amber blijft van Focus. **Eén beweging**: de dot ademt bij opstart.
- **Vector-eerst en schaalbaar**: SVG-bronnen (`features/branding/assets_src.py`), PNG's gerenderd
  (inkscape) op 4K/256/512. De wordmark wordt nooit in vaste pixels gezet: Plymouth schaalt naar 13 % van
  de schermbreedte (min 160, max 420 px), GRUB plaatst 'm als losse component (niet in de uitgerekte
  achtergrond). Typografie: Inter Display Black + Light voor de wordmark, verder Regular/Medium.
- Ontwerpcanvas met merkblad, opstart, aanmelden, bureaublad, kiosk en de niet-gekozen alternatieven
  (alles-nacht; kleur per rol) staat als artifact "Coolbx OS ontwerp".

## Gevolgen
`branding`-feature herbouwd (dconf licht, nieuwe wallpapers, Plymouth-script met schaling, GRUB-
component, GDM-nacht + logo), kiosk-waybar-stijl, iconen `coolbx-kiosk` (mint) / `coolbx-focus` (amber).
Alternatief B (kleur per rol) blijft mogelijk als subtiel randje op de wallpaper.

## Alternatieven
- Alles nacht (juni): verworpen — geen verschil meer tussen vrij werken en kiosk; vermoeiend bij daglicht.
- Kleur per rol: uitgesteld — drie accenten verwateren het merk; IT-herkenning kan via `coolbx-status`.
