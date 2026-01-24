# qs_ai/tribunal/exceptions.py
class ScottScheduleValidationError(RuntimeError):
    pass

class TribunalExportError(Exception):
    """Raised when tribunal export conditions are not satisfied."""
