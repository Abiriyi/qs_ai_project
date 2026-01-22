# qs_ai/tribunal/pdf_bundle/sealed_builder.py
from uuid import uuid4
from datetime import datetime

from qs_ai.tribunal.pdf_bundle.validator import BundleValidator
from qs_ai.tribunal.pdf_bundle.sealer import PdfBundleSealer
from qs_ai.tribunal.pdf_bundle.manifest import BundleManifest


class SealedTribunalBundleBuilder:

    def build(self, sections, pdf_path, version, prepared_by):
        BundleValidator().validate(sections)

        sha = PdfBundleSealer().seal(pdf_path)

        manifest = BundleManifest(
            bundle_id=str(uuid4()),
            version=str(version),
            sha256=sha,
            generated_at=datetime.utcnow(),
            prepared_by=prepared_by,
        )

        return manifest
