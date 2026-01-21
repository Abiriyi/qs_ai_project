def export_joint_statement_table(statement):
    """
    Returns Joint Statement in structured dict format
    (for Scott Schedules, PDFs, or reports).
    """
    return [
        {
            "Issue": i.reference,
            "Description": i.description,
            "Claimant": i.claimant_position,
            "Respondent": i.respondent_position,
            "Agreed": i.agreed_position,
            "Status": i.status,
            "Notes": i.disagreement_reason,
        }
        for i in statement.issues
    ]
