"""Beheerder `coolbx` + powerwash (ADR-0031/0034). Mutaties in de -snapshot-VM; draait als
(bijna) laatste test omdat de wipe alle homes raakt (de tester-home wordt hersteld)."""
import pytest

from harness import wait_for


@pytest.fixture(scope="module", autouse=True)
def _feature(vm):
    if not vm.ssh_ok("test -x /usr/bin/coolbx-powerwash"):
        pytest.skip("admin-feature niet in deze image")


def test_admin_user_hidden_wheel(vm):
    ent = vm.ssh("getent passwd coolbx").strip()
    assert ent.startswith("coolbx:x:900:"), ent
    assert "/var/home/coolbx" in ent
    assert "coolbx" in vm.ssh("getent group wheel")
    # uid < 1000 → niet in de GDM-gebruikerslijst (AccountsService toont geen systeemaccounts)
    assert not vm.ssh_ok("busctl call org.freedesktop.Accounts /org/freedesktop/Accounts org.freedesktop.Accounts ListCachedUsers | grep -q coolbx")


def test_powerwash_launcher_only_for_wheel(vm):
    # TryExec-truc: 0750 root:wheel → niet-beheerders zien de launcher niet.
    assert vm.ssh_sudo("stat -c '%a %U:%G' /usr/bin/coolbx-powerwash-gui").strip() == "750 root:wheel"
    assert vm.ssh_ok("test -f /usr/share/applications/coolbx-powerwash.desktop")
    assert vm.ssh_ok("grep -q '^TryExec=/usr/bin/coolbx-powerwash-gui' /usr/share/applications/coolbx-powerwash.desktop")
    # de kiosk-user (geen wheel) mag het niet uitvoeren
    assert not vm.ssh_ok("echo tester | sudo -S -u coolbx-kiosk test -x /usr/bin/coolbx-powerwash-gui")


def test_powerwash_requires_root_and_marker(vm):
    assert not vm.ssh_ok("/usr/bin/coolbx-powerwash request")
    assert vm.ssh_sudo("/usr/bin/coolbx-powerwash status").strip() == "niet aangevraagd"
    vm.ssh_sudo("/usr/bin/coolbx-powerwash request")
    assert vm.ssh_sudo("test -f /var/lib/coolbx/powerwash && echo ja").strip() == "ja"
    assert vm.ssh_ok("systemctl is-enabled --quiet coolbx-powerwash.service")
    vm.ssh_sudo("/usr/bin/coolbx-powerwash cancel")
    assert not vm.ssh_ok("echo tester | sudo -S test -f /var/lib/coolbx/powerwash")


def test_powerwash_run_wipes_state(vm):
    # Simuleer de vroege-boot-run: dummy-home + toestelstaat → alles weg, image/accounts blijven.
    vm.ssh_sudo("mkdir -p /var/home/dummy /var/lib/AccountsService/users && echo x > /var/home/dummy/f && echo x > /var/lib/AccountsService/users/dummy && echo geheim > /etc/coolbx/vault-pass && echo tok > /etc/opt/chrome/policies/enrollment/CloudManagementEnrollmentToken || true")
    vm.ssh_sudo("/usr/bin/coolbx-powerwash request")
    out = vm.ssh_sudo("/usr/bin/coolbx-powerwash run")
    assert "klaar" in out, out
    for gone in ("/var/home/dummy", "/var/lib/AccountsService/users/dummy", "/etc/coolbx/vault-pass",
                 "/etc/opt/chrome/policies/enrollment/CloudManagementEnrollmentToken", "/var/lib/coolbx/powerwash"):
        assert not vm.ssh_ok(f"echo tester | sudo -S test -e {gone}"), f"niet gewist: {gone}"
    # accounts en image blijven; device.yaml komt terug uit het image (tmpfiles)
    assert vm.ssh_ok("getent passwd coolbx tester >/dev/null")
    assert vm.ssh_ok("test -f /etc/coolbx/device.yaml")
    # tester-home herstellen voor de volgende tests
    vm.ssh_sudo("mkdir -p /var/home/tester && chown tester:tester /var/home/tester")
    assert vm.ssh_ok("test -d /home/tester")
