#!/bin/bash
set -e

SDK="/workspaces/math-sdk"
ENV_LIB="$SDK/env/src/stakeengine/games/1_1_shogun/library"
DEST_LIB="$SDK/games/1_1_shogun/library"

echo "=== Step 1: Copy sim output to correct location ==="
mkdir -p "$DEST_LIB"
cp -r "$ENV_LIB"/* "$DEST_LIB"/
echo "Copied library files OK"

echo "=== Step 1b: Add missing bias field to math_config.json ==="
MCFG="$DEST_LIB/configs/math_config.json"
python3 -c "
import json
with open('$MCFG') as f:
    d = json.load(f)
if 'bias' not in d:
    d['bias'] = [
        {'bet_mode': 'base', 'bias': []},
        {'bet_mode': 'buy_bonus', 'bias': []},
        {'bet_mode': 'super_buy_bonus', 'bias': []},
    ]
    with open('$MCFG', 'w') as f:
        json.dump(d, f, indent=2)
    print('Added bias field OK')
else:
    print('bias field already exists')
"

echo "=== Step 2: Source cargo ==="
. /usr/local/cargo/env

echo "=== Step 3: Run optimizer for all modes ==="
cd "$SDK/games/shogun"
python3 run_optimizer.py

echo "=== DONE ==="
