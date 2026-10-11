# Copyright (c) 2026 Ian Ryan Kirk. MIT License.
import json, os, unittest

from helpers import SKILLS, load_tool, run, tmpdir, write

hookscore = load_tool("yt-script", "hookscore.py")


class HookFormulas(unittest.TestCase):
    def test_twenty_one_formulas_with_valid_patterns(self):
        with open(os.path.join(SKILLS, "yt-script", "hooks.json"), encoding="utf-8") as fh:
            hooks = json.load(fh)["hooks"]
        self.assertEqual(len(hooks), 21)
        self.assertEqual(len({h["id"] for h in hooks}), 21)
        import re
        for h in hooks:
            for key in ("id", "name", "shape", "example", "fails_when", "match"):
                self.assertIn(key, h)
            for p in h["match"]:
                re.compile(p)


class HookScore(unittest.TestCase):
    def test_real_hook_beats_channel_intro(self):
        _, strong, name, _ = hookscore.score(
            "You are losing 40% of your viewers in 8 seconds and the reason is not your topic")
        _, weak, _, _ = hookscore.score("hey guys welcome back to the channel")
        self.assertGreater(strong, weak)
        self.assertEqual(hookscore.band(weak), "WEAK")
        self.assertEqual(name, "The Statistic")

    def test_properties_stay_in_range(self):
        for t in ["", "?", "x " * 200, "WHY WHY WHY WHY you you you you lose lose lose 99% 99% 99%"]:
            parts, verdict, _, _ = hookscore.score(t)
            for v in list(parts.values()) + [verdict]:
                self.assertGreaterEqual(v, 0)
                self.assertLessEqual(v, 100)


class HookCli(unittest.TestCase):
    def setUp(self):
        self.d = tmpdir(self)

    def test_file_ranked_json(self):
        path = write(self.d, "hooks.txt",
                     "hey guys welcome back\nYou are wasting 3 hours a week on thumbnails → here is why\n")
        r = run("yt-script", "hookscore.py", "--json", path)
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = json.loads(r.stdout)
        self.assertEqual(len(rows), 2)
        self.assertGreaterEqual(rows[0]["verdict"], rows[1]["verdict"])
        self.assertIn("→", rows[0]["hook"] + rows[1]["hook"])

    def test_missing_file_exits_nonzero(self):
        r = run("yt-script", "hookscore.py", os.path.join(self.d, "nope.txt"))
        self.assertEqual(r.returncode, 1)

    def test_empty_file_exits_nonzero(self):
        r = run("yt-script", "hookscore.py", write(self.d, "e.txt", ""))
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
