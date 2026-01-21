import pandas as pd


class JointStatementExcelExporter:
    """
    Exports Joint Statement of Experts in tribunal-ready Excel format.
    """

    def export(self, statement, output_path):
        rows = []

        for i in statement.issues:
            rows.append({
                "Issue Ref": i.reference,
                "Description": i.description,
                "Claimant Position": i.claimant_position,
                "Respondent Position": i.respondent_position,
                "Agreed Position": i.agreed_position,
                "Status": i.status,
                "Reason for Disagreement": i.disagreement_reason,
            })

        df = pd.DataFrame(rows)

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Joint Statement")

            ws = writer.sheets["Joint Statement"]
            ws.freeze_panes = "A2"

            # Auto column widths
            for col in ws.columns:
                max_length = max(len(str(c.value)) if c.value else 0 for c in col)
                ws.column_dimensions[col[0].column_letter].width = max(12, min(max_length + 2, 50))

        return output_path
