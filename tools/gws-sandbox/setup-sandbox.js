#!/usr/bin/env node
// Coolbx OS — Google Workspace sandbox-opzet (testaccounts + testgroepen).
//
// Maakt ALLEEN aan onder de OU /coolbx-sandbox. Weigert elke gebruiker die al
// bestaat buiten die OU. Idempotent: bestaande sandbox-objecten worden overgeslagen.
// Default = dry-run (alleen lezen). Live uitvoeren met --apply.
//
// Draaien (gebruikt de node_modules + service-account-sleutel van account-sync):
//   cd ~/code/sync_2026_2027/account-sync && NODE_PATH=node_modules \
//     GWS_KEYFILE=$(ls src/key/*.json) node ~/code/coolbx/coolbx-os/tools/gws-sandbox/setup-sandbox.js [--apply]
//
// Wachtwoorden van nieuw aangemaakte accounts gaan NOOIT naar stdout; ze worden
// (mode 0600) toegevoegd aan ~/.config/coolbx/secrets/test-accounts.txt.
'use strict'
const fs = require('fs')
const os = require('os')
const path = require('path')
const crypto = require('crypto')
const ga = require('g-admin-client')
const { google } = require('googleapis')

const APPLY = process.argv.includes('--apply')
const OU = '/coolbx-sandbox'
const DOMAIN = process.env.GWS_DOMAIN || 'edugolo.be'
const STUDENT_DOMAIN = process.env.GWS_STUDENT_DOMAIN || 'lln.edugolo.be'
const ADMIN = process.env.GWS_ADMIN || 'johan.coppens@edugolo.be'
const KEYFILE = process.env.GWS_KEYFILE
const SECRETS_DIR = path.join(os.homedir(), '.config', 'coolbx', 'secrets')
const SECRETS_FILE = path.join(SECRETS_DIR, 'test-accounts.txt')

const USERS = [
  { email: `coolbx-test-lln1@${STUDENT_DOMAIN}`, firstName: 'Coolbx Test', lastName: 'Leerling 1', groups: ['leerlingen'] },
  { email: `coolbx-test-lln2@${STUDENT_DOMAIN}`, firstName: 'Coolbx Test', lastName: 'Leerling 2', groups: ['leerlingen'] },
  { email: `coolbx-test-lkr1@${DOMAIN}`, firstName: 'Coolbx Test', lastName: 'Leerkracht 1', groups: ['personeel'] },
  { email: `coolbx-test-lkr2@${DOMAIN}`, firstName: 'Coolbx Test', lastName: 'Leerkracht 2', groups: ['personeel'] },
  { email: `coolbx-test-ict1@${DOMAIN}`, firstName: 'Coolbx Test', lastName: 'ICT 1', groups: ['personeel', 'ict'] }
]
const GROUPS = {
  leerlingen: { email: `coolbx-test-leerlingen@${DOMAIN}`, name: 'Coolbx test – leerlingen' },
  personeel: { email: `coolbx-test-personeel@${DOMAIN}`, name: 'Coolbx test – personeel' },
  ict: { email: `coolbx-test-ict@${DOMAIN}`, name: 'Coolbx test – ict' }
}

const log = (...a) => console.log(`[${APPLY ? 'APPLY' : 'DRY-RUN'}]`, ...a)
const fail = (msg) => { console.error('FOUT:', msg); process.exit(1) }
const newPassword = () => crypto.randomBytes(18).toString('base64url').slice(0, 20)
const sleep = (ms) => new Promise((r) => setTimeout(r, ms))

const main = async () => {
  if (!KEYFILE || !fs.existsSync(KEYFILE)) fail('GWS_KEYFILE ontbreekt of bestaat niet')
  await ga.init({ keyFile: KEYFILE, gSuiteAdminAccount: ADMIN, domain: DOMAIN })

  // 1. Harde vangrail: de sandbox-OU MOET bestaan (we maken 'm niet zelf aan).
  const dir = google.admin('directory_v1')
  try {
    const ou = await dir.orgunits.get({ customerId: 'my_customer', orgUnitPath: OU.replace(/^\//, '') })
    log(`OU gevonden: ${ou.data.orgUnitPath} (${ou.data.name})`)
    if (ou.data.orgUnitPath !== OU) fail(`OU-pad wijkt af: ${ou.data.orgUnitPath}`)
  } catch (err) {
    fail(`OU ${OU} niet gevonden of niet leesbaar: ${err.message}`)
  }

  // 2. Groepen.
  for (const [key, g] of Object.entries(GROUPS)) {
    const existing = await ga.getGroup({ groupKey: g.email })
    if (existing) { log(`groep bestaat: ${g.email}`); continue }
    log(`groep aanmaken: ${g.email} (${key})`)
    if (APPLY) await ga.createGroup({ email: g.email, name: g.name, description: 'Coolbx OS sandbox — testgroep, geen echte personen' })
  }

  // 3. Gebruikers (alleen in de sandbox-OU; nooit iets buiten de OU aanraken).
  const created = []
  for (const u of USERS) {
    const existing = await ga.getUser({ userKey: u.email })
    if (existing) {
      if (existing.orgUnitPath !== OU) fail(`${u.email} bestaat BUITEN de sandbox (${existing.orgUnitPath}) — stop, niets aangeraakt`)
      log(`gebruiker bestaat in sandbox: ${u.email}`)
      continue
    }
    log(`gebruiker aanmaken: ${u.email} in ${OU}`)
    if (APPLY) {
      const password = newPassword()
      await ga.createUser({ email: u.email, firstName: u.firstName, lastName: u.lastName, password, orgUnitPath: OU, changePasswordAtNextLogin: false })
      created.push({ email: u.email, password })
      await sleep(1000) // API-consistentie vóór groepslidmaatschap (zelfde workaround als sync.js)
    }
  }

  // 4. Wachtwoorden veilig wegschrijven (alleen nieuw aangemaakte).
  if (created.length) {
    fs.mkdirSync(SECRETS_DIR, { recursive: true, mode: 0o700 })
    const lines = created.map((c) => `${c.email}\t${c.password}`).join('\n') + '\n'
    fs.appendFileSync(SECRETS_FILE, lines, { mode: 0o600 })
    fs.chmodSync(SECRETS_FILE, 0o600)
    log(`${created.length} wachtwoord(en) toegevoegd aan ${SECRETS_FILE}`)
  }

  // 5. Lidmaatschappen.
  for (const u of USERS) {
    for (const key of u.groups) {
      const g = GROUPS[key]
      let members = []
      try { members = APPLY || await ga.getGroup({ groupKey: g.email }) ? await ga.getGroupMembers({ groupKey: g.email }) : [] } catch (_) { members = [] }
      if (members.some((m) => (m.email || '').toLowerCase() === u.email.toLowerCase())) { log(`lid al aanwezig: ${u.email} in ${g.email}`); continue }
      log(`lid toevoegen: ${u.email} -> ${g.email}`)
      if (APPLY) await ga.addUserToGroup({ groupKey: g.email, email: u.email })
    }
  }

  // 6. Eindcontrole: alles wat in de sandbox-OU staat.
  const res = await dir.users.list({ customer: 'my_customer', query: `orgUnitPath='${OU}'`, maxResults: 100 })
  const inOU = res.data.users || []
  log(`gebruikers in ${OU}: ${inOU.map((x) => x.primaryEmail).sort().join(', ') || '(geen)'}`)
  log('klaar')
}

main().catch((err) => { console.error('FOUT:', err.message || err); process.exit(1) })
