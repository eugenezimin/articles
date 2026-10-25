#!/usr/bin/env python3
"""term2svg.py — render captured terminal text as a Ghostty window SVG.

Usage: term2svg.py INPUT.txt OUTPUT.svg --title TITLE --cols N [--keep 1-12,30-41]

The look follows the author's Ghostty setup (~/.config/ghostty/config.ghostty):
Nordwand Mono at 13pt, background #132948, foreground #eff0eb and the custom
16-color palette, drawn inside a macOS window with a transparent drop-shadow
margin, the way a macOS window screenshot comes out.

--cols fixes the window width in terminal columns, so every figure gets the
same window. --keep selects 1-based line ranges; gaps between kept ranges are
shown as a dim "⋯" line so the reader can see the capture was trimmed.
Coloring is driven by a few line patterns that match ms-uninstall.sh output.
"""
import argparse
import re
from xml.sax.saxutils import escape

FONT = "'Nordwand Mono', Menlo, monospace"
SIZE = 13
CHAR_W = SIZE * 0.6             # Nordwand Mono advance: 600/1000 em
LINE_H = 18.5                   # Ghostty cell height at 13pt
PAD_X, PAD_Y = 16, 12           # inside the window, around the text
TITLE_H = 29                    # Ghostty's native title bar height
MARGIN_X, MARGIN_TOP, MARGIN_BOTTOM = 34, 28, 42   # shadow margin, like a window capture
RADIUS = 12

BG, TITLE_BG, TITLE_FG, FG = "#132948", "#0f2240", "#9fb0c8", "#eff0eb"
RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN = (
    "#ff8c82", "#5af78e", "#f3f99d", "#57c7ff", "#ff6ac1", "#9aedfe")
DIM = "#8796ad"                 # foreground blended into the background


def parse_keep(spec, n):
    if not spec:
        return [(1, n)]
    ranges = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        ranges.append((int(a), int(b or a)))
    return ranges


def style_line(line):
    """Return a list of (text, color, bold) spans for one line."""
    if line.startswith("$ "):
        return [("$ ", GREEN, True), (line[2:], FG, True)]
    if line == "⋯":
        return [("⋯", DIM, False)]
    if set(line.strip()) == {"-"}:
        return [(line, DIM, False)]
    if "KEPT" in line:
        head, _, tail = line.partition("KEPT")
        return [(head, FG, False), ("KEPT" + tail, YELLOW, True)]
    if "nothing you kept depends" in line:
        return [(line, GREEN, False)]
    if line.startswith("NOTE:") or "Copy them out" in line:
        return [(line, YELLOW, False)]
    if line.startswith("[dry-run]"):
        return [(line, CYAN, True)]
    if re.match(r"^  \[.*\]$", line):
        return [(line, BLUE, True)]
    if line in ("Microsoft products found", "Shared Microsoft components",
                "REMOVAL PLAN") or line.startswith("Select what"):
        return [(line, FG, True)]
    m = re.match(r"^(\s+)([\d.]+ [MG]B)(  )(.*)$", line)
    if m:  # plan row: size column + path
        return [(m.group(1), FG, False), (m.group(2), CYAN, False),
                (m.group(3), FG, False), (m.group(4), FG, False)]
    m = re.match(r"^(\s+\d+\) |\s+-- )(.*)$", line)
    if m:  # numbered menu entry
        return [(m.group(1), DIM, False), (m.group(2), FG, True)]
    if line.startswith("/") and line.endswith(":"):  # ls directory header
        return [(line, BLUE, False)]
    return [(line, FG, False)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--title", default="ghostty")
    ap.add_argument("--cols", type=int, required=True)
    ap.add_argument("--keep", default="")
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as fh:
        raw = fh.read().rstrip("\n").split("\n")

    lines, last = [], None
    for a, b in parse_keep(args.keep, len(raw)):
        if last is not None and a > last + 1:
            lines.append("⋯")
        lines.extend(raw[a - 1:b])
        last = b
    while lines and not lines[0].strip():
        lines.pop(0)

    widest = max(len(l) for l in lines)
    if widest > args.cols:
        raise SystemExit(f"{args.input}: a line is {widest} columns, window is {args.cols}")

    win_w = PAD_X * 2 + args.cols * CHAR_W
    win_h = TITLE_H + PAD_Y * 2 + LINE_H * len(lines)
    width = win_w + MARGIN_X * 2
    height = win_h + MARGIN_TOP + MARGIN_BOTTOM
    wx, wy = MARGIN_X, MARGIN_TOP

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}">',
        '<defs>',
        '<filter id="shadow" x="-20%" y="-20%" width="140%" height="150%">',
        '<feDropShadow dx="0" dy="10" stdDeviation="13" flood-color="#000" flood-opacity="0.45"/>',
        '</filter>',
        f'<clipPath id="win"><rect x="{wx}" y="{wy}" width="{win_w}" height="{win_h}" rx="{RADIUS}"/></clipPath>',
        '</defs>',
        f'<rect x="{wx}" y="{wy}" width="{win_w}" height="{win_h}" rx="{RADIUS}" fill="{BG}" filter="url(#shadow)"/>',
        f'<g clip-path="url(#win)">',
        f'<rect x="{wx}" y="{wy}" width="{win_w}" height="{TITLE_H}" fill="{TITLE_BG}"/>',
        '</g>',
        f'<rect x="{wx + 0.5}" y="{wy + 0.5}" width="{win_w - 1}" height="{win_h - 1}" rx="{RADIUS}" '
        f'fill="none" stroke="#ffffff" stroke-opacity="0.14"/>',
    ]
    for i, c in enumerate(("#ff5f57", "#febc2e", "#28c840")):
        out.append(f'<circle cx="{wx + 18 + i * 20}" cy="{wy + TITLE_H / 2}" r="6" fill="{c}"/>')
    out.append(
        f'<text x="{wx + win_w / 2}" y="{wy + TITLE_H / 2 + 4.5}" text-anchor="middle" fill="{TITLE_FG}" '
        f'font-family="-apple-system, \'Helvetica Neue\', sans-serif" font-size="13">'
        f'{escape(args.title)}</text>')

    top = wy + TITLE_H + PAD_Y
    for i, line in enumerate(lines):
        y = top + LINE_H * i + 13.5
        x = wx + PAD_X
        for text, color, bold in style_line(line):
            if text:
                weight = ' font-weight="bold"' if bold else ""
                out.append(
                    f'<text x="{x:.1f}" y="{y:.1f}" xml:space="preserve" fill="{color}" '
                    f'font-family="{FONT}" font-size="{SIZE}"{weight}>{escape(text)}</text>')
            x += len(text) * CHAR_W
    out.append("</svg>")

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
