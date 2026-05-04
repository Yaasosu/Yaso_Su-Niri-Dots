#!/bin/bash

set -e

echo "==> [1/4] Installing DankLinux..."
curl -fsSL https://install.danklinux.com | sh

echo ""
echo "==> [2/4] Removing alacritty and waybar..."
sudo pacman -Rns --noconfirm alacritty waybar 2>/dev/null || echo "Packages not found, skipping..."

echo ""
echo "==> [3/4] Installing software and configuring fish..."

sudo pacman -S --needed --noconfirm kitty fish util-linux

FISH_PATH="/usr/bin/fish"

if ! grep -q "$FISH_PATH" /etc/shells; then
    echo "$FISH_PATH" | sudo tee -a /etc/shells
fi

sudo chsh -s "$FISH_PATH" "$USER"

sudo ln -sf "$(command -v kitty)" /usr/local/bin/xterm 2>/dev/null || true

echo "✓ Software installed, fish set as shell for $USER"

echo ""
echo "==> [4/4] Cloning dotfiles..."

REPO_URL="https://github.com/Yaasosu/Yaso_Su-Niri-Dots.git"
TMP_DIR="$(mktemp -d)"

git clone "$REPO_URL" "$TMP_DIR"

mkdir -p "$HOME/.config"

echo "==> Copying files to ~/.config (overwriting existing)..."
cp -rf "$TMP_DIR"/. "$HOME/.config/"

rm -rf "$TMP_DIR"

echo ""
echo "---"
echo "✓ Done! Log out and back in to activate fish."
