# Game & Analytics Data Science Portfolio

This repository showcases my work as a data scientist focused on **games, analytics, and anti-cheat**.  
The projects here are designed to mirror real-world responsibilities from commercial data science and anti-cheat roles:

- Analyzing **in-game economies** and monetization
- Detecting **suspicious player behavior** with data & ML
- Building **end-to-end data pipelines**
- Delivering **internal tools** that help teams act on data

---

## Target Roles

- Data Scientist (Games / Product / Commercial)
- Data Scientist – Anti-Cheat / Game Security
- Analytics Engineer / Analytics-focused Data Engineer

---

## Tech Stack at a Glance

**Languages & Tools**

- **Python** (data analysis, modeling, scripting)
- **SQL** (advanced querying, feature engineering, KPIs)
- **Jupyter Notebooks** for exploration and analysis
- **Git & GitHub** for version control and project organization

**Data & Infrastructure**

- PostgreSQL (schema design, raw/curated layers, KPI views)
- ETL / data pipelines (Python-based orchestration, SQL transformations)
- Basic data quality checks & monitoring concepts

**Analytics & ML**

- Exploratory data analysis and visualization (matplotlib, seaborn)
- KPI & metric design (ARPU, retention, funnels, suspicion scores)
- Supervised learning for classification (Logistic Regression, Random Forest, XGBoost)
- Model evaluation: ROC-AUC, precision-recall, confusion matrices, feature importances

---

## Projects

### ✅ Project 1 — In-Game Economy & Monetization Analytics
**Status: Complete**

End-to-end analytics project on a simulated free-to-play game economy. Covers data generation, SQL schema design, KPI calculation, and visual reporting.

**Key deliverables:**
- `sql/01_schema.sql` — PostgreSQL schema (raw + curated layers)
- `sql/02_kpi_queries.sql` — KPI views: DAU, revenue, ARPU/ARPPU, retention cohorts, conversion funnel
- `notebooks/01_explore_data.ipynb` — EDA across 4 tables (users, sessions, items, economy_events)
- `notebooks/02_kpis_and_visuals.ipynb` — Pandas reimplementation of all SQL KPIs + 5 figures
- `reports/game_economy_report.md` — Written analysis of findings
- `reports/figures/` — DAU trend, ARPU/ARPPU, retention heatmap, conversion funnel, payer conversion

**Stack:** PostgreSQL · Python · pandas · matplotlib · seaborn

---

### ✅ Project 3 — Anti-Cheat Behavior Detection
**Status: Complete**

Full ML pipeline to detect cheating players from match telemetry. Covers data generation, feature engineering, multi-model training, evaluation, and a production strategy document.

**Key deliverables:**

| Layer | Files |
|---|---|
| Data generation | `src/generate_data.py`, `src/prepare_data.py` |
| Raw data | `data/raw/match_events.csv` (10k match events, 800 players, ~5% cheaters) |
| SQL | `sql/01_schema.sql`, `sql/player_aggregates.sql`, `sql/build_features.sql` |
| Feature engineering | `notebooks/02_feature_engineering.ipynb` → `data/processed/player_features_engineered.csv` |
| Model training | `notebooks/03_model_training.ipynb`, `src/train_model.py` |
| Model evaluation | `notebooks/04_model_evaluation.ipynb`, `src/evaluate_model.py` |
| Trained models | `src/logistic_regression_model.pkl`, `src/random_forest_model.pkl`, `src/xgboost_model.pkl` |
| Figures | Confusion matrices, ROC curves, precision-recall curves, feature importances |
| Strategy report | `reports/anti_cheat_report.md` |

**Models trained:** Logistic Regression (baseline) · Random Forest · XGBoost  
**Best model:** XGBoost (highest ROC-AUC and F1 on held-out test set)  
**Stack:** PostgreSQL · Python · pandas · scikit-learn · xgboost · joblib · matplotlib · seaborn

---

### 🔲 Project 4 — End-to-End Data Pipeline Platform
**Status: Placeholder — not yet started**

---

### 🔲 Project 6 — Internal Anti-Cheat Investigator Tool
**Status: Placeholder — not yet started**

---

## Repository Structure

```text
.
├── README.md
├── project1_game_economy_analytics/
│   ├── data/raw/                   # users, sessions, items, economy_events CSVs
│   ├── data/processed/             # daily_kpis.csv, cohorts.csv
│   ├── notebooks/                  # 01_explore_data, 02_kpis_and_visuals
│   ├── reports/figures/            # 5 chart PNGs
│   ├── sql/                        # schema + KPI views
│   └── src/generate_data.py
│
├── project3_anti_cheat_detection/
│   ├── data/raw/                   # match_events.csv
│   ├── data/processed/             # player_features_engineered.csv
│   ├── notebooks/                  # 01_exploration → 04_model_evaluation
│   ├── reports/figures/            # 15 chart PNGs (EDA + model evaluation)
│   ├── reports/anti_cheat_report.md
│   ├── sql/                        # schema, aggregates, feature build
│   └── src/                        # scripts + trained .pkl models
│
├── project4_data_pipeline_platform/   # placeholder
└── project6_anti_cheat_investigator_tool/  # placeholder
```
