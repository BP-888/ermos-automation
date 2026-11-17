import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from check_copy import check  # noqa: E402

BANNED = ["delve", "leverage", "seamless", "cutting-edge"]
EMPTY = ["just", "simply"]


def run(text, **kw):
    args = dict(banned=BANNED, empty=EMPTY, require="Resident AI|ResidentAI", max_chars=3000,
                target_chars=500, hook_chars=140, fail_phrases=["safely", "never worry", "comment below"],
                warn_phrases=["next post"])
    args.update(kw)
    return check(text, **args)


class CheckCopyTest(unittest.TestCase):
    def test_clean_copy_passes(self):
        r = run("56% of Australian workers who use AI at work use tools their employer hasn't approved.\n\n"
                "Resident AI keeps your firm's knowledge inside your business.")
        self.assertTrue(r["pass"], r)

    def test_em_dash_fails(self):
        r = run("Resident AI — private and onshore.")
        self.assertFalse(r["pass"])
        self.assertEqual(r["fails"][0]["check"], "dashes")

    def test_banned_word_whole_word_only(self):
        self.assertFalse(run("We leverage Resident AI.")["pass"])
        self.assertTrue(run("Leverages aside, Resident AI works.")["pass"])  # different word

    def test_hyphenated_banned_word(self):
        self.assertFalse(run("Cutting-edge Resident AI.")["pass"])

    def test_missing_required_term_fails(self):
        r = run("Private AI for your business.")
        self.assertIn("required term", [f["check"] for f in r["fails"]])

    def test_residentai_variant_accepted(self):
        self.assertTrue(run("ResidentAI for your business.")["pass"])

    def test_zero_risk_phrase_fails(self):
        self.assertFalse(run("Use Resident AI safely.")["pass"])

    def test_empty_word_only_warns(self):
        r = run("Resident AI just works.")
        self.assertTrue(r["pass"])
        self.assertEqual(r["warnings"][0]["check"], "empty word")

    def test_length_limits(self):
        long = "Resident AI. " + "word " * 700
        r = run(long)
        self.assertIn("length", [f["check"] for f in r["fails"]])

    def test_long_hook_warns(self):
        r = run("A" * 200 + "\nResident AI.")
        self.assertIn("hook", [w["check"] for w in r["warnings"]])

    def test_binary_contrast_warns_not_fails(self):
        r = run("It's not a chatbot, it's Resident AI.")
        self.assertTrue(r["pass"])
        self.assertIn("binary contrast", [w["check"] for w in r["warnings"]])


if __name__ == "__main__":
    unittest.main()
