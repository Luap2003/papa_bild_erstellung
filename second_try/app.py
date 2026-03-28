import base64
import json
import os
import sys
from io import BytesIO
from typing import Any, Dict, Set

import matplotlib.pyplot as plt
import streamlit as st
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas as rl_canvas

# Ensure this directory is on sys.path so local modules resolve
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
if _THIS_DIR not in sys.path:
    sys.path.insert(0, _THIS_DIR)

from drawing_helpers import F_LEFT, F_RIGHT, F_BOTTOM, F_TOP, C_BLACK, LW_MEDIUM
from drawing_helpers import draw_line as rl_draw_line, draw_text as rl_draw_text
from draw_border import draw_border
from draw_title_block import draw_title_block
from draw_cross_section import draw_cross_section, draw_dimensions
from draw_iso_table import draw_iso_table, draw_roughness_symbol, draw_standards_box

from spec_utils import (
    DEFAULT_JSON, INFO_ROWS, FIELD_TAG_MAP,
    deep_copy_default, get_path, set_path,
    compute_mass_g, active_tags_from_paths, tags_active,
)
from preview import render
from cad_model import has_cadquery, build_cadquery_model, cadquery_to_plotly_figure, cadquery_model_to_bytes
from ui_helpers import (
    FORM_CSS, serialize_spec, sync_widget_value,
    _lbl, _num, _txt, _row, _row_tol, _row_sym_tol, _sec,
)


# ---------------------------------------------------------------------------
# PDF generation
# ---------------------------------------------------------------------------

def generate_iso_pdf_bytes(data: Dict[str, Any]) -> bytes:
    buf = BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=landscape(A4))
    c.setAuthor("ISO 10110 Generator")
    tb = data.get("title_block", {})
    c.setTitle(f"ISO 10110 - {tb.get('designation', '')}")
    c.setSubject(tb.get("document_nr", ""))

    draw_border(c)

    frame_w = F_RIGHT - F_LEFT
    TB_H = 58.0
    lower_bottom = F_BOTTOM
    lower_top = lower_bottom + TB_H

    c.setStrokeColor(C_BLACK)
    rl_draw_line(c, F_LEFT, lower_top, F_RIGHT, lower_top, lw=LW_MEDIUM)

    tb_w = 180.0
    tb_x = F_RIGHT - tb_w
    draw_title_block(c, data, tb_x, lower_bottom, tb_w)
    draw_standards_box(c, data, F_LEFT, lower_bottom, tb_x - F_LEFT, TB_H)

    iso_table_top = lower_top + 48.0
    draw_iso_table(c, data, F_LEFT, iso_table_top - 6.0, frame_w)

    text_base = iso_table_top + 2
    rl_draw_text(c, "Angaben nach ISO 10110", F_LEFT + 2, text_base,
                 size=2.0, font="Helvetica-Bold")
    rohs = tb.get("rohs_note", "").split("\n")
    for i, line in enumerate(rohs):
        rl_draw_text(c, line, F_LEFT + 2, text_base + 4 + (len(rohs) - 1 - i) * 3, size=1.6)

    face_area_bottom = text_base + 4 + len(rohs) * 3 + 2
    upper_avail = F_TOP - face_area_bottom
    geo = data.get("geometry", {})
    geo_h = geo.get("width_mm", 65)
    geo_w = geo.get("length_mm", 75)
    scale = min((upper_avail - 18.0) / geo_h, (frame_w * 0.50) / geo_w, 1.0)

    cs_cx = F_LEFT + frame_w * 0.35
    cs_cy = face_area_bottom + 3.0 + (geo_h * scale) / 2.0
    coords = draw_cross_section(c, data, cs_cx, cs_cy, scale)
    draw_dimensions(c, data, coords)

    sr = data.get("surface_roughness", {})
    draw_roughness_symbol(c, sr.get("rq_nm", 1.2), sr.get("measurement_area", "P3"),
                          coords["xr"] + 35, coords["yt"] + 8)

    c.save()
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def init_state():
    if "spec" not in st.session_state:
        st.session_state["spec"] = deep_copy_default()
    if "active_field_path" not in st.session_state:
        st.session_state["active_field_path"] = None
    if "raw_json_text" not in st.session_state:
        st.session_state["raw_json_text"] = serialize_spec(st.session_state["spec"])
    if "refresh_form" not in st.session_state:
        st.session_state["refresh_form"] = False


# ---------------------------------------------------------------------------
# Form tab
# ---------------------------------------------------------------------------

