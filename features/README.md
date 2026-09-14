# Features — optionele, modulaire lagen (ADR-0012/0029/0030)

Elke feature is een self-contained map die via de build-arg `FEATURES="naam1 naam2"` wordt geactiveerd
(zie `build_files/install-features.sh`; volgorde telt bij afhankelijkheden). Een kale Coolbx OS (geen
`FEATURES`) bevat geen enkele feature en heeft geen Focus-afhankelijkheid.

```
features/<naam>/
  install.sh        # optioneel: pakketten/config voor deze feature
  system_files/     # optioneel: bestanden die in / worden gekopieerd
```

| Feature | Wat | Vereist |
|---|---|---|
| `chrome` | Google Chrome + Chrome Enterprise Core-gereedheid; gedeelde policy-dir | — |
| `chromium` | Fedora-Chromium (fallback / dev-harnas) | — |
| `kiosk` | generieke sway+waybar-kiosk; apps = `apps.d/*.yaml` (`coolbx-kiosk-apps`) | chrome of chromium |
| `focus` | Coolbx Focus: extensie force-install, attestatie, exam-policy, kiosk-app "Toetsmodus" | kiosk |
| `branding` | Plymouth/GRUB/GDM/desktop-identiteit | — |
| `hardware` | laptop-/input-quirks | branding (dconf-profiel) |
| `fleet` | staged update, greenboot, signing, ansible-pull, coolbx-status | — |
| `managed` | klok-lockdown | — |
| `apps` | gecureerde GNOME-basisapps | — |
| `media-nonfree` | codecs/VAAPI/Widevine (ADR-0027) | — |
| `google-login`, `role-*`, `admin` | Fase C/D (ROADMAP v3) | — |

Rol-samenstellingen staan in `docs/ROADMAP.md` §3. Dev-set: zie `DEV_FEATURES` in de `Justfile`.
