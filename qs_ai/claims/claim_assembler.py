# qs_ai/claims/claim_assembler.py
from uuid import uuid4
from datetime import date
from typing import List

from qs_ai.claims.models import (
    ClaimEvent,
    ClaimEntitlement,
    ClaimLine,
    ClaimPackage,
)


class ClaimAssembler:

    def assemble(
        self,
        project_name: str,
        contractor: str,
        employer: str,
        contract_form: str,
        events: List[ClaimEvent],
        entitlements: List[ClaimEntitlement],
        claim_lines: List[ClaimLine],
        prepared_by: str,
    ) -> ClaimPackage:

        total_value = round(sum(l.amount for l in claim_lines), 2)

        narrative = self._build_narrative(events, entitlements)

        return ClaimPackage(
            claim_id=str(uuid4()),
            project_name=project_name,
            contractor=contractor,
            employer=employer,
            contract_form=contract_form,
            submission_date=date.today(),
            events=events,
            entitlements=entitlements,
            claim_lines=claim_lines,
            total_claim_value=total_value,
            narrative_summary=narrative,
            prepared_by=prepared_by,
        )

    def _build_narrative(
        self,
        events: List[ClaimEvent],
        entitlements: List[ClaimEntitlement],
    ) -> str:

        lines = [
            "This claim arises from the following contractual events:"
        ]

        for e in events:
            lines.append(
                f"- {e.event_type} ({e.start_date}) — {e.description}"
            )

        lines.append("")
        lines.append("The Contractor claims entitlement as follows:")

        for ent in entitlements:
            lines.append(
                f"- {ent.entitlement_type}: {ent.justification}"
            )

        return "\n".join(lines)
