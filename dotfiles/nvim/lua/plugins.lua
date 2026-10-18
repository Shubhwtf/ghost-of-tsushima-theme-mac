-- Every Nerd Font glyph is written as a "\u{....}" escape so no editor or tool can strip it.
return {
  {
    "nvim-telescope/telescope.nvim",
    version = "*",
    cmd = "Telescope",
    dependencies = {
      "nvim-lua/plenary.nvim",
      { "nvim-telescope/telescope-fzf-native.nvim", build = "make" },
    },
    config = function()
      require("telescope").setup({
        defaults = {
          layout_strategy = "horizontal",
          sorting_strategy = "ascending",
          layout_config = { prompt_position = "top", width = 0.9, height = 0.85, preview_width = 0.58 },
          prompt_prefix = " \u{f002}  ",
          selection_caret = "\u{25c6} ",
          entry_prefix = "  ",
          borderchars = { " ", " ", " ", " ", " ", " ", " ", " " },
        },
      })
      pcall(require("telescope").load_extension, "fzf")
    end,
  },
  {
    -- the main branch is the rewrite for nvim 0.11+; parsers need the tree-sitter CLI
    "nvim-treesitter/nvim-treesitter",
    branch = "main",
    lazy = false,
    build = ":TSUpdate",
    config = function()
      require("nvim-treesitter").install({
        "c", "lua", "javascript", "typescript", "tsx", "python", "rust", "go", "bash", "swift",
        "json", "yaml", "toml", "html", "css", "markdown", "markdown_inline", "vim", "vimdoc", "query",
      })
      vim.api.nvim_create_autocmd("FileType", {
        callback = function(ev)
          if pcall(vim.treesitter.start, ev.buf) then
            vim.bo[ev.buf].indentexpr = "v:lua.require'nvim-treesitter'.indentexpr()"
          end
        end,
      })
    end,
  },
  {
    "nvim-neo-tree/neo-tree.nvim",
    branch = "v3.x",
    dependencies = {
      "nvim-lua/plenary.nvim",
      "MunifTanjim/nui.nvim",
      "nvim-tree/nvim-web-devicons",
    },
    lazy = false,
    opts = {
      close_if_last_window = true,
      popup_border_style = "rounded",
      default_component_configs = {
        indent = { with_markers = true, indent_marker = "│", last_indent_marker = "└" },
        icon = { folder_closed = "\u{f07b}", folder_open = "\u{f07c}", folder_empty = "\u{f114}" },
        git_status = { symbols = { added = "+", modified = "\u{25c6}", deleted = "\u{2716}", untracked = "\u{25c7}" } },
      },
      window = { width = 32 },
      filesystem = { follow_current_file = { enabled = true } },
    },
  },
  {
    "nvim-lualine/lualine.nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    opts = {
      options = {
        theme = "ghost-of-tsushima",
        component_separators = { left = "\u{e0b9}", right = "\u{e0bb}" },
        section_separators = { left = "\u{e0b8}", right = "\u{e0be}" },
        globalstatus = true,
        disabled_filetypes = { statusline = { "alpha" } },
      },
      sections = {
        lualine_a = { { "mode", icon = "冥" } },
        lualine_b = { { "branch", icon = "\u{f418}" }, "diff" },
        lualine_c = { { "filename", path = 1, symbols = { modified = " \u{25cf}", readonly = " \u{f023}" } } },
        lualine_x = { "diagnostics", "filetype" },
        lualine_y = { "progress" },
        lualine_z = { { "location", icon = "\u{f04e5}" } },
      },
    },
  },
  {
    "akinsho/bufferline.nvim",
    version = "*",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    event = "VeryLazy",
    opts = function()
      local c = require("got.palette")
      return {
        options = {
          separator_style = "slant",
          always_show_bufferline = false,
          diagnostics = "nvim_lsp",
          show_close_icon = false,
          modified_icon = "\u{25cf}",
          offsets = { { filetype = "neo-tree", text = "\u{25c6} 冥人", highlight = "NeoTreeRootName" } },
        },
        highlights = {
          fill = { bg = c.ink },
          background = { fg = c.smoke, bg = c.ash },
          buffer_visible = { fg = c.mist, bg = c.ash },
          buffer_selected = { fg = c.paper_hi, bg = c.charcoal, bold = true, italic = false },
          separator = { fg = c.ink, bg = c.ash },
          separator_selected = { fg = c.ink, bg = c.charcoal },
          separator_visible = { fg = c.ink, bg = c.ash },
          indicator_selected = { fg = c.lacquer, bg = c.charcoal },
          modified = { fg = c.gold, bg = c.ash },
          modified_selected = { fg = c.gold, bg = c.charcoal },
          close_button = { fg = c.smoke, bg = c.ash },
          close_button_selected = { fg = c.crimson, bg = c.charcoal },
        },
      }
    end,
  },
  {
    "goolord/alpha-nvim",
    dependencies = { "nvim-tree/nvim-web-devicons" },
    config = function()
      local alpha = require("alpha")
      local dash = require("alpha.themes.dashboard")
      local art = require("got.enso")
      dash.section.header = {
        type = "group",
        val = {
          { type = "text", val = art.lines, opts = { position = "center", hl = art.hl } },
          { type = "padding", val = 1 },
          { type = "text", val = "冥   人", opts = { position = "center", hl = "AlphaKanji" } },
          { type = "text", val = "G H O S T   O F   T S U S H I M A", opts = { position = "center", hl = "AlphaMotto" } },
        },
      }
      local function btn(key, icon, label, cmd)
        local b = dash.button(key, icon .. "  " .. label, cmd)
        b.opts.hl = "AlphaButtons"
        b.opts.hl_shortcut = "AlphaShortcut"
        return b
      end
      dash.section.buttons.val = {
        btn("f", "\u{f002}", "Find file", "<cmd>Telescope find_files<CR>"),
        btn("r", "\u{f1da}", "Recent files", "<cmd>Telescope oldfiles<CR>"),
        btn("g", "\u{f15c}", "Grep", "<cmd>Telescope live_grep<CR>"),
        btn("c", "\u{f013}", "Config", "<cmd>e $MYVIMRC<CR>"),
        btn("l", "\u{f0332}", "Lazy", "<cmd>Lazy<CR>"),
        btn("q", "\u{f011}", "Quit", "<cmd>qa<CR>"),
      }
      local mottos = {
        "The wind will guide you.",
        "One cut. One commit.",
        "Ink dries. The code remains.",
        "Strike from the shadows, ship in the light.",
        "A clean diff is its own honor.",
      }
      math.randomseed(os.time())
      dash.section.footer.val = "\u{2014} " .. mottos[math.random(#mottos)]
      dash.section.footer.opts.hl = "AlphaFooter"
      dash.config.layout = {
        { type = "padding", val = 1 },
        dash.section.header,
        { type = "padding", val = 2 },
        dash.section.buttons,
        { type = "padding", val = 1 },
        dash.section.footer,
      }
      alpha.setup(dash.config)
    end,
  },
  { "lewis6991/gitsigns.nvim", event = "BufReadPre", opts = { current_line_blame = false } },
  {
    "folke/which-key.nvim",
    event = "VeryLazy",
    opts = { preset = "modern", win = { border = "rounded" } },
  },
  {
    "lukas-reineke/indent-blankline.nvim",
    main = "ibl",
    event = "BufReadPost",
    opts = { indent = { char = "│" }, scope = { enabled = true, show_start = false, show_end = false } },
  },
  { "windwp/nvim-autopairs", event = "InsertEnter", opts = {} },
}
