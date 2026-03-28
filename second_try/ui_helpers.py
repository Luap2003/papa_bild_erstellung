import json
from typing import Any, Dict, Optional

import streamlit as st

from spec_utils import get_path, get_default_path, set_path


FORM_CSS = """
<style>
[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"] { display: none !important; }
</style>
"""


def serialize_spec(spec: Dict[str, Any]) -> str:
    return json.dumps(spec, indent=2, ensure_ascii=False)


def sync_widget_value(widget_key: str, value: Any):
    if st.session_state.get("refresh_form", False) or widget_key not in st.session_state:
        st.session_state[widget_key] = value


def _on_field_change(path: str, widget_key: str, as_number: bool = False):
    val = st.session_state[widget_key]
    set_path(st.session_state["spec"], path, float(val) if as_number else val)
    if as_number:
        st.session_state["active_field_path"] = path
    st.session_state["raw_json_text"] = serialize_spec(st.session_state["spec"])


def _normalize_float(path: str) -> float:
    value = get_path(st.session_state["spec"], path)
    try:
        return float(value)
    except (TypeError, ValueError):
        fallback = get_default_path(path)
        try:
            nv = float(fallback)
        except (TypeError, ValueError):
            nv = 0.0
        set_path(st.session_state["spec"], path, nv)
        st.session_state["raw_json_text"] = serialize_spec(st.session_state["spec"])
        return nv


def _lbl(text: str) -> None:
    st.markdown(
        f"<p style='margin-top:28px;margin-bottom:0;font-size:14px'>{text}</p>",
        unsafe_allow_html=True,
    )


def _num(path: str, label: str = "", step: float = 0.1) -> None:
    widget_key = f"field__{path.replace('.', '__')}"
    sync_widget_value(widget_key, _normalize_float(path))
    st.number_input(
        label, key=widget_key, step=step,
        label_visibility="visible" if label else "collapsed",
        on_change=_on_field_change, args=(path, widget_key, True),
    )


def _txt(path: str) -> None:
    widget_key = f"field__{path.replace('.', '__')}"
    value = get_path(st.session_state["spec"], path)
    sync_widget_value(widget_key, "" if value is None else str(value))
    st.text_input(
        "", key=widget_key, label_visibility="collapsed",
        on_change=_on_field_change, args=(path, widget_key, False),
    )


def _row(label: str, path: str, field_type: str, step: Optional[float] = None) -> None:
    c_l, c_i = st.columns([1.8, 2.2])
    with c_l:
        _lbl(label)
    with c_i:
        if field_type == "number":
            _num(path, step=step or 0.1)
        else:
            _txt(path)


def _row_tol(label: str, val_path: str, plus_path: str, minus_path: str,
             val_step: float = 0.1, tol_step: float = 0.01) -> None:
    """Row: label | value | +tol | -tol"""
    c_l, c_v, c_p, c_m = st.columns([1.8, 1.5, 1.0, 1.0])
    with c_l:
        _lbl(label)
    with c_v:
        _num(val_path, step=val_step)
    with c_p:
        _num(plus_path, label="+", step=tol_step)
    with c_m:
        _num(minus_path, label="−", step=tol_step)


def _row_sym_tol(label: str, val_path: str, tol_path: str,
                 val_step: float = 0.1, tol_step: float = 0.1) -> None:
    """Row: label | value | ±tol"""
    c_l, c_v, c_t = st.columns([1.8, 1.5, 1.2])
    with c_l:
        _lbl(label)
    with c_v:
        _num(val_path, step=val_step)
    with c_t:
        _num(tol_path, label="±", step=tol_step)


def _sec(title: str) -> None:
    st.markdown(f"**{title}**")
