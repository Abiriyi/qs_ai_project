from qs_ai.qs_override.approval_guard import require_approval

class ClaimsEngine:

    def submit_claim(self, baseline_boq, events):
        for item in baseline_boq:
            require_approval(item, stage="Claims baseline")

        # claims logic continues
        for event in events:
            require_approval(event, stage="Claims event")