"""Kiosk-start onder druk (gevonden op hardware, 15 sep): meerdere snelle starts mogen nooit eindigen in
een hangende sessie op een vergrendelde VT. Verwacht: één unit, sway draait als kiosk-user, na stop is de
VT terug op GNOME, geen gestapelde tmpfs-mounts, geen achtergebleven sessie-policy."""
import time

from harness import wait_for


def test_parallel_starts_yield_one_healthy_kiosk(vm):
    vm.kiosk_stop()
    time.sleep(2)
    # drie starts vlak na elkaar (zoals drie klikken op launchers)
    vm.ssh_sudo("for i in 1 2 3; do (setsid sh -c 'env COOLBX_KIOSK_DEBUG=1 /usr/bin/coolbx-kiosk-start test' >/dev/null 2>&1 &); sleep 0.3; done; true", check=False)
    wait_for(vm.kiosk_active, timeout=40, interval=2, desc="coolbx-kiosk active")
    wait_for(lambda: vm.ssh_ok("pgrep -u coolbx-kiosk -x sway >/dev/null"), timeout=40, interval=2, desc="sway als kiosk-user")
    # precies één tmpfs op de kiosk-home
    layers = vm.ssh_sudo("grep -c ' /var/lib/coolbx-kiosk ' /proc/self/mountinfo || true").strip()
    assert layers == "1", f"gestapelde mounts: {layers}"
    assert vm.ssh_sudo("fgconsole").strip() == "3"
    # netjes stoppen → terug naar GNOME, alles opgeruimd
    vm.ssh_sudo("systemctl stop coolbx-kiosk")
    wait_for(lambda: not vm.kiosk_active(), timeout=30, interval=2, desc="kiosk gestopt")
    assert vm.ssh_sudo("fgconsole").strip() == "2"
    assert vm.ssh_sudo("mountpoint -q /var/lib/coolbx-kiosk && echo ja || echo nee").strip() == "nee"
    assert not vm.ssh_ok("test -e /etc/chromium/policies/managed/coolbx-kiosk-app.json")


def test_start_while_running_is_refused(vm):
    vm.kiosk_stop()
    time.sleep(2)
    vm.kiosk_start(app="test", debug=True)
    wait_for(vm.kiosk_active, timeout=40, interval=2, desc="coolbx-kiosk active")
    out = vm.ssh_sudo("/usr/bin/coolbx-kiosk-start test 2>&1; echo rc=$?", check=False)
    assert ("draait al" in out or "wordt al een kiosk gestart" in out) and "rc=0" in out, out
    vm.kiosk_stop()
