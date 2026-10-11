#!/usr/bin/env python3
"""retention.py - read a YouTube Studio audience-retention export and find the leaks.

    python retention.py retention.csv
    python retention.py retention.csv --transcript transcript.srt   # names what was said at each drop
    python retention.py retention.csv --json
    python retention.py retention.csv --ratio      # values are 0-1 API ratios (--percent: already %)

Get the file from Studio: Analytics -> a video -> Engagement -> the audience-retention chart ->
the download icon -> "Audience retention". Two columns, a position (percent or seconds) and a
percentage still watching. A YouTube Analytics API audienceRetention report also works: its
elapsedVideoTimeRatio and audienceWatchRatio columns are 0-1 ratios and are scaled to percent.
The scale comes from the column header. --ratio or --percent overrides it; with neither, the values
decide and a note goes to stderr.

It reports three things, because they are three different problems with three different fixes:
  HOOK LEAK    what you lost in the first 30 seconds
  CLIFFS       single steep drops - a specific moment people left at
  SLIDE        the steady bleed rate across the flat middle

With --transcript it prints what you were saying at each cliff, which is the only version of this
report you can act on without scrubbing the video yourself.
"""
import csv, importlib.util, json, os, re, sys

def load_csv(path):
    """Returns the (position, retention) rows and the header labels above those two columns."""
    rows, header, labels = [], [], None
    with open(path, newline="", encoding="utf-8-sig", errors="replace") as fh:
        for r in csv.reader(fh):
            nums = []
            for c in r:
                c = c.strip().replace("%", "").replace(",", "")
                try: nums.append(float(c))
                except ValueError: nums.append(None)
            idx = [i for i, n in enumerate(nums) if n is not None]
            if len(idx) < 2:
                if not rows: header = r
                continue
            if labels is None: labels = [header[i] if i < len(header) else "" for i in idx[:2]]
            rows.append((nums[idx[0]], nums[idx[1]]))
    return rows, labels or ["", ""]

RATIO_COLUMNS = ("audiencewatchratio", "relativeretentionperformance", "elapsedvideotimeratio")

def column_kind(label):
    """'ratio' for YouTube Analytics API columns, 'percent' for Studio's labelled percentages,
    None when the header does not say."""
    low = label.strip().lower()
    if any(k in low for k in RATIO_COLUMNS): return "ratio"
    if "%" in low or "percent" in low: return "percent"
    return None

def to_percent(rows, labels=("", ""), force=None):
    """Studio exports percentages; the Analytics API returns 0-1 ratios. Scale ratios up so the
    thresholds below (25% hook leak, 0.8% cliffs) mean the same thing for both. Order of authority:
    the --ratio / --percent flag, then the column header, then (with a stderr note) the values."""
    xs = [r[0] for r in rows]; ys = [r[1] for r in rows]
    kx = force or column_kind(labels[0]); ky = force or column_kind(labels[1])
    if kx == "ratio" or (kx is None and max(xs) <= 1.0): xs = [x * 100 for x in xs]
    if ky is None:
        ky = "ratio" if max(ys) <= 2.0 else "percent"
        print(f"note: retention scale guessed from the values ({ky}); pass --ratio or --percent "
              "if that is wrong", file=sys.stderr)
    if ky == "ratio": ys = [y * 100 for y in ys]
    return list(zip(xs, ys))

def load_cues(path):
    """The transcript parser is yt-edit/deadair.py. Loaded by explicit path so it works from the
    plugin cache, ~/.claude/skills, or with deadair.py copied into this folder."""
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (os.path.join(here, "..", "yt-edit", "deadair.py"), os.path.join(here, "deadair.py")):
        if os.path.exists(p):
            spec = importlib.util.spec_from_file_location("yt_deadair", p)
            mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
            return mod.load(path)
    sys.exit("--transcript needs yt-edit/deadair.py. Install the yt-edit folder next to yt-retention.")

