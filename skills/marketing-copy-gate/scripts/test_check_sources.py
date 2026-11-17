import datetime as dt
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from check_sources import judge  # noqa: E402

TODAY = dt.date(2026, 11, 17)


class CheckSourcesTest(unittest.TestCase):
    def v(self, date, allow=False):
        return judge([{"title": "x", "date": date}], TODAY, allow)[0]["verdict"]

    def test_current_year_passes(self):
        self.assertEqual(self.v("2026-10-13"), "PASS")

    def test_previous_year_needs_yes(self):
        self.assertEqual(self.v("2025-09-02"), "FAIL")
        self.assertEqual(self.v("2025-09-02", allow=True), "PASS")

    def test_last_twelve_months_counts_as_current(self):
        self.assertEqual(self.v("2025-12-01"), "PASS")

    def test_old_always_fails(self):
        self.assertEqual(self.v("2024-10-29", allow=True), "FAIL")

    def test_missing_date_fails(self):
        self.assertEqual(self.v(""), "FAIL")


if __name__ == "__main__":
    unittest.main()
