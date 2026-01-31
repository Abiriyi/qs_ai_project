from qs_ai import __app_name__, __version__
from qs_ai.version import get_release_identity

def get_release_identity() -> str:
    return f"{__app_name__} {__version__}"
