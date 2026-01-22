# qs_ai/tribunal/pdf_bundle/footer_text.py
def build_footer_text(version, sha256, page, total_pages):
    short_hash = sha256[:8]
    return (
        f"Tribunal Bundle — {version} — "
        f"SHA256: {short_hash} — Page {page} of {total_pages}"
    )
