"""
make_ascii_svg.py

Converts source-prepped.png (grayscale, background already flattened to
white by prep_photo.py) into a monochrome, self-typing ASCII-art SVG.

Design choices:
  - One fill color only. Per-character rainbow coloring is what makes
    most ASCII portraits look noisy instead of clean.
  - High-contrast source -> a busy/white background collapses to the
    space glyph, so only the subject actually prints.
  - Animation lives entirely in SMIL (<animate>/<set>) inside the SVG,
    since GitHub strips <script> and external CSS from READMEs but
    still plays SVG animations embedded via <img>.
  - Each row wipes in left-to-right via an animated clip rect, rows
    staggered top-to-bottom. A small block cursor rides the wipe edge.
    The whole thing prints once and freezes (no looping).

Usage:
    python scripts/make_ascii_svg.py [source-prepped.png] [out.svg]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

# bright (sparse) -> dark (dense); leading space clears the background
RAMP = " .`:-=+*cs#%@"

COLS = 100          # character columns
CHAR_W = 6.0         # px per character cell (monospace, font-size ~10)
CHAR_H = 11.0        # px per row (line-height)
CHAR_ASPECT = CHAR_W / CHAR_H

FILL_COLOR = "var(--ascii-color, #8b949e)"
CHAR_DUR = 0.012     # seconds per character revealed
ROW_STAGGER = 0.02   # seconds between successive row starts


def image_to_grid(img_path: str) -> list[str]:
    img = Image.open(img_path).convert("L")
    w, h = img.size
    rows = max(1, round(COLS * (h / w) * CHAR_ASPECT))
    small = img.resize((COLS, rows), Image.LANCZOS)
    arr = np.array(small, dtype=np.float32)  # 0=black .. 255=white

    grid = []
    n = len(RAMP) - 1
    for row in arr:
        chars = []
        for brightness in row:
            idx = round((1.0 - brightness / 255.0) * n)
            idx = max(0, min(n, idx))
            chars.append(RAMP[idx])
        grid.append("".join(chars).rstrip() or " ")
    return grid


def esc(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def build_svg(grid: list[str]) -> str:
    rows = len(grid)
    width = COLS * CHAR_W
    height = rows * CHAR_H

    defs = []
    texts = []
    cursor_x_anims = []
    cursor_y_sets = []

    for i, line in enumerate(grid):
        row_y = (i + 1) * CHAR_H - 2.5
        row_width_px = len(line) * CHAR_W
        begin = i * ROW_STAGGER
        clip_id = f"clip{i}"

        defs.append(
            f'<clipPath id="{clip_id}">'
            f'<rect x="0" y="{i * CHAR_H:.1f}" width="0" height="{CHAR_H:.1f}">'
            f'<animate attributeName="width" from="0" to="{row_width_px:.1f}" '
            f'dur="{CHAR_DUR * len(line):.3f}s" begin="{begin:.3f}s" fill="freeze" '
            f'calcMode="linear"/>'
            f'</rect></clipPath>'
        )
        texts.append(
            f'<text x="0" y="{row_y:.1f}" clip-path="url(#{clip_id})" '
            f'font-family="Consolas, Menlo, monospace" font-size="10" '
            f'fill="{FILL_COLOR}" xml:space="preserve">{esc(line)}</text>'
        )
        row_dur = CHAR_DUR * len(line)
        cursor_x_anims.append(
            f'<animate attributeName="x" from="0" to="{row_width_px:.1f}" '
            f'dur="{row_dur:.3f}s" begin="{begin:.3f}s" fill="freeze"/>'
        )
        cursor_y_sets.append(
            f'<set attributeName="y" to="{i * CHAR_H:.1f}" begin="{begin:.3f}s"/>'
        )

    total_end = rows * ROW_STAGGER + CHAR_DUR * COLS

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" width="{width:.0f}" height="{height:.0f}">
<defs>
{''.join(defs)}
</defs>
<style>text{{white-space:pre;}}</style>
<g>
{''.join(texts)}
</g>
<rect width="{CHAR_W:.1f}" height="{CHAR_H - 2:.1f}" y="0" fill="{FILL_COLOR}" opacity="0.85">
{''.join(cursor_x_anims)}
{''.join(cursor_y_sets)}
<animate attributeName="opacity" from="0.85" to="0" dur="0.4s" begin="{total_end:.3f}s" fill="freeze"/>
</rect>
</svg>'''
    return svg


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "source-prepped.png"
    out = sys.argv[2] if len(sys.argv) > 2 else "avi-ascii.svg"
    if not Path(src).exists():
        print(f"error: {src} not found. Run prep_photo.py first.")
        sys.exit(1)
    grid = image_to_grid(src)
    svg = build_svg(grid)
    Path(out).write_text(svg)
    print(f"wrote {out} ({len(grid)} rows x {COLS} cols)")


if __name__ == "__main__":
    main()
