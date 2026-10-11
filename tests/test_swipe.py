import json, unittest

from helpers import load_tool, run, tmpdir, write

swipe = load_tool("yt-viral", "swipe.py")


def channel(name, views, title="An ordinary upload"):
    return [{"channel": name, "title": title, "views": v, "url": ""} for v in views]


class Swipe(unittest.TestCase):
    def setUp(self):
        self.d = tmpdir(self)

    def outliers(self, rows, *args):
        path = write(self.d, "c.json", json.dumps(rows, ensure_ascii=False))
        r = run("yt-viral", "swipe.py", path, "--json", *args)
        self.assertEqual(r.returncode, 0, r.stderr)
        return json.loads(r.stdout)

    def test_ranks_by_own_channel_median_not_raw_views(self):
        small = channel("Small", [1000, 1200, 900, 1100])
        small.append({"channel": "Small", "title": "Café 🚀 97% of creators quit", "views": 11000})
        big = channel("Big", [400000, 410000, 390000, 420000, 800000])
        out = self.outliers(small + big, "--min", "1.5")
        top = out["outliers"][0]
        self.assertEqual(top["channel"], "Small")
        self.assertEqual(top["title"], "Café 🚀 97% of creators quit")
        self.assertEqual(top["formula"], "The Statistic")
        self.assertEqual(top["multiple"], 10.0)

    def test_thin_channels_are_skipped_and_reported(self):
        out = self.outliers(channel("Thin", [5, 50, 500]))
        self.assertEqual(out["outliers"], [])
        self.assertEqual(out["skipped_thin_channels"], [["Thin", 3]])

    def test_data_api_shape_is_accepted(self):
        rows = [{"channelTitle": "Api", "title": "x", "statistics": {"viewCount": v}}
                for v in ("100", "100", "100", "1,000")]
        out = self.outliers(rows, "--min", "2")
        self.assertEqual(len(out["outliers"]), 1)
        self.assertEqual(out["outliers"][0]["views"], 1000)

    def test_empty_list(self):
        out = self.outliers([])
        self.assertEqual(out, {"outliers": [], "skipped_thin_channels": []})


if __name__ == "__main__":
    unittest.main()
