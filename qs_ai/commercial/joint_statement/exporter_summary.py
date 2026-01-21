def export_joint_statement_summary(statement):
    total = len(statement.issues)

    return {
        "Statement ID": statement.statement_id,
        "Contract Reference": statement.contract_ref,
        "Total Issues": total,
        "Agreed": sum(1 for i in statement.issues if i.status == "Agreed"),
        "Narrowed": sum(1 for i in statement.issues if i.status == "Narrowed"),
        "Disagreed": sum(1 for i in statement.issues if i.status == "Disagreed"),
    }
