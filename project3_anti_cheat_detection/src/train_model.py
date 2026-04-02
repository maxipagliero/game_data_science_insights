"""
train_model.py — Script version of notebook 03_model_training.

Loads player_features_engineered from PostgreSQL (or CSV fallback),
trains an XGBoost classifier, and saves the model to src/xgboost_model.pkl.

Usage:
    python src/train_model.py
"""

import os
import sys
import warnings
from pathlib import Path

import pandas as pd
import joblib
import xgboost as xgb
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

warnings.filterwarnings("ignore")
load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
SRC_DIR = Path(__file__).parent
CSV_PATH = SRC_DIR.parent / "data" / "processed" / "player_features_engineered.csv"
MODEL_OUT = SRC_DIR / "xgboost_model.pkl"
TEST_SET_OUT = SRC_DIR / "test_set.csv"

FEATURE_COLS = [
    "avg_kills", "avg_deaths", "kd_ratio",
    "avg_accuracy", "avg_headshot_rate", "avg_reaction_time_ms",
    "avg_damage_dealt", "matches_played",
    "stddev_accuracy", "stddev_reaction_time_ms",
    "accuracy_z_score", "reaction_z_score", "headshot_z_score",
    "suspicion_score", "consistency_flag",
]
TARGET_COL = "cheater_flag"
RANDOM_STATE = 42


# ---------------------------------------------------------------------------
# 1. Load data
# ---------------------------------------------------------------------------
def load_data() -> pd.DataFrame:
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(db_url)
            with engine.connect() as conn:
                df = pd.read_sql(
                    text("SELECT * FROM raw.player_features_engineered"), conn
                )
            print(f"[data] Loaded {len(df):,} rows from PostgreSQL")
            return df
        except Exception as exc:
            print(f"[data] PostgreSQL unavailable ({exc}), falling back to CSV")

    if not CSV_PATH.exists():
        sys.exit(f"[error] CSV not found: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"[data] Loaded {len(df):,} rows from {CSV_PATH}")
    return df


# ---------------------------------------------------------------------------
# 2. Train
# ---------------------------------------------------------------------------
def train(df: pd.DataFrame) -> xgb.XGBClassifier:
    X = df[FEATURE_COLS]
    y = df[TARGET_COL]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, stratify=y, random_state=RANDOM_STATE
    )
    print(f"[split] train={len(X_train):,}  test={len(X_test):,}")

    # Persist test set for evaluate_model.py
    test_df = X_test.copy()
    test_df[TARGET_COL] = y_test.values
    test_df.to_csv(TEST_SET_OUT, index=False)
    print(f"[split] Test set saved → {TEST_SET_OUT}")

    neg = (y_train == 0).sum()
    pos = (y_train == 1).sum()
    scale_pos_weight = neg / pos

    model = xgb.XGBClassifier(
        n_estimators=100,
        scale_pos_weight=scale_pos_weight,
        random_state=RANDOM_STATE,
        eval_metric="logloss",
        use_label_encoder=False,
        verbosity=0,
    )
    model.fit(X_train, y_train)
    print("[train] XGBoost fitted")

    y_pred = model.predict(X_test)
    print("\n" + "=" * 55)
    print("  XGBOOST — Classification Report (test set)")
    print("=" * 55)
    print(classification_report(y_test, y_pred, target_names=["Legit", "Cheater"]))

    return model


# ---------------------------------------------------------------------------
# 3. Save
# ---------------------------------------------------------------------------
def save_model(model: xgb.XGBClassifier) -> None:
    joblib.dump(model, MODEL_OUT)
    print(f"[save] Model saved → {MODEL_OUT}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    df = load_data()
    model = train(df)
    save_model(model)
    print("\nDone.")
