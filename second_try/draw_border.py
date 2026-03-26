"""Drawing border and zone markers per ISO 5457."""
from drawing_helpers import *


def draw_border(c):
    """Draw A4 landscape border with zone markers."""
    c.setStrokeColor(C_BLACK)

    # Outer trim rectangle
    draw_rect(c, 0, 0, 297, 210, lw=LW_HAIR)

    # Inner drawing frame
    draw_rect(c, F_LEFT, F_BOTTOM, F_RIGHT - F_LEFT, F_TOP - F_BOTTOM, lw=LW_THICK)

    # Zone labels
    zones_y = ['D', 'C', 'B', 'A']
    zones_x = ['1', '2', '3', '4', '5', '6']
    zh = (F_TOP - F_BOTTOM) / len(zones_y)
    zw = (F_RIGHT - F_LEFT) / len(zones_x)

    for i, label in enumerate(zones_y):
        yc = F_BOTTOM + (i + 0.5) * zh
        draw_text(c, label, F_LEFT / 2, yc - 1, size=2.5, anchor="center")
        draw_text(c, label, F_RIGHT + M_RIGHT / 2, yc - 1, size=2.5, anchor="center")
        if i > 0:
            ty = F_BOTTOM + i * zh
            draw_line(c, 0, ty, F_LEFT, ty, lw=LW_HAIR)
            draw_line(c, F_RIGHT, ty, 297, ty, lw=LW_HAIR)

    for i, label in enumerate(zones_x):
        xc = F_LEFT + (i + 0.5) * zw
        draw_text(c, label, xc, 1, size=2.5, anchor="center")
        draw_text(c, label, xc, F_TOP + 2, size=2.5, anchor="center")
        if i > 0:
            tx = F_LEFT + i * zw
            draw_line(c, tx, 0, tx, F_BOTTOM, lw=LW_HAIR)
            draw_line(c, tx, F_TOP, tx, 210, lw=LW_HAIR)
