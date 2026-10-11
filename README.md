# The YouTube agent skill

Eleven Claude skills that run a YouTube channel. Free, MIT, no signup, nothing to connect. An API
key is optional and only `/yt-viral` uses one.

Based on the original by Jake Schincariol:
[Jakeschincariol/youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill).
This is version 1.1.0 with fixes, tests and tighter instructions. See
[What changed from the original](#what-changed-from-the-original).

One of them writes your script off 21 hook formulas and scores the hook before you waste a take on
it. One lints the title and the thumbnail as a single pairing, because writing them separately is
why half of your click surface says the same thing twice. One reads your audience-retention export
and tells you the exact second people left and what you were saying when they did. One turns a
transcript into an edit decision list. One finds the Shorts already hiding inside a long video. One
goes and finds what is working in your niche and ranks it by how far each video beat its own
channel, not by how big the channel is.

**Nothing gets published until you do it.** These skills write. You upload.

## Install

Paste this into Claude:

```
https://github.com/Jakeschincariol/youtube-agent-skill

Install this skill, then confirm /yt-script works.
```

Or do it yourself, in Claude Code:

```bash
# macOS, Linux, or Git Bash on Windows
git clone https://github.com/Jakeschincariol/youtube-agent-skill.git
mkdir -p ~/.claude/skills
cp -r youtube-agent-skill/skills/yt-* ~/.claude/skills/
```

```powershell
# Windows PowerShell
git clone https://github.com/Jakeschincariol/youtube-agent-skill.git
New-Item -ItemType Directory -Force "$HOME\.claude\skills" | Out-Null
Copy-Item -Recurse youtube-agent-skill\skills\yt-* "$HOME\.claude\skills\"
```

Copy all eleven folders together. `yt-chapters` and `yt-retention` reuse the transcript parser in
`yt-edit`, and `yt-viral` reads the formulas in `yt-script`.

Or as a plugin:

```
/plugin marketplace add Jakeschincariol/youtube-agent-skill
/plugin install youtube-agent
```

Project-local instead of global: copy the same folders into your repo's `.claude/skills/`. No Claude
Code at all? Paste any single `SKILL.md` at the top of a chat and it runs as a mode. You lose the six
Python tools, which is most of the point of `/yt-script`, `/yt-retention` and `/yt-edit`, but the
rest works.

Then spend ten minutes on [`templates/voice.md`](templates/voice.md). Copy it to
`~/.claude/youtube/voice.md` (on Windows, `%USERPROFILE%\.claude\youtube\voice.md`) and fill it in, or send Claude three of your own videos and say "write
my voice.md from these". Every skill reads that file. It matters more here than anywhere else,
because you have to say the words out loud.

## The eleven

| command | what it does |
| --- | --- |
| `/yt-script` | One idea into a script. Five hooks off [21 formulas](skills/yt-script/hooks.json), scored, then the spoken script with the retention beats marked. |
| `/yt-package` | Title and thumbnail as one pairing, linted for truncation, duplication and vagueness. |
| `/yt-edit` | A transcript into an edit decision list: dead air, filler cues, retakes, with timecodes. |
| `/yt-comment` | The comment section triaged into four piles, then replies in your voice. Says which one to pin. |
| `/yt-plan` | A week that fits the hours you actually have. One anchor, one cheap one, three Shorts. |
| `/yt-viral` | What is working in your niche, ranked by multiple over each channel's own median. |
| `/yt-retention` | Your retention export read properly: hook leak, the cliffs, the slide, and what to change. |
| `/yt-shorts` | The Shorts already inside a long video, with a new first line written for each. |
| `/yt-seo` | The description, the tags that are worth having, and the three queries this should win. |
| `/yt-chapters` | Chapters from a transcript, validated against YouTube's own rules so they render. |
| `/yt-audit` | The whole channel, ending in ONE fix rather than twenty. |

## The six tools

Every one of these runs on a clean Python 3 with no dependencies and no network access. They are
the reason the skills are not just prompts.

```bash
python skills/yt-script/hookscore.py --hook "one line"        # 5-property hook panel
python skills/yt-package/title.py --title "..." --thumb "..." # title + thumbnail linter
python skills/yt-edit/deadair.py transcript.srt               # edit decision list
python skills/yt-chapters/chapters.py transcript.srt          # validated chapters
python skills/yt-retention/retention.py retention.csv         # where they left, and why
python skills/yt-viral/swipe.py collected.json --min 2.0      # outliers by own-channel multiple
```

On macOS and Linux the command may be `python3`. Inside Claude Code the skills call the tools by
their own folder (`${CLAUDE_SKILL_DIR}`), so it does not matter where you run Claude from.

To check the tools on your machine, from the repo root:

```bash
python -m unittest discover -s tests -v
```

## The fine print

The part most packs leave out.

**It does not publish.** YouTube's Data API would allow it with your own OAuth, which makes this
pack different from the LinkedIn and Instagram ones, where posting is not available at all. It is
still not built here: every skill ends in a block you copy and a question: ship it, or change it?
Anything that claims to run your channel unattended should be read with that distinction in mind.

**`hookscore.py` is a heuristic, not a predictor.** The panel was built and calibrated against 74
real short-form hooks (the first 15 seconds of auto-captions, top-8 and bottom-8 by views across
five channels). It separates deliberately bad hooks from real ones well. It separates a given
creator's hits from their own misses barely at all. A low score is a reason to look again; a high
score is not a promise.

**The formula classifier is about the words, not the result.** When `/yt-viral` says a title used
The Statistic, that is a judgement about the title you can see, not a claim about why the video got
its views.

**`/yt-viral` reads, it does not scrape.** It collects through the YouTube Data API with your own
key, or from a list you build by hand. No scrapers, no downloaders, no logged-in sessions. YouTube's
terms prohibit automated collection outside the API. For the same reason `/yt-comment` drafts
replies and never posts them.

**Tags barely matter** and this pack says so instead of selling you a tag generator.

**Nothing invents a number.** If a skill wants a figure it does not have, it asks you for it or
writes the line without it.

## What changed from the original

Version 1.1.0 fixes bugs found by running each tool on real inputs (Windows encoding, VTT cue ids,
Whisper JSON lists, argument order, chapter edge cases), adds a test suite, narrows the skill
triggers so they only fire on YouTube work, and moves data collection to official exports and APIs.
The full list is in [CHANGELOG.md](CHANGELOG.md).

## Licence

MIT. Use it, change it, ship it. Original work copyright (c) 2026 Jake Schincariol, modifications
copyright (c) 2026 Ian Ryan Kirk. See [LICENSE](LICENSE).
