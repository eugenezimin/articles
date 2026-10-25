#!/bin/zsh
# capture.sh — record the real terminal sessions used as figures.
# Every command here is read-only; ms-uninstall.sh only ever runs with --dry-run.
# Output goes to tools/src/*.txt with $HOME rewritten to ~.
#
# The script lives in development-utilities; override with MS_UNINSTALL_DIR.

set -u
root="${0:A:h:h}"
out="$root/tools/src"
script_dir="${MS_UNINSTALL_DIR:-$HOME/Developer/development-utilities/ms-uninstall}"
[[ -x "$script_dir/ms-uninstall.sh" ]] || { print -u2 "ms-uninstall.sh not found in $script_dir"; exit 1; }
mkdir -p "$out"

# session <file> <command...> : append "$ command" plus its real output
session() {
  local file="$1"; shift
  local cmd
  for cmd in "$@"; do
    print -r -- "\$ $cmd" >> "$file"
    (cd "$script_dir" && eval "$cmd") 2>&1 | sed "s|$HOME|~|g" >> "$file"
  done
}

f="$out/autoupdate-leftovers.txt"; : > "$f"
session "$f" \
  "ls /Library/{LaunchAgents,LaunchDaemons,PrivilegedHelperTools} | grep -iE 'microsoft|:\$'" \
  "plutil -p /Library/LaunchAgents/com.microsoft.update.agent.plist | grep -E 'RunAt|Interval'"

f="$out/dry-run-teams.txt"; : > "$f"
session "$f" "./ms-uninstall.sh --dry-run --select 1"

f="$out/dry-run-all.txt"; : > "$f"
session "$f" "./ms-uninstall.sh --dry-run --select all --shared all"

f="$out/receipts.txt"; : > "$f"
session "$f" \
  "pkgutil --pkgs | grep -i microsoft" \
  "pkgutil --files com.microsoft.MSTeamsAudioDevice | head -1" \
  "ls /Library/Audio/Plug-Ins/HAL | grep -i teams"
