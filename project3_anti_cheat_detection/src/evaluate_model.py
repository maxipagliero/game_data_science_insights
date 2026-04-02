"""
evaluate_model.py — Script version of notebook 04_model_evaluation.

Loads src/xgboost_model.pkl and src/test_set.csv, prints evaluation metrics,
and saves an ROC curve to reports/figures/06_roc_curves.png.

Usage:
    python src/evaluate_model.py
"""

import sys
import warnings
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.metrics import (
    classification_report,
    roc_curve, roc_auc_score,
    confusion_matrix,
)

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid", palette="muted")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SRC_DIR     = Path(__file__).parent
MODEL_PATH  = SRC_DIR / "xgboost_model.pkl"
TEST_PATH   = SRC_DIR / "test_set.csv"
FIGURES_DIR = SRC_DIR.parent / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

FEATURE_COLS = [
    "avg_kills", "avg_deaths", "kd_ratio",
    "avg_accuracy", "avg_headshot_rate", "avg_reaction_time_ms",
    "avg_damage_dealt", "matches_played",
    "stddev_accuracy", "stddev_reaction_time_ms",
    "accuracy_z_score", "reaction_z_score", "headshot_z_score",
    "suspicion_score", "consistency_flag",
]
TARGET_COL = "cheater_flag"


# ---------------------------------------------------------------------------
# 1. Load
# ---------------------------------------------------------------------------
def load_artifacts():
    for path in (MODEL_PATH, TEST_PATH):
        if not path.exists():
            sys.exit(f"[error] Required file not found: {path}\n"
                     "        Run train_model.py first.")

    model   = joblib.load(MODEL_PATH)
    test_df = pd.read_csv(TEST_PATH)
    X_test  = test_df[FEATURE_COLS]
    y_test  = test_df[TARGET_COL]
    print(f"[load] Model:    {MODEL_PATH}")
    print(f"[load] Test set: {len(test_df):,} rows  |  cheater rate: {y_test.mean():.1%}")
    return model, X_test, y_test


# ---------------------------------------------------------------------------
# 2. Metrics
# ---------------------------------------------------------------------------
def print_metrics(model, X_test, y_test) -> None:
    y_pred  = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]
    auc     = roc_auc_score(y_test, y_proba)

    print("\n" + "=" * 55)
    print("  XGBOOST — Classification Report (test set)")
    print("=" * 55)
    print(classification_report(y_test, y_pred, target_names=["Legit", "Cheater"]))

    print(f"ROC-AUC: {auc:.4f}")

    cm = confusion_matrix(y_test, y_pred)
    print("\nConfusion Matrix:")
    cm_df = pd.DataFrame(
        cm,
        index=["Actual Legit", "Actual Cheater"],
        columns=["Pred Legit", "Pred Cheater"],
    )
    print(cm_df.to_string())


# ---------------------------------------------------------------------------
# 3. ROC figure
# ---------------------------------------------------------------------------
def save_roc_figure(model, X_test, y_test) -> None:
    y_proba = model.predict_proba(X_test)[:, 1]
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    auc = roc_auc_score(y_test, y_proba)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot(fpr, tpr, color="#55A868", lw=2, label=f"XGBoost  (AUC = {auc:.3f})")
    ax.plot([0, 1], [0, 1], "k--", lw=1, label="Random baseline")
    ax.set_xlabel("False Positive Rate", fontsize=12)
    ax.set_ylabel("True Positive Rate", fontsize=12)
    ax.set_title("ROC Curve — Anti-Cheat Detection (XGBoost)", fontsize=13, fontweight="bold")
    ax.legend(loc="lower right", fontsize=11)
    ax.set_xlim([0, 1])
    ax.set_ylim([0, 1.02])

    out = FIGURES_DIR / "06_roc_curves.png"
    plt.tight_layout()
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\n[save] ROC figure saved → {out}")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    model, X_test, y_test = load_artifacts()
    print_metrics(model, X_test, y_test)
    save_roc_figure(model, X_test, y_test)
    print("\nDone.")
