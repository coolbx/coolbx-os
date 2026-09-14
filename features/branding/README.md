# Feature: `branding` — ontwerp "papier & inkt" (ADR-0035)

Het idee: play en focus zijn twee kanten van één vel. Het **bureaublad is licht papier** waar je
vrij werkt; **opstart, aanmelden en kiosk zijn nacht** — het kader dat je opent. Eén accent: mint.
Ontwerpcanvas (merk, opstart, aanmelden, bureaublad, kiosk): zie `docs/adr/0035-design-papier-en-inkt.md`.

## Palet
| Rol | Hex |
|---|---|
| papier (bureaublad, vensters) | `#FAF8F3` |
| inkt (tekst, glyph) | `#2B2620` |
| nacht (opstart, aanmelden, kiosk) | `#141210` |
| mint (hét accent, de dot) | `#50CE96` |
| amber — **gereserveerd voor Coolbx Focus** | `#E8902A` |

## Glyph & wordmark
- **Glyph** = het vel met de dot (`assets_src.py`): tegel (app-iconen), lichte tegel (bureaublad/'Over'),
  kale glyph (balken). SVG-bron, PNG's gerenderd op 256/512.
- **Wordmark** "coolbx os": Inter Display Black + Light. **Schaalt met het scherm**: Plymouth zet 'm op
  13 % van de schermbreedte (min 160, max 420 px); GRUB plaatst 'm als losse image-component;
  GDM toont een bescheiden 2×-logo.

## Wat het levert
- **Plymouth** (script-thema `coolbx`): nacht, wordmark, ademende dot; berekent positie én schaal per frame.
- **GRUB2-thema**: vlakke nacht, wordmark-component, mint geselecteerd item.
- **GDM**: nacht-achtergrond met zachte gloed, wordmark onderaan (google-login voegt de hint "Meld je aan met je schoolaccount" toe).
- **Bureaublad**: licht (`color-scheme=default`), papier-wallpaper (`coolbx-paper.svg` → 4K-PNG: zwakke
  schrijflijnen, mint kantlijn, dot met gloed), Inter-UI-font. Vergrendelscherm = nacht.
- **os-release** `Coolbx OS`; Fedora-logo-assets vervangen door de wordmark; 'Over'-logo = glyph.

## Assets herbouwen
```sh
python3 features/branding/gen-assets.py   # vereist inkscape + rsms-inter-fonts op de dev-machine
```
Bronnen: `assets_src.py` (SVG), `gen-assets.py` (render). PNG's zijn ingecheckt (reproduceerbaar).
