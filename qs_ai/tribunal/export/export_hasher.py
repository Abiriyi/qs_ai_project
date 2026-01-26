import hashlib
from pathlib import Path


def hash_file(path: Path) -> str:
    """
    Compute SHA-256 hash of a file.
    Tribunal-safe and deterministic.
    """
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_directory(directory: Path) -> dict:
    """
    Hash all files in a directory (recursively).
    Returns {relative_path: sha256}
    """
    hashes = {}

    for file in sorted(directory.rglob("*")):
        if file.is_file():
            rel = str(file.relative_to(directory))
            hashes[rel] = hash_file(file)

    return hashes
