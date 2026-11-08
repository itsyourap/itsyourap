"""Static artwork: animated header banner + toolkit card.

Not run by the scheduled workflow (nothing here changes on its own). Edit the
constants below and run `python -m readme_bot static` to regenerate.
Icons in ./icons come from tandpfun/skill-icons (MIT, see icons/LICENSE).
"""

from __future__ import annotations

import base64
from pathlib import Path

from .svg import MONO, SANS, THEME, card, delay, esc, write

T = THEME
ICONS = Path(__file__).with_name("icons")

NAME = "Ankan Pal"
ROLE = "Backend & DevOps Engineer"
TAGLINE = "Founding DevOps Engineer @ ProjectX Infinity Inc · Hybrid"
MOTTO = "Good systems begin with clear thinking."
CHIPS = ["Go", "Kubernetes", "Terraform", "AWS · Azure · GCP", "CI/CD"]

# (prompt?, text, colour class) — prompt lines are "typed", the rest print instantly.
TERMINAL = [
    (True, "whoami", ""),
    (False, "ankan — backend & devops engineer", "muted"),
    (True, "kubectl get stack -n itsyourap", ""),
    (False, "NAME          READY   STATUS", "dim"),
    (False, "api-services  3/3     Running", "ok"),
    (False, "infra         IaC     Applied", "ok"),
    (False, "pipelines     CI/CD   Passing", "ok"),
    (True, "uptime --since 2022", ""),
    (False, "shipping reliable systems ✓", "accent"),
]

TOOLKIT = [
    ("Languages", ["GoLang", "TypeScript", "Python-Dark", "Java-Dark", "Rust", "Bash-Dark"], []),
    ("Backend & Data", ["Spring-Dark", "NodeJS-Dark", "ExpressJS-Dark", "PostgreSQL-Dark", "MongoDB", "SQLite", "Prisma"], ["REST", "gRPC"]),
    ("Cloud & Infra", ["AWS-Dark", "Azure-Dark", "GCP-Dark", "Kubernetes", "Docker", "Terraform-Dark", "Linux-Dark"], []),
    ("Delivery", ["GithubActions-Dark", "Git"], ["ArgoCD", "CI/CD", "GitOps"]),
]


def _icon_uri(name: str) -> str:
    return "data:image/svg+xml;base64," + base64.b64encode((ICONS / f"{name}.svg").read_bytes()).decode()


def header_svg() -> str:
    w, h = 1000, 320
    char_w, type_speed = 7.9, 0.055
    tx, ty0, line_h = 552, 92, 21

    lines_svg, clips = [], []
    t = 0.6
    for i, (prompt, text, cls) in enumerate(TERMINAL):
        y = ty0 + i * line_h
        prefix_w = 0
        if prompt:
            prefix_w = 4 * char_w  # "~ $ "
            n = len(text)
            values = ";".join(f"{prefix_w + k * char_w:.1f}" for k in range(n + 1))
            anim = (
                f'<set attributeName="width" to="0" begin="0s"/>'
                f'<animate attributeName="width" values="{values}" calcMode="discrete" begin="{t:.2f}s" dur="{n * type_speed:.2f}s" fill="freeze"/>'
            )
            t += n * type_speed + 0.35
        else:
            anim = f'<set attributeName="width" to="0" begin="0s"/><set attributeName="width" to="440" begin="{t:.2f}s"/>'
            t += 0.12
        clips.append(f'<clipPath id="ln{i}"><rect x="{tx - 2}" y="{y - 15}" height="{line_h}" width="440">{anim}</rect></clipPath>')
        content = (
            f'<tspan class="ok">~</tspan> <tspan class="accent">$</tspan> {esc(text)}' if prompt else f'<tspan class="{cls}">{esc(text)}</tspan>'
        )
        lines_svg.append(f'<text clip-path="url(#ln{i})" x="{tx}" y="{y}" class="mono" font-size="13">{content}</text>')
    cursor_y = ty0 + len(TERMINAL) * line_h
    cursor = (
        f'<text x="{tx}" y="{cursor_y}" class="mono" font-size="13"><tspan class="ok">~</tspan> <tspan class="accent">$</tspan></text>'
        f'<rect x="{tx + 4 * char_w}" y="{cursor_y - 12}" width="8" height="15" fill="{T["accent"]}">'
        f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1" dur="1.1s" repeatCount="indefinite"/></rect>'
    )

    chips_svg, cx = [], 40
    for i, chip in enumerate(CHIPS):
        cw = len(chip) * 7.2 + 22
        chips_svg.append(
            f'<g class="fade" {delay(0.9 + i * 0.08)}><rect x="{cx}" y="246" width="{cw:.0f}" height="26" rx="13" fill="{T["chrome"]}" stroke="{T["border"]}"/>'
            f'<text x="{cx + cw / 2:.0f}" y="263" text-anchor="middle" class="mono" font-size="11.5" style="fill:{T["text"]}">{esc(chip)}</text></g>'
        )
        cx += cw + 8

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(NAME)} — {esc(ROLE)}">
<title>{esc(NAME)} — {esc(ROLE)}</title>
<style>
text {{ font-family: {SANS}; fill: {T['text']}; }}
.mono {{ font-family: {MONO}; white-space: pre; }}
.muted {{ fill: {T['muted']}; }} .dim {{ fill: {T['dim']}; }} .accent {{ fill: {T['accent']}; }} .ok {{ fill: {T['ok']}; }}
.fade {{ animation: fadeIn .8s ease-out both; }}
@keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(6px); }} to {{ opacity: 1; transform: none; }} }}
.glow {{ animation: drift 14s ease-in-out infinite alternate; }}
@keyframes drift {{ from {{ transform: translate(0,0); }} to {{ transform: translate(40px,-14px); }} }}
</style>
<defs>
  <pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1.1" fill="{T['grid']}"/></pattern>
  <radialGradient id="g1" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{T['accent']}" stop-opacity=".22"/><stop offset="1" stop-color="{T['accent']}" stop-opacity="0"/></radialGradient>
  <radialGradient id="g2" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{T['accent2']}" stop-opacity=".20"/><stop offset="1" stop-color="{T['accent2']}" stop-opacity="0"/></radialGradient>
  <linearGradient id="roleGrad" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{T['accent']}"/><stop offset="1" stop-color="{T['accent2']}"/></linearGradient>
  <clipPath id="frame"><rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16"/></clipPath>
  {''.join(clips)}
