"""Bureaublad-defaults (ADR-0035, design v2): vaste dock (Dash to Dock), papier-wallpaper met
rol-accent, lichte kleurmodus, mint accent. Statische dconf-/bestandschecks + de compiled dconf-db."""
import pytest


@pytest.fixture(scope="module", autouse=True)
def _feature(vm):
    if not vm.ssh_ok("test -f /etc/dconf/db/local.d/00-coolbx-branding"):
        pytest.skip("branding-feature niet in deze image")


def test_dash_to_dock_installed_and_enabled(vm):
    assert vm.ssh_ok("test -f /usr/share/gnome-shell/extensions/dash-to-dock@micxgx.gmail.com/metadata.json")
    # systeem-default uit de dconf-db (gebruiker 'tester' heeft geen eigen override)
    out = vm.ssh("gsettings get org.gnome.shell enabled-extensions")
    assert "dash-to-dock@micxgx.gmail.com" in out, out
    assert vm.ssh("gsettings get org.gnome.shell.extensions.dash-to-dock dock-position").strip() == "'BOTTOM'"
    assert vm.ssh("gsettings get org.gnome.shell.extensions.dash-to-dock dock-fixed").strip() == "true"


def test_wallpapers_present(vm):
    for f in ("coolbx-paper.png", "coolbx-paper-leerling.png", "coolbx-paper-leerkracht.png",
              "coolbx-paper-gedeeld.png", "coolbx-night.png", "coolbx-paper.svg"):
        assert vm.ssh_ok(f"test -s /usr/share/backgrounds/coolbx/{f}"), f


def test_light_desktop_mint_accent(vm):
    assert vm.ssh("gsettings get org.gnome.desktop.interface color-scheme").strip() == "'default'"
    assert vm.ssh("gsettings get org.gnome.desktop.interface accent-color").strip() == "'green'"
    uri = vm.ssh("gsettings get org.gnome.desktop.background picture-uri").strip()
    assert "coolbx-paper" in uri, uri


def test_role_wallpaper_when_role_feature_present(vm):
    # dev-image bevat role-gedeeld → zand-accent-wallpaper
    if not vm.ssh_ok("test -f /etc/dconf/db/local.d/40-coolbx-role-wallpaper"):
        pytest.skip("geen rol-feature in deze image")
    uri = vm.ssh("gsettings get org.gnome.desktop.background picture-uri").strip()
    assert "coolbx-paper-" in uri, uri


def test_screen_class_and_chrome_wrapper(vm):
    # dev-VM = 1280x800 → 'normal'; helper aanwezig; Chrome-launcher gaat via de wrapper (basic + schaal)
    assert vm.ssh("/usr/libexec/coolbx-screen-class").strip() == "normal"
    if vm.ssh_ok("test -f /usr/share/applications/google-chrome.desktop"):
        assert vm.ssh_ok("grep -q '^Exec=/usr/libexec/coolbx-chrome' /usr/share/applications/google-chrome.desktop")
    assert vm.ssh_ok("test -x /usr/libexec/coolbx-display-fit && test -f /etc/xdg/autostart/coolbx-display-fit.desktop")
