import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import git_cat  # noqa: E402


class Levels(unittest.TestCase):
    def test_thresholds(self):
        for n, lv in [(0, "calm"), (2, "calm"), (3, "happy"), (6, "happy"), (7, "joyful"), (50, "joyful")]:
            self.assertEqual(git_cat.level_for(n), lv)

    def test_every_gif_exists(self):
        for c in git_cat.COATS:
            for s in ("sleep", "calm", "happy", "joyful"):
                self.assertTrue(os.path.exists(os.path.join(git_cat.ROOT, "dist", c, f"{s}.gif")), (c, s))


if __name__ == "__main__":
    unittest.main()
