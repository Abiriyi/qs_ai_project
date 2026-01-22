# qs_ai/tribunal/joint_statement/renderer.py
import pandas as pd


class JointStatementRenderer:

    def to_dataframe(self, statement):
        rows = []

        for i in statement.issues:
            rows.append({
                "Issue ID": i.issue_id,
                "Description": i.description,
                "Claimant Position": i.claimant_position,
                "Respondent Position": i.respondent_position,
                "Agreed": "Yes" if i.agreed else "No",
                "Agreed Amount": i.agreed_amount,
                "Disagreement Reason": i.disagreement_reason,
            })

        return pd.DataFrame(rows)

    def to_excel(self, statement, path):
        df = self.to_dataframe(statement)
        df.to_excel(path, index=False)
