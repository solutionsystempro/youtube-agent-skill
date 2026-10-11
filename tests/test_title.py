# Copyright (c) 2026 Ian Ryan Kirk. MIT License.
import json, unittest

from helpers import load_tool, run, tmpdir, write

title = load_tool("yt-package", "title.py")


def kinds(result):
    return [k for k, _ in result["issues"]]


class TitleLint(unittest.TestCase):
    def test_clean_title_and_thumb(self):
        r = title.check("I tried 7 thumbnails for 30 days", "FACES WON")
        self.assertEqual(kinds(r), [])
        self.assertEqual(r["score"], 100)

    def test_length_limits(self):
        self.assertIn("length", kinds(title.check("x " * 31)))          # 61+ chars, desktop
        self.assertIn("mobile", kinds(title.check("a" * 41)))           # past the 40 mobile cut
        hard = title.check("y" * 101)
        self.assertIn("100", dict(hard["issues"])["length"])

    def test_thumbnail_repeating_title(self):
        r = title.check("Why thumbnails fail in 2026", "THUMBNAILS FAIL")
        self.assertIn("duplicate", kinds(r))

    def test_thumbnail_word_ceiling_is_three(self):
        self.assertNotIn("thumb-length", kinds(title.check("Edit 9 videos fast", "AI RAN IT")))
        self.assertIn("thumb-length", kinds(title.check("Edit 9 videos fast", "AI RAN IT TODAY")))

    def test_shouting_and_vague(self):
        r = title.check("The ULTIMATE INSANE GUIDE to everything")
        self.assertIn("shouting", kinds(r))
        self.assertIn("vague", kinds(r))
        self.assertIn("no-number", kinds(r))


class TitleCli(unittest.TestCase):
    def setUp(self):
        self.d = tmpdir(self)

    def test_file_with_unicode_and_thumb_flag_first(self):
        path = write(self.d, "titles.txt", "I tried 7 thumbnails 🔥\nThe best video ever\n")
        r = run("yt-package", "title.py", "--thumb", "AI RAN IT", path, "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        rows = json.loads(r.stdout)
        self.assertEqual(rows[0]["title"], "I tried 7 thumbnails 🔥")
        self.assertEqual(rows[0]["chars"], 22)  # read as UTF-8, not as cp1252 bytes

    def test_empty_file(self):
        r = run("yt-package", "title.py", write(self.d, "empty.txt", "\n\n"))
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
