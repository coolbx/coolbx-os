# Coolbx OS — roadmap v3 (heropname september 2026)

> Status: **uitvoeringsklare blauwdruk v3.** Vervangt v2 (juni 2026, in git-historie). v3 verwerkt de
> heropname-brainstorm van 14 sep 2026: Coolbx OS wordt eerst een **standalone, Chromebook-achtig
> schoolbesturingssysteem**, voorlopig **los van Coolbx Focus**. Wat in v2 gebouwd en geverifieerd is
> (bootc-kern, kiosk-mechaniek, vlootlaag, attestatie, e2e-harnas) blijft; het wordt hergroepeerd.
> Beslissingen staan in `docs/adr/` (0028–0034 zijn de v3-beslissingen). Lees ook `CLAUDE.md`.

## 1. Wat het is

**Coolbx OS** is een beheerd Fedora **bootc**-besturingssysteem voor schoollaptops die niet meer
Windows-waardig zijn. Het benadert de Chromebook-ervaring: inloggen met het school-Google-account,
een beheerde Chrome, een rustige GNOME-desktop, updates die vanzelf gaan, en een vergrendelde
**kiosk-modus** die vanuit de sessie gestart wordt om één web-app schermvullend en zonder ontsnapping
te draaien ("maak nu de toets in app X"). **Coolbx Focus** (de toetsentool) is één van die kiosk-apps,
als optionele feature bovenop het OS — nooit een aanname in de kern ([ADR-0012](adr/0012-standalone-os-focus-optioneel.md),
[ADR-0028](adr/0028-heropname-standalone-chromebook-richting.md)).

Eerlijke framing blijft: het OS beveiligt **het toestel**, niet de ruimte. Fysieke beveiliging
(firmware-wachtwoord, GRUB-wachtwoord) is **bewust uitgesteld** ([ADR-0034](adr/0034-powerwash-zonder-grub.md)).

## 2. Richtingsbeslissingen v3

| Knoop | Keuze | ADR |
|---|---|---|
| Doel | Standalone Chromebook-achtig OS; Focus = optionele feature | 0028 |
| Kiosk | Generiek: sway + waybar (balk bovenaan, "Sessie afsluiten"), start ALLEEN vanuit de GNOME-sessie, apps uit config | 0029 |
| Images | Drie rol-images: `leerling`, `leerkracht`, `gedeeld`; rol = image; wissel = `bootc switch` | 0030 |
| Accounts | Google Secure LDAP via SSSD (leerling/leerkracht, blijvende homes), lokale wachtwoordloze gebruiker met wisbare home (gedeeld), verborgen beheerder `coolbx` met sudo | 0031 |
| Config-naad | image → `/etc/coolbx/device.yaml` → git config-repo met `profiles/` + platte `devices.yml` op serienummer; geen OU-boom | 0032 |
| Browser | Google Chrome + Chrome Enterprise Core (gratis) als `chrome`-feature; Chromium blijft fallback | 0033 |
| Powerwash | Alleen via beheerder-launcher of vlag op afstand; géén GRUB-ingang | 0034 |
| Design | "Papier & inkt": licht bureaublad, nacht-kader, één glyph, één accent, vector-eerst | 0035 |
| Installatie | Anaconda-ISO via bootc-image-builder, school-specifiek (repo-URL + geheimen), hoort in v1 | 0032 |

## 3. Architectuur

```
                 ┌──────────────── Google Workspace ────────────────┐
                 │ identiteit (Secure LDAP)   browserbeleid (Admin) │
                 └───────────┬───────────────────────┬──────────────┘
                             │ SSSD                  │ Chrome Enterprise Core
┌─ Coolbx OS (bootc-image per rol) ──────────────────┴──────────────┐
│  GNOME-sessie ("play")            kiosk-sessie ("focus")          │
│   Chrome (beheerd)     ─launcher─▶ sway + waybar + chrome --app   │
│   apps · Flatpak (rol)             VT-vergrendeld, tmpfs-home     │
│                                    ◀─"Sessie afsluiten"─          │
│  ansible-pull ◀─── git config-repo: profiles/<naam> + devices.yml │
│  device.yaml (rol · profiel · kanaal)   coolbx (beheerder, sudo)  │
└───────────────────────────────────────────────────────────────────┘
```

