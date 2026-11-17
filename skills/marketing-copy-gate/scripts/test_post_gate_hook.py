import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

HOOK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "post_gate_hook.py")
CAPTION = "One line hook.\n\nBody of the post."
COMMENT = "What would you keep inside the office?"


def tsha(s):
    return hashlib.sha256(s.strip().encode()).hexdigest()


class HookTest(unittest.TestCase):
    def setUp(self):
        self.t = tempfile.TemporaryDirectory()
        self.d = os.path.join(self.t.name, "marketing", "linkedin", "posts", "p1")
        os.makedirs(os.path.join(self.d, "build"))
        open(os.path.join(self.d, "caption.txt"), "w").write(CAPTION)
        open(os.path.join(self.d, "Post title.pdf"), "wb").write(b"%PDF-1.4 test")
        json.dump({"post_name": "Test post", "caption_file": "caption.txt", "carousel_pdf": "Post title.pdf",
                   "first_comment": {"text": COMMENT}}, open(os.path.join(self.d, "post.json"), "w"))
        self.write_checklist("PASS")

    def tearDown(self):
        self.t.cleanup()

    def write_checklist(self, status):
        sha = lambda p: hashlib.sha256(open(os.path.join(self.d, p), "rb").read()).hexdigest()
        norm = lambda s: " ".join(s.split())
        json.dump({"status": status, "checked_at": "now",
                   "items": [{"n": 6, "step": "Images", "status": "FAIL" if status != "PASS" else "PASS", "problems": ["no photos"]}],
                   "fingerprints": {"manifest": sha("post.json"), "pdf": sha("Post title.pdf"),
                                    "caption": tsha(norm(CAPTION)), "first_comment": tsha(norm(COMMENT))}},
                  open(os.path.join(self.d, "build", "checklist.json"), "w"))

    def call(self, tool, ti):
        env = dict(os.environ, CLAUDE_PROJECT_DIR=self.t.name)
        out = subprocess.run([sys.executable, HOOK], input=json.dumps({"tool_name": tool, "tool_input": ti}),
                             capture_output=True, text=True, env=env).stdout.strip()
        return "ALLOW" if not out else json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"]

    def test_pass_allows_buffer_with_matching_caption_and_comment(self):
        r = self.call("mcp__Buffer__create_post", {"text": CAPTION, "metadata": {"linkedin": {"firstComment": COMMENT}}})
        self.assertEqual(r, "ALLOW")

    def test_blocked_checklist_denies_buffer(self):
        self.write_checklist("BLOCKED")
        self.assertIn("BLOCKED", self.call("mcp__Buffer__create_post", {"text": CAPTION}))

    def test_wrong_first_comment_denied(self):
        r = self.call("mcp__Buffer__create_post", {"text": CAPTION, "metadata": {"linkedin": {"firstComment": "Thoughts?"}}})
        self.assertIn("first comment", r)

    def test_caption_with_no_post_folder_denied(self):
        self.assertIn("does not match", self.call("mcp__Buffer__create_post", {"text": "Something else"}))

    def test_pdf_changed_after_pass_is_denied(self):
        open(os.path.join(self.d, "Post title.pdf"), "ab").write(b" edited")
        self.assertIn("changed after", self.call("SendUserFile", {"files": [os.path.join(self.d, "Post title.pdf")]}))

    def test_sending_a_pass_post_file_is_allowed(self):
        self.assertEqual(self.call("SendUserFile", {"files": [os.path.join(self.d, "build", "review.pdf")]}), "ALLOW")

    def test_post_file_copied_elsewhere_still_checked(self):
        self.write_checklist("BLOCKED")
        self.assertIn("BLOCKED", self.call("SendUserFile", {"files": ["/somewhere/else/Post title.pdf"]}))

    def test_buffer_edit_needs_recorded_id(self):
        self.assertIn("not recorded", self.call("mcp__Buffer__edit_post", {"postId": "abc", "dueAt": "x"}))
        json.dump({"buffer_post_ids": ["abc"]}, open(os.path.join(self.d, "buffer.json"), "w"))
        self.assertEqual(self.call("mcp__Buffer__edit_post", {"postId": "abc", "dueAt": "x"}), "ALLOW")

    def test_unrelated_calls_pass_through(self):
        self.assertEqual(self.call("SendUserFile", {"files": ["/tmp/other.png"]}), "ALLOW")
        self.assertEqual(self.call("Bash", {"command": "ls"}), "ALLOW")


if __name__ == "__main__":
    unittest.main()
