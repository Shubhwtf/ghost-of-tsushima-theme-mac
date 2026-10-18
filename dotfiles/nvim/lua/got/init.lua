-- Ghost of Tsushima colorscheme for Neovim
-- https://github.com/Shubhwtf/ghost-of-tsushima-theme-mac
-- ink, washi paper, lacquer red and gold leaf

local M = {}

M.palette = require("got.palette")
M.config = { transparent = false, italic_comments = true }

function M.setup(opts)
  M.config = vim.tbl_deep_extend("force", M.config, opts or {})
end

local function groups(c, cfg)
  local bg = cfg.transparent and "NONE" or c.charcoal
  local float = cfg.transparent and "NONE" or c.ash
  return {
    -- editor -------------------------------------------------------------
    Normal = { fg = c.paper, bg = bg },
    NormalNC = { fg = c.paper, bg = bg },
    NormalFloat = { fg = c.paper, bg = float },
    FloatBorder = { fg = c.slate, bg = float },
    FloatTitle = { fg = c.paper_hi, bg = c.lacquer, bold = true },
    FloatFooter = { fg = c.smoke, bg = float },
    Cursor = { fg = c.ink, bg = c.vermilion },
    lCursor = { fg = c.ink, bg = c.vermilion },
    CursorLine = { bg = c.ash },
    CursorColumn = { bg = c.ash },
    CursorLineNr = { fg = c.vermilion, bold = true },
    LineNr = { fg = c.slate },
    LineNrAbove = { fg = c.slate },
    LineNrBelow = { fg = c.slate },
    SignColumn = { bg = bg },
    ColorColumn = { bg = c.ash },
    Conceal = { fg = c.smoke },
    VertSplit = { fg = c.stone },
    WinSeparator = { fg = c.stone },
    Folded = { fg = c.mist, bg = c.stone },
    FoldColumn = { fg = c.slate },
    EndOfBuffer = { fg = bg },
    NonText = { fg = c.slate },
    Whitespace = { fg = c.stone },
    SpecialKey = { fg = c.slate },
    Visual = { bg = c.blood },
    VisualNOS = { bg = c.blood },
    Search = { fg = c.ink, bg = c.gold },
    IncSearch = { fg = c.paper_hi, bg = c.lacquer, bold = true },
    CurSearch = { fg = c.paper_hi, bg = c.lacquer, bold = true },
    Substitute = { fg = c.paper_hi, bg = c.crimson },
    MatchParen = { fg = c.gold_hi, bg = c.stone, bold = true },
    Pmenu = { fg = c.paper, bg = c.ash },
    PmenuSel = { fg = c.paper_hi, bg = c.lacquer, bold = true },
    PmenuSbar = { bg = c.stone },
    PmenuThumb = { bg = c.lacquer },
    PmenuKind = { fg = c.sky, bg = c.ash },
    PmenuExtra = { fg = c.smoke, bg = c.ash },
    StatusLine = { fg = c.mist, bg = c.ash },
    StatusLineNC = { fg = c.smoke, bg = c.ash },
    TabLine = { fg = c.smoke, bg = c.ash },
    TabLineFill = { bg = c.ink },
    TabLineSel = { fg = c.paper_hi, bg = c.lacquer, bold = true },
    WinBar = { fg = c.mist, bg = bg },
    WinBarNC = { fg = c.smoke, bg = bg },
    Title = { fg = c.gold, bold = true },
    Directory = { fg = c.sky },
    ErrorMsg = { fg = c.crimson, bold = true },
    WarningMsg = { fg = c.gold },
    MoreMsg = { fg = c.moss },
    ModeMsg = { fg = c.vermilion, bold = true },
    Question = { fg = c.sky },
    QuickFixLine = { bg = c.stone, bold = true },
    WildMenu = { fg = c.paper_hi, bg = c.lacquer },
    SpellBad = { sp = c.crimson, undercurl = true },
    SpellCap = { sp = c.gold, undercurl = true },
    SpellRare = { sp = c.sakura, undercurl = true },
    SpellLocal = { sp = c.jade, undercurl = true },

    -- syntax ---------------------------------------------------------------
    Comment = { fg = c.smoke, italic = cfg.italic_comments },
    Constant = { fg = c.ember },
    String = { fg = c.moss },
    Character = { fg = c.moss },
    Number = { fg = c.ember },
    Float = { fg = c.ember },
    Boolean = { fg = c.ember, bold = true },
    Identifier = { fg = c.paper },
    Function = { fg = c.gold_hi },
    Statement = { fg = c.crimson },
    Conditional = { fg = c.crimson },
    Repeat = { fg = c.crimson },
    Label = { fg = c.crimson },
    Operator = { fg = c.mist },
    Keyword = { fg = c.crimson },
    Exception = { fg = c.crimson, bold = true },
    PreProc = { fg = c.sakura },
    Include = { fg = c.sakura },
    Define = { fg = c.sakura },
    Macro = { fg = c.sakura },
    PreCondit = { fg = c.sakura },
    Type = { fg = c.sky },
    StorageClass = { fg = c.crimson },
    Structure = { fg = c.sky },
    Typedef = { fg = c.sky },
    Special = { fg = c.gold },
    SpecialChar = { fg = c.jade },
    Tag = { fg = c.crimson },
    Delimiter = { fg = c.mist },
    SpecialComment = { fg = c.mist, italic = true },
    Debug = { fg = c.ember },
    Underlined = { fg = c.sky, underline = true },
    Error = { fg = c.crimson },
    Todo = { fg = c.ink, bg = c.gold, bold = true },
    Added = { fg = c.moss },
    Changed = { fg = c.gold },
    Removed = { fg = c.crimson },

    -- treesitter -------------------------------------------------------------
    ["@variable"] = { fg = c.paper },
    ["@variable.builtin"] = { fg = c.sakura, italic = true },
    ["@variable.parameter"] = { fg = c.pampas, italic = true },
    ["@variable.member"] = { fg = c.pampas },
    ["@property"] = { fg = c.pampas },
    ["@constant"] = { fg = c.ember },
    ["@constant.builtin"] = { fg = c.ember, bold = true },
    ["@module"] = { fg = c.sky, italic = true },
    ["@label"] = { fg = c.crimson },
    ["@string"] = { fg = c.moss },
    ["@string.escape"] = { fg = c.jade },
    ["@string.regexp"] = { fg = c.jade },
    ["@string.special.url"] = { fg = c.sky, underline = true },
    ["@character"] = { fg = c.moss },
    ["@number"] = { fg = c.ember },
    ["@boolean"] = { fg = c.ember, bold = true },
    ["@type"] = { fg = c.sky },
    ["@type.builtin"] = { fg = c.sky, italic = true },
    ["@attribute"] = { fg = c.gold },
    ["@function"] = { fg = c.gold_hi },
    ["@function.builtin"] = { fg = c.gold },
    ["@function.call"] = { fg = c.gold_hi },
    ["@function.method"] = { fg = c.gold_hi },
    ["@function.macro"] = { fg = c.sakura },
    ["@constructor"] = { fg = c.sky },
    ["@operator"] = { fg = c.mist },
    ["@keyword"] = { fg = c.crimson },
    ["@keyword.function"] = { fg = c.crimson, italic = true },
    ["@keyword.return"] = { fg = c.crimson, bold = true },
    ["@keyword.import"] = { fg = c.sakura },
    ["@keyword.exception"] = { fg = c.crimson, bold = true },
    ["@punctuation"] = { fg = c.mist },
    ["@punctuation.bracket"] = { fg = c.mist },
    ["@punctuation.delimiter"] = { fg = c.smoke },
    ["@punctuation.special"] = { fg = c.gold },
    ["@comment"] = { link = "Comment" },
    ["@comment.todo"] = { link = "Todo" },
    ["@comment.error"] = { fg = c.paper_hi, bg = c.lacquer, bold = true },
    ["@comment.warning"] = { fg = c.ink, bg = c.gold, bold = true },
    ["@comment.note"] = { fg = c.ink, bg = c.sky, bold = true },
    ["@tag"] = { fg = c.crimson },
    ["@tag.attribute"] = { fg = c.gold, italic = true },
    ["@tag.delimiter"] = { fg = c.smoke },
    ["@markup.heading"] = { fg = c.gold, bold = true },
    ["@markup.heading.1"] = { fg = c.vermilion, bold = true },
    ["@markup.heading.2"] = { fg = c.gold, bold = true },
    ["@markup.heading.3"] = { fg = c.moss, bold = true },
    ["@markup.strong"] = { bold = true },
    ["@markup.italic"] = { italic = true },
    ["@markup.strikethrough"] = { strikethrough = true },
    ["@markup.link"] = { fg = c.sky },
    ["@markup.link.url"] = { fg = c.sky, underline = true },
    ["@markup.raw"] = { fg = c.jade },
    ["@markup.list"] = { fg = c.gold },
    ["@markup.quote"] = { fg = c.mist, italic = true },
    ["@diff.plus"] = { fg = c.moss },
    ["@diff.minus"] = { fg = c.crimson },
    ["@diff.delta"] = { fg = c.gold },

    -- lsp / diagnostics ------------------------------------------------------
    ["@lsp.type.namespace"] = { link = "@module" },
    ["@lsp.type.parameter"] = { link = "@variable.parameter" },
    ["@lsp.type.property"] = { link = "@property" },
    ["@lsp.type.enumMember"] = { link = "@constant" },
    ["@lsp.mod.deprecated"] = { strikethrough = true },
    DiagnosticError = { fg = c.crimson },
    DiagnosticWarn = { fg = c.gold },
    DiagnosticInfo = { fg = c.sky },
    DiagnosticHint = { fg = c.jade },
    DiagnosticOk = { fg = c.moss },
    DiagnosticVirtualTextError = { fg = c.crimson, bg = "#241213" },
    DiagnosticVirtualTextWarn = { fg = c.gold, bg = "#231d13" },
    DiagnosticVirtualTextInfo = { fg = c.sky, bg = "#161b21" },
    DiagnosticVirtualTextHint = { fg = c.jade, bg = "#151c1b" },
    DiagnosticUnderlineError = { sp = c.crimson, undercurl = true },
    DiagnosticUnderlineWarn = { sp = c.gold, undercurl = true },
    DiagnosticUnderlineInfo = { sp = c.sky, undercurl = true },
    DiagnosticUnderlineHint = { sp = c.jade, undercurl = true },
    LspReferenceText = { bg = c.stone },
    LspReferenceRead = { bg = c.stone },
    LspReferenceWrite = { bg = c.stone, underline = true },
    LspInlayHint = { fg = c.slate, italic = true },
    LspSignatureActiveParameter = { fg = c.gold_hi, bold = true, underline = true },

    -- diff / git --------------------------------------------------------------
    DiffAdd = { bg = "#18221a" },
    DiffChange = { bg = "#262016" },
    DiffDelete = { fg = c.crimson, bg = "#2a1214" },
    DiffText = { bg = "#3d3218" },
    GitSignsAdd = { fg = c.moss },
    GitSignsChange = { fg = c.gold },
    GitSignsDelete = { fg = c.crimson },
    GitSignsCurrentLineBlame = { fg = c.slate, italic = true },

    -- telescope ---------------------------------------------------------------
    TelescopeNormal = { fg = c.paper, bg = c.ink },
    TelescopeBorder = { fg = c.ink, bg = c.ink },
    TelescopePromptNormal = { fg = c.paper, bg = c.stone },
    TelescopePromptBorder = { fg = c.stone, bg = c.stone },
    TelescopePromptTitle = { fg = c.paper_hi, bg = c.lacquer, bold = true },
    TelescopePromptPrefix = { fg = c.crimson },
    TelescopePreviewTitle = { fg = c.ink, bg = c.gold, bold = true },
    TelescopeResultsTitle = { fg = c.ink, bg = c.pampas, bold = true },
    TelescopeSelection = { fg = c.paper_hi, bg = c.stone, bold = true },
    TelescopeSelectionCaret = { fg = c.crimson, bg = c.stone },
    TelescopeMatching = { fg = c.vermilion, bold = true },

    -- neo-tree ----------------------------------------------------------------
    NeoTreeNormal = { fg = c.rice, bg = c.ink },
    NeoTreeNormalNC = { fg = c.rice, bg = c.ink },
    NeoTreeEndOfBuffer = { fg = c.ink, bg = c.ink },
    NeoTreeWinSeparator = { fg = c.ink, bg = c.ink },
    NeoTreeRootName = { fg = c.vermilion, bold = true },
    NeoTreeDirectoryName = { fg = c.paper },
    NeoTreeDirectoryIcon = { fg = c.crimson },
    NeoTreeFileName = { fg = c.rice },
    NeoTreeFileNameOpened = { fg = c.gold_hi },
    NeoTreeIndentMarker = { fg = c.stone },
    NeoTreeExpander = { fg = c.smoke },
    NeoTreeCursorLine = { bg = c.stone },
    NeoTreeGitAdded = { fg = c.moss },
    NeoTreeGitModified = { fg = c.gold },
    NeoTreeGitDeleted = { fg = c.crimson },
    NeoTreeGitUntracked = { fg = c.ember },
    NeoTreeTitleBar = { fg = c.paper_hi, bg = c.lacquer },

    -- other plugins -------------------------------------------------------------
    WhichKey = { fg = c.crimson },
    WhichKeyGroup = { fg = c.sky },
    WhichKeyDesc = { fg = c.paper },
    WhichKeySeparator = { fg = c.slate },
    WhichKeyBorder = { fg = c.slate },
    WhichKeyTitle = { fg = c.paper_hi, bg = c.lacquer, bold = true },
    IblIndent = { fg = c.ash, nocombine = true },
    IblScope = { fg = c.blood, nocombine = true },
    BufferLineFill = { bg = c.ink },
    LazyH1 = { fg = c.paper_hi, bg = c.lacquer, bold = true },
    LazyButton = { fg = c.mist, bg = c.stone },
    LazyButtonActive = { fg = c.ink, bg = c.gold, bold = true },
    LazySpecial = { fg = c.gold },
    AlphaHeader = { fg = c.paper },
    AlphaMotto = { fg = c.gold, bold = true },
    AlphaKanji = { fg = c.crimson, bold = true },
    AlphaButtons = { fg = c.rice },
    AlphaShortcut = { fg = c.crimson, bold = true },
    AlphaFooter = { fg = c.smoke, italic = true },
    NotifyBackground = { bg = c.ash },
    MiniIndentscopeSymbol = { fg = c.blood },
  }
end

function M.load()
  if vim.g.colors_name then
    vim.cmd("hi clear")
  end
  vim.o.termguicolors = true
  vim.o.background = "dark"
  vim.g.colors_name = "ghost-of-tsushima"
  local c = M.palette
  for name, spec in pairs(groups(c, M.config)) do
    vim.api.nvim_set_hl(0, name, spec)
  end
  -- dashboard art colours
  local ok, art = pcall(require, "got.enso")
  if ok then
    for name, spec in pairs(art.groups) do
      vim.api.nvim_set_hl(0, name, spec)
    end
  end
  for i, col in ipairs(c.terminal) do
    vim.g["terminal_color_" .. (i - 1)] = col
  end
end

return M