def main():
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    a = sys.argv[1:]
    as_json = "--json" in a; a = [x for x in a if x != "--json"]
    if "--ratio" in a and "--percent" in a: sys.exit("pass --ratio or --percent, not both")
    force = "ratio" if "--ratio" in a else "percent" if "--percent" in a else None
    tr = a[a.index("--transcript") + 1] if "--transcript" in a else None
    values = {i + 1 for i, x in enumerate(a) if x in ("--transcript", "--duration")}
    files = [x for i, x in enumerate(a) if i not in values and not x.startswith("--")]
    if not files or not os.path.exists(files[0]): print(__doc__); sys.exit(1)
    rows, labels = load_csv(files[0])
    if len(rows) < 8: print("could not read at least 8 data points from that csv"); sys.exit(1)
    rows = to_percent(rows, labels, force)
    xs = [r[0] for r in rows]; ys = [r[1] for r in rows]
    pct_axis = max(xs) <= 100.5
    dur = None
    if "--duration" in a: dur = float(a[a.index("--duration") + 1])
    def at(x): return (x / 100.0 * dur) if (pct_axis and dur) else x
    start = ys[0] or 100.0
    # HOOK: the first 30 seconds, or the first 10% when the axis is a percentage and we have no duration
    cutoff = 30.0 if not pct_axis else (30.0 / dur * 100 if dur else 10.0)
    hook_end = min((y for x, y in rows if x <= cutoff), default=start)
    hook_leak = start - hook_end
    drops = []
    for i in range(1, len(rows)):
        d = ys[i - 1] - ys[i]
        span = xs[i] - xs[i - 1] or 1
        drops.append((d / span, xs[i - 1], xs[i], d))
    drops.sort(reverse=True)
    cliffs = [{"from": round(a1, 2), "to": round(b1, 2), "lost": round(d, 2),
               "at_seconds": round(at(a1), 1) if (not pct_axis or dur) else None}
              for _, a1, b1, d in drops[:5] if d > 0.8]
    mid = [d for d, x0, _, _ in [(r[0], r[1], r[2], r[3]) for r in drops] if x0 > cutoff]
    slide = sum(mid) / len(mid) if mid else 0
    said = {}
    if tr and os.path.exists(tr):
        cues = load_cues(tr)
        for c in cliffs:
            if c["at_seconds"] is None: continue
            t = c["at_seconds"]
            near = [q[2] for q in cues if q[0] <= t + 4 and q[1] >= t - 4]
            said[str(c["from"])] = " ".join(near)[:140]
    out = {"points": len(rows), "start": start, "hook_leak": round(hook_leak, 2),
           "end": ys[-1], "cliffs": cliffs, "slide_per_unit": round(slide, 3), "said": said}
    if as_json: print(json.dumps(out, indent=1)); return
    print(f"\n  {files[0]}   {len(rows)} points   {ys[0]:.1f}% -> {ys[-1]:.1f}%\n")
    verdict = "healthy" if hook_leak < 25 else "leaking" if hook_leak < 40 else "severe"
    print(f"  HOOK LEAK   {hook_leak:.1f}% lost in the opening   [{verdict}]")
    print(f"              under 25 is healthy for this length. Fix the first line before anything else.\n")
    print("  CLIFFS      the moments people actually left")
    for c in cliffs:
        where = f"{c['at_seconds']:.0f}s" if c["at_seconds"] is not None else f"{c['from']}"
        print(f"    -{c['lost']:5.1f}%  at {where:>8}" + (f"   \"{said.get(str(c['from']),'')}\"" if said else ""))
    if not cliffs: print("    none steeper than 0.8% - the loss is all slide, not moments")
    print(f"\n  SLIDE       {slide:.3f}% per unit across the middle")
    print( "              a flat slide is pacing, not content. Cut the middle, do not rewrite it.\n")

if __name__ == "__main__":
    main()
