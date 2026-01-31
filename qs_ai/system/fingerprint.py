import pkg_resources
import hashlib

def dependency_fingerprint() -> str:
    pkgs = sorted(
        f"{d.project_name}=={d.version}"
        for d in pkg_resources.working_set
    )
    blob = "|".join(pkgs).encode()
    return hashlib.sha256(blob).hexdigest()
