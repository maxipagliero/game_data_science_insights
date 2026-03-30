/* Daily DAU */

CREATE OR REPLACE VIEW curated.daily_dau AS
WITH daily_sessions AS (
  SELECT
    DATE(session_start_ts) AS activity_date,
    user_id
  FROM raw.sessions
  GROUP BY 1, 2
)
SELECT
  activity_date,
  COUNT(DISTINCT user_id) AS dau
FROM daily_sessions
GROUP BY activity_date
ORDER BY activity_date;

/* Daily Revenue + Payers */

CREATE OR REPLACE VIEW curated.daily_revenue AS
WITH daily_revenue AS (
  SELECT
    DATE(event_ts) AS revenue_date,
    user_id,
    SUM(revenue_usd) AS user_revenue
  FROM raw.economy_events
  WHERE event_type = 'iap_purchase'
  GROUP BY 1, 2
)
SELECT
  revenue_date,
  SUM(user_revenue)                       AS total_revenue,
  COUNT(DISTINCT user_id)                 AS payers
FROM daily_revenue
GROUP BY revenue_date
ORDER BY revenue_date;

/* Daily ARPU / ARPPU (join DAU + revenue) */

CREATE OR REPLACE VIEW curated.daily_arpu_arppu AS
WITH daily_dau AS (
  SELECT
    DATE(session_start_ts) AS activity_date,
    COUNT(DISTINCT user_id) AS dau
  FROM raw.sessions
  GROUP BY 1
),
daily_rev AS (
  SELECT
    DATE(event_ts) AS activity_date,
    SUM(revenue_usd) AS total_revenue,
    COUNT(DISTINCT user_id) AS payers
  FROM raw.economy_events
  WHERE event_type = 'iap_purchase'
  GROUP BY 1
)
SELECT
  d.activity_date,
  d.dau,
  COALESCE(r.total_revenue, 0) AS total_revenue,
  COALESCE(r.payers, 0) AS payers,
  CASE WHEN d.dau > 0
    THEN COALESCE(r.total_revenue, 0) / d.dau
    ELSE 0 END AS arpu,
  CASE WHEN COALESCE(r.payers, 0) > 0
    THEN COALESCE(r.total_revenue, 0) / r.payers
    ELSE 0 END AS arppu
FROM daily_dau d
LEFT JOIN daily_rev r
  ON d.activity_date = r.activity_date
ORDER BY d.activity_date;

/* Retention Cohorts (D1, D7, D30) */

CREATE OR REPLACE VIEW curated.retention_cohorts AS
WITH installs AS (
  SELECT
    user_id,
    install_date
  FROM raw.users
),

activity AS (
  SELECT DISTINCT
    s.user_id,
    DATE(s.session_start_ts) AS activity_date
  FROM raw.sessions s
),

retention AS (
  SELECT
    i.install_date AS cohort_date,
    COUNT(DISTINCT i.user_id) AS installs,
    COUNT(DISTINCT CASE
      WHEN a.activity_date = i.install_date + INTERVAL '1 day' THEN i.user_id END) AS d1_retained,
    COUNT(DISTINCT CASE
      WHEN a.activity_date = i.install_date + INTERVAL '7 day' THEN i.user_id END) AS d7_retained,
    COUNT(DISTINCT CASE
      WHEN a.activity_date = i.install_date + INTERVAL '30 day' THEN i.user_id END) AS d30_retained
  FROM installs i
  LEFT JOIN activity a
    ON i.user_id = a.user_id
  GROUP BY i.install_date
)
SELECT
  cohort_date,
  installs,
  d1_retained,
  d7_retained,
  d30_retained,
  d1_retained::FLOAT / installs AS d1_retention_rate,
  d7_retained::FLOAT / installs AS d7_retention_rate,
  d30_retained::FLOAT / installs AS d30_retention_rate
FROM retention
ORDER BY cohort_date;

/* Simple Conversion Funnel */

CREATE OR REPLACE VIEW curated.funnel AS
WITH base_users AS (
  SELECT user_id FROM raw.users
),
step_sessions AS (
  SELECT DISTINCT user_id
  FROM raw.sessions
),
step_spend_soft AS (
  SELECT DISTINCT user_id
  FROM raw.economy_events
  WHERE event_type = 'spend_soft'
),
step_payers AS (
  SELECT DISTINCT user_id
  FROM raw.economy_events
  WHERE event_type = 'iap_purchase'
)
SELECT
  'Installed' AS step,
  (SELECT COUNT(*) FROM base_users) AS users
UNION ALL
SELECT
  'Any session',
  (SELECT COUNT(*) FROM step_sessions)
UNION ALL
SELECT
  'Spent soft currency',
  (SELECT COUNT(*) FROM step_spend_soft)
UNION ALL
SELECT
  'Made IAP',
  (SELECT COUNT(*) FROM step_payers);
