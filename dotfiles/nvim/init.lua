-- 冥人 Ghost of Tsushima — Neovim
-- https://github.com/Shubhwtf/ghost-of-tsushima-theme-mac
-- "red" (default) or "kurosawa" for the black-and-white mode; install.sh --variant sets this
vim.g.got_variant = vim.g.got_variant or "red"
local scheme = vim.g.got_variant == "kurosawa" and "ghost-of-tsushima-kurosawa" or "ghost-of-tsushima"

vim.g.mapleader = " "
vim.g.maplocalleader = " "

vim.opt.expandtab = true
vim.opt.tabstop = 2
vim.opt.softtabstop = 2
vim.opt.shiftwidth = 2
vim.opt.number = true
vim.opt.relativenumber = true
vim.opt.cursorline = true
vim.opt.signcolumn = "yes"
vim.opt.termguicolors = true
vim.opt.scrolloff = 8
vim.opt.smartcase = true
vim.opt.ignorecase = true
vim.opt.splitright = true
vim.opt.splitbelow = true
vim.opt.updatetime = 250
vim.opt.undofile = true
vim.opt.showmode = false
vim.opt.clipboard = "unnamedplus"
vim.opt.fillchars = { eob = " ", fold = " ", vert = "│" }
vim.opt.pumheight = 12
vim.opt.laststatus = 3

local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not (vim.uv or vim.loop).fs_stat(lazypath) then
  local lazyrepo = "https://github.com/folke/lazy.nvim.git"
  local out = vim.fn.system({ "git", "clone", "--filter=blob:none", "--branch=stable", lazyrepo, lazypath })
  if vim.v.shell_error ~= 0 then
    vim.api.nvim_echo({
      { "Failed to clone lazy.nvim:\n", "ErrorMsg" },
      { out, "WarningMsg" },
      { "\nPress any key to exit..." },
    }, true, {})
    vim.fn.getchar()
    os.exit(1)
  end
end
vim.opt.rtp:prepend(lazypath)

-- flash yanked text in lacquer red
vim.api.nvim_create_autocmd("TextYankPost", {
  callback = function() vim.hl.on_yank({ higroup = "IncSearch", timeout = 180 }) end,
})

require("lazy").setup("plugins", {
  install = { colorscheme = { scheme } },
  ui = { border = "rounded", title = " \u{25c6} 冥人 " },
  change_detection = { notify = false },
})

vim.cmd.colorscheme(scheme)

local map = vim.keymap.set
map("n", "<C-p>", "<cmd>Telescope find_files<CR>", { desc = "Find files" })
map("n", "<leader>ff", "<cmd>Telescope find_files<CR>", { desc = "Find files" })
map("n", "<leader>fg", "<cmd>Telescope live_grep<CR>", { desc = "Live grep" })
map("n", "<leader>fb", "<cmd>Telescope buffers<CR>", { desc = "Buffers" })
map("n", "<leader>fr", "<cmd>Telescope oldfiles<CR>", { desc = "Recent files" })
map("n", "<C-n>", "<cmd>Neotree filesystem reveal left toggle<CR>", { desc = "File tree" })
map("n", "<S-l>", "<cmd>BufferLineCycleNext<CR>", { desc = "Next buffer" })
map("n", "<S-h>", "<cmd>BufferLineCyclePrev<CR>", { desc = "Previous buffer" })
map("n", "<leader>w", "<cmd>w<CR>", { desc = "Save" })
map("n", "<leader>q", "<cmd>bdelete<CR>", { desc = "Close buffer" })
map("n", "<Esc>", "<cmd>nohlsearch<CR>")
