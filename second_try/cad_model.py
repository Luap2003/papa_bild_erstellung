import math
import os
import tempfile
from typing import Any, Dict, Optional

import plotly.graph_objects as go

from spec_utils import safe_get, get_path

try:
    import cadquery as cq
except Exception:
    cq = None


def has_cadquery() -> bool:
    return cq is not None


def build_cadquery_model(spec: Dict[str, Any]):
    if not has_cadquery():
        return None

    L = max(0.1, safe_get(spec, "geometry.length_mm", 75))
    W = max(0.1, safe_get(spec, "geometry.width_mm", 65))
    T = max(0.1, safe_get(spec, "geometry.thickness_mm", 6))
    lc = max(0.0, safe_get(spec, "left_surface.chamfer.width_mm", 0.0))
    left_angle = max(1.0, min(89.0, safe_get(spec, "left_surface.chamfer.angle_deg", 45.0)))
    rc = max(0.0, safe_get(spec, "right_surface.chamfer.width_mm", 0.0))
    right_angle = max(1.0, min(89.0, safe_get(spec, "right_surface.chamfer.angle_deg", 30.0)))

    wp = cq.Workplane("XY").box(L, W, T)

    rc_run = min(rc, L * 0.24, W * 0.24)
    rc_rise = max(0.01, min(rc_run * math.tan(math.radians(right_angle)), T * 0.95))
    right_face_edges = wp.faces(">Z").edges()
    if rc_run > 0 and right_face_edges.size() > 0:
        wp = right_face_edges.chamfer(rc_run, rc_rise)

    lc_run = min(lc, L * 0.24, W * 0.24)
    lc_rise = max(0.01, min(lc_run * math.tan(math.radians(left_angle)), L * 0.24, W * 0.24))
    corner_edges = wp.edges("|Z and (<X or >X)")
    if lc_run > 0 and corner_edges.size() > 0:
        wp = corner_edges.chamfer(lc_run, lc_rise)

    return wp


def cadquery_to_plotly_figure(model) -> go.Figure:
    shape = model.val()
    vertices, triangles = shape.tessellate(0.15, 0.2)
    x = [v.x for v in vertices]
    y = [v.y for v in vertices]
    z = [v.z for v in vertices]

    mesh = go.Mesh3d(
        x=x, y=y, z=z,
        i=[t[0] for t in triangles],
        j=[t[1] for t in triangles],
        k=[t[2] for t in triangles],
        color="#8fa6bf",
        opacity=1.0,
        flatshading=False,
        lighting=dict(ambient=0.5, diffuse=0.6, roughness=0.6, specular=0.2, fresnel=0.1),
        lightposition=dict(x=100, y=60, z=120),
    )
    fig = go.Figure(data=[mesh])
    fig.update_layout(
        margin=dict(l=0, r=0, t=10, b=0),
        scene=dict(
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            aspectmode="data",
            bgcolor="rgba(0,0,0,0)",
            camera=dict(eye=dict(x=1.5, y=1.4, z=1.1)),
        ),
    )
    return fig


def cadquery_model_to_bytes(model, fmt: str) -> bytes:
    shape = model.val()
    fd, path = tempfile.mkstemp(suffix=f".{fmt}")
    os.close(fd)
    try:
        if fmt == "step":
            shape.exportStep(path)
        else:
            shape.exportStl(path)
        with open(path, "rb") as f:
            return f.read()
    finally:
        try:
            os.remove(path)
        except OSError:
            pass
