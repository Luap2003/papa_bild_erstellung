from copy import deepcopy
from typing import Any, Dict, Iterable, Set


DEFAULT_JSON = {
    "substrate_type": "plane",
    "title_block": {
        "document_nr": "000000-1061-510/01",
        "doc_type": "FUM",
        "part_doc": "001",
        "version": "03",
        "sheet": "1",
        "sheets_total": "1",
        "designation": "Kopieträger (75x65x6) mm³",
        "project_classification": "P54263232",
        "component_level": "T",
        "component_counter": "O",
        "component_char": "",
        "construction_group": "K54",
        "scale": "1:1",
        "format": "A4",
        "created_by": "",
        "created_date": "",
        "checked_by": "",
        "checked_date": "",
        "technical_by": "",
        "technical_date": "",
        "norm_by": "",
        "norm_date": "",
        "released_by": "",
        "released_date": "",
        "mass": "",
        "model_name": "",
        "model_version": "",
        "surface_treatment": "-",
        "material_description": "Fa. Schott / N-BK7",
        "gs_required": "nein",
        "general_tolerance": "ISO 10110 - 11",
        "size_standard": "ISO 14405",
        "edge_standard": "ISO 13715",
        "surface_standard": "ISO 10110 - 8",
        "drawing_standard": "ISO 10110",
        "rohs_note": "Werkstoffe, Schichten und Hilfsstoffe müssen\nRoHS konform sein gemäß Direktive 2015/863/EU.",
        "cz_position": "",
        "tolerances": {
            "plus_large": "+0.50",
            "minus_large": "-0.05",
            "plus_small": "+0.05",
            "minus_small": "-0.20",
        },
    },
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


FIELD_TAG_MAP = {
    "geometry.length_mm": ["front.length_dim", "front.outer_horizontal"],
    "geometry.length_tol_plus": ["front.length_dim"],
    "geometry.length_tol_minus": ["front.length_dim"],
    "geometry.width_mm": ["front.width_dim", "front.outer_vertical"],
    "geometry.width_tol_plus": ["front.width_dim"],
    "geometry.width_tol_minus": ["front.width_dim"],
    "geometry.thickness_mm": ["side.thickness_dim", "side.thickness_edges"],
    "geometry.thickness_tol_plus": ["side.thickness_dim"],
    "geometry.thickness_tol_minus": ["side.thickness_dim"],
    "geometry.ca_x_mm": ["front.ca_rect", "front.ca_x_dim"],
    "geometry.ca_y_mm": ["front.ca_rect", "front.ca_y_dim"],
    "parallelism.value_mm": ["side.gt_frame"],
    "parallelism.datum": ["side.gt_frame"],
    "left_surface.chamfer.width_mm": ["front.left_chamfer_width"],
    "left_surface.chamfer.tolerance_mm": ["front.left_chamfer_width"],
    "left_surface.chamfer.angle_deg": ["front.left_chamfer_angle"],
    "right_surface.chamfer.width_mm": ["side.right_chamfer_width"],
    "right_surface.chamfer.tolerance_mm": ["side.right_chamfer_width"],
    "right_surface.chamfer.angle_deg": ["side.right_chamfer_angle"],
    "material.ne": ["info.material.ne"],
    "material.ve": ["info.material.ve"],
    "surface_roughness.rq_nm": ["info.surface_roughness.rq_nm"],
}


INFO_ROWS = [
    ("material.ne", "Brechzahl ne"),
    ("material.ve", "Abbe-Zahl ve"),
    ("surface_roughness.rq_nm", "Rauheit Rq [nm]"),
]


GLASS_DENSITY: Dict[str, float] = {
    "N-BK7": 2.51, "N-BK10": 2.56, "N-K5": 2.59,
    "N-F2": 3.61, "N-SF11": 4.74, "N-SF6": 5.18,
    "N-BAK1": 3.19, "N-LAK22": 3.72, "N-LASF9": 4.44,
    "N-PK51": 3.68,
}


def deep_copy_default() -> Dict[str, Any]:
    return deepcopy(DEFAULT_JSON)


def get_path(spec: Dict[str, Any], path: str) -> Any:
    obj: Any = spec
    for key in path.split("."):
        obj = obj.get(key) if isinstance(obj, dict) else None
    return obj


def get_default_path(path: str) -> Any:
    return get_path(DEFAULT_JSON, path)


def safe_get(spec: Dict[str, Any], path: str, default: float = 0.0) -> float:
    obj: Any = spec
    for key in path.split("."):
        obj = obj.get(key, None) if isinstance(obj, dict) else None
    try:
        return float(obj)
    except (TypeError, ValueError):
        return float(default)


def set_path(spec: Dict[str, Any], path: str, value: Any) -> None:
    parts = path.split(".")
    obj = spec
    for key in parts[:-1]:
        if key not in obj or not isinstance(obj[key], dict):
            obj[key] = {}
        obj = obj[key]
    obj[parts[-1]] = value


def compute_mass_g(spec: Dict[str, Any]) -> float:
    L = safe_get(spec, "geometry.length_mm", 0)
    W = safe_get(spec, "geometry.width_mm", 0)
    T = safe_get(spec, "geometry.thickness_mm", 0)
    volume_cm3 = L * W * T / 1000.0
    material = (get_path(spec, "material.name") or "").strip()
    density = GLASS_DENSITY.get(material, 2.51)
    return round(volume_cm3 * density, 2)


def active_tags_from_paths(active_paths: Set[str]) -> Set[str]:
    tags: Set[str] = set()
    for path in active_paths:
        tags.update(FIELD_TAG_MAP.get(path, []))
    return tags


def tags_active(tags: Iterable[str], active_tags: Set[str]) -> bool:
    return any(tag in active_tags for tag in tags)
