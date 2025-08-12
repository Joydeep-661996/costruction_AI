from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, List, Optional


class BBSItem(BaseModel):
    bar_mark: str = Field(..., description="Unique bar mark")
    diameter_mm: float = Field(..., gt=0)
    shape: str = Field(..., description="Shape key, e.g., STRAIGHT, L_90, L_135, U_135_OPEN, STIRRUP_RECT")
    dims_mm: Dict[str, float] = Field(default_factory=dict, description="Map of dimension labels (A, B, C, ...) to millimetres. Assumed centreline unless noted.")
    quantity: int = Field(1, ge=1)
    bend_radii_mm: Optional[List[float]] = Field(default=None, description="Optional list of internal bend radii per bend in mm; fallback to config if not provided")
    notes: Optional[str] = None

    @staticmethod
    def from_csv_row(row: Dict[str, str]) -> "BBSItem":
        bar_mark = row.get("bar_mark") or row.get("mark") or row.get("Bar Mark") or ""
        shape = (row.get("shape") or row.get("Shape") or "").strip().upper()
        diameter = float(row.get("diameter_mm") or row.get("diameter") or row.get("Dia") or 0)
        quantity = int(float(row.get("quantity") or row.get("qty") or 1))
        dims_mm: Dict[str, float] = {}
        for key, val in row.items():
            k = key.strip().upper()
            if k in {"A", "B", "C", "D", "E", "F"} and val not in (None, ""):
                try:
                    dims_mm[k] = float(val)
                except ValueError:
                    continue
        return BBSItem(bar_mark=bar_mark, diameter_mm=diameter, shape=shape, dims_mm=dims_mm, quantity=quantity)


class BBSCalculationConfig(BaseModel):
    default_bend_radius_multiplier: float = Field(2.0, description="Default internal bend radius as multiple of bar diameter when not specified")
    neutral_axis_factor: float = Field(0.5, description="Factor k_b in allowance: (theta*pi/180) * (r + k_b*d)")
    hook_extension_multipliers: Dict[str, float] = Field(
        default_factory=lambda: {"90": 8.0, "135": 6.0, "180": 4.0},
        description="Hook straight extension after bend, as multiple of d. Review against IS code for project.",
    )
    unit_weight_formula: str = Field(
        "IS_D2_OVER_162",
        description="Weight formula: 'IS_D2_OVER_162' or 'DENSITY_PI_R2'",
    )
    steel_density_kg_per_m3: float = 7850.0


class BBSCalculationRequest(BaseModel):
    items: List[BBSItem]
    config: Optional[BBSCalculationConfig] = None


class BBSCalculationResponse(BaseModel):
    results: List[Dict[str, float | int | str]]
    warnings: List[str] = []