### Drie config-lagen
| Laag | Bron | Bepaalt |
|---|---|---|
| **Image** | `Containerfile` + `FEATURES` per rol | software, hardening, rol-standaardapps, kiosk-mechaniek |
| **Toestel** | `/etc/coolbx/device.yaml` (rol, profiel, kanaal) + config-repo `profiles/<naam>/` en `devices.yml` | kiosk-apps, dconf, Chrome-policies, flatpaks, printers, geheimen (vault) |
| **Gebruiker** | Google Admin-console (Chrome per OU/groep) + Google-groep → dconf-profiel-mapping in git | bladwijzers, extensies, bureaubladvergrendeling per groep |

### Features (build-time, modulair — `FEATURES="…"`)
| Feature | Inhoud | In rol |
|---|---|---|
| *(kern)* | GNOME, firmware, nl_BE, pipewire, libcamera, NetworkManager, Flatpak+Flathub (system), ansible-core | alle |
| `chrome` | Google Chrome-RPM, policy-dir gedeeld met Chromium, enrollment-pad | alle |
| `chromium` | Fedora-Chromium (fallback/dev) | dev |
| `kiosk` | sway+waybar-sessie, `coolbx-kiosk-start <app>`, apps uit `/etc/coolbx/kiosk-apps.d/`, per-app policy, VT-lock | alle |
| `focus` | Focus-extensie force-install + managed-storage, attestatie (HMAC/TPM), exam-policy, native-messaging-host, kiosk-app "Toetsmodus" | optioneel |
| `google-login` | SSSD + oddjob-mkhomedir, authselect, GDM zonder gebruikerslijst; cert/creds komen uit config | leerling, leerkracht |
| `role-leerling` / `role-leerkracht` / `role-gedeeld` | rol-defaults (dconf-locks, apps, gedeelde gebruiker) + `device.yaml`-default | resp. |
| `admin` | verborgen beheerder `coolbx` (wheel, uid<1000), powerwash-launcher + marker-mechanisme | alle |
| `branding` | Plymouth/GRUB/GDM/desktop-identiteit, assets per resolutie | alle |
| `hardware` | input-/laptop-quirks (Surface Type Cover) | alle |
| `fleet` | staged auto-update, greenboot, signing-verificatie, `coolbx-ansible-pull`, `coolbx-status` | alle |
| `managed` | klok-lockdown (NTP + polkit) | alle |
| `apps` | gecureerde GNOME-basisapps | alle |
| `media-nonfree` | codecs/VAAPI/Widevine (ADR-0027) | alle |

Rol-samenstelling (CI-matrix, [ADR-0030](adr/0030-drie-rol-images.md)):
- `leerling` = kern + chrome kiosk google-login role-leerling admin branding hardware fleet managed apps media-nonfree
- `leerkracht` = idem + role-leerkracht (GNOME Software, terminal) i.p.v. role-leerling
- `gedeeld` = kern + chrome kiosk role-gedeeld admin branding hardware fleet managed apps media-nonfree (geen google-login)
- `dev` (lokale e2e) = leerling-set + `chromium focus` zodat de volledige testsuite draait

## 4. Fasering v3

### Fase A — Vastleggen ✅
Roadmap v3 + ADR-0028…0034. Memory bijgewerkt.

### Fase B — Kiosk generiek, Focus apart ✅ (14 sep)
- `kiosk`: apps uit YAML (`id`, `name`, `icon`, `url`, `allow_domains`, `policy`), launcher-generator
  (`coolbx-kiosk-apps apply` → `.desktop` per app in `/var/lib/coolbx/share/applications`, via XDG_DATA_DIRS), per-app Chromium-policy
  tijdens de sessie (`coolbx-kiosk-app.json`), browser-agnostisch (chrome of chromium), waybar toont app-naam.
- `focus` = huidige `attest` + Focus-delen van `kiosk` (managed.json, domains, lobby-policy) + kiosk-app `focus`.
- greenboot/status/tests feature-bewust. e2e: Focus-tests skippen zonder `focus`.

