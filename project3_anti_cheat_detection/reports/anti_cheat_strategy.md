# Anti-Cheat Detection Strategy
**Project 3 — Game Data Science Portfolio**
*Author: Maxi Pagliero | Stack: PostgreSQL · Python · XGBoost · scikit-learn*

---

## 1. Detection Approach

The system combines two complementary layers — deterministic thresholds and probabilistic ML — to flag suspicious players while remaining robust to both obvious and subtle cheating.

### Rule-Based Thresholds (First Filter)
Hard thresholds provide cheap, interpretable, and near-zero false-negative coverage for the most egregious cheaters. Any player exceeding *all three* of these bounds in a rolling 10-match window is immediately escalated:

| Feature | Legitimate range (95th pct) | Cheat threshold |
|---|---|---|
| `avg_accuracy` | ≤ 0.55 | > 0.65 |
| `avg_headshot_rate` | ≤ 0.50 | > 0.60 |
| `avg_reaction_time_ms` | ≥ 150 ms | < 100 ms |

These thresholds are derived from the population z-score distributions established in the feature engineering phase. They catch the most extreme outliers instantly, without waiting for model inference.

### ML Probabilistic Layer (XGBoost)
For players who fall below the hard thresholds but still exhibit unusual patterns, an XGBoost classifier trained on 15 engineered features produces a continuous cheat probability score. The model handles non-linear interactions (e.g., high accuracy combined with low reaction time variance) that single-feature rules cannot express.

Three models were evaluated — Logistic Regression (baseline), Random Forest, and XGBoost. XGBoost achieved the highest ROC-AUC and F1 on the held-out test set, making it the recommended production model.

### Composite `suspicion_score`
The engineered `suspicion_score` (sum of z-scores for accuracy, headshot rate, and inverted reaction time) serves as a human-readable signal alongside the ML probability. It surfaces in analyst dashboards and player appeal workflows, giving reviewers an intuitive single number without requiring ML expertise to interpret.

---

## 2. Metrics & Trade-offs

### Why Recall Matters More Than Precision
In anti-cheat, the two error types carry asymmetric costs:

- **False Negative (missed cheater):** The cheater continues playing, degrading the experience for every legitimate player in future matches. At scale, one missed cheater can ruin dozens of matches per day — a multiplied harm.
- **False Positive (wrongly flagged player):** An innocent player is flagged, causing frustration and potential churn for *one* player. This is recoverable through a human review and appeal process.

Because false negatives damage the experience at scale while false positives affect individuals, **recall is the primary optimisation target**. The goal is to miss as few real cheaters as possible, accepting a controlled rate of false positives that feeds a review queue rather than triggering automatic bans.

### Recommended Operating Threshold
From the ROC curve (`reports/figures/roc_curves.png`), lowering the classification threshold from the default 0.5 to approximately **0.30** is recommended for Tier 1 flagging. At this point the model achieves recall > 0.95 while keeping the false positive rate below 0.05 — meaning fewer than 5% of legitimate players are flagged per cycle.

### Threshold Tuning by Player-Base Size
| Player-base scale | Recommended threshold | Rationale |
|---|---|---|
| < 50 k DAU | 0.40 | Small team; limit review queue volume |
| 50 k – 500 k DAU | 0.30 | Balanced recall with manageable queue |
| > 500 k DAU | 0.20 + auto-ban at 0.90 | High cheater volume; two-tier automation |

For studios with a large appeals volume, the threshold on the auto-ban tier (≥ 0.90) should be tuned quarterly by comparing ban-appeal overturn rates to the model's calibration curve.

---

## 3. Escalation Workflow

A three-tier workflow ensures the model's output is never the sole basis for a permanent ban.

### Tier 1 — Automated Flag (Score ≥ 0.30)
The player is added to an *enhanced monitoring* queue. Subsequent matches are logged at full telemetry resolution. No visible action is taken. A replay review ticket is created automatically in the analyst dashboard.

