from __future__ import annotations

def normalize_shape_label(label: str) -> str:
    up = (label or "").strip().upper()
    mapping = {
        "L": "L_90",
        "L-90": "L_90",
        "L90": "L_90",
        "L_90": "L_90",
        "L135": "L_135",
        "L-135": "L_135",
        "L_135": "L_135",
        "U": "U_135_OPEN",
        "U_135_OPEN": "U_135_OPEN",
        "STIRRUP": "STIRRUP_RECT",
        "STIRRUP_RECT": "STIRRUP_RECT",
        "STRAIGHT": "STRAIGHT",
    }
    return mapping.get(up, up)