# Copyright (c) 2026 Ian Ryan Kirk. MIT License.
"""Shared helpers for the tool tests. Standard library only."""
import importlib.util, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, "skills")


def tool_path(skill, name):
    return os.path.join(SKILLS, skill, name)


def load_tool(skill, name):
    """Import a tool by file path, the same way the tools import each other."""
    path = tool_path(skill, name)
    spec = importlib.util.spec_from_file_location(f"test_{skill}_{name[:-3]}".replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run(skill, name, *args):
    """Run a tool the way Claude does: a fresh isolated interpreter, output captured as UTF-8."""
    return subprocess.run([sys.executable, "-I", tool_path(skill, name), *args],
                          capture_output=True, encoding="utf-8", errors="replace")


def write(directory, filename, text, newline="\n"):
    path = os.path.join(directory, filename)
    with open(path, "w", encoding="utf-8", newline=newline) as fh:
        fh.write(text)
    return path


def tmpdir(testcase):
    d = tempfile.TemporaryDirectory()
    testcase.addCleanup(d.cleanup)
    return d.name


def srt_time(seconds):
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h):02d}:{int(m):02d}:{s:06.3f}".replace(".", ",")


def make_srt(cues, newline="\n"):
    """cues: list of (start, end, text)."""
    blocks = [f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{t}\n" for i, (a, b, t) in enumerate(cues, 1)]
    return "\n".join(blocks).replace("\n", newline)
