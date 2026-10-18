# Ghost of Tsushima Kurosawa — generated from palette.json by src/shell.py
# 冥人 — source this from ~/.zshrc (the installer adds the line for you):
#   source ~/.config/ghost-of-tsushima/ghost-of-tsushima-kurosawa.zsh
# Load it AFTER zsh-syntax-highlighting / zsh-autosuggestions if you use them.

# ---- zsh-syntax-highlighting -------------------------------------------
typeset -gA ZSH_HIGHLIGHT_STYLES
ZSH_HIGHLIGHT_STYLES[default]='fg=#e4e4e4'
ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=#f0f0f0,bold,underline'
ZSH_HIGHLIGHT_STYLES[reserved-word]='fg=#f0f0f0,bold'
ZSH_HIGHLIGHT_STYLES[alias]='fg=#dcdcdc'
ZSH_HIGHLIGHT_STYLES[suffix-alias]='fg=#dcdcdc,underline'
ZSH_HIGHLIGHT_STYLES[global-alias]='fg=#dcdcdc'
ZSH_HIGHLIGHT_STYLES[builtin]='fg=#b8b8b8'
ZSH_HIGHLIGHT_STYLES[function]='fg=#dcdcdc'
ZSH_HIGHLIGHT_STYLES[command]='fg=#dcdcdc'
ZSH_HIGHLIGHT_STYLES[precommand]='fg=#9c9c9c,italic'
ZSH_HIGHLIGHT_STYLES[commandseparator]='fg=#fafafa'
ZSH_HIGHLIGHT_STYLES[hashed-command]='fg=#b8b8b8'
ZSH_HIGHLIGHT_STYLES[autodirectory]='fg=#b0b0b0,underline'
ZSH_HIGHLIGHT_STYLES[path]='fg=#e4e4e4,underline'
ZSH_HIGHLIGHT_STYLES[path_pathseparator]='fg=#808080,underline'
ZSH_HIGHLIGHT_STYLES[path_prefix]='fg=#e4e4e4,underline'
ZSH_HIGHLIGHT_STYLES[globbing]='fg=#b0b0b0'
ZSH_HIGHLIGHT_STYLES[history-expansion]='fg=#9c9c9c'
ZSH_HIGHLIGHT_STYLES[command-substitution-delimiter]='fg=#a6a6a6'
ZSH_HIGHLIGHT_STYLES[process-substitution-delimiter]='fg=#a6a6a6'
ZSH_HIGHLIGHT_STYLES[single-hyphen-option]='fg=#b0b0b0'
ZSH_HIGHLIGHT_STYLES[double-hyphen-option]='fg=#b0b0b0'
ZSH_HIGHLIGHT_STYLES[back-quoted-argument]='fg=#c0c0c0'
ZSH_HIGHLIGHT_STYLES[single-quoted-argument]='fg=#a8a8a8,italic'
ZSH_HIGHLIGHT_STYLES[double-quoted-argument]='fg=#a8a8a8,italic'
ZSH_HIGHLIGHT_STYLES[dollar-quoted-argument]='fg=#a8a8a8'
ZSH_HIGHLIGHT_STYLES[dollar-double-quoted-argument]='fg=#c0c0c0'
ZSH_HIGHLIGHT_STYLES[back-double-quoted-argument]='fg=#c0c0c0'
ZSH_HIGHLIGHT_STYLES[assign]='fg=#c8c8c8'
ZSH_HIGHLIGHT_STYLES[redirection]='fg=#fafafa'
ZSH_HIGHLIGHT_STYLES[comment]='fg=#808080,italic'
ZSH_HIGHLIGHT_STYLES[arg0]='fg=#dcdcdc'
ZSH_HIGHLIGHT_STYLES[bracket-error]='fg=#f0f0f0,bold'
ZSH_HIGHLIGHT_STYLES[bracket-level-1]='fg=#b8b8b8'
ZSH_HIGHLIGHT_STYLES[bracket-level-2]='fg=#9c9c9c'
ZSH_HIGHLIGHT_STYLES[bracket-level-3]='fg=#b0b0b0'
ZSH_HIGHLIGHT_STYLES[cursor-matchingbracket]='fg=#0a0a0a,bg=#b8b8b8'