### Fase C — Rollen, accounts, beheer ✅ (14 sep)
- `admin`-feature (`coolbx`, wheel, verborgen; powerwash-marker + vroege-boot-wipe + launcher).
- `role-gedeeld` (gebruiker `leerling`, wachtwoordloos in GDM via PAM, autologin bij boot, home gewist bij logout/boot).
- `role-leerling` / `role-leerkracht` (dconf-locks, Software/terminal enkel leerkracht, `device.yaml`-default).
- Justfile + CI-matrix voor drie tags (`:leerling`, `:leerkracht`, `:gedeeld` + gedateerd), rechunk per rol.

### Fase D — Google-login, Chrome, config-repo ✅ (14 sep, e2e tegen de sandbox)
- `google-login`: SSSD-template (twee zoekbases, `simple_allow_groups`, cache, mkhomedir), authselect,
  GDM `disable-user-list`. e2e tegen de sandbox: `getent`, SSH-login als testleerling, weigering leerkracht.
- `chrome`: Google Chrome-RPM, `/etc/opt/chrome/policies/managed` → gedeelde policy-dir, enrollment-token uit config.
- config-repo `coolbx-ansible` herbouwd: `local.yml`, rollen (`device-identity`, `kiosk-apps`, `dconf`, `chrome`,
  `google-login`, `flatpaks`, `printers`, `admin-user`, `powerwash`), `profiles/`, `devices.yml`, `vault.yml`, CI.
- OS-kant: `coolbx-ansible-pull` leest `device.yaml` + serienummer, kanaal → branch, vault-wachtwoord uit `/etc/coolbx/vault-pass`.

### Fase E — Installatie-ISO ✅ (14 sep, `just build-iso` + `just iso-test`)
`just build-iso rol=…`: BIB `--type anaconda-iso`, minimale installer (enkel schijf), kickstart-`%post` zet
`device.yaml`, `ansible.conf`, `vault-pass`, beheerderswachtwoord uit een lokaal, git-genegeerd `school.env`.
Getest in de VM (ISO-boot → install → eerste boot → ansible-pull → Google-login).

### Fase F — Design & afwerking ✅ (ADR-0035, v2 na feedback)
Ontwerpcanvas (concept + opstart/aanmelden/bureaublad/kiosk-balk), dan assets vector-eerst per resolutie
(Plymouth, GRUB, GDM, wallpapers per rol, waybar-stijl, iconen). ADR-0035.

### Fase G — Docs & overdracht ✅ (UITROL.md v3) — hardware-installatie door Johan
`docs/UITROL.md` herschreven (school-installatie, sandbox→productie in Workspace, certificaatverval sep 2029,
powerwash, troubleshooting). Handmatige hardware-installatie door Johan.

## 5. Dev-loop & verificatie (ongewijzigd, [ADR-0020](adr/0020-e2e-dev-automation-harness.md))
`just build-qcow2` → `just dev-vm` → `just e2e`. Machine-leesbaar (SSH, CDP, QMP-screendump, OCR).
Google-sandbox-geheimen op de dev-machine in `~/.config/coolbx/secrets/` (nooit in git); de e2e pusht ze
via SSH in de VM. Workspace-testomgeving: OU `/coolbx-sandbox` (zie `docs/WORKSPACE.md`).

## 5b. Stand van zaken (14 sep 2026, nacht)
93/93 e2e groen (`just e2e`) op de dev-image (leerling-set + role-gedeeld + chromium + focus), inclusief echte
Google-login tegen de sandbox (test_17), config-pull vanaf de config-repo (test_20), admin/powerwash (test_18),
gedeeld toestel (test_19), bureaublad (test_21). Prod-rol-image `gedeeld` gebouwd en geïnspecteerd; ISO-installatie
in een lege VM getest (`just iso-test`). Open: canary-tags `:testing-<rol>`, fysieke beveiliging, Focus-e2e
tegen de live server (Focus-kant), hardware-rondgang.

## 6. Bewust uitgesteld
Fysieke beveiliging (firmware-/GRUB-wachtwoord, Secure-Boot-afdwinging) · tweestapsverificatie op de
laptop-aanmelding · beheer-UI/registry · centrale telemetrie · FOG-kloonpad · a11y-verdieping · web-filtering
vrije modus · linux-surface-camera (ADR-0026).
