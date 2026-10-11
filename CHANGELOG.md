# Changelog

## 1.1.0

Modifications by Ian Ryan Kirk to the original 1.0.0 by Jake Schincariol. Same eleven skills, same
six tools, same rules. The changes are fixes, tests and tighter instructions.

### Tool fixes

- `deadair.py`: a Whisper JSON file that is a bare list of segments crashed. A transcript with zero
  duration crashed on the percentage. VTT cue identifiers, NOTE blocks and `<c>` / `<i>` / word-timing
  tags leaked into the cue text. A spoken line made only of digits ("2024") was dropped. A UTF-8 BOM
  and an upper-case `.JSON` extension are now handled.
- `chapters.py`: draft titles changed order between runs when two words tied. `--target` below 3 is
  raised to 3, since YouTube ignores a list shorter than that. The shared parser is loaded by explicit
  path, with a clear message if `yt-edit/deadair.py` is missing.
- `retention.py`: `--duration 600 file.csv` (flag before the file) read `600` as the file. A YouTube
  Analytics API `audienceRetention` export (0-1 ratios) is now scaled to percent instead of being
  read as a near-zero curve. Same explicit-path loading of the shared parser.
- `retention.py`: the ratio-or-percent decision came from the values alone, so a Studio percentage
  export that stayed at or below 2% was scaled 100x. The column header now decides
  (`audienceWatchRatio`, `relativeRetentionPerformance` and `elapsedVideoTimeRatio` are ratios, a
  `%` or "percent" label is a percentage). New `--ratio` and `--percent` flags override it. The value
  guess is only a last resort and prints a note on stderr.
- `title.py`: `--thumb "..." titles.txt` (flag before the file) printed the help instead of running.
  The thumbnail word check now flags a fourth word, matching the documented three-word ceiling.
  An empty titles file is an error, not silence.
- `hookscore.py`: a missing input file exited 0. An empty file is now an error.
- `swipe.py`: accepts YouTube Data API field names (`statistics.viewCount` as a string,
  `channelTitle`) alongside `views` and `channel`.
- All tools read files as UTF-8 and write UTF-8 output. On Windows they previously read with the
  system code page (titles with emoji came through as mojibake) and could crash printing them.

### Tests

- New `tests/` folder: standard-library `unittest`, no dependencies, covering every tool.
  Run `python -m unittest discover -s tests -v`.

### Skill instructions

- Trigger descriptions name YouTube and the specific job, so they no longer fire on generic requests
  such as "edit this", "title ideas", "plan my week" or "SEO".
- Tool commands use `python "${CLAUDE_SKILL_DIR}/tool.py"`, which works from the plugin cache and from
  any working directory. A note covers `python3` on macOS and Linux.
- `/yt-viral` collects through the YouTube Data API with the user's own key, or a hand-built list.
  The `yt-dlp` and public-page suggestions are gone.
- `/yt-comment` states that replies are drafts only and are never posted, hearted or pinned on the
  user's behalf.
- `/yt-audit`, `/yt-retention`, `/yt-edit` and `/yt-shorts` point to Studio exports and the official
  APIs first, and to the user's own videos.

### Packaging

- Version 1.1.0 in `plugin.json` and `marketplace.json`.
- LICENSE keeps the original copyright and adds a line for the modifications.
- README: Windows install steps, a test command, and credit to the original.
