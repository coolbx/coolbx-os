"""Gedeeld toestel (ADR-0031, role-gedeeld): lokale wachtwoordloze gebruiker 'leerling', home
gewist bij afmelden (GDM PostSession) en bij boot (unit)."""
import pytest


@pytest.fixture(scope="module", autouse=True)
def _feature(vm):
    if not vm.ssh_ok("test -x /usr/bin/coolbx-gedeeld-reset"):
        pytest.skip("role-gedeeld niet in deze image")


def test_shared_user_exists(vm):
    ent = vm.ssh("getent passwd leerling").strip()
    assert ent.startswith("leerling:x:1500:"), ent


def test_gdm_pam_passwordless_for_shared_user_only(vm):
    pam = vm.ssh("cat /etc/pam.d/gdm-password")
    assert "pam_succeed_if.so user = leerling" in pam, pam
    # de gewone stack blijft eronder staan
    assert "password-auth" in pam


def test_reset_units_present(vm):
    assert vm.ssh_ok("systemctl is-enabled --quiet coolbx-gedeeld-reset.service")
    assert vm.ssh_ok("test -x /etc/gdm/PostSession/Default")
    assert "coolbx-gedeeld-reset" in vm.ssh("cat /etc/gdm/PostSession/Default")


def test_reset_gives_fresh_home(vm):
    vm.ssh_sudo("mkdir -p /var/home/leerling && echo rommel > /var/home/leerling/rommel.txt && chown -R leerling:leerling /var/home/leerling")
    vm.ssh_sudo("/usr/bin/coolbx-gedeeld-reset")
    assert not vm.ssh_ok("echo tester | sudo -S test -e /var/home/leerling/rommel.txt")
    assert vm.ssh_sudo("stat -c '%U %a' /var/home/leerling").strip() == "leerling 700"
