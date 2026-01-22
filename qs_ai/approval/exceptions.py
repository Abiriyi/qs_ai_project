class ApprovalError(RuntimeError):
    """
    Base exception for approval workflow violations.
    Raised when an action breaches approval rules.
    """
    pass


class UnauthorizedApproverError(ApprovalError):
    """
    Raised when a user without authority attempts
    to approve or reject a commercial action.
    """
    pass


class InvalidApprovalStateError(ApprovalError):
    """
    Raised when an approval action is attempted
    in an invalid workflow state.
    """
    pass


class ApprovalRevokedError(ApprovalError):
    """
    Raised when attempting to use or rely on
    an approval that has been revoked.
    """
    pass


class ApprovalRequiredError(ApprovalError):
    """
    Raised when an operation requires approval
    but none exists.
    """
    pass