def render_form_tab():
    st.caption("Formfelder aktualisieren die Zeichnung direkt. JSON-Tab bleibt synchron.")
    if st.button("Highlight zurücksetzen", use_container_width=True):
        st.session_state["active_field_path"] = None

    _sec("Geometrie")
    _row_tol("Länge [mm]", "geometry.length_mm",
             "geometry.length_tol_plus", "geometry.length_tol_minus",
             val_step=0.1, tol_step=0.01)
    _row_tol("Breite [mm]", "geometry.width_mm",
             "geometry.width_tol_plus", "geometry.width_tol_minus",
             val_step=0.1, tol_step=0.01)
    _row_tol("Dicke [mm]", "geometry.thickness_mm",
             "geometry.thickness_tol_plus", "geometry.thickness_tol_minus",
             val_step=0.01, tol_step=0.001)
    _row("Prüfbereich X [mm]", "geometry.ca_x_mm", "number", 0.1)
    _row("Prüfbereich Y [mm]", "geometry.ca_y_mm", "number", 0.1)

    st.divider()
    _sec("Parallelität")
    c1, c2 = st.columns(2)
    with c1:
        _row("Wert [mm]", "parallelism.value_mm", "number", 0.001)
    with c2:
        _row("Bezug", "parallelism.datum", "text")

    st.divider()
    _sec("Material")
    _row("Name", "material.name", "text")
    _row("Hersteller", "material.manufacturer", "text")
    _row("Brechzahl ne", "material.ne", "number", 0.00001)
    _row("Abbe-Zahl ve", "material.ve", "number", 0.01)

    mass_g = compute_mass_g(st.session_state["spec"])
    set_path(st.session_state["spec"], "title_block.mass", f"{mass_g:.2f}")
    c_ml, c_mv = st.columns([1.8, 2.2])
    with c_ml:
        _lbl("Masse (auto)")
    with c_mv:
        st.markdown(
            f"<p style='margin-top:28px;font-size:14px'><b>{mass_g:.2f} g</b></p>",
            unsafe_allow_html=True,
        )

    st.divider()
    _sec("Linke Fläche")
    _row("Formfehler 3/", "left_surface.figure_error", "text")
    _row("Zentrierung 4/", "left_surface.centering", "text")
    _row("Oberflächengüte 5/", "left_surface.surface_quality", "text")
    _row_sym_tol("Fase Breite [mm]", "left_surface.chamfer.width_mm",
                 "left_surface.chamfer.tolerance_mm", val_step=0.1, tol_step=0.05)
    _row("Fase Winkel [°]", "left_surface.chamfer.angle_deg", "number", 1.0)
    _row("Coating", "left_surface.coating", "text")

    st.divider()
    _sec("Rechte Fläche")
    _row("Formfehler 3/", "right_surface.figure_error", "text")
    _row("Zentrierung 4/", "right_surface.centering", "text")
    _row("Oberflächengüte 5/", "right_surface.surface_quality", "text")
    _row_sym_tol("Fase Breite [mm]", "right_surface.chamfer.width_mm",
                 "right_surface.chamfer.tolerance_mm", val_step=0.1, tol_step=0.05)
    _row("Fase Winkel [°]", "right_surface.chamfer.angle_deg", "number", 1.0)
    _row("Coating", "right_surface.coating", "text")

    st.divider()
    _sec("Oberfläche")
    _row("Rauheit Rq [nm]", "surface_roughness.rq_nm", "number", 0.1)

    st.divider()
    _sec("Titelblock")
    _row("Dokumenten-Nr.", "title_block.document_nr", "text")
    _row("Benennung", "title_block.designation", "text")
    _row("Projektklassifizierung", "title_block.project_classification", "text")
    _row("Maßstab", "title_block.scale", "text")
    _row("Werkstoff", "title_block.material_description", "text")
    _row("Oberflächenbehandlung", "title_block.surface_treatment", "text")


# ---------------------------------------------------------------------------
# JSON tab
# ---------------------------------------------------------------------------

def render_json_tab():
    st.caption("Roh-JSON bearbeiten und nur bei gültigem JSON übernehmen.")
    st.text_area("JSON", key="raw_json_text", height=740)
    if st.button("JSON übernehmen", type="primary", use_container_width=True):
        try:
            parsed = json.loads(st.session_state["raw_json_text"])
            if not isinstance(parsed, dict):
                st.error("JSON muss ein Objekt auf oberster Ebene sein.")
                return
            st.session_state["spec"] = parsed
            st.session_state["active_field_path"] = None
            st.session_state["refresh_form"] = True
            st.session_state["raw_json_text"] = serialize_spec(st.session_state["spec"])
            st.success("JSON erfolgreich übernommen.")
            st.rerun()
        except json.JSONDecodeError as exc:
            st.error(f"JSON Fehler: {exc}")


