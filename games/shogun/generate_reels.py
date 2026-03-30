"""Generate reel strip CSV files for SHOGUN."""

import os
import random


# Symbols: dragon, samurai, geisha, oni, A, K, Q, J, 10, W (wild), SC (scatter)
# SC only on reels 0, 2, 4

def make_paying_symbols(
    dragon=3, samurai=4, geisha=5, oni=6,
    A=8, K=8, Q=9, J=8, ten=8,
):
    """Create the list of paying symbols for a single reel strip."""
    syms = []
    syms += ["dragon"] * dragon
    syms += ["samurai"] * samurai
    syms += ["geisha"] * geisha
    syms += ["oni"] * oni
    syms += ["A"] * A
    syms += ["K"] * K
    syms += ["Q"] * Q
    syms += ["J"] * J
    syms += ["10"] * ten
    return syms


def interleave_symbols(symbols, seed=42):
    """Shuffle symbols but prevent runs of 3+ identical symbols."""
    random.seed(seed)
    shuffled = symbols[:]
    random.shuffle(shuffled)

    # Reduce long runs: swap offending symbols with later positions
    for attempt in range(5):
        changed = False
        for i in range(2, len(shuffled)):
            if shuffled[i] == shuffled[i - 1] == shuffled[i - 2]:
                for j in range(i + 1, len(shuffled)):
                    if shuffled[j] != shuffled[i]:
                        shuffled[i], shuffled[j] = shuffled[j], shuffled[i]
                        changed = True
                        break
        if not changed:
            break
    return shuffled


def insert_symbol(symbols, sym_name, count=1, seed=42):
    """Insert symbol(s) at pseudo-random positions."""
    random.seed(seed + 99)
    for _ in range(count):
        pos = random.randint(0, len(symbols))
        symbols.insert(pos, sym_name)
    return symbols


def generate_base_reels(path, length=100, seed_base=100):
    """
    Base game reels (BR0):
    - All reels can have W (wild) — 1 per reel
    - Reels 0, 2, 4 have SC (scatter) — 1 per scatter reel
    - Total per reel: 59 paying + 1 W + (1 SC on 0/2/4 or 1 extra pay on 1/3) = ~61
    Actually we build to target length.
    """
    reels = []
    scatter_reels = {0, 2, 4}

    for i in range(5):
        # Start with paying symbols (59 base)
        syms = make_paying_symbols()  # 59 symbols
        # Add extra low-pays to reach target minus specials
        specials = 1  # W always
        if i in scatter_reels:
            specials += 1  # SC
        needed = length - len(syms) - specials
        # Pad with mixed low-pays
        extras = (["A", "K", "Q", "J", "10"] * 3)[:needed]
        syms += extras

        syms = interleave_symbols(syms, seed=seed_base + i * 17)

        # Insert wild
        syms = insert_symbol(syms, "W", count=1, seed=seed_base + i * 17)

        # Insert scatter on reels 0, 2, 4
        if i in scatter_reels:
            syms = insert_symbol(syms, "SC", count=1, seed=seed_base + i * 17 + 50)

        # Trim or pad to exact length
        syms = syms[:length]
        while len(syms) < length:
            syms.append("Q")

        assert len(syms) == length, f"Reel {i} length {len(syms)} != {length}"
        reels.append(syms)

    _write_csv(path, "BR0.csv", reels, length)


def generate_freegame_reels(path, length=60, seed_base=500):
    """
    Free game reels (FR0):
    - No SC (scatters) — free spins don't need scatter trigger on strips
      (retrigger is checked programmatically or not available)
    - W (wild) present — 3 per reel (5% wild freq, expanding sticky)
    - Wilds that land expand to fill the whole reel and become sticky
    """
    reels = []
    wild_count = 3  # 3 wilds per reel = 5% frequency on 60 symbols
    for i in range(5):
        syms = make_paying_symbols(
            dragon=2, samurai=3, geisha=4, oni=5,
            A=6, K=6, Q=6, J=6, ten=6,
        )  # 44 symbols

        needed = length - len(syms) - wild_count
        extras = (["A", "K", "Q", "J", "10"] * 5)[:needed]
        syms += extras

        syms = interleave_symbols(syms, seed=seed_base + i * 23)

        # Insert 3 wilds per reel
        syms = insert_symbol(syms, "W", count=wild_count, seed=seed_base + i * 23)

        syms = syms[:length]
        while len(syms) < length:
            syms.append("J")

        assert len(syms) == length, f"FR reel {i} length {len(syms)} != {length}"
        reels.append(syms)

    _write_csv(path, "FR0.csv", reels, length)


def _write_csv(path, filename, reels, length):
    num_reels = len(reels)
    filepath = os.path.join(path, filename)
    with open(filepath, "w") as f:
        for row in range(length):
            line = ",".join(reels[col][row] for col in range(num_reels))
            f.write(line + "\n")
    print(f"  Generated {filepath} ({length} rows x {num_reels} reels)")


def generate_all(reels_dir):
    os.makedirs(reels_dir, exist_ok=True)
    generate_base_reels(reels_dir)
    generate_freegame_reels(reels_dir)
    print("Reel generation complete.")


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    generate_all(os.path.join(script_dir, "reels"))