### Tier 2 — Analyst Review (Score ≥ 0.60 or Tier 1 confirmed by replay)
A trust-and-safety analyst performs a manual evidence check: replay inspection, account history, session frequency, and social graph (shared IPs or friend networks with known cheaters). The analyst can escalate to Tier 3 or dismiss the flag.

### Tier 3 — Permanent Ban + Appeal
A permanent ban is issued only after analyst sign-off. An automated email notifies the player with an appeal link. Appeals are reviewed by a second analyst who was not involved in the original investigation. The `suspicion_score` history and replay timestamps are made available to the appeal reviewer through the internal dashboard.

### Avoiding Over-Reliance on the Model
- No automated ban is issued below a probability score of 0.90.
- All bans at 0.90–1.00 still require Tier 2 analyst confirmation until the model's false positive rate on live data drops below 1%.
- Periodic audits compare model predictions against confirmed cheater reports from the community and CS teams to detect drift.

---

## 4. Cross-Team Collaboration

### Game / Engineering Team
The telemetry pipeline must emit per-match records with the fields in `raw.match_events`. Any schema changes (new weapons, ability types, map sizes) require the data team to be consulted before deployment, since they affect the distribution of features like `avg_damage_dealt` and `kd_ratio`. A shared Slack channel or Jira label for "anti-cheat data contract" is the recommended coordination mechanism.

### Community / Support Teams
Customer support agents handling ban appeals can query the internal dashboard for a player's `suspicion_score` trend, historical flag timestamps, and the top contributing features (via SHAP values). This lets agents explain a ban clearly — e.g., "Your accuracy was 3.2 standard deviations above the player population over 12 consecutive matches" — without exposing the model's internals.

### Model Retraining
As the cheating landscape evolves, the model's signal degrades. The recommended retraining cadence:

1. **Monthly:** Retrain on a rolling 90-day window of labeled matches (confirmed bans + confirmed clean players).
2. **On drift detection:** Monitor the population distribution of `suspicion_score` weekly. A shift in the 95th percentile indicates either a new cheat method or a game balance change — both warrant investigation before retraining.
3. **After major patches:** Any patch that significantly changes weapon balance or movement mechanics may shift the feature distributions enough to require immediate retraining, validated on a held-out pre/post-patch sample.

---

## 5. Limitations & Next Steps

### Synthetic Data Caveats
This project was developed on synthetically generated match data. The cheater population was simulated with fixed statistical properties (accuracy ~ N(0.72, 0.04), reaction time ~ N(80, 10)). In production:

- Real cheaters adapt — aimbot scripts may be configured to *mimic* legitimate accuracy distributions, making z-score features less discriminating over time.
- Label quality is critical. Synthetic labels are perfect; real-world confirmed-ban labels carry noise from manual review errors and ban evasion.
- Legitimate players with unusually high skill (professional or semi-professional) may generate false positives at a higher rate than modelled.

### Features That Would Improve the Model
| Feature | Signal | Data source |
|---|---|---|
| Mouse movement entropy | Bots move in mechanically smooth arcs | Client-side telemetry |
| Network packet timing variance | Wallhacks often inject data with anomalous timing | Server networking layer |
| Account age & spend history | Cheaters frequently create throwaway accounts | User / payments DB |
| Per-weapon accuracy delta | Cheats typically affect all weapons equally | Match events |
| Kill distance distribution | Aimbots preferentially engage at long range | Match events |

### Unsupervised Approaches for Novel Cheat Detection
Supervised models like XGBoost require labeled examples of known cheat types. Novel or custom cheats may not yet appear in the training set. Complementary unsupervised approaches to explore:

- **Isolation Forest** — anomaly scores on raw feature vectors, no labels required.
- **Autoencoder reconstruction error** — players whose behaviour cannot be reconstructed well by a model trained on legitimate players are flagged.
- **Clustering + analyst spot-checks** — periodic k-means or HDBSCAN clustering of the player feature space to surface tightly grouped outlier clusters for analyst review, even without a prior label.

These methods would feed into Tier 1 of the escalation workflow as an additional signal channel, running in parallel with the XGBoost classifier.
