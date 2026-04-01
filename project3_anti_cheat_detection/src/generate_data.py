"""
generate_data.py

Produces synthetic match-level telemetry for the anti-cheat detection project:
  - data/raw/match_events.csv  (~10 000 rows)

Cheaters (~5 % of players) have statistically distinguishable stats:
  higher accuracy, higher headshot_rate, lower avg_reaction_time_ms.
Gaussian noise is added so the distributions overlap naturally.

Run from the project root:
  python src/generate_data.py
"""

import csv
import random
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

RANDOM_SEED = 42
NUM_ROWS = 10_000
NUM_PLAYERS = 800          # pool of unique player IDs
CHEATER_RATE = 0.05        # ~5 % of players are cheaters
SIM_START = datetime(2025, 1, 1)
SIM_END = datetime(2025, 3, 31)
OUTPUT_DIR = Path(__file__).parent.parent / "data" / "raw"

# ---------------------------------------------------------------------------
# Normal-player stat distributions  (mean, std)
# ---------------------------------------------------------------------------
LEGIT = {
    "accuracy":            (0.30, 0.10),
    "headshot_rate":       (0.20, 0.08),
    "avg_reaction_time_ms":(220,  50),
    "kills":               (8,    5),
    "deaths":              (7,    4),
    "assists":             (4,    3),
    "shots_fired":         (300,  120),
    "damage_dealt":        (1200, 500),
    "movement_speed_avg":  (5.5,  1.2),
    "play_duration_seconds":(1800, 600),
}

# Cheater overrides – same keys, different distribution
CHEAT = {
    "accuracy":            (0.72, 0.08),
    "headshot_rate":       (0.65, 0.10),
    "avg_reaction_time_ms":(80,   20),
    "kills":               (22,   6),
    "deaths":              (3,    2),
    "assists":             (5,    3),
    "shots_fired":         (260,  80),
    "damage_dealt":        (3500, 600),
    "movement_speed_avg":  (7.8,  1.0),
    "play_duration_seconds":(1800, 600),
}


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, value))


def sample_row(rng: random.Random, match_id: str, player_id: str,
               match_date: datetime, is_cheater: bool) -> dict:
    dist = CHEAT if is_cheater else LEGIT

    accuracy     = clamp(rng.gauss(*dist["accuracy"]),            0.01, 1.0)
    headshot_rate= clamp(rng.gauss(*dist["headshot_rate"]),       0.0,  1.0)
    reaction_ms  = clamp(rng.gauss(*dist["avg_reaction_time_ms"]),10,   800)
    kills        = max(0, int(rng.gauss(*dist["kills"])))
    deaths       = max(0, int(rng.gauss(*dist["deaths"])))
    assists      = max(0, int(rng.gauss(*dist["assists"])))
    shots_fired  = max(1, int(rng.gauss(*dist["shots_fired"])))
    damage_dealt = max(0, int(rng.gauss(*dist["damage_dealt"])))
    move_speed   = clamp(rng.gauss(*dist["movement_speed_avg"]),  0.5,  15.0)
    duration     = max(60, int(rng.gauss(*dist["play_duration_seconds"])))

    return {
        "match_id":              match_id,
        "player_id":             player_id,
        "match_date":            match_date.strftime("%Y-%m-%d"),
        "kills":                 kills,
        "deaths":                deaths,
        "assists":               assists,
        "accuracy":              round(accuracy, 4),
        "headshot_rate":         round(headshot_rate, 4),
        "avg_reaction_time_ms":  round(reaction_ms, 1),
        "shots_fired":           shots_fired,
        "damage_dealt":          damage_dealt,
        "movement_speed_avg":    round(move_speed, 2),
        "play_duration_seconds": duration,
        "is_cheater":            is_cheater,
    }


def random_date(rng: random.Random) -> datetime:
    delta = SIM_END - SIM_START
    return SIM_START + timedelta(seconds=rng.randint(0, int(delta.total_seconds())))


def main() -> None:
    rng = random.Random(RANDOM_SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "match_events.csv"

    # Build player pool with cheater flags
    player_ids = [f"player_{i:04d}" for i in range(NUM_PLAYERS)]
    cheater_set = set(rng.sample(player_ids, k=int(NUM_PLAYERS * CHEATER_RATE)))

    fieldnames = [
        "match_id", "player_id", "match_date",
        "kills", "deaths", "assists",
        "accuracy", "headshot_rate", "avg_reaction_time_ms",
        "shots_fired", "damage_dealt",
        "movement_speed_avg", "play_duration_seconds",
        "is_cheater",
    ]

    rows = []
    for _ in range(NUM_ROWS):
        player_id = rng.choice(player_ids)
        match_id  = str(uuid.UUID(int=rng.getrandbits(128)))
        match_date = random_date(rng)
        is_cheater = player_id in cheater_set
        rows.append(sample_row(rng, match_id, player_id, match_date, is_cheater))

    # Sort by match_date for a more natural ordering
    rows.sort(key=lambda r: r["match_date"])

    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    cheater_rows = sum(1 for r in rows if r["is_cheater"])
    print(f"Wrote {len(rows):,} rows to {output_path}")
    print(f"  Cheater rows : {cheater_rows:,}  ({cheater_rows/len(rows)*100:.1f} %)")
    print(f"  Legit rows   : {len(rows)-cheater_rows:,}")


if __name__ == "__main__":
    main()
