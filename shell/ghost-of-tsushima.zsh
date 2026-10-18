# Ghost of Tsushima — generated from palette.json by src/shell.py
# 冥人 — source this from ~/.zshrc (the installer adds the line for you):
#   source ~/.config/ghost-of-tsushima/ghost-of-tsushima.zsh
# Load it AFTER zsh-syntax-highlighting / zsh-autosuggestions if you use them.

# ---- zsh-syntax-highlighting -------------------------------------------
typeset -gA ZSH_HIGHLIGHT_STYLES
ZSH_HIGHLIGHT_STYLES[default]='fg=#ece6dc'
ZSH_HIGHLIGHT_STYLES[unknown-token]='fg=#e5444a,bold'
ZSH_HIGHLIGHT_STYLES[reserved-word]='fg=#e5444a'
ZSH_HIGHLIGHT_STYLES[alias]='fg=#e2c27f'
ZSH_HIGHLIGHT_STYLES[suffix-alias]='fg=#e2c27f,underline'
ZSH_HIGHLIGHT_STYLES[global-alias]='fg=#e2c27f'
ZSH_HIGHLIGHT_STYLES[builtin]='fg=#c9a45c'
ZSH_HIGHLIGHT_STYLES[function]='fg=#e2c27f'
ZSH_HIGHLIGHT_STYLES[command]='fg=#e2c27f'
ZSH_HIGHLIGHT_STYLES[precommand]='fg=#c97a8d,italic'
ZSH_HIGHLIGHT_STYLES[commandseparator]='fg=#e34a30'
ZSH_HIGHLIGHT_STYLES[hashed-command]='fg=#c9a45c'
ZSH_HIGHLIGHT_STYLES[autodirectory]='fg=#82a9d1,underline'
ZSH_HIGHLIGHT_STYLES[path]='fg=#ece6dc,underline'
ZSH_HIGHLIGHT_STYLES[path_pathseparator]='fg=#877e77,underline'
ZSH_HIGHLIGHT_STYLES[path_prefix]='fg=#ece6dc,underline'
ZSH_HIGHLIGHT_STYLES[globbing]='fg=#82a9d1'
ZSH_HIGHLIGHT_STYLES[history-expansion]='fg=#c97a8d'
ZSH_HIGHLIGHT_STYLES[command-substitution-delimiter]='fg=#a89f96'
ZSH_HIGHLIGHT_STYLES[process-substitution-delimiter]='fg=#a89f96'
ZSH_HIGHLIGHT_STYLES[single-hyphen-option]='fg=#82a9d1'
ZSH_HIGHLIGHT_STYLES[double-hyphen-option]='fg=#82a9d1'
ZSH_HIGHLIGHT_STYLES[back-quoted-argument]='fg=#86c2b9'
ZSH_HIGHLIGHT_STYLES[single-quoted-argument]='fg=#9db97c'
ZSH_HIGHLIGHT_STYLES[double-quoted-argument]='fg=#9db97c'
ZSH_HIGHLIGHT_STYLES[dollar-quoted-argument]='fg=#9db97c'
ZSH_HIGHLIGHT_STYLES[dollar-double-quoted-argument]='fg=#86c2b9'
ZSH_HIGHLIGHT_STYLES[back-double-quoted-argument]='fg=#86c2b9'
ZSH_HIGHLIGHT_STYLES[assign]='fg=#d8c9a3'
ZSH_HIGHLIGHT_STYLES[redirection]='fg=#e34a30'
ZSH_HIGHLIGHT_STYLES[comment]='fg=#877e77,italic'
ZSH_HIGHLIGHT_STYLES[arg0]='fg=#e2c27f'
ZSH_HIGHLIGHT_STYLES[bracket-error]='fg=#e5444a,bold'
ZSH_HIGHLIGHT_STYLES[bracket-level-1]='fg=#c9a45c'
ZSH_HIGHLIGHT_STYLES[bracket-level-2]='fg=#c97a8d'
ZSH_HIGHLIGHT_STYLES[bracket-level-3]='fg=#82a9d1'
ZSH_HIGHLIGHT_STYLES[cursor-matchingbracket]='fg=#0b0a0a,bg=#c9a45c'

