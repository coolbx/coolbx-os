# Google Workspace — testomgeving en productiekoppeling

Coolbx OS gebruikt Google Workspace voor twee dingen: **identiteit** (Secure LDAP → SSSD, ADR-0031) en
**browserbeheer** (Chrome Enterprise Core, ADR-0033). Beide zijn gratis in Education Fundamentals.

## Sandbox (ontwikkeling en tests)
Alles wat de ontwikkeling raakt, leeft in de organisatie-eenheid **`/coolbx-sandbox`**. Niets buiten die OU
wordt aangeraakt. Aangemaakt 14 sep 2026 met `tools/gws-sandbox/setup-sandbox.js` (idempotent, dry-run
standaard, weigert alles buiten de OU).

| Wat | Waarde |
|---|---|
| Testaccounts | `coolbx-test-lln1/2@lln.edugolo.be`, `coolbx-test-lkr1/2@edugolo.be`, `coolbx-test-ict1@edugolo.be` |
| Testgroepen | `coolbx-test-leerlingen@`, `coolbx-test-personeel@`, `coolbx-test-ict@edugolo.be` |
| LDAP-client | "Coolbx OS sandbox", scope `/coolbx-sandbox`, groepsinfo lezen AAN, status AAN; certificaat geldig tot **13 sep 2029** |
| Chrome-token | aangemaakt in `/coolbx-sandbox` (Linux) |

Geheimen staan **alleen** op de dev-machine in `~/.config/coolbx/secrets/` (0600): `ldap-client.crt`,
`ldap-client.key`, `ldap-access.txt` (regel 1 gebruikersnaam, regel 2 wachtwoord), `chrome-enrollment.txt`,
`test-accounts.txt`. Nooit in git, nooit in chat.

### Wat er geverifieerd is (14 sep 2026)
- `ldaps://ldap.google.com:636` met TLS-clientcert + toegangsgegevens: OK.
- Gebruikers zijn `posixAccount` (uidNumber, gidNumber, homeDirectory, loginShell, memberOf); groepen zijn
  `posixGroup` + `groupOfNames` (memberUid + member).
- **Secundaire domeinen zijn aparte subbomen**: personeel onder `dc=edugolo,dc=be`, leerlingen onder
  `dc=lln,dc=edugolo,dc=be`; groepen altijd `ou=Groups,dc=edugolo,dc=be`. Een sub-search vanaf de hoofdboom
  vindt de leerlingen niet → SSSD krijgt meerdere zoekbases.
- Bind met volledige DN (SSSD-stijl) en met e-mailadres: OK. Bind met kale uid: geweigerd. Fout wachtwoord:
  `Invalid credentials (49)`.
- `ldapwhoami` geeft "Protocol error" — Google ondersteunt die extended-operatie niet; geen fout van de bind.

Snelle hertest vanaf de dev-machine (geen geheimen in de uitvoer):
```bash
cd ~/.config/coolbx/secrets && podman run --rm -v "$PWD":/s:ro,Z quay.io/fedora/fedora:43 bash -c '
  dnf -y -q install openldap-clients >/dev/null; U=$(sed -n 1p /s/ldap-access.txt); P=$(sed -n 2p /s/ldap-access.txt)
  LDAPTLS_CERT=/s/ldap-client.crt LDAPTLS_KEY=/s/ldap-client.key LDAPTLS_REQCERT=demand \
  ldapsearch -LLL -H ldaps://ldap.google.com:636 -x -D "$U" -w "$P" -b dc=lln,dc=edugolo,dc=be "(mail=coolbx-test-*)" mail memberOf'
```

## Van sandbox naar productie (later, door de school)
1. LDAP-client: scope verbreden naar de echte OU's (of een tweede client "Coolbx OS productie").
2. Chrome-token aanmaken in de productie-OU voor toestellen; browserbeleid onder *Chrome-browser → Instellingen*.
3. Groepen `leerlingen`/`personeel`/`ict` (of bestaande) in de toestelprofielen zetten.
4. Geheimen in de config-repo-vault vervangen; certificaatverval **sep 2029** in de kalender.

## Tweestapsverificatie
LDAP is wachtwoord-only. Bewust zo gelaten (14 sep 2026). Chrome binnen de sessie doet wél de volledige
Google-login mét tweede factor.
