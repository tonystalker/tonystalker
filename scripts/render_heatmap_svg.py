"""
render_heatmap_svg.py

Renders data/contributions.json as the classic 53-week x 7-day
contribution calendar: rounded, colored boxes on a GitHub-ish green
ramp. Reveals once with a diagonal, line-after-line slide-down (plays
on load, then freezes — no looping "glow"). Adds a Less->More legend
and a stats footer.

Usage:
    python scripts/render_heatmap_svg.py
Reads:
    data/contributions.json
Writes:
    contrib-heatmap.svg
"""
import json
from datetime import datetime
from pathlib import Path

PALETTE = [
    "#161b22",  # 0: none
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0",  # 5: brightest (neon top end)
]

CELL = 11
GAP = 3
LEFT_PAD = 28
TOP_PAD = 20
BOTTOM_PAD = 34

STAGGER_PER_COL = 0.035
DUR = 0.28


def load_data():
    return json.loads(Path("data/contributions.json").read_text())


def weeks_from_days(days: list[dict]) -> list[list[dict | None]]:
    """Group days into GitHub-style weeks (columns), Sunday-start."""
    weeks: list[list[dict | None]] = []
    week: list[dict | None] = []

    first_date = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
    lead_blank = (first_date.weekday() + 1) % 7  # Mon=0..Sun=6 -> Sun-start offset
    week.extend([None] * lead_blank)

    for d in days:
        d_date = datetime.strptime(d["date"], "%Y-%m-%d").date()
        dow = (d_date.weekday() + 1) % 7
        if dow == 0 and week:
            weeks.append(week)
            week = []
        week.append(d)
    if week:
        while len(week) < 7:
            week.append(None)
        weeks.append(week)
    return weeks


def level_to_color(level: int) -> str:
    return PALETTE[max(0, min(5, level))]


def build_svg(data: dict) -> str:
    days = data["days"]
    stats = data["stats"]
    weeks = weeks_from_days(days)
    n_cols = len(weeks)

    width = LEFT_PAD + n_cols * (CELL + GAP)
    height = TOP_PAD + 7 * (CELL + GAP) + BOTTOM_PAD

    cells_svg = []
    for col, week in enumerate(weeks):
        begin = col * STAGGER_PER_COL
        for row, day in enumerate(week):
            if day is None:
                continue
            x = LEFT_PAD + col * (CELL + GAP)
            y_final = TOP_PAD + row * (CELL + GAP)
            color = level_to_color(day.get("level", 0))
            cells_svg.append(
                f'<rect x="{x}" y="{y_final - 6}" width="{CELL}" height="{CELL}" '
                f'rx="2" fill="{color}" opacity="0">'
                f'<title>{day["date"]}: {day["count"]} contributions</title>'
                f'<animate attributeName="opacity" from="0" to="1" dur="{DUR}s" '
                f'begin="{begin:.3f}s" fill="freeze"/>'
                f'<animate attributeName="y" from="{y_final - 6}" to="{y_final}" '
                f'dur="{DUR}s" begin="{begin:.3f}s" fill="freeze" calcMode="spline" '
                f'keySplines="0.2 0 0.2 1" keyTimes="0;1"/>'
                f'</rect>'
            )

    # Month labels along the top
    month_labels = []
    last_month = None
    for col, week in enumerate(weeks):
        first_real = next((d for d in week if d), None)
        if not first_real:
            continue
        month = first_real["date"][:7]
        if month != last_month:
            x = LEFT_PAD + col * (CELL + GAP)
            m_name = datetime.strptime(month, "%Y-%m").strftime("%b")
            month_labels.append(
                f'<text x="{x}" y="12" font-family="Consolas, Menlo, monospace" '
                f'font-size="10" fill="#8b949e">{m_name}</text>'
            )
            last_month = month

    legend_x = width - 150
    legend_y = height - 14
    legend_cells = []
    for i, color in enumerate(PALETTE):
        cx = legend_x + 34 + i * (CELL + GAP)
        legend_cells.append(
            f'<rect x="{cx}" y="{legend_y - CELL + 3}" width="{CELL}" height="{CELL}" '
            f'rx="2" fill="{color}"/>'
        )

    footer = (
        f'{stats["total_last_year"]:,} contributions in the last year   '
        f'|   current streak: {stats["current_streak"]}d   '
        f'|   longest streak: {stats["longest_streak"]}d'
    )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
<rect width="{width}" height="{height}" fill="#0d1117"/>
{''.join(month_labels)}
{''.join(cells_svg)}
<text x="{LEFT_PAD}" y="{height - 14}" font-family="Consolas, Menlo, monospace" font-size="11" fill="#8b949e">{footer}</text>
<text x="{legend_x}" y="{legend_y}" font-family="Consolas, Menlo, monospace" font-size="10" fill="#8b949e">Less</text>
{''.join(legend_cells)}
<text x="{legend_x + 34 + len(PALETTE) * (CELL + GAP) + 4}" y="{legend_y}" font-family="Consolas, Menlo, monospace" font-size="10" fill="#8b949e">More</text>
</svg>'''
    return svg


def main():
    data = load_data()
    svg = build_svg(data)
    Path("contrib-heatmap.svg").write_text(svg)
    print(f"wrote contrib-heatmap.svg ({len(data['days'])} days)")


if __name__ == "__main__":
    main()
