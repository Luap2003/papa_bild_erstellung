"""Cross-section view and dimensioning for ISO 10110 drawings."""
import math
from drawing_helpers import *


def draw_cross_section(c, data: dict, cx: float, cy: float, scale: float):
    """
    Draw the substrate front face view (length x width).
    Returns coordinate dict for dimensioning.
    """
    geo = data["geometry"]
    ls  = data["left_surface"]
    rs  = data["right_surface"]

    # Front face: length (horizontal) x width (vertical)
    w = geo["length_mm"] * scale
    h = geo["width_mm"] * scale

    xl = cx - w / 2
    xr = cx + w / 2
    yb = cy - h / 2
    yt = cy + h / 2

    # Chamfer geometry at corners
    # Left surface chamfer: top-left and bottom-left corners
    lc_w = ls["chamfer"]["width_mm"] * scale
    lc_a = ls["chamfer"]["angle_deg"]
    lc_h = lc_w * math.tan(math.radians(lc_a))
    # Right surface chamfer: top-right and bottom-right corners
    rc_w = rs["chamfer"]["width_mm"] * scale
    rc_a = rs["chamfer"]["angle_deg"]
    rc_h = rc_w * math.tan(math.radians(rc_a))

    # Outline path with chamfered corners (clockwise from bottom-left)
    pts = [
        (xl, yb + lc_h),       # bottom-left corner, going up
        (xl + lc_w, yb),       # bottom-left corner, going right
        (xr - rc_w, yb),       # bottom-right corner start
        (xr, yb + rc_h),       # bottom-right corner end
        (xr, yt - rc_h),       # top-right corner start
        (xr - rc_w, yt),       # top-right corner end
        (xl + lc_w, yt),       # top-left corner start
        (xl, yt - lc_h),       # top-left corner end
    ]

    c.setStrokeColor(C_BLACK)
    c.setLineWidth(LW_THICK)
    path = c.beginPath()
    path.moveTo(pt(pts[0][0]), pt(pts[0][1]))
    for p in pts[1:]:
        path.lineTo(pt(p[0]), pt(p[1]))
    path.close()
    c.drawPath(path, stroke=1, fill=0)

    # Cross-hatching (two directions for glass material)
    c.setStrokeColor(C_GREY)
    c.setLineWidth(LW_HAIR)
    c.saveState()
    clip_path = c.beginPath()
    clip_path.moveTo(pt(pts[0][0]), pt(pts[0][1]))
    for p in pts[1:]:
        clip_path.lineTo(pt(p[0]), pt(p[1]))
    clip_path.close()
    c.clipPath(clip_path, stroke=0)

    spacing = HATCH_SPACING
    diag = math.sqrt(w**2 + h**2) * 1.5
    n_lines = int(diag / spacing) + 2

    for angle in [HATCH_ANGLE, -HATCH_ANGLE]:
        angle_rad = math.radians(angle)
        cos_a, sin_a = math.cos(angle_rad), math.sin(angle_rad)
        for i in range(-n_lines, n_lines):
            offset = i * spacing
            x1 = cx + offset * cos_a - diag * sin_a
            y1 = cy + offset * sin_a + diag * cos_a
            x2 = cx + offset * cos_a + diag * sin_a
            y2 = cy + offset * sin_a - diag * cos_a
            c.line(pt(x1), pt(y1), pt(x2), pt(y2))

    c.restoreState()
    c.setStrokeColor(C_BLACK)

    # Clear Aperture (dashed rectangle inside face)
    ca_x = geo["ca_x_mm"] * scale
    ca_y = geo["ca_y_mm"] * scale
    ca_l = cx - ca_x / 2
    ca_r = cx + ca_x / 2
    ca_b = cy - ca_y / 2
    ca_t = cy + ca_y / 2

    c.setStrokeColor(C_GREEN)
    draw_dashed_line(c, ca_l, ca_b, ca_r, ca_b, lw=LW_THIN, dash=(3, 1.5))
    draw_dashed_line(c, ca_l, ca_t, ca_r, ca_t, lw=LW_THIN, dash=(3, 1.5))
    draw_dashed_line(c, ca_l, ca_b, ca_l, ca_t, lw=LW_THIN, dash=(3, 1.5))
    draw_dashed_line(c, ca_r, ca_b, ca_r, ca_t, lw=LW_THIN, dash=(3, 1.5))
    c.setStrokeColor(C_BLACK)

    # "Prüfbereich" label (rotated 90°, next to CA right line inside face)
    c.saveState()
    c.translate(pt(ca_r - 2), pt(cy))
    c.rotate(90)
    font_size = 1.8 * mm * 0.85
    c.setFont("Helvetica", font_size)
    c.setFillColor(C_BLACK)
    tw = c.stringWidth("Prüfbereich", "Helvetica", font_size)
    c.drawString(-tw / 2, 0, "Prüfbereich")
    c.restoreState()
    c.setFillColor(C_BLACK)

    # Datum A on left edge
    draw_datum_symbol(c, xl, cy, "A", side="left")

    return {
        "xl": xl, "xr": xr, "yb": yb, "yt": yt,
        "ca_l": ca_l, "ca_r": ca_r, "ca_t": ca_t, "ca_b": ca_b,
        "cx": cx, "cy": cy, "scale": scale,
        "w": w, "h": h,
    }


