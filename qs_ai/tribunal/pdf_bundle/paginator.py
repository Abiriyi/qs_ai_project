# qs_ai/tribunal/pdf_bundle/paginator.py
class PageTracker:

    def __init__(self):
        self.current_page = 1
        self.entries = []

    def add_section(self, title, page_count):
        self.entries.append({
            "title": title,
            "start_page": self.current_page,
            "end_page": self.current_page + page_count - 1,
        })
        self.current_page += page_count
