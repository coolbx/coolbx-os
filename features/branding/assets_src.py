#!/usr/bin/env python3
"""Vector-bronnen van de Coolbx OS-identiteit (ontwerp 'papier & inkt', ADR-0035).
Wordt door gen-assets.py aangeroepen; levert SVG-strings. Eén glyph, één palet."""

PAPER = "#faf8f3"; INK = "#2b2620"; NIGHT = "#141210"; MINT = "#50ce96"; AMBER = "#e8902a"; SUB = "#968e82"


def glyph_svg(size=512, tile=INK, sheet=PAPER, dot=MINT, tile_stroke=None, bare=False):
    """Het vel met de dot. bare=True → enkel vel+dot (geen tegel), voor balken/symbolic."""
    s = size / 120.0
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 120 120">']
    if not bare:
        stroke = f' stroke="{tile_stroke}" stroke-width="3"' if tile_stroke else ""
        out.append(f'<rect x="6" y="6" width="108" height="108" rx="26" fill="{tile}"{stroke}/>')
        out.append(f'<rect x="28" y="34" width="64" height="52" rx="10" fill="none" stroke="{sheet}" stroke-width="5"/>')
        out.append(f'<circle cx="60" cy="60" r="8" fill="{dot}"/>')
    else:
        out.append(f'<rect x="22" y="28" width="76" height="64" rx="12" fill="none" stroke="{sheet}" stroke-width="9"/>')
        out.append(f'<circle cx="60" cy="60" r="11" fill="{dot}"/>')
    out.append("</svg>")
    return "\n".join(out)


def paper_wallpaper_svg(w=3840, h=2160):
    """Bureaublad: licht papier, zwakke schrijflijnen, één mint kantlijn, mint dot met zachte gloed."""
    line_gap = round(h / 38)            # ~56 px op 1080p-equivalent
    margin_x = round(w * 0.083)
    dot_x, dot_y = round(w * 0.82), round(h * 0.88)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <pattern id="lijn" width="{w}" height="{line_gap}" patternUnits="userSpaceOnUse">
      <line x1="0" y1="{line_gap - 1}" x2="{w}" y2="{line_gap - 1}" stroke="{INK}" stroke-opacity="0.055" stroke-width="{max(1, round(h/1080))}"/>
    </pattern>
    <radialGradient id="vlek" cx="{dot_x}" cy="{dot_y}" r="{round(w*0.42)}" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{MINT}" stop-opacity="0.22"/>
      <stop offset="1" stop-color="{MINT}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="{PAPER}"/>
  <rect width="{w}" height="{h}" fill="url(#lijn)"/>
  <rect width="{w}" height="{h}" fill="url(#vlek)"/>
  <line x1="{margin_x}" y1="0" x2="{margin_x}" y2="{h}" stroke="{MINT}" stroke-opacity="0.35" stroke-width="{max(2, round(h/540))}"/>
  <circle cx="{dot_x}" cy="{dot_y}" r="{round(h/120)}" fill="{MINT}"/>
</svg>
'''


def night_wallpaper_svg(w=3840, h=2160):
    """Aanmelden/vergrendelscherm: nacht met één dot en zachte gloed — de wordmark komt van GDM zelf."""
    dot_x, dot_y = round(w * 0.5), round(h * 0.5)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
  <defs>
    <radialGradient id="gloed" cx="{dot_x}" cy="{dot_y}" r="{round(w*0.36)}" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="{MINT}" stop-opacity="0.10"/>
      <stop offset="1" stop-color="{MINT}" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="{w}" height="{h}" fill="{NIGHT}"/>
  <rect width="{w}" height="{h}" fill="url(#gloed)"/>
</svg>
'''
