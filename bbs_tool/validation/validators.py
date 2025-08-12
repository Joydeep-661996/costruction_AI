from __future__ import annotations
from typing import List

from ..models.schemas import BBSItem, BBSCalculationConfig


def validate_item(item: BBSItem, config: BBSCalculationConfig) -> List[str]:
    warnings: List[str] = []

    if item.diameter_mm <= 0:
        warnings.append(f"{item.bar_mark}: diameter must be > 0")
    if item.quantity <= 0:
        warnings.append(f"{item.bar_mark}: quantity must be >= 1")

    # Simple min dimension check: each leg must be at least some multiple of d
    min_leg_mult = 4.0
    for k, v in item.dims_mm.items():
        if v < min_leg_mult * item.diameter_mm:
            warnings.append(f"{item.bar_mark}: dim {k}={v} mm is < {min_leg_mult}d; verify feasibility")

    # Bend radius check
    r_default = config.default_bend_radius_multiplier * item.diameter_mm
    if r_default < 2.0 * item.diameter_mm:
        warnings.append(f"{item.bar_mark}: default bend radius {r_default} mm < 2d; verify against code")

    return warnings