def draw_datum_symbol(c, x, y, label, side="left"):
    s = 2.5
    c.setStrokeColor(C_BLACK)
    c.setLineWidth(LW_THIN)

    if side == "left":
        path = c.beginPath()
        path.moveTo(pt(x), pt(y))
        path.lineTo(pt(x - s * 1.3), pt(y + s * 0.7))
        path.lineTo(pt(x - s * 1.3), pt(y - s * 0.7))
        path.close()
        c.drawPath(path, stroke=1, fill=0)
        bx = x - s * 1.3 - 7
        draw_line(c, x - s * 1.3, y, bx + 4, y, lw=LW_THIN)
    else:
        path = c.beginPath()
        path.moveTo(pt(x), pt(y))
        path.lineTo(pt(x + s * 1.3), pt(y + s * 0.7))
        path.lineTo(pt(x + s * 1.3), pt(y - s * 0.7))
        path.close()
        c.drawPath(path, stroke=1, fill=0)
        bx = x + s * 1.3 + 3
        draw_line(c, x + s * 1.3, y, bx, y, lw=LW_THIN)

    bs = 4
    bx_start = bx if side == "right" else x - s * 1.3 - bs - 3
    draw_rect(c, bx_start, y - bs / 2, bs, bs, lw=LW_THIN)
    draw_text(c, label, bx_start + bs / 2, y - 0.8, size=2.5, anchor="center")


def draw_dimensions(c, data: dict, coords: dict):
    """Add ISO-style dimensions to the front face view."""
    geo = data["geometry"]
    xl, xr = coords["xl"], coords["xr"]
    yb, yt = coords["yb"], coords["yt"]
    ca_l, ca_r = coords["ca_l"], coords["ca_r"]
    ca_t, ca_b = coords["ca_t"], coords["ca_b"]
    cx, cy = coords["cx"], coords["cy"]
    sc = coords["scale"]

    c.setStrokeColor(C_RED)
    c.setFillColor(C_RED)

    # ── Bottom dimensions ──────────────────────────────────────────
    # Row 1: CA width with "Prüfbereich" label and offset "5"
    dim_y1 = yb - 7
    draw_dim_linear_h(c, ca_l, ca_r, dim_y1, f"{geo['ca_x_mm']}",
                      ext_from_y=yb)

    # Offset dimension "5" (right gap between CA and face edge)
    offset_x = (geo["length_mm"] - geo["ca_x_mm"]) / 2.0
    if offset_x > 0:
        draw_dim_linear_h(c, ca_r, xr, dim_y1, f"{int(offset_x)}",
                          ext_from_y=yb)

    # "Prüfbereich" label below the CA dimension
    draw_text(c, "Prüfbereich", (ca_l + ca_r) / 2, dim_y1 - 3.5,
              size=1.8, anchor="center", color=C_BLACK)

    # Row 2: Total length (75 ±0.1)
    dim_y2 = yb - 15
    draw_dim_linear_h(c, xl, xr, dim_y2, f"{geo['length_mm']}",
                      tol=f"±{geo['length_tol_plus']}",
                      ext_from_y=yb)

    # ── Right dimensions ───────────────────────────────────────────
    # Column 1: offset "2" (bottom gap) + CA height (61)
    dim_x1 = xr + 10
    offset_y = (geo["width_mm"] - geo["ca_y_mm"]) / 2.0

    # CA height dimension
    draw_dim_linear_v(c, ca_b, ca_t, dim_x1, f"{geo['ca_y_mm']}",
                      ext_from=xr)

    # Column 2: Total width (65 ±0.1)
    dim_x2 = xr + 22
    draw_dim_linear_v(c, yb, yt, dim_x2, f"{geo['width_mm']}",
                      tol=f"±{geo['width_tol_plus']}",
                      ext_from=xr)

    # Offset "2" between face bottom and CA bottom
    if offset_y > 0:
        # Small text label for offset
        draw_text(c, f"{int(offset_y)}", dim_x1 - 1.5,
                  (yb + ca_b) / 2 - 0.8, size=1.8, color=C_RED)

    # ── Thickness dimension (bottom-left, under face edge) ──────────
    # Show "6 ±0.1" as a small horizontal dimension at the left
    th_w = geo["thickness_mm"] * sc
    draw_dim_linear_h(c, xl, xl + th_w, dim_y1,
                      f"{geo['thickness_mm']}",
                      tol=f"±{geo['thickness_tol_plus']}",
                      ext_from_y=yb)

    # ── Chamfer labels ─────────────────────────────────────────────
    ls = data["left_surface"]["chamfer"]
    rs = data["right_surface"]["chamfer"]

    # Left surface chamfer label (top-left)
    lc_text = f"Schutzfasen {ls['width_mm']} ±{ls['tolerance_mm']} x {int(ls['angle_deg'])}°"
    draw_text(c, lc_text, xl - 5, yt + 12, size=1.8, color=C_BLACK)
    lc_w_sc = ls["width_mm"] * sc
    c.setStrokeColor(C_BLACK)
    draw_line(c, xl + lc_w_sc, yt, xl + 3, yt + 11, lw=LW_HAIR)
    c.setStrokeColor(C_RED)

    # Right surface chamfer label (top-right)
    rc_text = f"{rs['width_mm']} ±{rs['tolerance_mm']} x {int(rs['angle_deg'])}°"
    draw_text(c, rc_text, xr - 8, yt + 12, size=1.8, color=C_BLACK)
    c.setStrokeColor(C_BLACK)
    draw_line(c, xr - rs["width_mm"] * sc, yt, xr - 3, yt + 11, lw=LW_HAIR)
    c.setStrokeColor(C_RED)

    # ── Parallelism tolerance frame (bottom-right of cross-section) ─
    par = data["parallelism"]
    draw_tolerance_frame(c, par["value_mm"], par["datum"],
                         ca_r + 5, dim_y2 + 1)

    c.setStrokeColor(C_BLACK)
    c.setFillColor(C_BLACK)


