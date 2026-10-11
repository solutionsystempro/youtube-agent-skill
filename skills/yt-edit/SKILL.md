---
name: yt-edit
description: >-
  Turn the transcript (SRT, VTT or Whisper JSON) of a raw YouTube recording
  into an edit decision list - dead air, filler cues and retakes, with
  timecodes. Use for "cut the dead space from my video", "tighten this
  recording", or any request to shorten video footage from its transcript.
license: MIT
metadata:
  maintainer: Ian Ryan Kirk
  original-author: Jake Schincariol
---

# yt-edit

An edit decision list from a timestamped transcript. It prints the cuts. You apply them.

```bash
python "${CLAUDE_SKILL_DIR}/deadair.py" transcript.srt              # srt, vtt or whisper json
python "${CLAUDE_SKILL_DIR}/deadair.py" transcript.srt --floor 0.35 --json
```

`${CLAUDE_SKILL_DIR}` is this skill's folder. Use `python3` if that is what your system calls
Python (common on macOS and Linux); on Windows it is usually `python`.

No transcript yet? Ask for one, or produce one first - `whisper`, `faster-whisper`, or the caption
track YouTube generates on the user's own unlisted upload (download it from Studio, Subtitles) all
work. Do not guess at timings.

## What it finds

- **DEAD** - gaps longer than the floor, trimmed from the MIDDLE so both sides keep a breath.
  Cutting flush against speech is what makes a tightened take sound gasping.
- **FILLER** - cues that are nothing but "um", "so yeah", "basically".
- **REPEAT** - a sentence restarted. Compared against the last cue that was actually speech, not
  the literal previous cue, because most retakes have an "um" between the two attempts.

## What it will not do

It does not touch media. It has no opinion about your B-roll. A 40% cut on the report is a 40% cut
of SPEECH, and if the video has a long silent demo in it that number is wrong - check the report
against the footage before you trust the runtime at the bottom.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
