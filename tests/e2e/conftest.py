import pytest
from qs_ai.measurement_context import MeasurementContext


@pytest.fixture
def simple_geometry():
    return [
        {"length": 5.0, "height": 3.0},
        {"length": 4.0, "height": 3.0},
    ]


@pytest.fixture
def default_context():
    return MeasurementContext(
        confirmed=True,
        storey_height=3.0,
        scale_confidence=1.0,
        storey_height_confidence=1.0,
    )

@pytest.fixture
def confirmed_context(default_context):
    """
    Alias for readability in E2E tests.
    Represents a QS-confirmed measurement context.
    """
    return default_context
