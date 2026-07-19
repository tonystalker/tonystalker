"""
make_info_card.py

Hand-authored SVG that looks like the output of `neofetch`: a title
bar, then colored key/value rows. This card carries the story numbers
can't tell (role, current focus, stack, highlights) — the contribution
heatmap already covers raw GitHub stats, so there's no overlap.

Each line fades + slides in on a short stagger. Set STATIC=1 to emit a
frozen frame (all lines already visible) for local previews.

Usage:
    python scripts/make_info_card.py
Writes:
    info-card.svg
"""
import os
from pathlib import Path

TITLE = "tony@github"
ROWS = [
    ("Now", "Building FlowDesk — agentic customer support platform"),
    ("Prev", "VoiceFlow AI — local always-on voice assistant"),
    ("Edu", "IIT (BHU) Varanasi — Ceramic Eng. '26"),
    ("Stack", "LangGraph · LangChain · FastAPI · Qdrant · GCP"),
    ("Rank", "LeetCode Knight · Codeforces Specialist"),
    ("Looking for", "SDE / AI-GenAI roles at early-stage startups"),
]

KEY_COL_W = 108
CHAR_PX = 7.9  # approx monospace advance at font-size 13
WIDTH = round(KEY_COL_W + max(len(v) for _, v in ROWS) * CHAR_PX + 2 * 20)
BAR_H = 32
ROW_H = 28
PAD_X = 20
TOP_PAD = 14

KEY_COLOR = "#39d353"
VAL_COLOR = "#c9d1d9"
BG = "#0d1117"
BORDER = "#30363d"
BAR_BG = "#161b22"

STAGGER = 0.12
DUR = 0.35
static = os.environ.get("STATIC") == "1"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg() -> str:
    height = BAR_H + TOP_PAD + len(ROWS) * ROW_H + TOP_PAD

    rows_svg = []
    for i, (key, val) in enumerate(ROWS):
        y = BAR_H + TOP_PAD + i * ROW_H + 18
        begin = i * STAGGER

        if static:
            opacity_attr = 'opacity="1"'
            transform = ""
            anim = ""
        else:
            opacity_attr = 'opacity="0"'
            transform = 'transform="translate(-8,0)"'
            anim = (
                f'<animate attributeName="opacity" from="0" to="1" '
                f'dur="{DUR}s" begin="{begin:.2f}s" fill="freeze"/>'
                f'<animateTransform attributeName="transform" type="translate" '
                f'from="-8,0" to="0,0" dur="{DUR}s" begin="{begin:.2f}s" fill="freeze"/>'
            )

        rows_svg.append(
            f'<g {opacity_attr} {transform}>'
            f'<text x="{PAD_X}" y="{y}" font-family="Consolas, Menlo, monospace" '
            f'font-size="13" font-weight="700" fill="{KEY_COLOR}">{esc(key)}</text>'
            f'<text x="{PAD_X + KEY_COL_W}" y="{y}" font-family="Consolas, Menlo, monospace" '
            f'font-size="13" fill="{VAL_COLOR}">{esc(val)}</text>'
            f'{anim}'
            f'</g>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}">
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<path d="M0.5 {BAR_H} h{WIDTH - 1}" stroke="{BORDER}"/>
<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{BAR_H}" rx="10" fill="{BAR_BG}"/>
<rect x="0.5" y="{BAR_H / 2}" width="{WIDTH - 1}" height="{BAR_H / 2}" fill="{BAR_BG}"/>
<circle cx="24" cy="{BAR_H / 2}" r="6" fill="#ff5f56"/>
<circle cx="44" cy="{BAR_H / 2}" r="6" fill="#ffbd2e"/>
<circle cx="64" cy="{BAR_H / 2}" r="6" fill="#27c93f"/>
<text x="{WIDTH / 2}" y="{BAR_H / 2 + 4}" text-anchor="middle" font-family="Consolas, Menlo, monospace" font-size="12" fill="#8b949e">{esc(TITLE)}</text>
{''.join(rows_svg)}
</svg>'''
    return svg


def main():
    out = "info-card.svg"
    Path(out).write_text(build_svg())
    print(f"wrote {out} ({'static' if static else 'animated'})")


if __name__ == "__main__":
    main()
