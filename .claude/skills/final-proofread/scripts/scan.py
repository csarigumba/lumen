#!/usr/bin/env python3
"""Flag mechanical AI-slop candidates in a markdown post.

Usage: python3 scan.py content/posts/<post>/index.md

It only finds candidates. A human (or agent) still reads every line,
because invented details and rhythm problems can't be caught by regex.
"""
import re
import sys

BANNED = (
    "delve foster leverage utilize facilitate empower streamline robust tapestry "
    "realm beacon multifaceted meticulous intricate paramount transformative "
    "elevate embark harness testament pivotal"
).split()
EMPTY = [
    "just", "literally", "honestly", "simply", "actually", "truly",
    "fundamentally", "importantly", "crucially", "ultimately",
    "it's worth noting", "at its core", "the reality is", "the truth is",
    "in order to", "here's the thing", "what nobody tells you",
]
CHECKS = [
    ("em dash", re.compile(r"—")),
    ("binary contrast", re.compile(
        r"\b(isn't|is not|wasn't|not just|not only|doesn't|don't)\b[^.]{0,80}[.,;]\s*(it's|it is|but|a |an |the )",
        re.I)),
    ("colon reveal", re.compile(r"^[A-Z][^:.]{2,40}: [a-z]")),
    ("faux insight / throat-clearing", re.compile(
        r"\b(here's the thing|the truth is|the reality is|what nobody tells|the key point|that's the (dangerous|hard|important|real) part|let me be clear)\b",
        re.I)),
    ("puffery", re.compile(r"\b(most powerful|most important|game.?changer|life.?changing)\b", re.I)),
    ("reassurance kicker", re.compile(r"\b(and that's (okay|fine)|there's nothing wrong with)\b", re.I)),
]


def body_lines(text):
    lines = text.splitlines()
    start = 0
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start = i + 1
                break
    for n, line in enumerate(lines[start:], start=start + 1):
        s = line.strip()
        if not s or s.startswith(">") or s.startswith("![") or s.startswith("<"):
            continue
        yield n, line


def main(path):
    text = open(path, encoding="utf-8").read()
    hits = []
    for n, line in body_lines(text):
        low = line.lower()
        for name, rx in CHECKS:
            if rx.search(line):
                hits.append((n, name, line.strip()))
        for w in BANNED:
            if re.search(rf"\b{w}\w*\b", low):
                hits.append((n, f"banned word '{w}'", line.strip()))
        for w in EMPTY:
            if re.search(rf"\b{re.escape(w)}\b", low):
                hits.append((n, f"often-empty '{w}'", line.strip()))
        # short fragments (<= 4 words) used for drama, outside headers
        if not line.lstrip().startswith("#"):
            for sent in re.split(r"(?<=[.!?])\s+", line.strip()):
                words = re.findall(r"[A-Za-z']+", sent)
                if 0 < len(words) <= 4 and sent.endswith((".", "!")):
                    hits.append((n, "short fragment", sent))
        # paragraph ending in a short punchy sentence (kicker candidate)
        sents = re.split(r"(?<=[.!?])\s+", line.strip())
        if len(sents) >= 2 and not line.lstrip().startswith("#"):
            last = re.findall(r"[A-Za-z']+", sents[-1])
            if 0 < len(last) <= 9:
                hits.append((n, "possible kicker", sents[-1]))

    if not hits:
        print("No mechanical flags. Still read every line for invented details and rhythm.")
        return
    for n, name, snippet in hits:
        print(f"L{n:<4} {name:<32} {snippet[:110]}")
    print(f"\n{len(hits)} flags. Review each; not every flag is slop.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
