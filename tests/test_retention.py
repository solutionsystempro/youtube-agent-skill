import json, unittest

from helpers import make_srt, run, tmpdir, write


def studio_csv():
    """101 points on a percent axis: a 20-point drop at 3%, a 15-point cliff at 40%, a slow slide."""
    rows = ["Video position (%),Absolute audience retention (%)"]
    for i in range(101):
        y = 100 - i * 0.5 - (20 if i >= 3 else 0) - (15 if i >= 40 else 0)
        rows.append(f"{i},{y}")
    return "\n".join(rows) + "\n"


def api_csv():
    """The same curve as YouTube Analytics API ratios (elapsedVideoTimeRatio, audienceWatchRatio)."""
    rows = ["elapsedVideoTimeRatio,audienceWatchRatio"]
    for i in range(101):
        y = 100 - i * 0.5 - (20 if i >= 3 else 0) - (15 if i >= 40 else 0)
        rows.append(f"{i / 100},{y / 100}")
    return "\n".join(rows) + "\n"


class Retention(unittest.TestCase):
    def setUp(self):
        self.d = tmpdir(self)

    def report(self, *args):
        r = run("yt-retention", "retention.py", *args, "--json")
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        return json.loads(r.stdout)

    def test_studio_export(self):
        out = self.report(write(self.d, "r.csv", studio_csv()), "--duration", "600")
        self.assertAlmostEqual(out["hook_leak"], 22.5)          # first 30s = first 5% of 600s
        seconds = [c["at_seconds"] for c in out["cliffs"]]
        self.assertIn(12.0, seconds)                            # the 3% drop, at 18s -> starts at 12s
        self.assertIn(234.0, seconds)                           # the 40% cliff, 39% of 600s

    def test_flag_before_file(self):
        out = self.report("--duration", "600", write(self.d, "r.csv", studio_csv()))
        self.assertEqual(out["points"], 101)

    def test_api_ratios_match_studio_percentages(self):
        studio = self.report(write(self.d, "r.csv", studio_csv()), "--duration", "600")
        api = self.report(write(self.d, "a.csv", api_csv()), "--duration", "600")
        self.assertAlmostEqual(api["hook_leak"], studio["hook_leak"], places=6)
        self.assertEqual([c["at_seconds"] for c in api["cliffs"]],
                         [c["at_seconds"] for c in studio["cliffs"]])

    def test_transcript_names_what_was_said(self):
        srt = make_srt([(0, 10, "intro line"), (230, 240, "now a long sponsor read")])
        out = self.report(write(self.d, "r.csv", studio_csv()), "--duration", "600",
                          "--transcript", write(self.d, "t.srt", srt))
        self.assertIn("sponsor", " ".join(out["said"].values()))

    def test_too_few_points(self):
        r = run("yt-retention", "retention.py", write(self.d, "e.csv", "a,b\n1,2\n"))
        self.assertEqual(r.returncode, 1)


if __name__ == "__main__":
    unittest.main()