</defs>
<g clip-path="url(#frame)">
  <rect width="{w}" height="{h}" fill="{T['bg']}"/>
  <rect width="{w}" height="{h}" fill="url(#dots)"/>
  <ellipse class="glow" cx="170" cy="70" rx="320" ry="190" fill="url(#g1)"/>
  <ellipse class="glow" cx="860" cy="280" rx="340" ry="200" fill="url(#g2)" style="animation-delay:-7s"/>

  <g class="fade">
    <text x="40" y="62" class="mono" font-size="13"><tspan class="accent">//</tspan> <tspan class="muted">hello, world — i'm</tspan></text>
    <text x="38" y="118" font-size="54" font-weight="800" letter-spacing="-1">{esc(NAME)}</text>
  </g>
  <g class="fade" {delay(0.25)}>
    <text x="40" y="156" font-size="24" font-weight="700" fill="url(#roleGrad)" style="fill:url(#roleGrad)">{esc(ROLE)}</text>
    <text x="40" y="186" font-size="14" class="muted">{esc(TAGLINE)}</text>
  </g>
  <g class="fade" {delay(0.5)}>
    <rect x="40" y="204" width="3" height="22" rx="1.5" fill="{T['accent']}"/>
    <text x="52" y="220" font-size="14" font-style="italic" style="fill:{T['text']}">“{esc(MOTTO)}”</text>
  </g>
  {''.join(chips_svg)}

  <g>
    <rect x="530" y="30" width="440" height="262" rx="12" fill="{T['chrome']}" fill-opacity=".92" stroke="{T['border']}"/>
    <path d="M530 62 h440" stroke="{T['border']}"/>
    <circle cx="550" cy="46" r="5.5" fill="#ff5f57"/><circle cx="568" cy="46" r="5.5" fill="#febc2e"/><circle cx="586" cy="46" r="5.5" fill="#28c840"/>
    <text x="750" y="50" text-anchor="middle" class="mono dim" font-size="11.5">ankan@prod: ~</text>
    {''.join(lines_svg)}
    {cursor}
  </g>
</g>
<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="16" fill="none" stroke="{T['border']}"/>
</svg>
"""


def toolkit_svg() -> str:
    w = 1000
    row_h, icon, gap = 66, 44, 12
    h = 36 + 24 + row_h * len(TOOLKIT) + 8
    body = []
    for r, (label, icons, pills) in enumerate(TOOLKIT):
        y = 24 + r * row_h
        body.append(
            f'<g class="fade" {delay(r * 0.12)}>'
            f'<text x="24" y="{y + 27}" class="mono" font-size="12.5"><tspan class="accent">{esc(label.lower().replace(" & ", "_").replace(" ", "_"))}</tspan><tspan class="dim">:</tspan></text>'
        )
        x = 190
        for name in icons:
            body.append(f'<image x="{x}" y="{y}" width="{icon}" height="{icon}" href="{_icon_uri(name)}"><title>{esc(name.split("-")[0])}</title></image>')
            x += icon + gap
        for pill in pills:
            pw = len(pill) * 7.6 + 24
            body.append(
                f'<rect x="{x}" y="{y + 9}" width="{pw:.0f}" height="26" rx="13" fill="{T["chrome"]}" stroke="{T["border"]}"/>'
                f'<text x="{x + pw / 2:.0f}" y="{y + 26}" text-anchor="middle" class="mono" font-size="12">{esc(pill)}</text>'
            )
            x += pw + 8
        body.append("</g>")
        if r < len(TOOLKIT) - 1:
            body.append(f'<line x1="24" y1="{y + row_h - 10}" x2="{w - 24}" y2="{y + row_h - 10}" stroke="{T["grid"]}"/>')
    return card(w, h, "~/toolkit.yaml", "\n".join(body), right_label="what I build with")


def build(root: Path) -> None:
    out = root / "assets" / "static"
    write(out / "header.svg", header_svg())
    write(out / "toolkit.svg", toolkit_svg())
