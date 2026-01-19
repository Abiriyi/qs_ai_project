class FinalAccountNotApprovedError(RuntimeError):
    pass

class AuditFailureError(RuntimeError):
    def __init__(self, issues):
        self.issues = issues
        super().__init__("Final Account audit failed")


class MissingApprovalError(RuntimeError):
    pass


class MissingReferenceError(RuntimeError):
    pass
