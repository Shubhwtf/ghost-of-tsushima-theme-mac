#!/usr/bin/env bash
# Ghost of Tsushima Kurosawa — generated from palette.json by src/claude.py
# Claude Code status line: ~/.claude/settings.json -> "statusLine": {"type": "command", "command": "<this file>"}
# Reads the session JSON on stdin and prints:  冥  model  ~/dir   branch
input="$(cat)"
field() { printf '%s' "$input" | sed -n "s/.*\"$1\"[[:space:]]*:[[:space:]]*\"\([^\"]*\)\".*/\1/p" | head -n1; }
model="$(field display_name)"
dir="$(field current_dir)"
[[ -n "$dir" ]] || dir="$PWD"
branch="$(git -C "$dir" branch --show-current 2>/dev/null)"
short="${dir/#$HOME/\~}"
off='\033[0m'
out="\033[48;2;228;228;228m\033[38;2;10;10;10m\033[1m 冥 $off\033[38;2;228;228;228m\033[48;2;38;38;38m"
out+="\033[48;2;38;38;38m\033[38;2;220;220;220m\033[1m ${model:-Claude} $off\033[38;2;38;38;38m\033[48;2;28;28;28m"
out+="\033[48;2;28;28;28m\033[38;2;228;228;228m $short $off\033[38;2;28;28;28m$off"
[[ -n "$branch" ]] && out+=" \033[38;2;176;176;176m $branch$off"
printf '%b\n' "$out"
