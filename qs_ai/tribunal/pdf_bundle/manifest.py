# qs_ai/tribunal/pdf_bundle/manifest.py
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class BundleManifest:
    bundle_id: str
    version: str
    sha256: str
    generated_at: datetime
    prepared_by: str
