"""ISO 10110 parameter table (3-column: Left Surface | Material | Right Surface)."""
from drawing_helpers import *


def draw_iso_table(c, data: dict, x: float, y: float, total_w: float = None):
    """
    Draw the 3-column ISO 10110 parameter table.
    x, y: top-left corner of the header row.
    total_w: total table width; defaults to frame width.
    Table grows downward from y.
    Returns the y coordinate of the bottom of the last row.
    """
    ls = data["left_surface"]
    rs = data["right_surface"]
    mat = data["material"]

    if total_w is None:
        total_w = F_RIGHT - F_LEFT
    col_w = total_w / 3.0
    rh = 5.5
    hdr_h = 6.0

    c.setStrokeColor(C_BLACK)

    # Header row
    headers = [ls["label"], "Material", rs["label"]]
    for i, hdr in enumerate(headers):
        hx = x + i * col_w
        draw_rect(c, hx, y, col_w, hdr_h, lw=LW_MEDIUM)
        draw_text(c, hdr, hx + col_w / 2, y + hdr_h / 2 - 0.8,
                  size=2.2, anchor="center", font="Helvetica-Bold")

    # Data rows (growing downward)
    rows = [
        (ls["radius_display"],
         f"{mat['manufacturer']} / {mat['name']}",
         rs["radius_display"]),

        (f"R_Kenn {ls['r_kenn']}", "", f"R_Kenn {rs['r_kenn']}"),

        (f"Schutzfasen {ls['chamfer']['width_mm']} ± {ls['chamfer']['tolerance_mm']} x {int(ls['chamfer']['angle_deg'])}°",
         f"ne {mat['ne']}",
         f"{rs['chamfer']['width_mm']} ± {rs['chamfer']['tolerance_mm']} x {int(rs['chamfer']['angle_deg'])}°"),

        (ls["figure_error"],
         f"ve {mat['ve']}",
         rs["figure_error"]),

        (ls["centering"],
         mat["stress_birefringence"],
         rs["centering"]),

        (ls["surface_quality"],
         mat["bubbles_inclusions"],
         rs["surface_quality"]),

        ("l -",
         mat["homogeneity_striae"],
         "l -"),
    ]

    for row_idx, (lv, mv, rv) in enumerate(rows):
        ry = y - (row_idx + 1) * rh
        vals = [lv, mv, rv]
        for col in range(3):
            cell_x = x + col * col_w
            draw_rect(c, cell_x, ry, col_w, rh, lw=LW_HAIR)
            if vals[col]:
                draw_text(c, vals[col], cell_x + 1.5, ry + rh / 2 - 0.8, size=1.8)

    bottom_y = y - len(rows) * rh
    return bottom_y


def draw_roughness_symbol(c, rq, area, x, y):
    """Draw the ISO 1302 surface roughness check-mark symbol."""
    c.setStrokeColor(C_BLACK)
    c.setLineWidth(LW_THIN)
    s = 3.5

    path = c.beginPath()
    path.moveTo(pt(x), pt(y))
    path.lineTo(pt(x + s * 0.4), pt(y + s))
    path.lineTo(pt(x + s * 0.8), pt(y))
    c.drawPath(path, stroke=1, fill=0)

    draw_line(c, x + s * 0.4, y + s, x + s * 0.4 + 10, y + s, lw=LW_THIN)
    draw_text(c, f"Rq {rq}", x + s * 0.4 + 1, y + s + 1, size=2.0)
    draw_text(c, area, x + s * 0.8 + 1, y - 1, size=1.8, color=C_GREY)


def draw_standards_box(c, data: dict, x, y, w, h):
    """Draw the tolerance and standards reference box with border.
    x, y: bottom-left corner in mm.
    w: width, h: height.
    """
    tb = data["title_block"]
    tol = tb.get("tolerances", {})

    c.setStrokeColor(C_BLACK)
    draw_rect(c, x, y, w, h, lw=LW_MEDIUM)

    # "Angaben nach ISO 10110" header at top
    header_y = y + h - 5
    draw_text(c, "Angaben nach ISO 10110", x + 2, header_y, size=2.0, font="Helvetica-Bold")

    # RoHS note
    rohs = tb.get("rohs_note", "").split('\n')
    for i, line in enumerate(rohs):
        draw_text(c, line, x + 2, header_y - 4 - i * 3, size=1.6)

    # Tolerance lines at the bottom of the box
    tol_lines = [
        (f"{tol.get('plus_large', '')}  Oberfläche", 1.8),
        (f"{tol.get('minus_large', '')}  {tb['surface_standard']}", 1.8),
        (f"{tol.get('plus_small', '')}  {tb['edge_standard']} -", 1.8),
        (f"{tol.get('minus_small', '')}  {tb['general_tolerance']}", 1.8),
        (f"Size {tb['size_standard']} · {tb['mass']}", 1.8),
    ]
    tol_start_y = y + 2 + (len(tol_lines) - 1) * 3.5
    for i, (text, sz) in enumerate(tol_lines):
        draw_text(c, text, x + 2, tol_start_y - i * 3.5, size=sz)
