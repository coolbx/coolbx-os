"""Laag B — systeemstaat na boot (SSH-CLI-asserts; geen pixels). De goedkoopste, minst brosse laag."""


def test_gdm_active(vm):
    assert vm.ssh_ok("systemctl is-active --quiet gdm")


def test_networkmanager_active(vm):
    assert vm.ssh_ok("systemctl is-active --quiet NetworkManager")


def test_default_target_graphical(vm):
    assert vm.ssh("systemctl get-default").strip() == "graphical.target"


def test_gnome_shell_running(vm):
    assert vm.ssh_ok("pgrep -x gnome-shell")


def test_no_failed_units(vm):
    failed = vm.ssh("systemctl --failed --no-legend --plain 2>/dev/null || true").strip()
    assert failed == "", f"gefaalde units:\n{failed}"


def test_locale_nl_be(vm):
    assert "nl_BE" in vm.ssh("cat /etc/locale.conf")


def test_browser_present(vm):
    # Chrome (chrome-feature) óf Chromium (chromium-feature) — ADR-0033
    out = vm.ssh("command -v google-chrome-stable chromium-browser chromium 2>/dev/null || true")
    assert "chrome" in out or "chromium" in out, out


def test_kiosk_unit_files_present(vm):
    # de generieke kiosk (ADR-0029): launcher, registry, browserwrapper, sway-config, enforcement
    for f in (
        "/usr/bin/coolbx-kiosk-start",
        "/usr/bin/coolbx-kiosk-apps",
        "/usr/share/coolbx/kiosk/chromium-kiosk.sh",
        "/usr/share/coolbx/kiosk/sway.conf",
        "/etc/chromium/policies/managed/coolbx-enforcement.json",
    ):
        assert vm.ssh_ok(f"test -f {f}"), f"ontbreekt: {f}"


def test_kiosk_app_registry_lists_dev_test_app(vm):
    # dev-build: de 'test'-app (placeholder) staat in de registry en heeft een launcher
    out = vm.ssh("coolbx-kiosk-apps list")
    assert "test\tTestmodus" in out, out
    assert vm.ssh_ok("test -f /usr/share/applications/coolbx-kiosk-test.desktop")
