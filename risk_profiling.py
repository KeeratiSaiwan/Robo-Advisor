from __future__ import annotations

import math
from typing import Dict


ALLOCATION_TABLE: Dict[str, Dict[str, float]] = {
    "low": {
        "VTI": 0.20,
        "VXUS": 0.10,
        "BND": 0.40,
        "BNDX": 0.20,
        "VNQ": 0.10,
    },
    "medium": {
        "VTI": 0.35,
        "VXUS": 0.20,
        "BND": 0.25,
        "BNDX": 0.10,
        "VNQ": 0.10,
    },
    "high": {
        "VTI": 0.45,
        "VXUS": 0.30,
        "BND": 0.10,
        "BNDX": 0.05,
        "VNQ": 0.10,
    },
}


def get_allocation(risk_level: str) -> Dict[str, float]:
    """
    Return target ETF allocation for a given risk level.

    The function is pure and does not depend on any pricing logic.

    Args:
        risk_level: User-selected risk level (e.g. 'low', 'Medium', 'HIGH').

    Raises:
        ValueError: if the risk level is invalid, or if the configured
            allocation does not sum to 1.0 (configuration error).
    """
    normalized = risk_level.strip().lower()

    if normalized not in ALLOCATION_TABLE:
        valid_levels = ", ".join(sorted(ALLOCATION_TABLE.keys()))
        raise ValueError(f"Invalid risk level '{risk_level}'. Valid values: {valid_levels}.")

    allocation = ALLOCATION_TABLE[normalized]
    total_weight = sum(allocation.values())

    if not math.isclose(total_weight, 1.0, rel_tol=1e-9, abs_tol=1e-9):
        raise ValueError(
            f"Allocation weights for risk level '{normalized}' must sum to 1.0, "
            f"but got {total_weight}."
        )

    # Return a shallow copy to avoid accidental mutation of the constant table.
    return allocation.copy()

