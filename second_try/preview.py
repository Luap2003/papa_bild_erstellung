import math
from typing import Any, Dict, Iterable, Optional, Set, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import Arc, FancyArrowPatch, Polygon, Rectangle

from spec_utils import safe_get, tags_active, active_tags_from_paths


def line_style(tags: Iterable[str], active_tags: Set[str], base_lw: float = 0.8) -> Dict:
    if tags_active(tags, active_tags):
        return {"color": "red", "linewidth": max(base_lw + 0.8, 1.2)}
    return {"color": "black", "linewidth": base_lw}


def text_style(tags: Iterable[str], active_tags: Set[str]) -> Dict:
    if tags_active(tags, active_tags):
        return {"color": "red", "fontweight": "bold"}
    return {"color": "black"}


def draw_dim_arrow(
    ax,
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    text: str,
    tags: Iterable[str],
    active_tags: Set[str],
    text_offset=(0, 0),
    base_lw=1.0,
    text_rotation: Optional[float] = None,
):
    style = line_style(tags, active_tags, base_lw)
    tstyle = text_style(tags, active_tags)
    ax.add_patch(FancyArrowPatch(
        p1, p2,
        arrowstyle="<->",
        mutation_scale=10,
        linewidth=style["linewidth"],
        color=style["color"],
        shrinkA=0,
        shrinkB=0,
    ))
    tx = (p1[0] + p2[0]) / 2 + text_offset[0]
    ty = (p1[1] + p2[1]) / 2 + text_offset[1]
    if text_rotation is None:
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        text_rotation = math.degrees(math.atan2(dy, dx))
    ax.text(
        tx, ty, text,
        fontsize=8,
        rotation=text_rotation,
        rotation_mode="anchor",
        ha="center",
        va="center",
        bbox=dict(facecolor="white", edgecolor="none", pad=0.5),
        **tstyle,
    )


def draw_line(ax, x1: float, y1: float, x2: float, y2: float,
              tags: Iterable[str], active_tags: Set[str], lw: float = 0.8):
    style = line_style(tags, active_tags, lw)
    ax.plot([x1, x2], [y1, y2], color=style["color"], linewidth=style["linewidth"])


def draw_text(ax, x: float, y: float, text: str,
              tags: Iterable[str], active_tags: Set[str], fontsize: float = 8, **kwargs):
    ax.text(x, y, text, fontsize=fontsize, **text_style(tags, active_tags), **kwargs)


