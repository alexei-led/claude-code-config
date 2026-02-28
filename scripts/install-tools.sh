#!/bin/bash
# Install recommended CLI tools for Claude Code
# Run: ~/.claude/scripts/install-tools.sh

set -euo pipefail

echo "🛠️  Installing recommended CLI tools for Claude Code..."
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

check_installed() {
	command -v "$1" &>/dev/null
}

install_brew() {
	local pkg=$1
	local cmd=${2:-$1}
	if check_installed "$cmd"; then
		echo -e "${GREEN}✓${NC} $pkg (already installed)"
	else
		echo -e "${YELLOW}→${NC} Installing $pkg..."
		brew install "$pkg" 2>/dev/null || echo -e "${RED}✗${NC} Failed to install $pkg"
	fi
}

install_npm() {
	local pkg=$1
	local cmd=${2:-$1}
	if check_installed "$cmd"; then
		echo -e "${GREEN}✓${NC} $pkg (already installed)"
	else
		echo -e "${YELLOW}→${NC} Installing $pkg globally..."
		npm install -g "$pkg" 2>/dev/null || echo -e "${RED}✗${NC} Failed to install $pkg"
	fi
}

install_go() {
	local pkg=$1
	local cmd=$2
	if check_installed "$cmd"; then
		echo -e "${GREEN}✓${NC} $cmd (already installed)"
	else
		echo -e "${YELLOW}→${NC} Installing $cmd..."
		go install "$pkg" 2>/dev/null || echo -e "${RED}✗${NC} Failed to install $cmd"
	fi
}

echo "=== Modern CLI Replacements (Homebrew) ==="
install_brew "ripgrep" "rg"       # grep replacement
install_brew "fd"                 # find replacement
install_brew "bat"                # cat replacement
install_brew "eza"                # ls replacement (maintained fork of exa)
install_brew "sd"                 # sed replacement
install_brew "delta"              # diff/git pager
install_brew "dust"               # du replacement
install_brew "procs"              # ps replacement
install_brew "bottom" "btm"       # top replacement
install_brew "hyperfine"          # benchmarking
install_brew "tokei"              # code statistics
install_brew "glow"               # markdown viewer
install_brew "zoxide" "zoxide"    # smarter cd
install_brew "difftastic" "difft" # structural diff
install_brew "jq"                 # JSON processor
install_brew "yq"                 # YAML processor
install_brew "fzf"                # fuzzy finder
install_brew "tldr"               # simplified man pages
install_brew "lazygit"            # git TUI

echo ""
echo "=== LSP Servers ==="
# Go LSP
install_go "golang.org/x/tools/gopls@latest" "gopls"

# Python LSP
install_npm "pyright" "pyright"

# TypeScript/JavaScript LSP
install_npm "typescript-language-server" "typescript-language-server"
install_npm "typescript" "tsc"

# Linters/Formatters
install_npm "eslint" "eslint"
install_npm "prettier" "prettier"

echo ""
echo "=== Python Tools (via uv/pip) ==="
if check_installed "uv"; then
	echo -e "${GREEN}✓${NC} uv (already installed)"
else
	echo -e "${YELLOW}→${NC} Installing uv..."
	brew install uv 2>/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
fi

if check_installed "ruff"; then
	echo -e "${GREEN}✓${NC} ruff (already installed)"
else
	echo -e "${YELLOW}→${NC} Installing ruff..."
	brew install ruff 2>/dev/null || uv tool install ruff
fi

echo ""
echo "=== Claude Code Scripts ==="
CE_SCRIPT="$HOME/.claude/scripts/ce"
CE_LINK="$HOME/.local/bin/ce"
if [ -x "$CE_SCRIPT" ]; then
	mkdir -p "$HOME/.local/bin"
	ln -sf "$CE_SCRIPT" "$CE_LINK" 2>/dev/null &&
		echo -e "${GREEN}✓${NC} ce → $CE_LINK" ||
		echo -e "${RED}✗${NC} Failed to link ce (try: ln -sf $CE_SCRIPT $CE_LINK)"
else
	echo -e "${YELLOW}→${NC} ce script not found at $CE_SCRIPT"
fi

echo ""
echo "=== Verification ==="
echo "Checking installed tools..."
echo ""

tools=(
	"rg:ripgrep"
	"fd:fd"
	"bat:bat"
	"eza:eza"
	"sd:sd"
	"delta:delta"
	"dust:dust"
	"procs:procs"
	"btm:bottom"
	"hyperfine:hyperfine"
	"tokei:tokei"
	"glow:glow"
	"zoxide:zoxide"
	"difft:difftastic"
	"jq:jq"
	"yq:yq"
	"fzf:fzf"
	"gopls:gopls"
	"pyright:pyright"
	"typescript-language-server:ts-lsp"
	"ce:ce"
)

missing=()
for tool in "${tools[@]}"; do
	cmd="${tool%%:*}"
	name="${tool##*:}"
	if check_installed "$cmd"; then
		echo -e "${GREEN}✓${NC} $name"
	else
		echo -e "${RED}✗${NC} $name (not found)"
		missing+=("$name")
	fi
done

echo ""
if [ ${#missing[@]} -eq 0 ]; then
	echo -e "${GREEN}All tools installed successfully!${NC}"
else
	echo -e "${YELLOW}Missing tools: ${missing[*]}${NC}"
	echo "Try running this script again or install manually."
fi

echo ""
echo "📝 Don't forget to add shell integrations:"
echo "   # Add to ~/.zshrc or ~/.bashrc:"
# shellcheck disable=SC2016
echo '   eval "$(zoxide init zsh)"'
# shellcheck disable=SC2016
echo '   eval "$(fzf --zsh)"'
