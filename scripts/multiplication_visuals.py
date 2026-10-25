from __future__ import annotations

from xml.sax.saxutils import escape

from scripts.multiplication_common import MultiplicationFact
from scripts.multiplication_content import animal_name


def visual_filename(fact: MultiplicationFact) -> str:
    return f"fact_{fact.left:02d}x{fact.right:02d}.svg"


def render_rows(group_count: int, group_size: int) -> str:
    circles: list[str] = []
    start_x = 230
    start_y = 170
    x_gap = 62
    y_gap = 110
    radius = 22
    label_x = 180

    for row_index in range(group_count):
        y = start_y + (row_index * y_gap)
        circles.append(
            f'<text x="{label_x}" y="{y + 10}" text-anchor="end" font-size="28" font-weight="700" fill="#0f172a">'
            f"Grupo {row_index + 1}</text>"
        )
        for column_index in range(group_size):
            x = start_x + (column_index * x_gap)
            circles.append(
                f'<circle cx="{x}" cy="{y}" r="{radius}" fill="#f59e0b" stroke="#0f172a" stroke-width="4" />'
            )
    return "\n      ".join(circles)


def render_fact_svg(fact: MultiplicationFact) -> str:
    title = escape(f"{fact.left} grupos de {fact.right} {animal_name(fact)}")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="900" height="620" viewBox="0 0 900 620">
  <rect width="900" height="620" rx="36" fill="#fffaf0" />
  <text x="450" y="70" text-anchor="middle" font-size="38" font-weight="800" fill="#0f172a">{title}</text>
  <rect x="80" y="135" width="740" height="420" rx="28" fill="#ffffff" stroke="#0f172a" stroke-width="5" />
  <g>
      {render_rows(fact.left, fact.right)}
  </g>
</svg>"""