def draw_dim_linear_h(c, x1, x2, y, value, tol="", ext_from_y=None):
    c.setStrokeColor(C_RED)
    c.setLineWidth(LW_THIN)
    if ext_from_y is not None:
        draw_line(c, x1, ext_from_y, x1, y - 1.5, lw=LW_HAIR)
        draw_line(c, x2, ext_from_y, x2, y - 1.5, lw=LW_HAIR)
    else:
        draw_line(c, x1, y + 3, x1, y - 1.5, lw=LW_HAIR)
        draw_line(c, x2, y + 3, x2, y - 1.5, lw=LW_HAIR)
    draw_line(c, x1, y, x2, y, lw=LW_THIN)
    a = 1.8
    aw = 0.5
    for ax, direction in [(x1, 1), (x2, -1)]:
        path = c.beginPath()
        path.moveTo(pt(ax), pt(y))
        path.lineTo(pt(ax + direction * a), pt(y + aw))
        path.lineTo(pt(ax + direction * a), pt(y - aw))
        path.close()
        c.setFillColor(C_RED)
        c.drawPath(path, stroke=0, fill=1)
    cx = (x1 + x2) / 2
    text = f"{value}"
    if tol:
        text += f" {tol}"
    draw_text(c, text, cx, y + 0.5, size=2.2, anchor="center", color=C_RED)


def draw_dim_linear_v(c, y1, y2, x, value, tol="", ext_from=None):
    c.setStrokeColor(C_RED)
    c.setLineWidth(LW_THIN)
    if ext_from is not None:
        draw_line(c, ext_from, y1, x + 1.5, y1, lw=LW_HAIR)
        draw_line(c, ext_from, y2, x + 1.5, y2, lw=LW_HAIR)
    draw_line(c, x, y1, x, y2, lw=LW_THIN)
    a = 1.8
    aw = 0.5
    for ay, direction in [(y1, 1), (y2, -1)]:
        path = c.beginPath()
        path.moveTo(pt(x), pt(ay))
        path.lineTo(pt(x + aw), pt(ay + direction * a))
        path.lineTo(pt(x - aw), pt(ay + direction * a))
        path.close()
        c.setFillColor(C_RED)
        c.drawPath(path, stroke=0, fill=1)
    cy = (y1 + y2) / 2
    text = f"{value}"
    if tol:
        text += f" {tol}"
    c.saveState()
    c.translate(pt(x - 1.5), pt(cy))
    c.rotate(90)
    font_size = 2.2 * mm * 0.85
    c.setFont("Helvetica", font_size)
    c.setFillColor(C_RED)
    tw = c.stringWidth(text, "Helvetica", font_size)
    c.drawString(-tw / 2, 0, text)
    c.restoreState()
    c.setFillColor(C_BLACK)


def draw_tolerance_frame(c, value, datum, x, y):
    c.setStrokeColor(C_BLACK)
    c.setLineWidth(LW_THIN)
    fh = 5
    cw = [7, 10, 5]
    cx = x
    for w in cw:
        draw_rect(c, cx, y, w, fh, lw=LW_THIN)
        cx += w
    sx = x + cw[0] / 2
    sy = y + fh / 2
    ll = 3
    gap = 1.0
    draw_line(c, sx - ll / 2, sy - gap / 2, sx + ll / 2, sy - gap / 2, lw=LW_THIN)
    draw_line(c, sx - ll / 2, sy + gap / 2, sx + ll / 2, sy + gap / 2, lw=LW_THIN)
    draw_text(c, str(value), x + cw[0] + cw[1] / 2, y + fh / 2 - 0.8,
              size=2.2, anchor="center")
    draw_text(c, datum, x + cw[0] + cw[1] + cw[2] / 2, y + fh / 2 - 0.8,
              size=2.2, anchor="center")
