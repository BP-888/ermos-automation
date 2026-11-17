import os
import sys
import tempfile
import unittest

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(__file__))
from check_visual import DEFAULT_BENCH, check  # noqa: E402


def make_pdf(path, colours, accent=None):
    pages = []
    for c in colours:
        im = Image.new("RGB", (1080, 1350), c)
        if accent:
            ImageDraw.Draw(im).rectangle([72, 600, 900, 700], fill=accent)
        pages.append(im)
    pages[0].save(path, save_all=True, append_images=pages[1:], resolution=96)


class CheckVisualTest(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.t.cleanup()

    def pdf(self, colours, accent=None):
        p = os.path.join(self.t.name, "d.pdf")
        make_pdf(p, colours, accent)
        return p

    def test_benchmark_passes_itself(self):
        r = check(DEFAULT_BENCH, DEFAULT_BENCH)
        self.assertTrue(r["pass"], r["fails"])
        self.assertEqual(r["warnings"], [])

    def test_paper_with_teal_passes_but_warns_without_photo(self):
        r = check(self.pdf(["#EFEEEA"] * 5, accent="#2F8A80"), DEFAULT_BENCH)
        self.assertTrue(r["pass"], r["fails"])
        self.assertTrue(any("no photo" in w for w in r["warnings"]))

    def test_dark_navy_slides_fail(self):
        r = check(self.pdf(["#EFEEEA", "#212E41", "#EFEEEA", "#212E41", "#212E41"]), DEFAULT_BENCH)
        self.assertFalse(r["pass"])
        self.assertTrue(any("paper background" in f for f in r["fails"]))

    def test_electric_blue_accent_fails(self):
        r = check(self.pdf(["#EFEEEA"] * 5, accent="#2563FF"), DEFAULT_BENCH)
        self.assertFalse(r["pass"])
        self.assertTrue(any("electric blue" in f for f in r["fails"]))

    def test_too_few_slides_fail(self):
        r = check(self.pdf(["#EFEEEA"] * 3, accent="#2F8A80"), DEFAULT_BENCH)
        self.assertFalse(r["pass"])


if __name__ == "__main__":
    unittest.main()
