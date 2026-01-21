def summarise(statement):
    total = len(statement.issues)

    return {
        "total_issues": total,
        "agreed": sum(1 for i in statement.issues if i.status == "Agreed"),
        "narrowed": sum(1 for i in statement.issues if i.status == "Narrowed"),
        "disagreed": sum(1 for i in statement.issues if i.status == "Disagreed"),
    }
