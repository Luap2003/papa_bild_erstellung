#!/usr/bin/env python3
"""
ISO 10110 Optical Drawing → PDF Generator
==========================================
Renders a precise, ISO 10110-compliant technical drawing as a vector PDF
from JSON parameter input using reportlab.

Usage:
    python iso10110_generator.py input.json [output.pdf]

Layout (top to bottom):
    Upper area  — front face view with dimensions
    Text area   — "Angaben nach ISO 10110" + RoHS note
    Table area  — ISO 10110 parameter table
    Lower band  — standards box (left) + title block (right)
"""

import json
import sys
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas

from drawing_helpers import (
    F_LEFT, F_RIGHT, F_BOTTOM, F_TOP,
    C_BLACK, LW_MEDIUM,
    draw_line, draw_text,
)
from draw_border import draw_border
from draw_title_block import draw_title_block
from draw_cross_section import draw_cross_section, draw_dimensions
from draw_iso_table import draw_iso_table, draw_roughness_symbol, draw_standards_box


def load_data(json_path: str) -> dict:
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_pdf(json_path: str, output_path: str):
    data = load_data(json_path)

    c = canvas.Canvas(output_path, pagesize=landscape(A4))
    c.setAuthor("ISO 10110 Generator")
    c.setTitle(f"ISO 10110 - {data['title_block']['designation']}")
    c.setSubject(data['title_block']['document_nr'])

    # 1. Border + zone markers
    draw_border(c)

    # ── Layout zones ──────────────────────────────────────────────
    # Frame: F_LEFT(20) → F_RIGHT(287), F_BOTTOM(10) → F_TOP(200)
    # Frame width = 267mm, height = 190mm
    frame_w = F_RIGHT - F_LEFT

    # Lower band: title block (right) + standards box (left)
    TB_H = 58.0
    lower_bottom = F_BOTTOM
    lower_top = lower_bottom + TB_H          # 68mm

    # Separator line at top of title block
    c.setStrokeColor(C_BLACK)
    draw_line(c, F_LEFT, lower_top, F_RIGHT, lower_top, lw=LW_MEDIUM)

    # ── 2. Lower band: title block (right) + standards box (left) ─
    tb_w = 180.0
    tb_x = F_RIGHT - tb_w
    draw_title_block(c, data, tb_x, lower_bottom, tb_w)

    stb_w = tb_x - F_LEFT
    draw_standards_box(c, data, F_LEFT, lower_bottom, stb_w, TB_H)

    # ── 3. ISO parameter table ───────────────────────────────────
    # Place table header just above the title block separator
    # with "Angaben" text above the table
    tb = data["title_block"]

    # "Angaben nach ISO 10110" and RoHS note above the table
    # Table header bottom (header grows up from here by 6mm)
    iso_table_top = lower_top + 48.0  # table header top at ~116mm
    iso_header_bottom = iso_table_top - 6.0
    draw_iso_table(c, data, F_LEFT, iso_header_bottom, frame_w)

    # Text between table and face: RoHS note above, "Angaben" below
    text_base = iso_table_top + 2
    draw_text(c, "Angaben nach ISO 10110", F_LEFT + 2, text_base,
              size=2.0, font="Helvetica-Bold")
    rohs = tb.get("rohs_note", "").split('\n')
    for i, line in enumerate(rohs):
        draw_text(c, line, F_LEFT + 2, text_base + 4 + (len(rohs) - 1 - i) * 3,
                  size=1.6)

    face_area_bottom = text_base + 4 + len(rohs) * 3 + 2  # ~132mm

    # ── 4. Front face drawing ────────────────────────────────────
    upper_top = F_TOP
    upper_avail = upper_top - face_area_bottom
    margin_above = 15.0
    margin_below = 3.0
    max_cs_h = upper_avail - margin_above - margin_below
    geo_h = data["geometry"]["width_mm"]
    geo_w = data["geometry"]["length_mm"]
    max_cs_w = frame_w * 0.50
    scale = min(max_cs_h / geo_h, max_cs_w / geo_w, 1.0)

    cs_cx = F_LEFT + frame_w * 0.35
    cs_cy = face_area_bottom + margin_below + (geo_h * scale) / 2.0

    coords = draw_cross_section(c, data, cs_cx, cs_cy, scale)
    draw_dimensions(c, data, coords)

    # ── 5. Roughness symbol (top-right of drawing area) ──────────
    draw_roughness_symbol(c, data["surface_roughness"]["rq_nm"],
                          data["surface_roughness"]["measurement_area"],
                          coords["xr"] + 35, coords["yt"] + 8)

    c.save()
    print(f"PDF saved: {output_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python iso10110_generator.py <input.json> [output.pdf]")
        sys.exit(1)
    inp = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else inp.replace(".json", "_drawing.pdf")
    generate_pdf(inp, out)
