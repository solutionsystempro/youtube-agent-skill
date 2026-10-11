---
name: yt-retention
description: >-
  Read a YouTube Studio audience-retention export and find where viewers
  actually leave, then say what to change. Use for "why do people stop
  watching my YouTube video", "my YouTube retention is bad", a pasted YouTube
  retention chart or CSV, or "fix the pacing of my video".
---

# yt-retention

The retention graph is the only honest feedback YouTube gives you. Almost nobody exports it.

```bash
python "${CLAUDE_SKILL_DIR}/retention.py" retention.csv --duration 600
python "${CLAUDE_SKILL_DIR}/retention.py" retention.csv --transcript transcript.srt
python "${CLAUDE_SKILL_DIR}/retention.py" retention.csv --ratio     # or --percent
```

`${CLAUDE_SKILL_DIR}` is this skill's folder. Use `python3` if that is what your system calls
Python (common on macOS and Linux); on Windows it is usually `python`.
`--transcript` reuses the parser in `yt-edit/deadair.py`, so keep `yt-edit` installed next to this
folder.

Getting the file: Studio -> a video -> Analytics -> Engagement -> the audience-retention chart ->
the download icon -> "Audience retention". The YouTube Analytics API `audienceRetention` report
(the user's own OAuth) works too: its 0-1 ratio columns are scaled to percent automatically.
The scale is read from the column header (`audienceWatchRatio` is a ratio, a `(%)` label is a
percentage). If the header says neither, pass `--ratio` or `--percent`; otherwise the tool guesses
from the values and prints a note on stderr. Either flag overrides the header.

## Three different problems

- **HOOK LEAK** - what is lost in the first 30 seconds. Under 25% is healthy. This is always the
  first thing to fix and it is always the first fifteen seconds of script, never the edit.
- **CLIFFS** - single steep drops. A cliff is a moment: a topic change with no signposting, a
  sponsor read, a long setup. With `--transcript` the tool prints what was being said there, which
  is what makes the report actionable instead of interesting.
- **SLIDE** - the steady bleed across the middle. A flat slide is pacing. The fix is cutting, not
  rewriting.

## What to hand back

Name the single biggest leak and one change for it. Not a list of five. Then, only if asked, the
rest. And if the hook leak is healthy and the slide is flat, say the video is fine and the problem
is packaging - send them to `/yt-package`.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
