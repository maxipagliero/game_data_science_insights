# Project 3 – Anti-Cheat Behavior Detection

**Status: 🔨 In Progress (Step 1 complete)**

## Objective
Detect cheating players in a competitive FPS game by analysing match-level
telemetry. The project mirrors a real trust-and-safety pipeline: synthetic data
generation → SQL ingestion → feature engineering → ML classification →
investigator-ready reporting.

## Tech Stack
- PostgreSQL (schema, analytical queries)
- Python (pandas, numpy, scikit-learn, matplotlib, seaborn)
- sqlalchemy + psycopg2 (database connectivity)
- python-dotenv (credential management)
- Jupyter Notebooks

## Structure

```
project3_anti_cheat_detection/
├── data/
│   ├── raw/
│   │   └── match_events.csv      ← 10 000-row synthetic dataset
│   └── processed/                ← engineered features, model outputs
├── notebooks/                    ← EDA, feature engineering, model training
├── reports/                      ← findings, figures
├── sql/
│   ├── 01_schema.sql             ← DDL for raw.match_events
│   └── 02_detection_queries.sql  ← rule-based detection & KPIs (Step 2+)
├── src/
│   ├── generate_data.py          ← synthetic dataset generator
│   └── prepare_data.py           ← CSV → PostgreSQL loader
├── .env.example
└── README.md
```

## Dataset

`data/raw/match_events.csv` – 10 000 match records across ~800 players.

| Column | Description |
|---|---|
| `match_id` | UUID per match |
| `player_id` | Player identifier |
| `match_date` | Date of match (2025-01-01 – 2025-03-31) |
| `kills` | Kills in match |
| `deaths` | Deaths in match |
| `assists` | Assists in match |
| `accuracy` | Shot accuracy (0–1) |
| `headshot_rate` | Headshot fraction (0–1) |
| `avg_reaction_time_ms` | Average reaction time in ms |
| `shots_fired` | Total shots fired |
| `damage_dealt` | Total damage output |
| `movement_speed_avg` | Average movement speed |
| `play_duration_seconds` | Match play time |
| `is_cheater` | Ground-truth label (~5 % True) |

**Cheater signal:** cheaters have significantly higher `accuracy` (≈0.72 vs 0.30),
higher `headshot_rate` (≈0.65 vs 0.20), and lower `avg_reaction_time_ms` (≈80 vs 220),
with Gaussian noise so distributions overlap.

## Setup

1. Copy `.env.example` → `.env` and fill in your PostgreSQL credentials:

```bash
cp .env.example .env
```

2. Install dependencies:

```bash
pip install pandas sqlalchemy psycopg2-binary python-dotenv
```

3. Generate the dataset (already committed, but re-run if needed):

```bash
python src/generate_data.py
```

4. Load into PostgreSQL:

```bash
python src/prepare_data.py
```

---

## Roadmap

| Step | Description | Status |
|---|---|---|
| 1 | Data generation & PostgreSQL ingestion | ✅ Done |
| 2 | EDA & rule-based detection | 🔜 |
| 3 | Feature engineering | 🔜 |
| 4 | ML classification (Logistic Regression, Random Forest, XGBoost) | 🔜 |
| 5 | Evaluation & reporting | 🔜 |
