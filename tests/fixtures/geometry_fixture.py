import pytest

@pytest.fixture
def simple_geometry():
    return [
        {"Room": "Living", "length": 6, "height": 3},
        {"Room": "Bedroom", "length": 4, "height": 3},
    ]
