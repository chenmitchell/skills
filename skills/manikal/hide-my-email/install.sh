#!/bin/bash
set -e

REPO="https://github.com/manikal/hide-my-email"
INSTALL_DIR="$HOME/.hme"
BIN_DIR="$INSTALL_DIR/bin"

# Colors
GREEN='\033[0;32m'
DIM='\033[2m'
RED='\033[0;31m'
RESET='\033[0m'

echo ""
echo "  Installing hme — Hide My Email CLI"
echo ""

# macOS only
if [[ "$(uname)" != "Darwin" ]]; then
  echo -e "  ${RED}Error:${RESET} hme requires macOS."
  exit 1
fi

# Check for git
if ! command -v git &>/dev/null; then
  echo -e "  ${RED}Error:${RESET} git is required. Run: xcode-select --install"
  exit 1
fi

# Clone or update
if [[ -d "$INSTALL_DIR/.git" ]]; then
  echo -e "  ${DIM}Updating...${RESET}"
  git -C "$INSTALL_DIR" pull --ff-only --quiet
else
  echo -e "  ${DIM}Cloning repository...${RESET}"
  git clone --depth=1 --quiet "$REPO" "$INSTALL_DIR"
fi

# Set up bin dir with the hme script
mkdir -p "$BIN_DIR"
cp "$INSTALL_DIR/hme" "$BIN_DIR/hme"
chmod +x "$BIN_DIR/hme"

# Detect shell profile
detect_profile() {
  if [[ -n "${PROFILE:-}" && -f "$PROFILE" ]]; then
    echo "$PROFILE"
  elif [[ -f "$HOME/.zshrc" ]]; then
    echo "$HOME/.zshrc"
  elif [[ -f "$HOME/.bashrc" ]]; then
    echo "$HOME/.bashrc"
  elif [[ -f "$HOME/.bash_profile" ]]; then
    echo "$HOME/.bash_profile"
  elif [[ -f "$HOME/.profile" ]]; then
    echo "$HOME/.profile"
  fi
}

PATH_LINE='export PATH="$HOME/.hme/bin:$PATH"'
PROFILE_FILE="$(detect_profile)"

if [[ -n "$PROFILE_FILE" ]]; then
  if ! grep -q '.hme/bin' "$PROFILE_FILE"; then
    printf '\n# hme\n%s\n' "$PATH_LINE" >> "$PROFILE_FILE"
    echo -e "  ${GREEN}✓${RESET} Added hme to PATH in $PROFILE_FILE"
  else
    echo -e "  ${GREEN}✓${RESET} PATH already configured in $PROFILE_FILE"
  fi
else
  echo -e "  ${DIM}Could not detect shell profile. Add this manually:${RESET}"
  echo -e "  $PATH_LINE"
fi

echo ""
echo -e "  ${GREEN}✓${RESET} Installed to $BIN_DIR/hme"
echo ""
echo -e "  ${DIM}Restart your shell, then:${RESET}"
echo -e "  hme \"Twitter\""
echo ""
echo -e "  ${DIM}Note: Grant Accessibility permissions to Terminal in${RESET}"
echo -e "  ${DIM}System Settings → Privacy & Security → Accessibility${RESET}"
echo ""
