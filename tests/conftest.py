import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from qs_ai.measurement_context import MeasurementContext

@pytest.fixture
def default_context():
    return MeasurementContext(
        scale=0.01,
        storey_height=3.0,
        slab_thickness=0.15,
        confirmed=True,
        source="test",
        scale_confidence=0.9,
        storey_height_confidence=0.9
    )
