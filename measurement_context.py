# measurement_context.py

from dataclasses import dataclass, field
from typing import Optional, Dict

@dataclass
class MeasurementContext:
    # Drawing interpretation
    scale: Optional[float] = None            # e.g. 1/100 → 0.01
    units: str = "metric"                    # metric | imperial

    # Building geometry assumptions
    storey_height: Optional[float] = None    # metres
    wall_thickness: Optional[float] = None   # metres
    slab_thickness: Optional[float] = None   # metres

    # Measurement rules
    deduct_openings: bool = True
    measure_internal: bool = True
    measure_external: bool = False

    # Geometry defaults
    storey_height: float | None = None
    slab_thickness: float | None = None

    # Optional fallbacks
    default_floor_area: float | None = None
    
    # Confidence & provenance
    source: str = "ai"                       # ai | user | bim
    scale_confidence: float = 1.0
    storey_height_confidence: float = 1.0
    confirmed: bool = False                  # QS approval flag

    # Arbitrary extensions
    metadata: Dict = field(default_factory=dict)

    @property
    def overall_confidence(self) -> float:
        return min(
            self.scale_confidence,
            self.storey_height_confidence
        )


