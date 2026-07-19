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
import requests
from pathlib import Path

TITLE = "ayush@github"

def get_latest_repo():
    try:
        r = requests.get("https://api.github.com/users/tonystalker/repos?sort=updated&per_page=1")
        if r.status_code == 200 and r.json():
            repo = r.json()[0]
            name = repo.get("name", "")
            desc = repo.get("description") or "Working on new features"
            text = f"{name} — {desc}"
            if len(text) > 55:
                text = text[:52] + "..."
            return text
    except Exception:
        pass
    return "Building FlowDesk — agentic customer support platform"

ITEMS = [
    {"type": "header", "text": "ayush@github"},
    {"type": "row", "key": "Now", "val": get_latest_repo()},
    {"type": "row", "key": "Edu", "val": "IIT (BHU) Varanasi '26"},
    {"type": "header", "text": "— Stack"},
    {"type": "row", "key": "Frontend", "val": "React, Next.js, TypeScript, R3F"},
    {"type": "row", "key": "Backend", "val": "Node, NestJS, GraphQL, Django"},
    {"type": "row", "key": "AI / ML", "val": "LangChain, Vercel AI SDK, OpenAI"},
    {"type": "row", "key": "Cloud", "val": "AWS, Docker, Vercel, Prisma"},
    {"type": "header", "text": "— Seeking"},
    {"type": "row", "key": "Roles", "val": "SDE / AI-GenAI at early-stage startups"},
]

KEY_COL_W = 90
CHAR_PX = 7.9  
WIDTH = 567
BAR_H = 32
ROW_H = 28
PAD_X = 20
TOP_PAD = 14

KEY_COLOR = "#ffb86c" # Orange
VAL_COLOR = "#c9d1d9" # Gray
HEADER_COLOR = "#8be9fd" # Cyan
BG = "#0d1117"
BORDER = "#30363d"
BAR_BG = "#161b22"
LINE_COLOR = "#30363d"

STAGGER = 0.12
DUR = 0.35
static = os.environ.get("STATIC") == "1"

def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def build_svg() -> str:
    height = BAR_H + TOP_PAD + len(ITEMS) * ROW_H + TOP_PAD
    
    rows_svg = []
    for i, item in enumerate(ITEMS):
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
            
        if item["type"] == "header":
            text = item["text"]
            text_width = len(text) * CHAR_PX + 10
            line_y = y - 4
            rows_svg.append(
                f'<g {opacity_attr} {transform}>'
                f'<text x="{PAD_X}" y="{y}" font-family="Consolas, Menlo, monospace" '
                f'font-size="13" font-weight="700" fill="{HEADER_COLOR}">{esc(text)}</text>'
                f'<line x1="{PAD_X + text_width}" y1="{line_y}" x2="{WIDTH - PAD_X}" y2="{line_y}" stroke="{LINE_COLOR}" />'
                f'{anim}'
                f'</g>'
            )
        else:
            key = item["key"]
            val = item["val"]
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
    Path(out).write_text(build_svg(), encoding="utf-8")
    print(f"wrote {out} ({'static' if static else 'animated'})")

if __name__ == "__main__":
    main()
