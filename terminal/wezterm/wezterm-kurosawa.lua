-- Ghost of Tsushima Kurosawa — generated from palette.json by src/terminals.py
-- Drop this file in ~/.config/wezterm/wezterm.lua, or copy the colour scheme table into yours.
local wezterm = require("wezterm")
local config = wezterm.config_builder and wezterm.config_builder() or {}

local scheme = {
  foreground = "#e4e4e4",
  background = "#121212",
  cursor_bg = "#fafafa",
  cursor_fg = "#0a0a0a",
  cursor_border = "#fafafa",
  selection_fg = "#f5f5f5",
  selection_bg = "#404040",
  scrollbar_thumb = "#262626",
  split = "#3a3a3a",
  visual_bell = "#404040",
  compose_cursor = "#b8b8b8",
  ansi = { "#1f1f1f", "#f5f5f5", "#8f8f8f", "#c4c4c4", "#7f7f7f", "#a0a0a0", "#b2b2b2", "#d6d6d6" },
  brights = { "#6a6a6a", "#ffffff", "#a8a8a8", "#dadada", "#9a9a9a", "#bababa", "#cacaca", "#ebebeb" },
  tab_bar = {
    background = "#0a0a0a",
    active_tab = { bg_color = "#5e5e5e", fg_color = "#f5f5f5", intensity = "Bold" },
    inactive_tab = { bg_color = "#1c1c1c", fg_color = "#a6a6a6" },
    inactive_tab_hover = { bg_color = "#262626", fg_color = "#e4e4e4" },
    new_tab = { bg_color = "#0a0a0a", fg_color = "#808080" },
    new_tab_hover = { bg_color = "#404040", fg_color = "#f5f5f5" },
  },
}

config.color_schemes = { ["Ghost of Tsushima Kurosawa"] = scheme }
config.color_scheme = "Ghost of Tsushima Kurosawa"
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
