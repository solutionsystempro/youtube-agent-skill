---
name: yt-viral
description: >-
  Find what is actually working in the user's niche on YouTube and rank it
  by how far each video beat its own channel, then name the formula. Use for
  "what's working on YouTube in my niche", "find outlier YouTube videos",
  "why did this YouTube video blow up", YouTube competitor research, or a
  YouTube swipe file.
---

# yt-viral

Raw view counts rank channel size, not ideas. This ranks by **multiple over each channel's own
median**, which is the only version of the question that is about the video.

```bash
python "${CLAUDE_SKILL_DIR}/swipe.py" collected.json --min 2.0
```

`${CLAUDE_SKILL_DIR}` is this skill's folder. Use `python3` if that is what your system calls
Python (common on macOS and Linux); on Windows it is usually `python`.

## Collecting the input

You need at least **four videos per channel** or a median means nothing, and the tool will skip the
channel and tell you it did. Two ways to collect them, both inside YouTube's terms:

- **The YouTube Data API v3** with the user's own API key: `channels.list` for the uploads playlist,
  `playlistItems.list` for the video ids, `videos.list?part=snippet,statistics` for titles and view
  counts. Ask for the key at run time; never write it into a file. Mind the daily quota.
- **A list the user assembles by hand** from what they have watched.

Do not scrape YouTube pages, do not use a downloader such as `yt-dlp`, and never download the videos
themselves. YouTube's terms prohibit automated collection outside the API.

```json
[{"channel":"...","title":"...","views":412000,"url":"...","duration":613}]
```

From `videos.list`, `statistics.viewCount` and `channelTitle` are read as they are; flatten
`snippet.title` (and `snippet.channelTitle`) to the top level. Never a logged-in session, never the
user's account credentials.

## Reading the output

The multiple is the signal. The formula line is a judgement about the TITLE, matched against
[the 21 formulas](../yt-script/hooks.json) - it is not a claim about why the video worked, and you
should say so when you present it.

What to hand back: the top five with their multiples, the formula each used, and the ONE structural
thing they share. Then the harder line - which of those the user could actually make this week, in
their voice, with what they have.

## The gate

Nothing here publishes. This skill writes and you publish. Every output ends in a block the user
copies, and the last line of every run is the question: **ship it, or change it?**
