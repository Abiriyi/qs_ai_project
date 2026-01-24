# qs_ai/tribunal/pdf_bundle/pdf_merge.py

from PyPDF2 import PdfMerger
from pathlib import Path


def merge_pdfs(output_path: str, *pdf_paths):
    merger = PdfMerger()
    for p in pdf_paths:
        merger.append(str(p))
    merger.write(output_path)
    merger.close()
    return Path(output_path)
