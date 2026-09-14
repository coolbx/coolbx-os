# ADR-0028: Heropname — standalone Chromebook-achtig OS, voorlopig los van Focus

- **Status:** Aanvaard
- **Datum:** 2026-09-14
- **Beslissers:** Johan, Claude

## Context
Het project lag stil sinds juli 2026. Aanleiding voor heropname: een set schoollaptops die niet meer
Windows-waardig zijn. De v2-bouw (kiosk, attestatie, vlootlaag) was sterk op Coolbx Focus gericht; de
Focus-kant leeft in een andere repo en ander tempo. ADR-0012 zei al dat de OS-kern los van Focus moet
staan, maar de code deed dat niet (de `kiosk`-feature bevatte de Focus-extensie-policy en -domeinen).

## Beslissing
1. Coolbx OS wordt **eerst een volwaardig standalone schoolbesturingssysteem** dat de Chromebook-ervaring
   benadert: Google-account-login, beheerde Chrome, rustige desktop, automatische updates, kiosk-modus.
2. **Voorlopig los van Coolbx Focus.** Alle Focus-binding (extensie, managed-storage, attestatie, exam-policy,
   native-messaging-host) verhuist naar één optionele `focus`-feature. De rol-images bouwen zonder.
3. "Snel en eenvoudig naar resultaat" én "een echt mooi esthetisch eindproduct" zijn beide expliciete doelen.

## Gevolgen
Herstructurering van features (ADR-0029), drie rol-images (ADR-0030), nieuw accountmodel (ADR-0031),
nieuwe config-naad (ADR-0032), Chrome i.p.v. Chromium (ADR-0033). De v2-tests blijven; Focus-tests worden
feature-gegate. `docs/ROADMAP.md` v3 is het levende plan.

## Alternatieven
- Doorbouwen op de Focus-koppeling: verworpen, Focus is niet klaar en blokkeert het OS-nut.
- ChromeOS Flex: verworpen, geen eigen kiosk-mechaniek, geen bootc-modulariteit, geen Focus-pad later.