# ---- zsh-autosuggestions -------------------------------------------------
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=#5c5c5c,italic'

# ---- fzf -------------------------------------------------------------------
export FZF_DEFAULT_OPTS="${FZF_DEFAULT_OPTS:+$FZF_DEFAULT_OPTS }--color=bg+:#262626,bg:#121212,spinner:#fafafa,hl:#f0f0f0,fg:#c4c4c4,header:#b8b8b8,info:#b8b8b8,pointer:#fafafa,marker:#fafafa,fg+:#f5f5f5,prompt:#f0f0f0,hl+:#fafafa,border:#3a3a3a,gutter:#121212,query:#e4e4e4,label:#b8b8b8,preview-bg:#0a0a0a,separator:#262626,scrollbar:#5e5e5e --border=rounded --prompt='❯ ' --pointer='◆' --marker='✓' --separator='─' --scrollbar='│' --info=inline-right"

# ---- eza ---------------------------------------------------------------------
export EZA_COLORS="reset:di=38;2;176;176;176;1:ex=38;2;240;240;240;1:fi=38;2;228;228;228:ln=38;2;192;192;192:or=38;2;250;250;250;4:so=38;2;156;156;156:pi=38;2;184;184;184:bd=38;2;184;184;184;1:cd=38;2;184;184;184:ur=38;2;184;184;184:uw=38;2;240;240;240:ux=38;2;168;168;168:ue=38;2;168;168;168;1:gr=38;2;184;184;184:gw=38;2;240;240;240:gx=38;2;168;168;168:tr=38;2;184;184;184:tw=38;2;240;240;240:tx=38;2;168;168;168:su=38;2;250;250;250;1:sf=38;2;250;250;250:xa=38;2;128;128;128:sn=38;2;200;200;200:sb=38;2;128;128;128:df=38;2;200;200;200:ds=38;2;128;128;128:uu=38;2;166;166;166:un=38;2;250;250;250:gu=38;2;166;166;166:gn=38;2;250;250;250:da=38;2;128;128;128:in=38;2;128;128;128:bl=38;2;128;128;128:hd=38;2;184;184;184;4:lp=38;2;192;192;192:cc=38;2;250;250;250:ga=38;2;168;168;168;1:gm=38;2;184;184;184:gd=38;2;240;240;240;9:gv=38;2;176;176;176:gt=38;2;156;156;156:gi=38;2;58;58;58:xx=38;2;58;58;58:im=38;2;156;156;156:vi=38;2;156;156;156:mu=38;2;176;176;176:co=38;2;184;184;184:tm=38;2;128;128;128:bu=38;2;220;220;220;4:sc=38;2;168;168;168:*.md=38;2;200;200;200:*.lua=38;2;176;176;176:*.json=38;2;184;184;184:*.toml=38;2;184;184;184"

# ---- bat / delta / less --------------------------------------------------------
export BAT_THEME="Ghost of Tsushima Kurosawa"
export LESS_TERMCAP_md=$'\e[1;38;2;240;240;240m'
export LESS_TERMCAP_me=$'\e[0m'
export LESS_TERMCAP_us=$'\e[4;38;2;184;184;184m'
export LESS_TERMCAP_ue=$'\e[0m'
export LESS_TERMCAP_so=$'\e[38;2;245;245;245;48;2;64;64;64m'
export LESS_TERMCAP_se=$'\e[0m'

# ---- BSD ls (macOS) and GNU ls ----------------------------------------------------
export CLICOLOR=1
export LSCOLORS="exfxcxdxbxegedabagacad"

# ---- prompt ----------------------------------------------------------------------
if [[ -z "$GOT_NO_STARSHIP" ]] && command -v starship >/dev/null 2>&1; then
  export STARSHIP_CONFIG="${STARSHIP_CONFIG:-$HOME/.config/starship.toml}"
  eval "$(starship init zsh)"
fi
