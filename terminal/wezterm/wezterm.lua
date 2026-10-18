-- Ghost of Tsushima — generated from palette.json by src/terminals.py
-- Drop this file in ~/.config/wezterm/wezterm.lua, or copy the colour scheme table into yours.
local wezterm = require("wezterm")
local config = wezterm.config_builder and wezterm.config_builder() or {}

local scheme = {
  foreground = "#ece6dc",
  background = "#141212",
  cursor_bg = "#e0452b",
  cursor_fg = "#0b0a0a",
  cursor_border = "#e0452b",
  selection_fg = "#f6f1e7",
  selection_bg = "#8e1118",
  scrollbar_thumb = "#2a2523",
  split = "#3a3330",
  visual_bell = "#8e1118",
  compose_cursor = "#c9a45c",
  ansi = { "#1e1b1a", "#e23d43", "#7a9a5a", "#c9a45c", "#4f7ca8", "#c97a8d", "#5f9c94", "#c9c1b5" },
  brights = { "#837a73", "#e0452b", "#9db97c", "#e2c27f", "#82a9d1", "#e3a3b2", "#86c2b9", "#f6f1e7" },
  tab_bar = {
    background = "#0b0a0a",
    active_tab = { bg_color = "#c1121f", fg_color = "#f6f1e7", intensity = "Bold" },
    inactive_tab = { bg_color = "#1e1b1a", fg_color = "#a89f96" },
    inactive_tab_hover = { bg_color = "#2a2523", fg_color = "#ece6dc" },
    new_tab = { bg_color = "#0b0a0a", fg_color = "#837a73" },
    new_tab_hover = { bg_color = "#8e1118", fg_color = "#f6f1e7" },
  },
}

config.color_schemes = { ["Ghost of Tsushima"] = scheme }
config.color_scheme = "Ghost of Tsushima"
config.font = wezterm.font("JetBrainsMono Nerd Font")
config.font_size = 14.0
config.line_height = 1.1
config.window_padding = { left = 14, right = 14, top = 12, bottom = 12 }
config.window_decorations = "RESIZE|INTEGRATED_BUTTONS"
config.window_background_opacity = 0.95
config.macos_window_background_blur = 20
config.use_fancy_tab_bar = false
config.tab_bar_at_bottom = false
config.hide_tab_bar_if_only_one_tab = true
config.default_cursor_style = "BlinkingBar"
config.send_composed_key_when_left_alt_is_pressed = false
config.send_composed_key_when_right_alt_is_pressed = false
config.initial_cols = 120
config.initial_rows = 34

return config
