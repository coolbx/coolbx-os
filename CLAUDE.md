# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> Notitie: de gebruiker werkt in het Nederlands — antwoord en schrijf in het Nederlands.

## Status (heropname 14 sep 2026)

**Lees eerst `docs/ROADMAP.md` (v3)** en de ADRs `docs/adr/0028`–`0034` — dat is de gezaghebbende richting.
Kern: Coolbx OS is een **standalone, Chromebook-achtig schoolbesturingssysteem** (fedora-bootc + GNOME),
voorlopig **los van Coolbx Focus** (Focus = optionele `focus`-feature). Drie rol-images (`leerling`,
`leerkracht`, `gedeeld`), Google-login via Secure LDAP/SSSD, Google Chrome + Chrome Enterprise Core,
generieke sway-kiosk met apps uit config, config via git (`coolbx-ansible`: profielen + serienummerlijst),
verborgen beheerder `coolbx`, powerwash zonder GRUB-ingang. Design: eigen karakter, vector-eerst.

Wat uit de juni-bouw (v2) blijft: bootc-kern, kiosk-mechaniek (sway+waybar, VT-lock), vlootlaag (staged
update, greenboot, signing, ansible-pull, coolbx-status), attestatie (nu in `focus`), e2e-harnas (`just e2e`).
Dev-omgeving: passwordless `sudo podman`; qemu-direct VM-loop (`docs/DEVELOPING.md`). Google-sandbox: `docs/WORKSPACE.md`
(geheimen in `~/.config/coolbx/secrets/`, nooit in git).

## Wat dit is

**Coolbx OS** is een vergrendelde Linux "device floor": een Fedora bootc / Universal Blue image die van een gewone laptop het equivalent van een managed Chromebook maakt. Het levert de echte toets-vergrendeling die de in-klas-toetsentool **Coolbx Focus** op zichzelf níét belooft. Samen (vergrendeld toestel + geforceerde productie-Focus-extensie) vormen ze waterdichte toetsafname. De twee lanceren als familie onder de coolbx-vlag maar leven in **aparte repos** — deze OS-toolchain (bootc/podman/`just`/ansible) deelt niets met de pnpm/vite-wereld van Focus.

## Vastliggende beslissingen

- **Aparte repo** los van de Focus-monorepo. Afstemming gebeurt via drie naden: gedeelde brand, één umbrella-site, en het integratiecontract hieronder.
- **Vers herbouwen — niet de POC verderzetten.** De POC bundelt een legacy Electron `focus-app`; droppen. Bouw rond de **productie student-extensie**.
- Het OS draait **Chromium + de productie student-extensie** (force-installed), nooit de Electron-app.

## Open beslissingen — ⚠️ INMIDDELS BESLIST in `docs/ROADMAP.md` (onderstaande lijst is historisch)

- **Kiosk-/WM-mechanisme is niet gekozen**: cage vs gnome-kiosk vs labwc/sway vs een vergrendelde GNOME-sessie. De POC is hier half in transitie en inconsistent (zie onder).
- Hoeveel "gewoon toestel" vs "pure kiosk" (alleen Chromium, of een beperkt bureaublad eronder).
- Definitieve branding/naam (Coolbx OS vs restanten "SchoolBX").

## Integratiecontract (de kern van het project)

Het **WAT ligt vast, het HOE (kiosk/WM) is open.**

- Vast: het OS draait **Chromium** met de **productie student-extensie force-installed** + managed-storage. Geen Electron-app.
- Open: hóe Chromium als kiosk draait (compositor-keuze hierboven).

Harde feiten (geverifieerd uit `manifest.json` + `public/managed_schema.json` van de extensie):

| Item | Waarde |
|---|---|
| Extension-ID (vast via `key` in manifest) | `makdakigkdbicdljgdclgnejachcohag` |
| `minimum_chrome_version` | `116` |
| Update-bron (`update.xml`) | `https://focus-dashboard.edugolo.be/extension-updates/update.xml` |
| Managed-storage schema | `serverUrl` (string), `kioskMode` (boolean) |
| Aan te leveren managed values | `serverUrl = https://focus-api.edugolo.be`, `kioskMode = true` |

**Spike te verifiëren vóór je bouwt** — het Linux-Chromium-mechanisme:
- **Force-install** vanaf de eigen `update.xml` via policy `ExtensionInstallForcelist` (of `ExtensionSettings` met `installation_mode: force_installed` + `update_url`) als JSON in `/etc/chromium/policies/managed/`.
- **`chrome.storage.managed` aanleveren** (serverUrl, kioskMode) op Linux Chromium — dit is een *ander* mechanisme dan browser-policy; uitzoeken waar Chromium de 3rd-party per-extensie managed-storage JSON leest. Bevestig dit vroeg experimenteel in een VM.
- Controleer via `chrome://policy` en `chrome.storage.managed.get()` dat de waarden aankomen.

## POC-referentie (lezen, niet klakkeloos kopiëren)

Bevroren in **`/home/johan/code/coolbx-poc/coolbx-os`**. Herbruikbare patronen: `Containerfile` (bootc-build), `Justfile` (VM/ISO/qcow2-recepten), `build_files/01-packages.sh` (chromium/gnome/ansible-pakketten), first-boot user + `nl_BE`/`be`-locale, periodieke `ansible-pull`-config, en GHCR + cosign CI in `.github/workflows/`. **Droppen**: de legacy Electron `focus-app` RPM onder `features/focus-mode/local_rpms/`. De kiosk-feature (`features/focus-mode/install.sh`, `start-focus`) is **open ontwerp** — de POC heeft cage uitgecommentarieerd in packages maar nog actief geïnstalleerd in de feature, met óók `gnome-session`; lees zijn `cage -- /usr/bin/focus-app` als één mogelijke aanpak, niet als de gekozen. Hernoem `schoolbx-*`-artefacten naar `coolbx-*`.

## Toolchain (zodra er gebouwd wordt)

Mikt op de Fedora bootc / Universal Blue workflow: `podman` bouwt vanuit een `Containerfile`, `just`-recepten sturen build en VM-runs (bijv. `just run-vm-*`), `ansible` voor periodieke config-pull, images gepubliceerd op GHCR en gesigneerd met cosign. Er bestaan nog geen commando's in deze repo — port ze bewust vanuit de POC.

## Belangrijke pointers

- Productie-extensie: `/home/johan/code/coolbx/coolbx-focus/apps/student-extension`
- Focus-repo (productie): `/home/johan/code/coolbx/coolbx-focus`
- Brand-masters (coolbx-familie): `…/coolbx-focus/branding`
- Volledig strategieplan: `/home/johan/.claude/plans/stateless-crunching-tide.md`
- Productie-server/API: `https://focus-api.edugolo.be`, dashboard `https://focus-dashboard.edugolo.be`
