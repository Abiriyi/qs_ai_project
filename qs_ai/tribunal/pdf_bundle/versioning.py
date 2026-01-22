# qs_ai/tribunal/pdf_bundle/versioning.py
class BundleVersion:

    def __init__(self, major=1, minor=0):
        self.major = major
        self.minor = minor

    def bump_minor(self):
        return BundleVersion(self.major, self.minor + 1)

    def bump_major(self):
        return BundleVersion(self.major + 1, 0)

    def __str__(self):
        return f"v{self.major}.{self.minor}"
