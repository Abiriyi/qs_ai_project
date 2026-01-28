import pytest
from qs_ai.tribunal.export import generate_tribunal_pack

def test_tribunal_pack_requires_approved_data():
    with pytest.raises(ValueError):
        generate_tribunal_pack(
            project_id="TEST_PROJECT_001"
        )
