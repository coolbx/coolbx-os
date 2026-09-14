#!/usr/bin/env python3
"""Genereer de Coolbx OS-brandingassets (ontwerp 'papier & inkt', ADR-0035).
Vector-eerst: glyph/wallpapers zijn SVG (assets-src.py), PNG's worden gerenderd met inkscape;
de wordmark wordt met Inter gezet (PIL). Reproduceerbaar: draai vanuit de repo-root.
  python3 features/branding/gen-assets.py
"""
import base64
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
import assets_src as src  # noqa: E402

SF = os.path.join(os.path.dirname(__file__), "system_files")
KIOSK_SF = os.path.join(os.path.dirname(__file__), "..", "kiosk", "system_files")
FOCUS_SF = os.path.join(os.path.dirname(__file__), "..", "focus", "system_files")
FD = "/usr/share/fonts/rsms-inter-fonts/"
MINT = (80, 206, 150); PAPER = (250, 248, 243); BG = (20, 18, 16); INK = (43, 38, 32)


def f(n, s):
    return ImageFont.truetype(FD + n, s)


def ensure(p):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def svg_to_png(svg, out, w=None, h=None):
    tmp = out + ".svg"
    open(ensure(tmp), "w").write(svg)
    cmd = ["inkscape", tmp, "--export-type=png", f"--export-filename={out}"]
    if w: cmd.append(f"--export-width={w}")
    if h: cmd.append(f"--export-height={h}")
    subprocess.run(cmd, check=True, capture_output=True)
    os.remove(tmp)


def wordmark(size, accent=MINT, cool=PAPER):
    b = f("InterDisplay-Black.ttf", size); l = f("InterDisplay-Light.ttf", size)
    tmp = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    w1 = tmp.textbbox((0, 0), "coolbx", font=b)[2]; gap = int(size * 0.30)
    w2 = tmp.textbbox((0, 0), "os", font=l)[2]
    W = w1 + gap + w2; H = int(size * 1.4)
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    d.text((0, 0), "coolbx", font=b, fill=cool)
    d.text((w1 + gap, 0), "os", font=l, fill=accent)
    return img.crop(img.getbbox())


def embed_svg(png_path, w, h):
    b = base64.b64encode(open(png_path, "rb").read()).decode()
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{w}" height="{h}" viewBox="0 0 {w} {h}">\n'
            f'  <image width="{w}" height="{h}" xlink:href="data:image/png;base64,{b}"/>\n</svg>\n')


# ── Plymouth: GROTE wordmark-bron (het script schaalt naar 13 % van de schermbreedte) + dot ──
wordmark(300).save(ensure(f"{SF}/usr/share/plymouth/themes/coolbx/logo.png"))
dot = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
ImageDraw.Draw(dot).ellipse([0, 0, 63, 63], fill=MINT)
dot.save(ensure(f"{SF}/usr/share/plymouth/themes/coolbx/dot.png"))

# ── GRUB: vlakke nacht-achtergrond + losse wordmark als image-component (theme.txt) ──
Image.new("RGB", (1920, 1080), BG).save(ensure(f"{SF}/usr/share/grub/themes/coolbx/background.png"))
wordmark(76).save(ensure(f"{SF}/usr/share/grub/themes/coolbx/logo.png"))

# ── Wordmarks (wit voor donker, inkt voor licht) — GNOME 'Over', GDM-logo, Fedora-asset-vervanging ──
white_wm = wordmark(120, cool=PAPER)
white_wm.save(ensure(f"{SF}/usr/share/coolbx/branding/coolbx-wordmark-white.png"))
open(ensure(f"{SF}/usr/share/coolbx/branding/coolbx-wordmark-white.svg"), "w").write(
    embed_svg(f"{SF}/usr/share/coolbx/branding/coolbx-wordmark-white.png", white_wm.width, white_wm.height))
ink_wm = wordmark(120, cool=INK)
ink_png = f"{SF}/usr/share/coolbx/branding/coolbx-wordmark-ink.png"
ink_wm.save(ensure(ink_png))
open(ensure(f"{SF}/usr/share/coolbx/branding/coolbx-wordmark-ink.svg"), "w").write(embed_svg(ink_png, ink_wm.width, ink_wm.height))
# GDM-logo (onderaan het aanmeldscherm): bescheiden, 2×-scherp.
wordmark(56, cool=PAPER).save(ensure(f"{SF}/usr/share/coolbx/branding/coolbx-gdm-logo.png"))

# ── Glyph: het vel met de dot (tegel voor icoon-lookups; kale glyph voor balken) ──
for name, kw in {
    "coolbx-logo":       dict(tile=src.PAPER, sheet=src.INK, dot=src.MINT, tile_stroke="#d9d2c6"),   # lichte modus ('Over')
    "coolbx-logo-dark":  dict(tile=src.INK, sheet=src.PAPER, dot=src.MINT),                          # donkere modus
    "coolbx-logo-white": dict(tile=src.INK, sheet=src.PAPER, dot=src.MINT),
}.items():
    svg = src.glyph_svg(512, **kw)
    open(ensure(f"{SF}/usr/share/coolbx/branding/{name}.svg"), "w").write(svg)
    svg_to_png(svg, ensure(f"{SF}/usr/share/icons/hicolor/256x256/apps/{name}.png"), 256, 256)
    svg_to_png(svg, ensure(f"{SF}/usr/share/icons/hicolor/512x512/apps/{name}.png"), 512, 512)
    svg_to_png(svg, ensure(f"{SF}/usr/share/coolbx/branding/{name}.png"), 256, 256)
# kiosk-app-icoon (mint) in de kiosk-feature; Toetsmodus (amber) in de focus-feature
for sf, name, dotc in ((KIOSK_SF, "coolbx-kiosk", src.MINT), (FOCUS_SF, "coolbx-focus", src.AMBER)):
    svg = src.glyph_svg(512, tile=src.INK, sheet=src.PAPER, dot=dotc)
    open(ensure(f"{sf}/usr/share/icons/hicolor/scalable/apps/{name}.svg"), "w").write(svg)
    svg_to_png(svg, ensure(f"{sf}/usr/share/icons/hicolor/256x256/apps/{name}.png"), 256, 256)
    svg_to_png(svg, ensure(f"{sf}/usr/share/icons/hicolor/512x512/apps/{name}.png"), 512, 512)

# ── Wallpapers: papier (bureaublad) en nacht (aanmelden/vergrendelen), SVG-bron + 4K-PNG ──
paper = src.paper_wallpaper_svg()
open(ensure(f"{SF}/usr/share/backgrounds/coolbx/coolbx-paper.svg"), "w").write(paper)
svg_to_png(paper, ensure(f"{SF}/usr/share/backgrounds/coolbx/coolbx-paper.png"))
night = src.night_wallpaper_svg()
open(ensure(f"{SF}/usr/share/backgrounds/coolbx/coolbx-night.svg"), "w").write(night)
svg_to_png(night, ensure(f"{SF}/usr/share/backgrounds/coolbx/coolbx-night.png"))
# oude namen weg
for old in ("coolbx-dark.png", "coolbx-login.png"):
    p = f"{SF}/usr/share/backgrounds/coolbx/{old}"
    if os.path.exists(p): os.remove(p)
old_icon = f"{KIOSK_SF}/usr/share/icons/hicolor/256x256/apps/coolbx-kiosk.png"
print("branding-assets gegenereerd in", SF)
