# Copyright (c) 2026 Ian Ryan Kirk. MIT License.
import json, os, shutil, unittest

from helpers import SKILLS, make_srt, run, tmpdir, write

TOPICS = [
    "thumbnails contrast faces emotion colour",
    "titles numbers length truncation mobile",
    "retention graphs cliffs slide pacing",
    "scripting hooks stakes curiosity brevity",
]


def long_transcript(start_offset=0.0):
    """Four topics, six 8-second cues each, with a 3-second pause between topics."""
    cues, t = [], start_offset
    for n, topic in enumerate(TOPICS):
        if n: t += 3.0
        for k in range(6):
            cues.append((t, t + 8.0, f"{topic} point {k}"))
            t += 8.2
    return make_srt(cues)


class Chapters(unittest.TestCase):
    def setUp(self):
        self.d = tmpdir(self)

    def chapters(self, srt, *args):
        r = run("yt-chapters", "chapters.py", write(self.d, "t.srt", srt), "--json", *args)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_youtube_rules_hold(self):
        out = self.chapters(long_transcript())
        ch = out["chapters"]
        self.assertTrue(out["valid"])
        self.assertGreaterEqual(len(ch), 3)
        self.assertEqual(ch[0]["start"], 0)
        self.assertEqual(ch[0]["label"], "0:00")
        self.assertTrue(all(c["seconds"] >= 10 for c in ch))
        self.assertEqual([c["start"] for c in ch], sorted(c["start"] for c in ch))

    def test_hour_long_labels(self):
        out = self.chapters(long_transcript(start_offset=3590.0))
        labels = [c["label"] for c in out["chapters"]]
        self.assertEqual(labels[0], "0:00")
        self.assertTrue(all(l.count(":") == 2 for l in labels[1:]), labels)

    def test_target_below_three_is_raised_to_three(self):
        out = self.chapters(long_transcript(), "--target", "1")
        self.assertTrue(out["valid"])
        self.assertEqual(len(out["chapters"]), 3)

    def test_too_short_is_flagged_invalid(self):
        cues = [(i * 2.0, i * 2.0 + 1.9, f"word{i} thing{i}") for i in range(8)]
        out = self.chapters(make_srt(cues))
        self.assertFalse(out["valid"])

    def test_output_is_deterministic(self):
        srt = long_transcript()
        first = self.chapters(srt)
        for _ in range(3):
            self.assertEqual(self.chapters(srt), first)

    def test_works_when_deadair_sits_next_to_it(self):
        # Someone copies only yt-chapters and drops deadair.py into it.
        solo = os.path.join(self.d, "yt-chapters")
        os.makedirs(solo)
        shutil.copy(os.path.join(SKILLS, "yt-chapters", "chapters.py"), solo)
        shutil.copy(os.path.join(SKILLS, "yt-edit", "deadair.py"), solo)
        import subprocess, sys
        r = subprocess.run([sys.executable, "-I", os.path.join(solo, "chapters.py"),
                            write(self.d, "t.srt", long_transcript()), "--json"],
                           capture_output=True, encoding="utf-8")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(json.loads(r.stdout)["valid"])

    def test_missing_deadair_gives_a_clear_message(self):
        solo = os.path.join(self.d, "only-chapters")
        os.makedirs(solo)
        shutil.copy(os.path.join(SKILLS, "yt-chapters", "chapters.py"), solo)
        import subprocess, sys
        r = subprocess.run([sys.executable, "-I", os.path.join(solo, "chapters.py"), "x.srt"],
                           capture_output=True, encoding="utf-8")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("deadair.py", r.stderr)


if __name__ == "__main__":
    unittest.main()
