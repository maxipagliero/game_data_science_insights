# Project 1 – In-Game Economy & Monetization Analytics

## Objective
Analyze a game's in-game economy to understand player spending, retention, and monetization performance, and translate findings into actionable recommendations for game and monetization designers.

## Tech Stack
- PostgreSQL (schema, KPI views)
- Python (pandas, numpy, matplotlib/plotly)
- Jupyter Notebooks

## Key Questions
- Which player segments drive most revenue?
- How do retention and spending evolve over time?
- Which items or offers are underperforming or overperforming?
- What monetization changes would I recommend?

## Structure
- `data/` – raw and processed datasets
- `sql/` – table definitions and KPI views
- `notebooks/` – exploration and analysis
- `src/` – reusable data prep and metric functions
- `reports/` – stakeholder-oriented summaries and figures

---

## Database Setup

### Schemas
The database uses two schemas:

| Schema | Purpose |
|---|---|
| `raw` | Data as-is from source CSVs — no transformations |
| `curated` | Business-ready views built on top of `raw` |

### SQL Files

| File | Description |
|---|---|
| `sql/01_schema.sql` | Creates `raw` and `curated` schemas, and defines the four `raw` tables |
| `sql/02_kpi_queries.sql` | Creates KPI views in the `curated` schema |

### Curated Views

| View | Description |
|---|---|
| `curated.daily_dau` | Daily active users |
| `curated.daily_revenue` | Daily revenue and payer count |
| `curated.daily_arpu_arppu` | ARPU and ARPPU joined with DAU |
| `curated.retention_cohorts` | D1 / D7 / D30 retention rates by install cohort |
| `curated.funnel` | 4-step conversion funnel (install → session → soft spend → IAP) |

---

## psql Reference

### Database server
This project runs against a local PostgreSQL server hosted on a home network and exposed on port 5432. Replace the placeholders below with your own connection details.

| Placeholder | Description |
|---|---|
| `<database_url>` | Hostname or IP of your PostgreSQL server |
| `<database_user>` | PostgreSQL user |
| `<database_name>` | Target database name |

### Connect to the database
```bash
psql -h <database_url> -p 5432 -U <database_user> -d <database_name>
```
You will be prompted for a password. To avoid repeated prompts, create `~/.pgpass`:
```
<database_url>:5432:*:<database_user>:YOUR_PASSWORD
```
Then restrict permissions:
```bash
chmod 600 ~/.pgpass
```

### Execute a SQL file
```bash
psql -h <database_url> -p 5432 -U <database_user> -d <database_name> -f path/to/file.sql
```

### Create schemas and tables
```bash
psql -h <database_url> -p 5432 -U <database_user> -d <database_name> \
  -f sql/01_schema.sql
```

### Load CSV data
Run these in order to respect foreign key constraints:
```bash
psql -h <database_url> -p 5432 -U <database_user> -d <database_name>
```
Then inside the psql session:
```sql
\copy raw.users          FROM 'data/raw/users.csv'          WITH (FORMAT csv, HEADER true);
\copy raw.items          FROM 'data/raw/items.csv'          WITH (FORMAT csv, HEADER true);
\copy raw.sessions       FROM 'data/raw/sessions.csv'       WITH (FORMAT csv, HEADER true);
\copy raw.economy_events FROM 'data/raw/economy_events.csv' WITH (FORMAT csv, HEADER true);
```

> Note: Use absolute paths if running `\copy` from outside the project directory.

### Create KPI views
```bash
psql -h <database_url> -p 5432 -U <database_user> -d <database_name> \
  -f sql/02_kpi_queries.sql
```

### Query a view
```sql
SELECT * FROM curated.daily_dau;
SELECT * FROM curated.funnel;
```
