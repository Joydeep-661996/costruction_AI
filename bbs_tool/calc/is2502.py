from __future__ import annotations
from typing import Dict
from math import pi

from ..models.schemas import BBSItem, BBSCalculationConfig
from ..recognition.shape_recognizer import normalize_shape_label


def bend_allowance_mm(angle_deg: float, bar_diameter_mm: float, config: BBSCalculationConfig, radius_mm: float | None = None) -> float:
    r_mm = radius_mm if radius_mm is not None else config.default_bend_radius_multiplier * bar_diameter_mm
    k_b = config.neutral_axis_factor
    return (angle_deg * pi / 180.0) * (r_mm + k_b * bar_diameter_mm)


def hook_extension_mm(angle_deg: int, bar_diameter_mm: float, config: BBSCalculationConfig) -> float:
    mult = config.hook_extension_multipliers.get(str(angle_deg))
    if mult is None:
        return 0.0
    return mult * bar_diameter_mm


def unit_weight_kg_per_m(diameter_mm: float, config: BBSCalculationConfig) -> float:
    if config.unit_weight_formula == "IS_D2_OVER_162":
        return (diameter_mm ** 2) / 162.0
    # density based exact: pi * (d/2)^2 * density / 1e6
    area_mm2 = pi * (diameter_mm / 2.0) ** 2
    return area_mm2 * config.steel_density_kg_per_m3 / 1_000_000.0


def calculate_cutting_length_for_item(item: BBSItem, config: BBSCalculationConfig) -> float:
    shape = normalize_shape_label(item.shape)
    d = item.diameter_mm
    dims = item.dims_mm

    if shape == "STRAIGHT":
        if "A" not in dims:
            raise ValueError("STRAIGHT requires dim A (centreline length in mm)")
        return float(dims["A"])  # centreline length

    if shape == "L_90":
        # L-shaped bar with one 90° bend; dims A,B as legs on centreline
        a = dims.get("A")
        b = dims.get("B")
        if a is None or b is None:
            raise ValueError("L_90 requires dims A and B (centreline)")
        return float(a + b + bend_allowance_mm(90.0, d, config))

    if shape == "L_135":
        a = dims.get("A")
        b = dims.get("B")
        if a is None or b is None:
            raise ValueError("L_135 requires dims A and B (centreline)")
        return float(a + b + bend_allowance_mm(135.0, d, config))

    if shape == "U_135_OPEN":
        # Open U-shaped bar (like stirrup with two 135° bends and hook extensions)
        # dims A,B are the legs; optional hook angle defaults to 135°
        a = dims.get("A")
        b = dims.get("B")
        if a is None or b is None:
            raise ValueError("U_135_OPEN requires dims A and B (centreline)")
        bends = 2 * bend_allowance_mm(135.0, d, config)
        hooks = 2 * hook_extension_mm(135, d, config)
        return float(a + b + bends + hooks)

    if shape == "STIRRUP_RECT":
        # Closed rectangular stirrup. dims A,B are the centreline sides
        a = dims.get("A")
        b = dims.get("B")
        if a is None or b is None:
            raise ValueError("STIRRUP_RECT requires dims A and B (centreline)")
        # Four 90° bends
        bends = 4 * bend_allowance_mm(90.0, d, config)
        return float(2 * (a + b) + bends)

    raise ValueError(f"Unsupported shape: {shape}")