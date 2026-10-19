#!/usr/bin/env bash
# Ghost of Tsushima — generated from palette.json by src/claude.py
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
out="\033[48;2;193;18;31m\033[38;2;246;241;231m\033[1m 冥 $off\033[38;2;193;18;31m\033[48;2;42;37;35m"
out+="\033[48;2;42;37;35m\033[38;2;226;194;127m\033[1m ${model:-Claude} $off\033[38;2;42;37;35m\033[48;2;30;27;26m"
out+="\033[48;2;30;27;26m\033[38;2;236;230;220m $short $off\033[38;2;30;27;26m$off"
[[ -n "$branch" ]] && out+=" \033[38;2;130;169;209m $branch$off"
printf '%b\n' "$out"
