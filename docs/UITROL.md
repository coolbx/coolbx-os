# Coolbx OS — uitrolgids voor scholen (v3, september 2026)

Voor de school-IT'er. Alles in gewone taal; de *waarom*-beslissingen staan in `docs/adr/` (0028–0035),
het levende plan in `docs/ROADMAP.md`.

## 1. Wat je uitrolt

Coolbx OS maakt van een laptop die niet meer Windows-waardig is een beheerd schooltoestel dat aanvoelt
als een Chromebook: aanmelden met het school-Google-account, een beheerde Chrome, een rustige desktop,
updates die vanzelf gaan, en een **kiosk-modus** om één web-app vergrendeld te draaien ("maak nu de
toets in app X"). Coolbx Focus is daar een optionele laag bovenop (§9).

**Drie rollen = drie images.** Rol wisselen is één commando (§8).

| Rol | Aanmelden | Home | Extra |
|---|---|---|---|
| `leerling` | Google-account (groep *leerlingen* + *ict*) | blijvend, per gebruiker | vergrendelde instellingen, geen terminal/Software |
| `leerkracht` | Google-account (groep *personeel*) | blijvend, per gebruiker | GNOME Software (eigen Flatpaks), terminal |
| `gedeeld` | lokale gebruiker **Leerling**, zonder wachtwoord | gewist bij afmelden en bij opstart | voor gang/lokaal/klasset |

**Drie lagen bepalen hoe een toestel zich gedraagt:**

| Laag | Waar | Wat |
|---|---|---|
| Image | `ghcr.io/coolbx/coolbx-os:<rol>` | software, beveiliging, rol-standaard |
| Toestel | `/etc/coolbx/device.yaml` op de laptop + de **config-repo** in git | kiosk-apps, bureaubladinstellingen, Chrome-beleid, Flatpaks, printers, geheimen |
| Gebruiker | Google Admin-console | Chrome-bladwijzers/extensies per OU of groep; wie in welke groep zit |

Op elk toestel bestaat een verborgen beheerder **`coolbx`** (sudo). Het wachtwoord kies je zelf (§3.3).

## 2. Hardware-eisen

| Onderdeel | Eis |
|---|---|
| CPU | x86_64 |
| Firmware | UEFI (Legacy-BIOS is niet getest) |
| RAM | 4 GB werkt; 8 GB is comfortabel |
| Schijf | minstens 32 GB (twee OS-versies naast elkaar + homes) |
| Wifi | brede firmware ingebakken (Intel, Atheros, Broadcom, MediaTek, Realtek, …) |
| GPU | Intel/AMD volledig; NVIDIA via nouveau (geen proprietaire driver) |
| Camera | UVC-webcams en Intel IPU6 werken; Surface Go 2-camera niet (ADR-0026) |
| TPM 2.0 | alleen nodig voor Focus-examens (ADR-0027); niet voor gewoon gebruik |

Getest op een Intel-laptop met AX200-wifi en een Microsoft Surface Go 2 (Type Cover, touch, pen).
**Fysieke beveiliging** (firmware-wachtwoord, GRUB-wachtwoord) is bewust nog niet ingepland (ADR-0034);
wie van USB boot, kan om het OS heen. Zet het op de lijst zodra de vloot draait.

## 3. Eenmalige voorbereiding

### 3.1 Google Workspace (Admin-console)
Zie `docs/WORKSPACE.md` voor de klikpaden. Samengevat:
1. **Groepen**: `leerlingen`, `personeel`, `ict` (of bestaande groepen). Deze namen komen in de profielen.
2. **Secure LDAP-client** (Apps → LDAP): rechten *aanmeldgegevens verifiëren*, *gebruikersinfo lezen*,
   *groepsinfo lezen*, scope = de OU's van leerlingen en personeel. Certificaat + sleutel downloaden,
   toegangsgegevens genereren, status **Aan**. Het certificaat vervalt na drie jaar (sandbox: 13 sep 2029).
3. **Chrome Enterprise Core-token** (Chrome-browser → Beheerde browsers → OU kiezen → Inschrijven, tab Linux).
   Browserbeleid stel je daarna in onder Chrome-browser → Instellingen.
4. Tweestapsverificatie: LDAP is wachtwoord-only; dat is bewust zo gelaten (ADR-0031).

### 3.2 Config-repo (`github.com/coolbx/coolbx-ansible`)
De repo bevat `profiles/` (basis + per rol), `devices.yml` (platte lijst op serienummer) en `vault.yml`
(versleutelde geheimen). Lees de README daar. Kort:
- **Profiel** = één YAML: kiosk-apps, Chrome-beleid, dconf, Flatpaks, printers, en voor leerling/leerkracht
  het `google_login`-blok (zoekbases, groepen). Standaard: `leerling-standaard`, `leerkracht-standaard`,
  `gedeeld-standaard`.
- **devices.yml**: per toestel `serial`, `name`, `profile`, optioneel `channel` en `powerwash`.
  Een toestel dat er niet in staat, krijgt `<rol>-standaard`.
- **Kanaal**: `stabiel` = branch `main`, `test` = branch `testing`. Test wijzigingen eerst op een paar toestellen.
- **Vault**: zet de geheimen op je IT-machine in `~/.config/coolbx/secrets/` (`ldap-client.crt`,
  `ldap-client.key`, `ldap-access.txt`, `chrome-enrollment.txt`, `admin-password-hash.txt`) en draai
  `scripts/make-vault.sh` → `vault.yml` + `vault-pass`. **`vault-pass` komt nooit in git.**
- De repo is publiek; alles geheims MOET in de vault. Overweeg de repo privé te zetten.

### 3.3 school.env op de IT-machine
Kopieer `school.env.example` naar `school.env` (git-genegeerd) in de coolbx-os-checkout en vul in:
config-repo-URL, image-registry, kanaal, pad naar `vault-pass`, pad naar de beheerders-wachtwoordhash
(`openssl passwd -6`).

## 4. Installatie-USB maken

Op een Fedora-machine met `podman`, `just` en passwordless `sudo podman`:

```bash
just build-iso leerling      # of leerkracht / gedeeld
```

Dit bouwt de rol-image, bakt ze in een minimale Anaconda-installer (alleen schijfkeuze) en schrijft
`output/bootiso/install.iso`. De installer zet bij het installeren automatisch `device.yaml`,
`ansible.conf`, `vault-pass` en het beheerderswachtwoord, en koppelt het toestel aan de GHCR-rol-tag
voor updates. **Installeren = ingeschreven.** Schrijf de ISO naar USB (`dd` of Fedora Media Writer).

Eén ISO per rol, en opnieuw bouwen als `school.env` wijzigt (bv. nieuw vault-wachtwoord).

## 5. Een toestel installeren

1. Boot van de USB (UEFI). Kies de schijf. **De schijf wordt gewist.** Wacht op de herstart.
2. Eerste opstart: het toestel haalt binnen het uur zijn profiel op (`coolbx-ansible-pull.timer`); forceren:
   ```bash
   sudo systemctl start coolbx-ansible-pull.service
   ```
3. Controleer met `coolbx-status`: rol/profiel/kanaal, serienummer, config-pull OK, Google-login actief, kiosk-apps.
4. Noteer het serienummer (sticker of `coolbx-status`) en voeg het toestel toe aan `devices.yml` als het een
   ander profiel dan de standaard moet krijgen.
5. Meld één keer aan met een Google-account terwijl het toestel online is; daarna werkt aanmelden ook offline.

Zonder Google-login (nog geen config, of LDAP onbereikbaar) kun je altijd aanmelden als `coolbx`
("Niet in de lijst?" op het aanmeldscherm).

## 6. Dagelijks gebruik en beheer

- **Aanmelden**: naam vóór de apenstaart volstaat (`voornaam.naam`), of het volledige e-mailadres.
  Een leerkracht krijgt op een leerling-laptop "toegang geweigerd" (groepsregel in het profiel).
- **Kiosk-apps**: staan in de dock en het app-raster (bv. Smartschool, Bingel). Klik → vergrendelde
  sessie met balk bovenaan (wifi, batterij, klok, *Sessie afsluiten*). Geen tabbladen, geen sneltoetsen,
  geen VT-wissel. Apps toevoegen = profiel aanpassen in git; het toestel pikt het binnen het uur op.
- **Gedeeld toestel**: start automatisch aangemeld als *Leerling*; afmelden wist alles.
- **Beheerder**: `coolbx` met het gekozen wachtwoord; `sudo` werkt. Alleen de beheerder ziet de
  launcher **Toestel wissen**.
- **Powerwash** (toestel wissen): als `coolbx` → *Toestel wissen* → herstart. Op afstand: `powerwash: true`
  bij het toestel in `devices.yml`; het wist zich bij de eerstvolgende herstart zonder actieve gebruiker.
  Zet de vlag daarna terug op `false`. Na powerwash is het toestel niet meer ingeschreven: herinstalleren
  met de USB, of handmatig `device.yaml` + `vault-pass` terugzetten.
- **Software toevoegen**: Flatpaks in het profiel (`flatpaks:`) worden systeembreed geïnstalleerd en
  overleven alles. Leerkrachten mogen zelf extra Flatpaks installeren voor hun eigen account.

## 7. Updates

- Elke nacht om 04:00 (± 15 min) wordt de nieuwe image **klaargezet** (`bootc upgrade`, geen herstart).
  Ze wordt actief bij de volgende opstart. Een toets wordt nooit onderbroken.
- Elke rol volgt zijn eigen tag: `ghcr.io/coolbx/coolbx-os:leerling`, `:leerkracht`, `:gedeeld`
  (+ gedateerde tags `:<rol>.JJJJMMDD`). Een canary-tag `:testing-<rol>` is voorzien maar nog niet gepubliceerd.
- **Greenboot** rolt automatisch terug na herhaald mislukte boots (lokale checks; nooit een externe dienst).
- Handmatig: `sudo bootc upgrade` (nu klaarzetten), `sudo bootc rollback` (terug), `sudo bootc status`.
- Examenperiode: `sudo ostree admin pin 0` zet de huidige versie vast.

## 8. Rol wisselen

```bash
sudo bootc switch ghcr.io/coolbx/coolbx-os:leerkracht && sudo systemctl reboot
```
Homes, accounts en `device.yaml` blijven staan. Pas daarna `role:` in `/etc/coolbx/device.yaml` aan
(of laat het toestel in `devices.yml` een ander profiel geven).

## 9. Coolbx Focus (optioneel)

De rol-images bevatten Focus **niet**. Wil je de toetsentool met attestatie, bouw dan een image met de
`focus`-feature erbij (`FEATURES="$(scripts/role-features.sh leerling) focus"`) — zie `docs/ATTESTATION.md`
en ADR-0029. De kiosk-app *Toetsmodus* verschijnt dan naast de andere kiosk-apps.

## 10. Problemen oplossen

| Symptoom | Kijk naar |
|---|---|
| Aanmelden met Google lukt niet | `coolbx-status` (Google-login), `sudo sssctl domain-status google`, `sudo journalctl -u sssd`, `/var/log/sssd/sssd_google.log`. Certificaat verlopen? (3 jaar) |
| "Toegang geweigerd" voor een echte leerling | staat de gebruiker in de groep uit `allow_groups` van het profiel? (`getent group leerlingen`) |
| Profiel komt niet aan | `coolbx-status` (Config-pull), `sudo /usr/libexec/coolbx-ansible-pull`, `/var/lib/coolbx/ansible-status.json`; klopt `vault-pass`? |
| Kiosk-app start niet | `coolbx-kiosk-apps list`, `sudo journalctl -u coolbx-kiosk` |
| Chrome niet beheerd | bestaat `/etc/opt/chrome/policies/enrollment/CloudManagementEnrollmentToken`? `chrome://policy` |
| Toestel boot niet meer na update | greenboot rolt terug; anders in GRUB de vorige versie kiezen, dan `sudo bootc rollback` |
| Schermschaal/klaviertaal | dconf/profiel; standaard nl_BE + Belgisch toetsenbord |

## 11. Checklist nieuw toestel
1. UEFI aan, van USB booten, schijf kiezen, wachten op herstart.
2. Online? `coolbx-status` → Config-pull OK, Google-login actief.
3. Serienummer in `devices.yml` (indien afwijkend profiel).
4. Eén keer aanmelden met een testaccount; kiosk-app openen en afsluiten.
5. Sticker met rol op het toestel.
