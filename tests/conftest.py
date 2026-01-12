import pytest
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
