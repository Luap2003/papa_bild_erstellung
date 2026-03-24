import json
from io import BytesIO
from typing import Any, Dict, Tuple

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle
import streamlit as st


DEFAULT_JSON = {
    "geometry": {
        "length_mm": 75,
        "length_tol_plus": 0.1,
        "length_tol_minus": 0.1,
        "width_mm": 65,
        "width_tol_plus": 0.1,
        "width_tol_minus": 0.1,
        "thickness_mm": 6,
        "thickness_tol_plus": 0.1,
        "thickness_tol_minus": 0.1,
        "ca_x_mm": 65,
        "ca_y_mm": 61,
    },
    "parallelism": {"value_mm": 0.05, "datum": "A"},
    "material": {
        "name": "N-BK7",
        "manufacturer": "Fa. Schott",
        "ne": 1.51872,
        "ve": 63.96,
        "stress_birefringence": "0/-",
        "bubbles_inclusions": "1/",
        "homogeneity_striae": "2/",
    },
    "left_surface": {
        "label": "linke Flaeche",
        "radius": "PL",
        "radius_display": "R PL",
        "r_kenn": "-",
        "chamfer": {"width_mm": 0.5, "tolerance_mm": 0.2, "angle_deg": 45, "type": "Schutzfase"},
        "figure_error": "3/-",
        "centering": "4/-",
        "surface_quality": "5/-",
        "coating": "-",
        "coating_spec": "",
    },
    "right_surface": {
        "label": "rechte Flaeche",
        "radius": "PL",
        "radius_display": "R PL",
        "r_kenn": "-",
        "chamfer": {"width_mm": 1.5, "tolerance_mm": 0.2, "angle_deg": 30, "type": "Funktionsfase"},
        "figure_error": "3/5 (2)",
        "centering": "4/-",
        "surface_quality": "5/ 10x0,063",
        "coating": "-",
        "coating_spec": "",
    },
    "surface_roughness": {"rq_nm": 1.2, "measurement_area": "P3"},
}


def fmt_tol(value: Any, plus: Any, minus: Any, unit: str = "mm") -> str:
    return f"{value:g} {unit}  +{plus:g} / -{minus:g}"


def dim_arrow(ax, p1: Tuple[float, float], p2: Tuple[float, float], text: str, text_offset=(0, 0), lw=1.0):
    arrow = FancyArrowPatch(
        p1,
        p2,
        arrowstyle="<->",
        mutation_scale=10,
        linewidth=lw,
        color="black",
        shrinkA=0,
        shrinkB=0,
    )
    ax.add_patch(arrow)
    tx = (p1[0] + p2[0]) / 2 + text_offset[0]
    ty = (p1[1] + p2[1]) / 2 + text_offset[1]
    ax.text(tx, ty, text, fontsize=8, ha="center", va="center", bbox=dict(facecolor="white", edgecolor="none", pad=0.5))


def safe_get(spec: Dict[str, Any], path: str, default: float = 0.0) -> float:
    obj: Any = spec
    for key in path.split("."):
        obj = obj.get(key, None) if isinstance(obj, dict) else None
    try:
        return float(obj)
    except (TypeError, ValueError):
        return float(default)


