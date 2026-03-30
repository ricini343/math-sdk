#!/bin/bash
set -e

SDK="/workspaces/math-sdk"
ENV_LIB="$SDK/env/src/stakeengine/games/1_1_shogun/library"
DEST_LIB="$SDK/games/1_1_shogun/library"

echo "=== Step 1: Copy sim output to correct location ==="
mkdir -p "$DEST_LIB"
cp -r "$ENV_LIB"/* "$DEST_LIB"/
echo "Copied library files OK"

echo "=== Step 2: Source cargo ==="
. /usr/local/cargo/env

echo "=== Step 3: Run optimizer for all modes ==="
cd "$SDK/games/shogun"
python3 run_optimizer.py

echo "=== DONE ==="
