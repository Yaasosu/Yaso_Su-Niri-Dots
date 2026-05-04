#!/bin/bash

set -e

echo "==> [1/4] Установка DankLinux..."
curl -fsSL https://install.danklinux.com | sh

echo ""
echo "==> [2/4] Удаление alacritty и waybar..."
sudo pacman -Rns --noconfirm alacritty waybar 2>/dev/null || echo "Пакеты не найдены, пропускаем..."

echo ""
echo "==> [3/4] Установка sofта и настройка fish..."

sudo pacman -S --needed --noconfirm kitty fish util-linux

FISH_PATH="/usr/bin/fish"

if ! grep -q "$FISH_PATH" /etc/shells; then
    echo "$FISH_PATH" | sudo tee -a /etc/shells
fi

sudo chsh -s "$FISH_PATH" "$USER"

sudo ln -sf "$(command -v kitty)" /usr/local/bin/xterm 2>/dev/null || true

echo "✓ Софт установлен, fish назначен шеллом для $USER"

echo ""
echo "==> [4/4] Клонирование dotfiles..."

REPO_URL="https://github.com/Yaasosu/Yaso_Su-Niri-Dots.git"
TMP_DIR="$(mktemp -d)"

git clone "$REPO_URL" "$TMP_DIR"

mkdir -p "$HOME/.config"

echo "==> Копирование файлов в ~/.config (с перезаписью)..."
cp -rf "$TMP_DIR"/. "$HOME/.config/"

rm -rf "$TMP_DIR"

echo ""
echo "---"
echo "✓ Готово! Перезайди в систему для активации fish."
