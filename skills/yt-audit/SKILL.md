---
name: yt-audit
description: >-
  Audit the user's own YouTube channel end to end - packaging, consistency,
  the first fifteen seconds, and what to fix first. Use for "audit my YouTube
  channel", "why isn't my YouTube channel growing", or when the user shares
  their own YouTube channel for review.
license: MIT
metadata:
  maintainer: Ian Ryan Kirk
  original-author: Jake Schincariol
---

# yt-audit

An audit that lists twenty problems is a way of avoiding the one that matters. This ends in ONE fix.

## Before you write

1. Read `~/.claude/youtube/voice.md` if it exists. That is the user's voice profile: how they talk
   on camera, the words they never use, who they are talking to, what they will not claim. If it
   does not exist, ask for **three of their own videos**, read or transcribe them, infer the voice,
   and write the file. A script in the wrong voice is worse than no script, because they have to
   read it out loud.
2. Never invent a number, a result or a source. If a figure would strengthen it and you do not have
   one, ask for it or write the line without it.

## Getting the data

From the user, in this order of preference: a YouTube Studio export (Content and Analytics both
download as CSV), the YouTube Data API or YouTube Analytics API with the user's own key or OAuth, or
titles and transcripts they paste. Do not scrape the channel page or drive a browser to collect it.

## What to look at, in this order

1. **The last ten titles, as a set.** Read them as a list, the way the channel page shows them. Do
   they promise different things? Run them through
   `python "${CLAUDE_SKILL_DIR}/../yt-package/title.py" titles.txt`. A channel where every title is
   the same shape has a format problem, not a title problem.
2. **The thumbnails, at feed size.** Shrink them. What survives? If three of them are unreadable at
   that size, that is the fix and nothing else matters yet.
3. **The first fifteen seconds of the three most recent.** Transcribe them and score with
   `python "${CLAUDE_SKILL_DIR}/../yt-script/hookscore.py"`. This is where most channels lose.
4. **Upload rhythm.** Not frequency - CONSISTENCY. Six videos in one week and then nothing for a
   month is worse than one a fortnight forever.
5. **The retention shape**, if they can export it. `/yt-retention`.

`${CLAUDE_SKILL_DIR}` is this skill's folder. Use `python3` if that is what your system calls
Python (common on macOS and Linux); on Windows it is usually `python`.

## What to hand back

- The single biggest fix, named, with what to do this week.
- Three things that are already working, so they do not break them. Be specific; "your energy is
  good" is not an observation.
- What NOT to do yet, and why.

Never open an audit with praise you do not mean, and never end one with a list of twenty things.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