def render(spec: Dict[str, Any]):
    g = spec.get("geometry", {})
    left = spec.get("left_surface", {})
    right = spec.get("right_surface", {})
    L = safe_get(spec, "geometry.length_mm", 75)
    W = safe_get(spec, "geometry.width_mm", 65)
    T = safe_get(spec, "geometry.thickness_mm", 6)
    CAx = safe_get(spec, "geometry.ca_x_mm", L * 0.8)
    CAy = safe_get(spec, "geometry.ca_y_mm", W * 0.8)

    lc = max(0.0, safe_get(spec, "left_surface.chamfer.width_mm", 0.0))
    rc = max(0.0, safe_get(spec, "right_surface.chamfer.width_mm", 0.0))

    fig = plt.figure(figsize=(12, 6.8), dpi=120)
    gs = fig.add_gridspec(1, 2, width_ratios=[3.4, 1.9], wspace=0.28)

    ax_front = fig.add_subplot(gs[0, 0])
    ax_side = fig.add_subplot(gs[0, 1])

    # Front view (ISO-like style)
    ax_front.add_patch(Rectangle((0, 0), L, W, fill=False, linewidth=1.5, color="black"))

    ca_x0 = (L - CAx) / 2
    ca_y0 = (W - CAy) / 2
    ax_front.add_patch(Rectangle((ca_x0, ca_y0), CAx, CAy, fill=False, hatch="xx", linewidth=1.0, color="black"))

    # Horizontal dimensions: CA and total length
    dim_arrow(ax_front, (ca_x0, -7), (ca_x0 + CAx, -7), f"{CAx:g}", text_offset=(0, -2))
    ax_front.text((ca_x0 * 2 + CAx) / 2, -12.0, "Prüfbereich", fontsize=9, ha="center", va="center")
    ax_front.plot([ca_x0, ca_x0], [0, -9], color="black", linewidth=0.8)
    ax_front.plot([ca_x0 + CAx, ca_x0 + CAx], [0, -9], color="black", linewidth=0.8)
    ax_front.plot([L, L], [0, -9], color="black", linewidth=0.8)
    dim_arrow(ax_front, (ca_x0 + CAx, -7), (L, -7), f"{(L - (ca_x0 + CAx)):g}", text_offset=(0, -2))

    dim_arrow(
        ax_front,
        (0, -16),
        (L, -16),
        f"{L:g} ±{g.get('length_tol_plus', 0):g}",
        text_offset=(0, -2),
    )
    ax_front.plot([0, 0], [0, -16], color="black", linewidth=0.8)
    ax_front.plot([L, L], [0, -16], color="black", linewidth=0.8)

    # Vertical dimensions: CA and total width
    dim_arrow(ax_front, (L + 6, ca_y0), (L + 6, ca_y0 + CAy), f"{CAy:g}", text_offset=(5, 0))
    ax_front.plot([L, L + 6], [ca_y0, ca_y0], color="black", linewidth=0.8)
    ax_front.plot([L, L + 6], [ca_y0 + CAy, ca_y0 + CAy], color="black", linewidth=0.8)
    ax_front.text(L + 11.5, W / 2, "Prüfbereich", fontsize=9, rotation=90, va="center", ha="center")

    dim_arrow(
        ax_front,
        (L + 13, 0),
        (L + 13, W),
        f"{W:g} ±{g.get('width_tol_plus', 0):g}",
        text_offset=(7, 0),
    )
    ax_front.plot([L, L + 13], [0, 0], color="black", linewidth=0.8)
    ax_front.plot([L, L + 13], [W, W], color="black", linewidth=0.8)

    # Simple chamfer note on front top-left similar to reference
    left_ch = left.get("chamfer", {})
    ax_front.plot([-10, 0], [W + 10, W], color="black", linewidth=0.8)
    ax_front.text(
        -16,
        W + 13,
        f"{left_ch.get('width_mm', '-')} ±{left_ch.get('tolerance_mm', '-')} (4x)",
        fontsize=8,
        rotation=52,
        ha="left",
        va="center",
    )
    ax_front.text(-2, W + 7.5, f"{left_ch.get('angle_deg', '-')}°", fontsize=8, rotation=-55, ha="left", va="center")

    ax_front.set_xlim(-22, L + 25)
    ax_front.set_ylim(-22, W + 18)
    ax_front.set_aspect("equal", adjustable="box")
    ax_front.axis("off")

    # Side view with right chamfer and callouts
    rc_eff = min(rc, T / 2, W / 2)
    side_poly = [
        (0, 0),
        (T, 0),
        (T, W - rc_eff),
        (T - rc_eff, W),
        (0, W),
    ]
    ax_side.add_patch(Polygon(side_poly, closed=True, fill=False, hatch="//", linewidth=1.4, color="black"))
    ax_side.plot([T / 2, T / 2], [W * 0.25, W * 0.78], color="black", linewidth=0.8, linestyle=(0, (4, 4)))

    # Datum A
    ay = W * 0.58
    ax_side.add_patch(Rectangle((-10.5, ay - 3), 6.5, 6, fill=False, linewidth=0.8, color="black"))
    ax_side.text(-7.25, ay, "A", fontsize=9, ha="center", va="center")
    ax_side.add_patch(FancyArrowPatch((-4.0, ay), (0.0, ay), arrowstyle="-|>", mutation_scale=9, linewidth=0.8, color="black"))

    # Chamfer callout and angle
    right_ch = right.get("chamfer", {})
    ax_side.plot([T - rc_eff / 2, T + 8], [W - rc_eff / 2, W + 8], color="black", linewidth=0.8)
    ax_side.text(
        T + 8.4,
        W + 8.3,
        f"{right_ch.get('width_mm', '-')} ±{right_ch.get('tolerance_mm', '-')}",
        fontsize=8,
        rotation=-55,
        ha="left",
        va="center",
    )
    ax_side.text(T + 1.3, W * 0.68, f"{right_ch.get('angle_deg', '-')}°", fontsize=12, rotation=35, ha="left", va="center")
    ax_side.text(T + 4.4, W * 0.62, "±2°", fontsize=8, rotation=35, ha="left", va="center")

    # Bottom thickness dimension and geometric tolerance frame
    dim_arrow(
        ax_side,
        (0, -8),
        (T, -8),
        f"{T:g} ±{g.get('thickness_tol_plus', 0):g}",
        text_offset=(0, -2),
    )
    ax_side.plot([0, 0], [0, -8], color="black", linewidth=0.8)
    ax_side.plot([T, T], [0, -8], color="black", linewidth=0.8)

    gt_x, gt_y = T + 7, -9
    ax_side.add_patch(Rectangle((gt_x, gt_y), 17, 5, fill=False, linewidth=0.8, color="black"))
    ax_side.plot([gt_x + 4, gt_x + 4], [gt_y, gt_y + 5], color="black", linewidth=0.8)
    ax_side.plot([gt_x + 11, gt_x + 11], [gt_y, gt_y + 5], color="black", linewidth=0.8)
    ax_side.text(gt_x + 2, gt_y + 2.5, "//", fontsize=10, ha="center", va="center")
    ax_side.text(gt_x + 7.5, gt_y + 2.5, f"{spec.get('parallelism', {}).get('value_mm', 0.05):g}", fontsize=9, ha="center", va="center")
    ax_side.text(gt_x + 14, gt_y + 2.5, f"{spec.get('parallelism', {}).get('datum', 'A')}", fontsize=9, ha="center", va="center")

    ax_side.set_xlim(-13, T + 27)
    ax_side.set_ylim(-14, W + 14)
    ax_side.set_aspect("equal", adjustable="box")
    ax_side.axis("off")

    return fig


