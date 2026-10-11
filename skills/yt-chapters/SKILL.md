---
name: yt-chapters
description: >-
  Write YouTube chapters from a video transcript, validated against
  YouTube's own rules so they actually render. Use for "add YouTube
  chapters", "chapter timestamps for my video description", or "break this
  YouTube video into chapters".
license: MIT
metadata:
  maintainer: Ian Ryan Kirk
  original-author: Jake Schincariol
---

# yt-chapters

```bash
python "${CLAUDE_SKILL_DIR}/chapters.py" transcript.srt --target 8
```

`${CLAUDE_SKILL_DIR}` is this skill's folder. Use `python3` if that is what your system calls
Python (common on macOS and Linux); on Windows it is usually `python`.
It reuses the transcript parser in `yt-edit/deadair.py`, so keep the `yt-edit` folder installed next
to this one (or copy `deadair.py` into this folder).

## The rules, which are not optional

A chapter list that breaks any of these silently does not become chapters at all - the block just
sits in the description doing nothing:

- The first entry must be **00:00**.
- There must be **at least three**.
- Each must be **at least 10 seconds** long.

The tool checks all three, never aims for fewer than three, and tells you when a list is invalid rather than letting you paste it.

## Retitle every line

`chapters.py` finds the BOUNDARIES well - it scores the pauses you actually took by how much the
vocabulary shifts across them. The titles it emits are the topic words, and they are a draft. A
chapter called "Thumbnails Titles Packaging" is a placeholder. Rewrite each one as the promise of
that section, in the user's voice, three to five words.

Chapters are also a retention diagnostic: if a section cannot be named in five words, it is two
sections or it is filler.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
