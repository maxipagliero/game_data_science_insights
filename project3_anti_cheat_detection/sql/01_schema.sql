-- Anti-Cheat Detection – Schema
-- Run once to create the raw schema and match_events table.
-- prepare_data.py handles the actual data load (uses to_sql with if_exists='replace').

CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.match_events (
    match_id                TEXT        NOT NULL,
    player_id               TEXT        NOT NULL,
    match_date              DATE        NOT NULL,
    kills                   INT         NOT NULL,
    deaths                  INT         NOT NULL,
    assists                 INT         NOT NULL,
    accuracy                NUMERIC(6,4) NOT NULL,   -- 0.0000 – 1.0000
    headshot_rate           NUMERIC(6,4) NOT NULL,   -- 0.0000 – 1.0000
    avg_reaction_time_ms    NUMERIC(7,1) NOT NULL,
    shots_fired             INT         NOT NULL,
    damage_dealt            INT         NOT NULL,
    movement_speed_avg      NUMERIC(6,2) NOT NULL,
    play_duration_seconds   INT         NOT NULL,
    is_cheater              BOOLEAN     NOT NULL
);

-- Useful indexes for filtering
CREATE INDEX IF NOT EXISTS idx_match_events_player  ON raw.match_events (player_id);
CREATE INDEX IF NOT EXISTS idx_match_events_date    ON raw.match_events (match_date);
CREATE INDEX IF NOT EXISTS idx_match_events_cheater ON raw.match_events (is_cheater);