# ---- zsh-autosuggestions -------------------------------------------------
ZSH_AUTOSUGGEST_HIGHLIGHT_STYLE='fg=#6b625c'

# ---- fzf -------------------------------------------------------------------
export FZF_DEFAULT_OPTS="${FZF_DEFAULT_OPTS:+$FZF_DEFAULT_OPTS }--color=bg+:#2a2523,bg:#141212,spinner:#e34a30,hl:#e5444a,fg:#c9c1b5,header:#c9a45c,info:#c9a45c,pointer:#e34a30,marker:#e34a30,fg+:#f6f1e7,prompt:#e5444a,hl+:#e34a30,border:#3a3330,gutter:#141212,query:#ece6dc,label:#c9a45c,preview-bg:#0b0a0a,separator:#2a2523,scrollbar:#c1121f --border=rounded --prompt='❯ ' --pointer='◆' --marker='✓' --separator='─' --scrollbar='│' --info=inline-right"

# ---- eza ---------------------------------------------------------------------
export EZA_COLORS="reset:di=38;2;130;169;209;1:ex=38;2;229;68;74;1:fi=38;2;236;230;220:ln=38;2;134;194;185:or=38;2;227;74;48;4:so=38;2;201;122;141:pi=38;2;201;164;92:bd=38;2;201;164;92;1:cd=38;2;201;164;92:ur=38;2;201;164;92:uw=38;2;229;68;74:ux=38;2;157;185;124:ue=38;2;157;185;124;1:gr=38;2;201;164;92:gw=38;2;229;68;74:gx=38;2;157;185;124:tr=38;2;201;164;92:tw=38;2;229;68;74:tx=38;2;157;185;124:su=38;2;227;74;48;1:sf=38;2;227;74;48:xa=38;2;135;126;119:sn=38;2;216;201;163:sb=38;2;135;126;119:df=38;2;216;201;163:ds=38;2;135;126;119:uu=38;2;168;159;150:un=38;2;227;74;48:gu=38;2;168;159;150:gn=38;2;227;74;48:da=38;2;135;126;119:in=38;2;135;126;119:bl=38;2;135;126;119:hd=38;2;201;164;92;4:lp=38;2;134;194;185:cc=38;2;227;74;48:ga=38;2;157;185;124:gm=38;2;201;164;92:gd=38;2;229;68;74:gv=38;2;130;169;209:gt=38;2;201;122;141:gi=38;2;58;51;48:xx=38;2;58;51;48:im=38;2;201;122;141:vi=38;2;201;122;141:mu=38;2;130;169;209:co=38;2;201;164;92:tm=38;2;135;126;119:bu=38;2;226;194;127;4:sc=38;2;157;185;124:*.md=38;2;216;201;163:*.lua=38;2;130;169;209:*.json=38;2;201;164;92:*.toml=38;2;201;164;92"

# ---- bat / delta / less --------------------------------------------------------
export BAT_THEME="Ghost of Tsushima"
export LESS_TERMCAP_md=$'\e[1;38;2;229;68;74m'
export LESS_TERMCAP_me=$'\e[0m'
export LESS_TERMCAP_us=$'\e[4;38;2;201;164;92m'
export LESS_TERMCAP_ue=$'\e[0m'
export LESS_TERMCAP_so=$'\e[38;2;246;241;231;48;2;142;17;24m'
export LESS_TERMCAP_se=$'\e[0m'

# ---- BSD ls (macOS) and GNU ls ----------------------------------------------------
export CLICOLOR=1
export LSCOLORS="exfxcxdxbxegedabagacad"

# ---- prompt ----------------------------------------------------------------------
if [[ -z "$GOT_NO_STARSHIP" ]] && command -v starship >/dev/null 2>&1; then
  export STARSHIP_CONFIG="${STARSHIP_CONFIG:-$HOME/.config/starship.toml}"
  eval "$(starship init zsh)"
fi
