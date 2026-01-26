from qs_ai.tribunal.export import generate_tribunal_pack

def test_tribunal_pack_requires_approved_data():
    pack = generate_tribunal_pack(
        project_id="TEST_PROJECT_001"
    )

    assert pack.index_pdf is not None
    assert pack.evidence_bundle is not None
    assert pack.hash_manifest is not None

    # Integrity check
    assert pack.verify_hashes() is True
