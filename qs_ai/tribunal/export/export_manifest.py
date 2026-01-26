from datetime import datetime
from pathlib import Path
import json
import hashlib


def generate_bundle_checksum(file_hashes: dict) -> str:
    """
    Hash of all file hashes (order-independent).
    """
    h = hashlib.sha256()
    for k in sorted(file_hashes.keys()):
        h.update(k.encode())
        h.update(file_hashes[k].encode())
    return h.hexdigest()


def write_export_manifest(
    export_dir: Path,
    case_reference: str,
    exported_by: str,
    file_hashes: dict,
):
    """
    Creates MANIFEST.json inside export bundle.
    """
    manifest = {
        "case_reference": case_reference,
        "exported_by": exported_by,
        "export_datetime_utc": datetime.utcnow().isoformat() + "Z",
        "hash_algorithm": "SHA-256",
        "files": file_hashes,
        "bundle_checksum": generate_bundle_checksum(file_hashes),
    }

    manifest_path = export_dir / "MANIFEST.json"
    with manifest_path.open("w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    return manifest