def main():
    st.set_page_config(page_title="Optik CAD Skizzen Generator", layout="wide")
    st.title("Optik CAD Skizzen Generator")
    st.caption("Links JSON editieren, rechts wird die Zeichnung live erzeugt.")

    left_col, right_col = st.columns([1.1, 1.4])

    with left_col:
        st.subheader("Spezifikation (JSON)")
        default_text = json.dumps(DEFAULT_JSON, indent=2, ensure_ascii=False)
        raw = st.text_area("JSON", value=default_text, height=780)

    with right_col:
        st.subheader("Zeichnung")
        try:
            spec = json.loads(raw)
            fig = render(spec)
            st.pyplot(fig, clear_figure=True, use_container_width=True)

            svg_io = BytesIO()
            pdf_io = BytesIO()
            fig.savefig(svg_io, format="svg", bbox_inches="tight")
            fig.savefig(pdf_io, format="pdf", bbox_inches="tight")
            plt.close(fig)

            st.download_button(
                "Als SVG exportieren",
                data=svg_io.getvalue(),
                file_name="optik_skizze.svg",
                mime="image/svg+xml",
            )
            st.download_button(
                "Als PDF exportieren",
                data=pdf_io.getvalue(),
                file_name="optik_skizze.pdf",
                mime="application/pdf",
            )
        except json.JSONDecodeError as exc:
            st.error(f"JSON Fehler: {exc}")
        except Exception as exc:
            st.error(f"Fehler beim Rendern: {exc}")


if __name__ == "__main__":
    main()