def draw_front_view(ax_front, spec: Dict[str, Any], active_tags: Set[str],
                    L: float, W: float, T: float, CAx: float, CAy: float):
    g = spec.get("geometry", {})
    left_ch = spec.get("left_surface", {}).get("chamfer", {})
    ch = min(max(0.0, safe_get(spec, "left_surface.chamfer.width_mm", 0.5)), L / 4, W / 4)

    def chamfered_rect_points(x0, y0, w, h, c):
        c = min(max(0.0, c), w / 4, h / 4)
        return [
            (x0 + c, y0 + h), (x0 + w - c, y0 + h),
            (x0 + w, y0 + h - c), (x0 + w, y0 + c),
            (x0 + w - c, y0), (x0 + c, y0),
            (x0, y0 + c), (x0, y0 + h - c),
        ]

    contour_active = tags_active(["front.outer_horizontal", "front.outer_vertical"], active_tags)
    ax_front.add_patch(Polygon(
        chamfered_rect_points(0, 0, L, W, ch),
        closed=True, fill=False,
        linewidth=1.8 if contour_active else 1.0,
        color="red" if contour_active else "black",
        zorder=3,
    ))

    edge_inset = max(0.6, min(1.2, T * 0.15))
    ax_front.add_patch(Rectangle(
        (edge_inset, edge_inset), L - 2 * edge_inset, W - 2 * edge_inset,
        fill=False, linewidth=0.9, color="black", zorder=3,
    ))

    ca_x0 = (L - CAx) / 2
    ca_y0 = (W - CAy) / 2
    ca_style = line_style(["front.ca_rect"], active_tags, 0.8)
    ax_front.add_patch(Rectangle(
        (ca_x0, ca_y0), CAx, CAy,
        fill=False, hatch="xx",
        linewidth=ca_style["linewidth"], color=ca_style["color"],
    ))

    draw_dim_arrow(ax_front, (ca_x0, -7), (ca_x0 + CAx, -7), f"{CAx:g}",
                   ["front.ca_x_dim"], active_tags, text_offset=(0, -2), base_lw=0.8)
    draw_text(ax_front, (ca_x0 * 2 + CAx) / 2, -12.0, "Prüfbereich",
              ["front.ca_x_dim"], active_tags, fontsize=9, ha="center", va="center")
    draw_line(ax_front, ca_x0, 0, ca_x0, -9, ["front.ca_x_dim"], active_tags, 0.8)
    draw_line(ax_front, ca_x0 + CAx, 0, ca_x0 + CAx, -9, ["front.ca_x_dim"], active_tags, 0.8)
    draw_line(ax_front, L, 0, L, -9, ["front.ca_x_dim"], active_tags, 0.8)
    draw_dim_arrow(ax_front, (ca_x0 + CAx, -7), (L, -7),
                   f"{(L - (ca_x0 + CAx)):g}", ["front.ca_x_dim"], active_tags,
                   text_offset=(0, -2), base_lw=0.8)

    draw_dim_arrow(ax_front, (0, -16), (L, -16),
                   f"{L:g} +{g.get('length_tol_plus', 0):g} / -{g.get('length_tol_minus', 0):g}",
                   ["front.length_dim"], active_tags, text_offset=(0, -2), base_lw=0.8)
    draw_line(ax_front, 0, 0, 0, -16, ["front.length_dim"], active_tags, 0.8)
    draw_line(ax_front, L, 0, L, -16, ["front.length_dim"], active_tags, 0.8)

    draw_dim_arrow(ax_front, (L + 6, ca_y0), (L + 6, ca_y0 + CAy), f"{CAy:g}",
                   ["front.ca_y_dim"], active_tags, text_offset=(2, 0), base_lw=0.8)
    draw_line(ax_front, L, ca_y0, L + 6, ca_y0, ["front.ca_y_dim"], active_tags, 0.8)
    draw_line(ax_front, L, ca_y0 + CAy, L + 6, ca_y0 + CAy, ["front.ca_y_dim"], active_tags, 0.8)
    draw_text(ax_front, L + 11.5, W / 2, "Prüfbereich",
              ["front.ca_y_dim"], active_tags, fontsize=9, rotation=90, va="center", ha="center")

    draw_dim_arrow(ax_front, (L + 13, 0), (L + 13, W),
                   f"{W:g} +{g.get('width_tol_plus', 0):g} / -{g.get('width_tol_minus', 0):g}",
                   ["front.width_dim"], active_tags, text_offset=(7, 0), base_lw=0.8)
    draw_line(ax_front, L, 0, L + 13, 0, ["front.width_dim"], active_tags, 0.8)
    draw_line(ax_front, L, W, L + 13, W, ["front.width_dim"], active_tags, 0.8)

    p_a = (0.0, W - ch)
    p_b = (ch, W)
    d = (1.0 / 2**0.5, 1.0 / 2**0.5)
    n = (-1.0 / 2**0.5, 1.0 / 2**0.5)
    ext = 6.2
    a_ext = (p_a[0] + n[0] * ext, p_a[1] + n[1] * ext)
    b_ext = (p_b[0] + n[0] * ext, p_b[1] + n[1] * ext)
    draw_line(ax_front, p_a[0], p_a[1], a_ext[0], a_ext[1], ["front.left_chamfer_width"], active_tags, 0.8)
    draw_line(ax_front, p_b[0], p_b[1], b_ext[0], b_ext[1], ["front.left_chamfer_width"], active_tags, 0.8)
    draw_line(ax_front, a_ext[0], a_ext[1], b_ext[0], b_ext[1], ["front.left_chamfer_width"], active_tags, 0.8)
    m = ((a_ext[0] + b_ext[0]) / 2, (a_ext[1] + b_ext[1]) / 2)
    draw_text(ax_front, m[0] + n[0] * 1, m[1] + n[1] * 1,
              f"{left_ch.get('width_mm', '-')} ±{left_ch.get('tolerance_mm', '-')}",
              ["front.left_chamfer_width"], active_tags,
              fontsize=8, rotation=55, ha="center", va="center")
    draw_text(ax_front, m[0] + n[0] * 4.0, m[1] + n[1] * 4.0, "(4x)",
              ["front.left_chamfer_width"], active_tags,
              fontsize=8, rotation=55, ha="center", va="center")

    left_angle = left_ch.get("angle_deg", 45)
    arc_style = line_style(["front.left_chamfer_angle"], active_tags, 0.8)
    draw_line(ax_front, p_b[0], p_b[1], p_b[0] + d[0] * 7.2, p_b[1] + d[1] * 7.2,
              ["front.left_chamfer_angle"], active_tags, 0.8)
    draw_line(ax_front, p_b[0], p_b[1], p_b[0] + 10.2, p_b[1],
              ["front.left_chamfer_angle"], active_tags, 0.8)
    ax_front.add_patch(Arc((p_b[0], p_b[1]), 9.4, 9.4, angle=0, theta1=0, theta2=45,
                           linewidth=arc_style["linewidth"], color=arc_style["color"]))
    ax_front.add_patch(FancyArrowPatch(
        (p_b[0] + 4.8, p_b[1] + 0.08), (p_b[0] + 4.25, p_b[1] + 0.08),
        arrowstyle="-|>", mutation_scale=8.2,
        linewidth=arc_style["linewidth"], color=arc_style["color"],
    ))
    ax_front.add_patch(FancyArrowPatch(
        (p_b[0] + 3.6, p_b[1] + 3.6), (p_b[0] + 3.2, p_b[1] + 3.2),
        arrowstyle="-|>", mutation_scale=8.2,
        linewidth=arc_style["linewidth"], color=arc_style["color"],
    ))
    draw_text(ax_front, p_b[0] + 11.0, p_b[1] + 2.9, f"{left_angle}°",
              ["front.left_chamfer_angle"], active_tags, fontsize=8, rotation=-35, ha="left", va="center")

    ax_front.set_xlim(-22, L + 25)
    ax_front.set_ylim(-22, W + 18)
    ax_front.set_aspect("equal", adjustable="box")
    ax_front.axis("off")


