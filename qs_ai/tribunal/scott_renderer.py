# qs_ai/tribunal/scott_renderer.py
import pandas as pd


class ScottScheduleRenderer:

    def to_dataframe(self, schedule):
        rows = []

        for item in schedule.items:
            rows.append({
                "Issue ID": item.issue.issue_id,
                "Issue Description": item.issue.description,
                "Claimant Position": item.issue.claimant_position,
                "Respondent Position": item.issue.respondent_position,
                "Bound Quantity ID": item.quantity_ref.bound_quantity_id,
                "Rate": item.rate,
                "Claimed Amount": item.claimed_amount,
                "Confidence": item.confidence,
                "Approval Snapshot": item.approval_snapshot_id,
            })

        return pd.DataFrame(rows)

    def to_excel(self, schedule, path):
        df = self.to_dataframe(schedule)
        df.to_excel(path, index=False)
