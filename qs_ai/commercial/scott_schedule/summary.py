def generate_summary(issues):
    return {
        "total_claimed": round(sum(i.claimant.amount for i in issues), 2),
        "total_assessed": round(sum(i.respondent.amount for i in issues), 2),
        "total_agreed": round(sum(i.agreed_amount for i in issues), 2),
        "total_disputed": round(sum(i.disputed_amount for i in issues), 2),
    }
