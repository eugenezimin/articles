#!/bin/zsh
# render.sh — build every figure PNG in images/ from the sources in images/src/.
# Terminal captures (.txt) go through term2svg.py as Ghostty windows; diagrams are
# hand-written SVG. Every PNG comes out exactly $WIDTH pixels wide.
# Run tools/capture.sh beforehand to refresh the captures.

set -eu
root="${0:A:h:h}"
src="$root/images/src"
img="$root/images"
tools="$root/tools"
WIDTH=2400   # every figure, terminal or diagram
COLS=96      # every terminal window, so they all share one window size

term() {  # term <capture.txt> <figure name> <window title> [line ranges]
  python3 -I "$tools/term2svg.py" "$src/$1" "$src/$2.svg" \
    --title "$3" --cols "$COLS" --keep "${4:-}"
}

term autoupdate-leftovers.txt fig-01-autoupdate-leftovers "ls /Library"
term dry-run-teams.txt        fig-03-discovery            "ms-uninstall.sh --dry-run --select 1" "1-16"
term dry-run-teams.txt        fig-07-veto                 "ms-uninstall.sh --dry-run --select 1" "1,22-34"
term dry-run-all.txt          fig-08-plan                 "ms-uninstall.sh --dry-run --select all --shared all" "1,40-53,62-67,74-83,104-111"
term receipts.txt             fig-10-receipts             "pkgutil --pkgs"

for svg in "$src"/fig-*.svg; do
  rsvg-convert -w "$WIDTH" -o "$img/${${svg:t}:r}.png" "$svg"
done
for png in "$img"/fig-*.png; do
  printf '%-36s %s\n' "${png:t}" "$(sips -g pixelWidth -g pixelHeight "$png" | awk '/pixel/ {printf "%s ", $2}')"
done
