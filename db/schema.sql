CREATE TABLE IF NOT EXISTS field (
    key            TEXT PRIMARY KEY,
    raw_code       TEXT NOT NULL UNIQUE,
    display_name   TEXT NOT NULL,
    gender         TEXT NOT NULL,          -- 'M' / 'V'
    weight_class   TEXT NOT NULL,          -- 'open' / 'light'
    age_category   TEXT NOT NULL           -- 'Elite' / 'Gevorderde' / 'Senior B'
);

CREATE TABLE IF NOT EXISTS code_alias (
    id             INTEGER PRIMARY KEY,
    year           INTEGER NOT NULL,
    alias_code     TEXT NOT NULL,
    field_key      TEXT NOT NULL REFERENCES field(key),
    UNIQUE(year, alias_code)
);

CREATE TABLE IF NOT EXISTS category (
    id                  INTEGER PRIMARY KEY,
    year                INTEGER NOT NULL,
    field_key           TEXT NOT NULL REFERENCES field(key),
    raw_code            TEXT NOT NULL,
    raw_label           TEXT NOT NULL,
    participant_count   INTEGER,
    result_url          TEXT,             -- NULL when no race was scheduled that year (e.g. LHE/LDE some years)
    scraped_at          TEXT NOT NULL,
    UNIQUE(year, field_key)
);
CREATE INDEX IF NOT EXISTS idx_category_year      ON category(year);
CREATE INDEX IF NOT EXISTS idx_category_field_key ON category(field_key);

CREATE TABLE IF NOT EXISTS result (
    id            INTEGER PRIMARY KEY,
    category_id   INTEGER NOT NULL REFERENCES category(id) ON DELETE CASCADE,
    pos           INTEGER,
    club_code     TEXT,
    athlete_name  TEXT NOT NULL,
    team_name     TEXT,
    time_seconds  REAL,
    time_raw      TEXT,
    diff_raw      TEXT,
    spm           REAL,
    UNIQUE(category_id, pos, athlete_name)
);
CREATE INDEX IF NOT EXISTS idx_result_category      ON result(category_id);
CREATE INDEX IF NOT EXISTS idx_result_category_time ON result(category_id, time_seconds);
