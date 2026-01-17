class QSOverrideError(Exception):
    pass


class InvalidOverrideError(QSOverrideError):
    pass


class PermissionDeniedError(QSOverrideError):
    pass


class WorkflowError(QSOverrideError):
    pass
