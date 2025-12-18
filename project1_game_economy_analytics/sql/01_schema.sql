CREATE TABLE users (
  user_id TEXT PRIMARY KEY,
  install_date DATE,
  country TEXT,
  platform TEXT,
  acquisition_channel TEXT,
  device_type TEXT
);

CREATE TABLE sessions (
  session_id TEXT PRIMARY KEY,
  user_id TEXT REFERENCES users(user_id),
  session_start_ts TIMESTAMP,
  session_end_ts TIMESTAMP,
  session_number INT
);

CREATE TABLE items (
  item_id TEXT PRIMARY KEY,
  item_name TEXT,
  item_type TEXT,
  soft_cost INT,
  hard_cost INT,
  is_iap BOOLEAN
);

CREATE TABLE economy_events (
  event_id TEXT PRIMARY KEY,
  user_id TEXT REFERENCES users(user_id),
  session_id TEXT REFERENCES sessions(session_id),
  event_ts TIMESTAMP,
  event_type TEXT,
  item_id TEXT REFERENCES items(item_id),
  soft_delta INT,
  hard_delta INT,
  revenue_usd REAL,
  txn_id TEXT
);