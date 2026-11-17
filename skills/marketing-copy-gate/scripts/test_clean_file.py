import os
import sys
import tempfile
import unittest

from pypdf import PdfWriter

sys.path.insert(0, os.path.dirname(__file__))
from clean_file import check, clean, leaks  # noqa: E402


def make_pdf(path, title):
    w = PdfWriter()
    w.add_blank_page(width=200, height=250)
    w.add_blank_page(width=200, height=250)
    w.add_metadata({"/Title": title, "/Creator": "HeadlessChrome"})
    with open(path, "wb") as f:
        w.write(f)


class CleanFileTest(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()

    def test_leaks(self):
        self.assertIn("V4", leaks("ERMOS LinkedIn Post 2 carousel V4 (Post 1 template)"))
        self.assertIn("template", leaks("Post 1 template"))
        self.assertEqual(leaks("AI in legal practice - three questions for your firm"), [])
        self.assertEqual(leaks("Victorian lawyers"), [])  # words starting with v are fine
        self.assertEqual(leaks("284102ec-REF_Carousel_ERMOS"), ["REF_"])

    def test_dirty_file_fails_check(self):
        p = os.path.join(self.d, "Carousel V6_2026-11-16.pdf")
        make_pdf(p, "ERMOS LinkedIn Post 2 carousel V4 (Post 1 template)")
        problems = check(p)
        self.assertTrue(any("file name" in x for x in problems))
        self.assertTrue(any("Title" in x for x in problems))
        self.assertTrue(any("Creator" in x for x in problems))

    def test_clean_copy_passes_and_keeps_pages(self):
        p = os.path.join(self.d, "Carousel V6.pdf")
        make_pdf(p, "carousel V4 template")
        out, pages = clean(p, "AI in legal practice: three questions for your firm", self.d)
        self.assertEqual(pages, 2)
        self.assertEqual(os.path.basename(out), "AI in legal practice - three questions for your firm.pdf")
        self.assertEqual(check(out), [])


if __name__ == "__main__":
    unittest.main()
