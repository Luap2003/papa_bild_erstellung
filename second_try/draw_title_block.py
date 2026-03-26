"""Title block (ISO 7200) for optical drawings."""
from drawing_helpers import *


def draw_title_block(c, data: dict, tb_x: float, tb_y: float, tb_w: float):
    """
    Draw the title block at a given position.
    tb_x, tb_y: bottom-left corner in mm.
    tb_w: total width in mm.
    Returns (tb_x, tb_y, tb_x + tb_w, tb_y + tb_h).
    """
    tb = data["title_block"]

    TB_H = 58.0
    TB_TOP = tb_y + TB_H

    c.setStrokeColor(C_BLACK)
    draw_rect(c, tb_x, tb_y, tb_w, TB_H, lw=LW_MEDIUM)

    # Row heights (bottom to top)
    rh = [8, 8, 8, 8, 8, 8, 5, 5]
    rows = []
    y = tb_y
    for h in rh:
        rows.append(y)
        y += h

    # Horizontal grid
    for ry in rows[1:]:
        draw_line(c, tb_x, ry, tb_x + tb_w, ry, lw=LW_THIN)

    # Column offsets (relative to tb_x), scaled proportionally to width
    scale = tb_w / 180.0
    cols_abs = [0, 30, 58, 90, 120, 150, 170]
    col_x = [tb_x + cx * scale for cx in cols_abs]

    for cx in col_x[1:]:
        draw_line(c, cx, tb_y, cx, TB_TOP, lw=LW_THIN)

    def cell_text(text, col_idx, row_idx, size=2.0, dy=0, anchor="left", color=C_BLACK):
        x = col_x[col_idx] + 1.2
        y = rows[row_idx] + rh[row_idx] / 2 - 0.8 + dy
        draw_text(c, text, x, y, size=size, anchor=anchor, color=color)

    def cell_label(text, col_idx, row_idx, size=1.5):
        x = col_x[col_idx] + 0.8
        y = rows[row_idx] + rh[row_idx] - 2
        draw_text(c, text, x, y, size=size, color=C_GREY)

    # ROW 0: Document number
    cell_label("Dokumenten-Nr.", 0, 0)
    cell_text(tb["document_nr"], 0, 0, size=2.5, dy=-1.5)
    cell_label("Dok.-Art", 2, 0)
    cell_text(tb["doc_type"], 2, 0, size=2.5, dy=-1.5)
    cell_label("Teil-Dok.", 3, 0)
    cell_text(tb["part_doc"], 3, 0, size=2.5, dy=-1.5)
    cell_label("Version", 4, 0)
    cell_text(tb["version"], 4, 0, size=2.5, dy=-1.5)
    cell_label("Bl.", 5, 0)
    cell_text(tb["sheet"], 5, 0, size=2.5, dy=-1.5)
    cell_label("von", 6, 0)
    cell_text(tb["sheets_total"], 6, 0, size=2.5, dy=-1.5)

    # ROW 1: Supplementary doc type, scale, format
    cell_label("Zusatzunterlagenart", 0, 1)
    cell_label("Maßstab", 4, 1)
    cell_text(tb["scale"], 4, 1, dy=-1.5)
    cell_label("Format", 5, 1)
    cell_text(tb["format"], 5, 1, dy=-1.5)

    # ROW 2: Change / Designation
    cell_label("Änderung", 0, 2)
    cell_label("Benennung", 3, 2)
    cell_text(tb["designation"], 3, 2, size=2.2, dy=-1.5)

    # ROW 3: Component classification
    cell_label("Komp.-Stufe", 0, 3)
    cell_text(tb["component_level"], 0, 3, dy=-1.5)
    cell_label("Komp.-Zähl.", 1, 3)
    cell_label("Komp.-Char.", 2, 3)
    cell_text(tb.get("component_counter", ""), 1, 3, dy=-1.5)
    cell_text(tb.get("component_char", ""), 2, 3, dy=-1.5)
    cell_label("Projektklassifizierung", 3, 3)
    cell_text(tb["project_classification"], 3, 3, size=2.2, dy=-1.5)
    cell_label("Labor/Büro", 6, 3)

    # ROW 4: Approvals
    cell_label("Datum", 0, 4)
    cell_label("Name", 1, 4)
    approvals = [
        ("Bearb.", tb["created_date"], tb["created_by"]),
        ("Gepr.", tb["checked_date"], tb["checked_by"]),
        ("Techn.", tb["technical_date"], tb["technical_by"]),
        ("GS", "", ""),
        ("Norm", tb["norm_date"], tb["norm_by"]),
    ]
    sub_h = rh[4] / len(approvals)
    for i, (role, date, name) in enumerate(approvals):
        sy = rows[4] + rh[4] - (i + 0.5) * sub_h - 0.8
        if i > 0:
            sep_y = rows[4] + rh[4] - i * sub_h
            draw_line(c, col_x[0], sep_y, col_x[2], sep_y, lw=LW_HAIR)
        draw_text(c, role, col_x[0] + 1, sy, size=1.5)
        draw_text(c, date, col_x[0] + 12, sy, size=1.5)
        draw_text(c, name, col_x[1] + 1, sy, size=1.5)

    # ROW 5: Surface treatment / Material
    cell_label("Oberflächenbehandlung", 0, 5)
    cell_text(tb["surface_treatment"], 0, 5, dy=-1.5)
    cell_label("Werkstoff", 3, 5)
    cell_text(tb["material_description"], 3, 5, dy=-1.5)

    # ROW 6: GS / Manufacturing / Mass
    cell_label("GS-prüfpflichtig", 0, 6)
    cell_text(tb["gs_required"], 0, 6, dy=-0.5, size=1.8)
    cell_label("Technologie/Herstellverfahren", 1, 6)
    cell_label("Masse", 3, 6)
    cell_text(tb["mass"], 3, 6, dy=-0.5, size=1.8)

    # ROW 7: Copyright
    draw_text(c, "Schutzvermerk ISO 16016 beachten / Copyright reserved",
              tb_x + 1, rows[7] + 1, size=1.6, color=C_GREY)

    return tb_x, tb_y, tb_x + tb_w, TB_TOP
