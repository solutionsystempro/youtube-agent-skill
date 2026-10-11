import json, unittest

from helpers import load_tool, make_srt, run, tmpdir, write

deadair = load_tool("yt-edit", "deadair.py")


class ParseTimestamps(unittest.TestCase):
    def test_srt_and_vtt_forms(self):
        self.assertAlmostEqual(deadair.parse_ts("00:00:01,500"), 1.5)
        self.assertAlmostEqual(deadair.parse_ts("00:01.250"), 1.25)

    def test_hours(self):
        self.assertAlmostEqual(deadair.parse_ts("01:02:03,004"), 3723.004)
        self.assertAlmostEqual(deadair.parse_ts("12:00:00.000"), 43200.0)


class LoadTranscripts(unittest.TestCase):
    def setUp(self):
        self.d = tmpdir(self)

    def test_srt_with_crlf_bom_and_unicode(self):
        text = "﻿" + make_srt([(0, 2, "café ✨ first"), (2.5, 4, "second line")], newline="\r\n")
        cues = deadair.load(write(self.d, "a.srt", text, newline=""))
        self.assertEqual(cues, [(0.0, 2.0, "café ✨ first"), (2.5, 4.0, "second line")])

    def test_vtt_cue_ids_tags_and_header_stay_out_of_text(self):
        vtt = ("WEBVTT\nKind: captions\nLanguage: en\n\nNOTE written by hand\n\n"
               "intro\n00:00.000 --> 00:04.000 align:start position:0%\n"
               "<00:00:00.500><c>hello</c><00:00:01.000><c> there</c>\n\n"
               "second\n00:05.000 --> 00:08.000\n<i>world</i> again\n")
        cues = deadair.load(write(self.d, "a.vtt", vtt))
        self.assertEqual(cues, [(0.0, 4.0, "hello there"), (5.0, 8.0, "world again")])

    def test_numeric_spoken_line_is_kept(self):
        cues = deadair.load(write(self.d, "n.srt", make_srt([(0, 1, "2024")])))
        self.assertEqual(cues, [(0.0, 1.0, "2024")])

    def test_whisper_json_dict_and_bare_list(self):
        segs = [{"start": 0, "end": 1, "text": " hi "}, {"start": 2, "end": 3, "text": "there"}]
        as_dict = deadair.load(write(self.d, "a.json", json.dumps({"segments": segs})))
        as_list = deadair.load(write(self.d, "b.JSON", json.dumps(segs)))
        self.assertEqual(as_dict, [(0.0, 1.0, "hi"), (2.0, 3.0, "there")])
        self.assertEqual(as_list, as_dict)


class EditDecisionList(unittest.TestCase):
    def setUp(self):
        self.d = tmpdir(self)

    def test_finds_dead_filler_and_repeat(self):
        srt = make_srt([
            (0.0, 2.0, "So today we look at thumbnails"),
            (2.1, 2.6, "um"),
            (2.7, 5.0, "So today we look at thumbnail design"),
            (7.0, 9.0, "Contrast matters more than colour"),
        ])
        r = run("yt-edit", "deadair.py", write(self.d, "t.srt", srt), "--json")
        self.assertEqual(r.returncode, 0, r.stderr)
        kinds = [c["kind"] for c in json.loads(r.stdout)["cuts"]]
        self.assertEqual(kinds, ["REPEAT", "FILLER", "DEAD"])
        dead = json.loads(r.stdout)["cuts"][-1]
        self.assertAlmostEqual(dead["start"], 5.225)  # trimmed from the middle, half the floor kept
        self.assertAlmostEqual(dead["end"], 6.775)

    def test_zero_length_transcript_does_not_crash(self):
        r = run("yt-edit", "deadair.py", write(self.d, "z.srt", make_srt([(0, 0, "hi")])))
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("0.0% shorter", r.stdout)

    def test_empty_file_is_a_clear_error(self):
        r = run("yt-edit", "deadair.py", write(self.d, "e.srt", ""))
        self.assertEqual(r.returncode, 1)
        self.assertIn("no cues found", r.stdout)


if __name__ == "__main__":
    unittest.main()
