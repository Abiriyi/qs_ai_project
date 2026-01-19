# qs_ai/commercial/sensitivity.py

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class SensitivityVariable:
    name: str
    base_value: float
    delta_percent: float


def run_sensitivity(
    base_cost: float,
    variables: List[SensitivityVariable]
) -> Dict[str, Dict[str, float]]:
    """
    QS-grade sensitivity analysis.
    Returns low / high cost bounds per variable.
    """
    results = {}

    for v in variables:
        delta = base_cost * (v.delta_percent / 100)
        results[v.name] = {
            "low": round(base_cost - delta, 2),
            "high": round(base_cost + delta, 2),
        }

    return results

