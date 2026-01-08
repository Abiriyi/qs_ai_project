# measurement_context.py

from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class MeasurementContext:
    # Drawing interpretation
    scale: Optional[float] = None          # e.g. 1/100 → 0.01
    units: str = "metric"                  # metric | imperial

    # Building geometry assumptions
    storey_height: Optional[float] = None  # metres
    wall_thickness: Optional[float] = None # metres
    slab_thickness: Optional[float] = None # metres

    # Measurement rules
    deduct_openings: bool = True
    measure_internal: bool = True
    measure_external: bool = False

    # Confidence & provenance
    source: str = "ai"                     # ai | user | bim
    confidence: float = 0.0                # 0–1
    confirmed: bool = False                # QS approval flag

    # Arbitrary extensions
    metadata: Dict = field(default_factory=dict)
