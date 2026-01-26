import pytest

@pytest.fixture
def qs_user():
    return {"id": "qs_001", "role": "QS"}

@pytest.fixture
def senior_qs_user():
    return {"id": "qs_002", "role": "Senior QS"}
