# tests/test_claims_packaging.py
from datetime import date
from qs_ai.claims.models import ClaimEvent, ClaimEntitlement, ClaimLine
from qs_ai.claims.claim_assembler import ClaimAssembler


def test_claim_package_assembly():

    events = [
        ClaimEvent(
            event_id="E1",
            event_type="Delay",
            description="Late issue of drawings",
            cause="Employer",
            start_date=date(2024, 1, 10),
            end_date=date(2024, 2, 5),
            contract_clause="FIDIC 8.4",
            notified=True,
            notification_date=date(2024, 1, 15),
        )
    ]

    entitlements = [
        ClaimEntitlement(
            event_id="E1",
            entitlement_type="EOT",
            days_entitled=20,
            cost_entitled=150000.0,
            basis="Contractual",
            justification="Employer-caused delay",
        )
    ]

    claim_lines = [
        ClaimLine(
            line_id="L1",
            description="Prolongation costs",
            amount=150000.0,
            basis="Site overheads",
        )
    ]

    assembler = ClaimAssembler()
    claim = assembler.assemble(
        project_name="Office Development",
        contractor="ABC Contractors Ltd",
        employer="XYZ Developments",
        contract_form="FIDIC Red Book",
        events=events,
        entitlements=entitlements,
        claim_lines=claim_lines,
        prepared_by="Senior QS",
    )

    assert claim.total_claim_value == 150000.0
    assert "Late issue of drawings" in claim.narrative_summary
