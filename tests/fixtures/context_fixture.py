import pytest
from qs_ai.measurement_context import MeasurementContext

@pytest.fixture
def confirmed_context():
    return MeasurementContext(
        storey_height=3.0,
        slab_thickness=0.15,
        scale_confidence=1.0,
        storey_height_confidence=1.0,
        confirmed=True,
    )
