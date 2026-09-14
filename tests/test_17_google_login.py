"""Google-login via Secure LDAP → SSSD (ADR-0031), end-to-end tegen de Workspace-sandbox.

Vereist de sandbox-geheimen op de dev-machine (~/.config/coolbx/secrets, docs/WORKSPACE.md) en
netwerk in de VM. Bewijst: config+geheimen → sssd actief; testleerling resolvet (getent) en kan
via PAM (ssh met wachtwoord) aanmelden → home aangemaakt; een leerkracht buiten allow_groups wordt
GEWEIGERD; groepen uit Google resolven. Mutaties draaien in de -snapshot-VM.
"""
import base64
import os
import subprocess

import pytest

from harness import wait_for, SSH_PORT, SSH_HOST

SECRETS = os.path.expanduser("~/.config/coolbx/secrets")
LLN = "coolbx-test-lln1"
LKR = "coolbx-test-lkr1"

pytestmark = pytest.mark.skipif(
    not all(os.path.exists(os.path.join(SECRETS, f)) for f in ("ldap-client.crt", "ldap-client.key", "ldap-access.txt", "test-accounts.txt")),
    reason="sandbox-geheimen ontbreken in ~/.config/coolbx/secrets",
)

CONFIG = """domain: lln.edugolo.be
search_bases:
  - dc=lln,dc=edugolo,dc=be
  - dc=edugolo,dc=be
group_base: ou=Groups,dc=edugolo,dc=be
allow_groups:
  - coolbx-test-leerlingen
  - coolbx-test-ict
"""


def _pw(email):
    for line in open(os.path.join(SECRETS, "test-accounts.txt")):
        parts = line.rstrip("\n").split("\t")
        if parts[0] == email:
            return parts[1]
    raise KeyError(email)


def _put(vm, remote, data, mode="0600"):
    """Schrijf bytes/str als root naar de VM zonder quoting-gedoe (base64 over ssh)."""
    if isinstance(data, str):
        data = data.encode()
    b64 = base64.b64encode(data).decode()
    vm.ssh_sudo(f"install -d -m0755 $(dirname {remote}) && echo {b64} | base64 -d > {remote} && chmod {mode} {remote}")


def _push(vm, local, remote, mode="0600"):
    _put(vm, remote, open(local, "rb").read(), mode)


def _login(user, password):
    """Echte PAM-login over ssh (password-auth) — bewijst auth + access-filter + mkhomedir."""
    p = subprocess.run(
        ["sshpass", "-p", password, "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
         "-o", "ConnectTimeout=10", "-o", "NumberOfPasswordPrompts=1", "-p", SSH_PORT, f"{user}@{SSH_HOST}", "echo LOGIN_OK; echo $HOME"],
        capture_output=True, text=True, timeout=60,
    )
    return p.returncode, p.stdout


@pytest.fixture(scope="module")
def sssd(vm):
    if not vm.ssh_ok("test -x /usr/libexec/coolbx-google-login-apply"):
        pytest.skip("google-login-feature niet in deze image")
    if not vm.ssh_ok("curl -sf -o /dev/null --max-time 10 https://www.google.com/generate_204 || curl -sf -o /dev/null --max-time 10 https://ldap.google.com/"):
        pytest.fail("VM heeft geen netwerk naar Google — Google-login-test kan niet draaien")
    _push(vm, os.path.join(SECRETS, "ldap-client.crt"), "/etc/sssd/coolbx-ldap.crt")
    _push(vm, os.path.join(SECRETS, "ldap-client.key"), "/etc/sssd/coolbx-ldap.key")
    _push(vm, os.path.join(SECRETS, "ldap-access.txt"), "/etc/coolbx/google-login/access")
    _put(vm, "/etc/coolbx/google-login/config.yaml", CONFIG, "0644")
    out = vm.ssh_sudo("/usr/libexec/coolbx-google-login-apply")
    assert "actief" in out, out
    wait_for(lambda: vm.ssh_ok("systemctl is-active --quiet sssd.service"), timeout=30, desc="sssd actief")
    yield vm


def test_sssd_config_root_only(sssd):
    assert sssd.ssh_sudo("stat -c '%a' /etc/sssd/conf.d/coolbx-google.conf").strip() == "600"
    assert not sssd.ssh_ok("cat /etc/sssd/conf.d/coolbx-google.conf")


def test_student_resolves_via_nss(sssd):
    out = wait_for(lambda: sssd.ssh(f"getent passwd {LLN} || true").strip(), timeout=60, interval=3, desc="getent leerling")
    assert out.startswith(f"{LLN}:"), out
    assert f"/home/{LLN}" in out


def test_google_groups_resolve(sssd):
    out = sssd.ssh("getent group coolbx-test-leerlingen || true").strip()
    assert out.startswith("coolbx-test-leerlingen:"), out
    assert LLN in out


def test_student_login_creates_home(sssd):
    rc, out = _login(LLN, _pw(f"{LLN}@lln.edugolo.be"))
    assert rc == 0 and "LOGIN_OK" in out, out
    assert sssd.ssh_ok(f"test -d /home/{LLN}")
    assert sssd.ssh_sudo(f"stat -c '%U' /home/{LLN}").strip() == LLN


def test_wrong_password_rejected(sssd):
    rc, out = _login(LLN, "verkeerd-wachtwoord")
    assert rc != 0 and "LOGIN_OK" not in out


def test_teacher_denied_on_student_device(sssd):
    # lkr1 zit in coolbx-test-personeel, niet in de allow_groups van dit (leerling-)profiel.
    rc, out = _login(LKR, _pw(f"{LKR}@edugolo.be"))
    assert rc != 0 and "LOGIN_OK" not in out, out
    assert not sssd.ssh_ok(f"test -d /home/{LKR}")


def test_teacher_allowed_after_profile_change(sssd):
    cfg = CONFIG.replace("  - coolbx-test-leerlingen\n  - coolbx-test-ict\n", "  - coolbx-test-personeel\n")
    _put(sssd, "/etc/coolbx/google-login/config.yaml", cfg, "0644")
    sssd.ssh_sudo("/usr/libexec/coolbx-google-login-apply")
    sssd.ssh_sudo("sss_cache -E || true")
    wait_for(lambda: sssd.ssh_ok("systemctl is-active --quiet sssd.service"), timeout=30, desc="sssd actief")
    rc, out = _login(LKR, _pw(f"{LKR}@edugolo.be"))
    assert rc == 0 and "LOGIN_OK" in out, out
    # en de leerling is nu de uitgeslotene
    rc, out = _login(LLN, _pw(f"{LLN}@lln.edugolo.be"))
    assert rc != 0
