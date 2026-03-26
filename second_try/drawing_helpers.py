"""
Low-level drawing primitives for ISO 10110 PDF generation.
All coordinates are in mm unless noted otherwise.
"""
import math
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.lib.colors import black, red, Color

# =============================================================================
# CONSTANTS
# =============================================================================

PAGE_W, PAGE_H = landscape(A4)

# Margins (mm)
M_LEFT   = 20.0
M_RIGHT  = 10.0
M_TOP    = 10.0
M_BOTTOM = 10.0

# Drawing frame corners (mm)
F_LEFT   = M_LEFT
F_RIGHT  = 297.0 - M_RIGHT
F_BOTTOM = M_BOTTOM
F_TOP    = 210.0 - M_TOP

# Line widths (mm → pt)
LW_THICK  = 0.50 * mm
LW_MEDIUM = 0.35 * mm
LW_THIN   = 0.25 * mm
LW_HAIR   = 0.13 * mm

# Colors
C_BLACK = black
C_RED   = red
C_GREY  = Color(0.55, 0.55, 0.55)
C_GREEN = Color(0, 0.5, 0)

# Hatching
HATCH_SPACING = 1.2
HATCH_ANGLE   = 45


# =============================================================================
# PRIMITIVES
# =============================================================================

def pt(millimeters: float) -> float:
    """Convert mm to points."""
    return millimeters * mm

def draw_rect(c, x, y, w, h, lw=LW_THIN, stroke=True, fill=False):
    c.setLineWidth(lw)
    c.rect(pt(x), pt(y), pt(w), pt(h), stroke=int(stroke), fill=int(fill))

def draw_line(c, x1, y1, x2, y2, lw=LW_THIN):
    c.setLineWidth(lw)
    c.line(pt(x1), pt(y1), pt(x2), pt(y2))

def draw_text(c, text, x, y, size=2.5, anchor="left", color=C_BLACK, font="Helvetica"):
    c.setFillColor(color)
    c.setFont(font, size * mm * 0.85)
    tw = c.stringWidth(str(text), font, size * mm * 0.85)
    px = pt(x)
    if anchor == "center":
        px = pt(x) - tw / 2
    elif anchor == "right":
        px = pt(x) - tw
    c.drawString(px, pt(y), str(text))
    c.setFillColor(C_BLACK)

def draw_dashed_line(c, x1, y1, x2, y2, lw=LW_THIN, dash=(2, 1.5)):
    c.setLineWidth(lw)
    c.setDash(pt(dash[0]), pt(dash[1]))
    c.line(pt(x1), pt(y1), pt(x2), pt(y2))
    c.setDash()

def draw_centerline(c, x1, y1, x2, y2, lw=LW_HAIR):
    c.setLineWidth(lw)
    c.setDash([pt(6), pt(1.5), pt(1.5), pt(1.5)])
    c.line(pt(x1), pt(y1), pt(x2), pt(y2))
    c.setDash()