def draw_side_view(ax_side, spec: Dict[str, Any], active_tags: Set[str], W: float, T: float):
    g = spec.get("geometry", {})
    right_ch = spec.get("right_surface", {}).get("chamfer", {})
    rc_eff = min(max(0.0, safe_get(spec, "right_surface.chamfer.width_mm", 0.0)), T / 2, W / 2)

    side_active = tags_active(["side.thickness_edges"], active_tags)
    side_poly = [(0, 0), (T, 0), (T, W - rc_eff), (T - rc_eff, W), (0, W)]
    ax_side.add_patch(Polygon(
        side_poly, closed=True, fill=False, hatch="//",
        linewidth=2.0 if side_active else 1.4,
        color="red" if side_active else "black",
    ))
    draw_line(ax_side, T / 2, W * 0.25, T / 2, W * 0.78, ["side.thickness_edges"], active_tags, 0.8)

    ay = W * 0.58
    ax_side.add_patch(Rectangle((-10.5, ay - 3), 6.5, 6, fill=False, linewidth=0.8, color="black"))
    draw_text(ax_side, -7.25, ay, "A", [], active_tags, fontsize=9, ha="center", va="center")
    ax_side.add_patch(FancyArrowPatch((-4.0, ay), (0.0, ay), arrowstyle="-|>", mutation_scale=9,
                                      linewidth=0.8, color="black"))

    p1 = (T, W - rc_eff)
    p2 = (T - rc_eff, W)
    d_side = (1.0 / 2**0.5, -1.0 / 2**0.5)
    n_side = (1.0 / 2**0.5, 1.0 / 2**0.5)
    ext_side = 6.0
    p1_ext = (p1[0] + n_side[0] * ext_side, p1[1] + n_side[1] * ext_side)
    p2_ext = (p2[0] + n_side[0] * ext_side, p2[1] + n_side[1] * ext_side)
    draw_line(ax_side, p1[0], p1[1], p1_ext[0], p1_ext[1], ["side.right_chamfer_width"], active_tags, 0.8)
    draw_line(ax_side, p2[0], p2[1], p2_ext[0], p2_ext[1], ["side.right_chamfer_width"], active_tags, 0.8)
    draw_line(ax_side, p1_ext[0], p1_ext[1], p2_ext[0], p2_ext[1], ["side.right_chamfer_width"], active_tags, 0.8)
    m_side = ((p1_ext[0] + p2_ext[0]) / 2, (p1_ext[1] + p2_ext[1]) / 2)
    draw_text(ax_side, m_side[0] + n_side[0] * 2.2, m_side[1] + n_side[1] * 2.2,
              f"{right_ch.get('width_mm', '-')} ±{right_ch.get('tolerance_mm', '-')}",
              ["side.right_chamfer_width"], active_tags,
              fontsize=8, rotation=-45, ha="left", va="center")

    right_angle = right_ch.get("angle_deg", 30)
    arc_style = line_style(["side.right_chamfer_angle"], active_tags, 0.8)
    draw_line(ax_side, p2[0], p2[1], p2[0] + d_side[0] * 7.2, p2[1] + d_side[1] * 7.2,
              ["side.right_chamfer_angle"], active_tags, 0.8)
    draw_line(ax_side, p2[0], p2[1], p2[0] + 9.6, p2[1], ["side.right_chamfer_angle"], active_tags, 0.8)
    ax_side.add_patch(Arc(p2, 9.0, 9.0, angle=0, theta1=315, theta2=360,
                          linewidth=arc_style["linewidth"], color=arc_style["color"]))
    ax_side.add_patch(FancyArrowPatch(
        (p2[0] + 4.6, p2[1] - 0.05), (p2[0] + 4.1, p2[1] - 0.05),
        arrowstyle="-|>", mutation_scale=8.5,
        linewidth=arc_style["linewidth"], color=arc_style["color"],
    ))
    ax_side.add_patch(FancyArrowPatch(
        (p2[0] + 3.25, p2[1] - 3.25), (p2[0] + 2.9, p2[1] - 2.9),
        arrowstyle="-|>", mutation_scale=8.5,
        linewidth=arc_style["linewidth"], color=arc_style["color"],
    ))
    draw_text(ax_side, p2[0] + 10.1, p2[1] - 2.1, f"{right_angle}°",
              ["side.right_chamfer_angle"], active_tags, fontsize=11, rotation=35, ha="left", va="center")

    draw_dim_arrow(ax_side, (0, -8), (T, -8),
                   f"{T:g} +{g.get('thickness_tol_plus', 0):g} / -{g.get('thickness_tol_minus', 0):g}",
                   ["side.thickness_dim"], active_tags, text_offset=(0, -2))
    draw_line(ax_side, 0, 0, 0, -8, ["side.thickness_dim"], active_tags, 0.8)
    draw_line(ax_side, T, 0, T, -8, ["side.thickness_dim"], active_tags, 0.8)

    gt_style = line_style(["side.gt_frame"], active_tags, 0.8)
    gt_text_st = text_style(["side.gt_frame"], active_tags)
    gt_x, gt_y = T + 7, -9
    ax_side.add_patch(Rectangle((gt_x, gt_y), 17, 5, fill=False,
                                 linewidth=gt_style["linewidth"], color=gt_style["color"]))
    ax_side.plot([gt_x + 4, gt_x + 4], [gt_y, gt_y + 5], color=gt_style["color"], linewidth=gt_style["linewidth"])
    ax_side.plot([gt_x + 11, gt_x + 11], [gt_y, gt_y + 5], color=gt_style["color"], linewidth=gt_style["linewidth"])
    ax_side.text(gt_x + 2, gt_y + 2.5, "//", fontsize=10, ha="center", va="center", **gt_text_st)
    ax_side.text(gt_x + 7.5, gt_y + 2.5,
                 f"{spec.get('parallelism', {}).get('value_mm', 0.05):g}",
                 fontsize=9, ha="center", va="center", **gt_text_st)
    ax_side.text(gt_x + 14, gt_y + 2.5,
                 f"{spec.get('parallelism', {}).get('datum', 'A')}",
                 fontsize=9, ha="center", va="center", **gt_text_st)

    ax_side.set_xlim(-13, T + 27)
    ax_side.set_ylim(-14, W + 14)
    ax_side.set_aspect("equal", adjustable="box")
    ax_side.axis("off")


def render(spec: Dict[str, Any], active_paths: Set[str]):
    L = safe_get(spec, "geometry.length_mm", 75)
    W = safe_get(spec, "geometry.width_mm", 65)
    T = safe_get(spec, "geometry.thickness_mm", 6)
    CAx = safe_get(spec, "geometry.ca_x_mm", L * 0.8)
    CAy = safe_get(spec, "geometry.ca_y_mm", W * 0.8)
    active_tags = active_tags_from_paths(active_paths)

    fig = plt.figure(figsize=(12, 6.8), dpi=120)
    gs = fig.add_gridspec(1, 2, width_ratios=[3.4, 1.9], wspace=0.28)
    ax_front = fig.add_subplot(gs[0, 0])
    ax_side = fig.add_subplot(gs[0, 1])

    draw_front_view(ax_front, spec, active_tags, L, W, T, CAx, CAy)
    draw_side_view(ax_side, spec, active_tags, W, T)
    return fig
