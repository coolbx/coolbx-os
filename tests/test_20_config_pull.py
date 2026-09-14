"""Config-naad end-to-end (ADR-0032): het toestel trekt de config-repo (coolbx-ansible v3) en past een
profiel toe — kiosk-apps, Chrome-beleid + enrollment-token, Google-login-config, beheerderswachtwoord.

De repo wordt vanaf de dev-machine geserveerd (git dumb-HTTP op 10.0.2.2) zodat de test niet van
GitHub afhangt. Vereist ~/.config/coolbx/secrets/vault-pass (scripts/make-vault.sh in coolbx-ansible).
"""
import base64
import os
import subprocess
import threading
import http.server
import functools

import pytest

from harness import wait_for

REPO = os.path.expanduser("~/code/coolbx/coolbx-ansible")
SECRETS = os.path.expanduser("~/.config/coolbx/secrets")
PORT = 8765
HOST_FROM_VM = "10.0.2.2"

pytestmark = pytest.mark.skipif(
    not (os.path.isdir(os.path.join(REPO, ".git")) and os.path.exists(os.path.join(SECRETS, "vault-pass"))),
    reason="config-repo of vault-pass ontbreekt op de dev-machine",
)


def _put(vm, remote, data, mode="0644"):
    b64 = base64.b64encode(data.encode() if isinstance(data, str) else data).decode()
    vm.ssh_sudo(f"install -d -m0755 $(dirname {remote}) && echo {b64} | base64 -d > {remote} && chmod {mode} {remote}")


@pytest.fixture(scope="module")
def repo_server():
    subprocess.run(["git", "-C", REPO, "update-server-info"], check=True)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=REPO)
    srv = http.server.ThreadingHTTPServer(("0.0.0.0", PORT), handler)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    yield f"http://{HOST_FROM_VM}:{PORT}/.git"
    srv.shutdown()


@pytest.fixture(scope="module")
def pulled(vm, repo_server):
    if not vm.ssh_ok("test -x /usr/libexec/coolbx-ansible-pull"):
        pytest.skip("fleet-feature niet in deze image")
    # --full: git dumb-HTTP (de testserver) kent geen shallow clones
    _put(vm, "/etc/coolbx/ansible.conf", f'ANSIBLE_PULL_URL="{repo_server}"\nANSIBLE_PULL_PLAYBOOK="local.yml"\nANSIBLE_PULL_EXTRA_ARGS="--full"\n')
    _put(vm, "/etc/coolbx/vault-pass", open(os.path.join(SECRETS, "vault-pass"), "rb").read(), "0600")
    _put(vm, "/etc/coolbx/device.yaml", "role: leerling\nprofile: leerling-standaard\nchannel: stabiel\n")
    vm.ssh_sudo("rm -rf /var/lib/coolbx/ansible-checkout /etc/coolbx/kiosk-apps.d/* 2>/dev/null; true")
    out = vm.ssh_sudo("/usr/libexec/coolbx-ansible-pull 2>&1; echo rc=$?", timeout=600)
    assert "rc=0" in out, out[-3000:]
    assert "failed=0" in out, out[-3000:]
    yield vm


def test_status_json_written(pulled):
    st = pulled.ssh("cat /var/lib/coolbx/ansible-status.json")
    assert '"rc":0' in st and '"branch":"main"' in st and '"vault":true' in st, st


def test_kiosk_apps_from_profile(pulled):
    lst = pulled.ssh("coolbx-kiosk-apps list")
    assert "smartschool\tSmartschool" in lst and "bingel\tBingel" in lst, lst
    assert pulled.ssh_ok("test -f /var/lib/coolbx/share/applications/coolbx-kiosk-smartschool.desktop")
    pol = pulled.ssh("coolbx-kiosk-apps policy smartschool")
    assert '"URLBlocklist"' in pol and "smartschool.be" in pol


def test_chrome_policy_and_token(pulled):
    assert pulled.ssh_ok("test -f /etc/chromium/policies/managed/coolbx-profile.json")
    assert "HomepageLocation" in pulled.ssh("cat /etc/chromium/policies/managed/coolbx-profile.json")
    tok = pulled.ssh_sudo("cat /etc/opt/chrome/policies/enrollment/CloudManagementEnrollmentToken").strip()
    assert len(tok) == 36, "token ontbreekt of heeft onverwachte vorm"


def test_google_login_configured_from_vault(pulled):
    assert pulled.ssh_ok("test -f /etc/coolbx/google-login/config.yaml")
    assert "coolbx-test-leerlingen" in pulled.ssh("cat /etc/coolbx/google-login/config.yaml")
    assert pulled.ssh_sudo("stat -c '%a %G' /etc/sssd/coolbx-ldap.key").strip() in ("600 root", "640 sssd")
    wait_for(lambda: pulled.ssh_ok("systemctl is-active --quiet sssd.service"), timeout=30, desc="sssd actief")


def test_admin_password_from_vault(pulled):
    pw = open(os.path.join(SECRETS, "admin-password.txt")).read().strip()
    # Echte PAM-login van de beheerder (ssh) — en sudo werkt (wheel).
    p = subprocess.run(
        ["sshpass", "-p", pw, "ssh", "-o", "StrictHostKeyChecking=no", "-o", "UserKnownHostsFile=/dev/null",
         "-o", "NumberOfPasswordPrompts=1", "-p", "2222", "coolbx@127.0.0.1", f"echo {pw} | sudo -S id -u"],
        capture_output=True, text=True, timeout=60)
    assert p.returncode == 0 and p.stdout.strip().endswith("0"), p.stdout + p.stderr


def test_second_pull_is_noop(pulled):
    out = pulled.ssh_sudo("/usr/libexec/coolbx-ansible-pull 2>&1; echo rc=$?", timeout=300)
    assert "rc=0" in out