# ---------------------------------------------------------------------------
# Info block
# ---------------------------------------------------------------------------

def render_info_block(spec: Dict[str, Any], active_tags: Set[str]):
    st.markdown("**Numerische Werte ohne direkte Geometrieabbildung**")
    rows = []
    for path, label in INFO_ROWS:
        value = get_path(spec, path)
        is_active = tags_active(FIELD_TAG_MAP.get(path, []), active_tags)
        color = "#d40000" if is_active else "#222"
        weight = "700" if is_active else "400"
        rows.append(
            f"<tr><td style='padding:4px 8px; color:{color}; font-weight:{weight}'>{label}</td>"
            f"<td style='padding:4px 8px; color:{color}; font-weight:{weight}; text-align:right'>{value}</td></tr>"
        )
    table = (
        "<table style='width:100%; border-collapse:collapse; border:1px solid #ddd;'>"
        "<thead><tr>"
        "<th style='text-align:left; padding:4px 8px; border-bottom:1px solid #ddd'>Feld</th>"
        "<th style='text-align:right; padding:4px 8px; border-bottom:1px solid #ddd'>Wert</th>"
        f"</tr></thead><tbody>{''.join(rows)}</tbody></table>"
    )
    st.markdown(table, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="Optik CAD Skizzen Generator", layout="wide")
    st.title("Optik CAD Skizzen Generator")
    st.markdown(FORM_CSS, unsafe_allow_html=True)
    st.caption("Links Formular/JSON bearbeiten, rechts wird die Zeichnung live erzeugt.")

    init_state()

    left_col, right_col = st.columns([1.2, 1.4])

    with left_col:
        st.subheader("Spezifikation")
        form_tab, json_tab = st.tabs(["Form", "JSON"])
        with form_tab:
            render_form_tab()
        with json_tab:
            render_json_tab()

    with right_col:
        st.subheader("Zeichnung")
        active_path = st.session_state.get("active_field_path")
        active_paths = {active_path} if active_path else set()
        active_tags = active_tags_from_paths(active_paths)

        try:
            fig = render(st.session_state["spec"], active_paths)
            st.pyplot(fig, clear_figure=True, use_container_width=True)

            svg_io = BytesIO()
            fig.savefig(svg_io, format="svg", bbox_inches="tight")
            plt.close(fig)

            st.download_button("Als SVG exportieren", data=svg_io.getvalue(),
                               file_name="optik_skizze.svg", mime="image/svg+xml")

            iso_pdf_bytes = generate_iso_pdf_bytes(st.session_state["spec"])
            st.download_button("Als ISO 10110 PDF exportieren", data=iso_pdf_bytes,
                               file_name="optik_zeichnung.pdf", mime="application/pdf")

            st.markdown("---")
            st.subheader("3D Modell (CadQuery)")
            step_bytes = None
            if has_cadquery():
                model = build_cadquery_model(st.session_state["spec"])
                if model is not None:
                    st.plotly_chart(cadquery_to_plotly_figure(model),
                                    use_container_width=True, config={"displaylogo": False})
                    step_bytes = cadquery_model_to_bytes(model, "step")
                    st.download_button("Als STL exportieren",
                                       data=cadquery_model_to_bytes(model, "stl"),
                                       file_name="optik_koerper.stl", mime="model/stl")
                else:
                    st.info("CadQuery-Modell konnte nicht erzeugt werden.")
            else:
                st.info("Für die 3D-Ansicht bitte `cadquery` installieren.")

            st.markdown("---")
            export_data: Dict[str, Any] = {
                "user_id": 1,
                "spec": st.session_state["spec"],
                "pdf": base64.b64encode(iso_pdf_bytes).decode("ascii"),
            }
            if step_bytes is not None:
                export_data["step"] = base64.b64encode(step_bytes).decode("ascii")
            st.download_button("Komplettexport (JSON)",
                               data=json.dumps(export_data, indent=2, ensure_ascii=False),
                               file_name="optik_export.json", mime="application/json")

            render_info_block(st.session_state["spec"], active_tags)

            if active_path:
                st.caption(f"Aktives Feld: `{active_path}`")

        except Exception as exc:
            st.error(f"Fehler beim Rendern: {exc}")
        finally:
            st.session_state["refresh_form"] = False


if __name__ == "__main__":
    main()
