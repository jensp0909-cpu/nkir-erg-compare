# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A local website comparing a rower's 2000m indoor-rowing erg time against historical NKIR (Nederlands Kampioenschap Indoor Roeien) results in the same category. Data is scraped once from Time-Team (`regatta.time-team.nl/nkir/{year}/results/`) into a local SQLite database; a small Flask app serves the comparison UI against that database.

**Scope is intentionally narrow**: only 12 individual senior/elite category codes (defined in `db/fields.py`) across seasons **2018–2023**. Years before 2018 use inconsistent category naming/page templates on the source site (verified by inspection, not guessed) and were excluded — see the comments in `config.py` and `db/fields.py` for what was checked.

## Commands

```
py -m venv .venv                                  # one-time setup
.venv\Scripts\python.exe -m pip install -r requirements.txt

.venv\Scripts\python.exe -m db.init_db             # create data/nkir.db + seed the 12 fields
.venv\Scripts\python.exe -m scraper.inspect_one_year --year 2023   # human-checkable single-year dry run
.venv\Scripts\python.exe -m scraper.pipeline --years 2018-2023     # full scrape (idempotent, re-runnable)

.venv\Scripts\python.exe -m pytest -q              # run all tests
.venv\Scripts\python.exe -m pytest tests/test_queries.py -q   # run a single test file

.venv\Scripts\python.exe run.py                    # start the dev server at http://127.0.0.1:5000/
```

## Architecture

- **`config.py`** — single source of truth for the source URL, year range, DB path, and scrape politeness settings (rate limit, User-Agent).
- **`db/fields.py`** — the fixed list of 12 target category codes (`raw_code`, e.g. `HE`, `DE`, `LHSB`) mapped to canonical `field.key` slugs. The site uses `D` for Dames (women) and `LH`/`LD` for lightweight men/women — not the `V`/`LM`/`LV` naming one might expect; this was confirmed against real scraped HTML, not assumed.
- **`db/schema.sql`** — `field` (the 12 canonical categories) → `category` (one row per scraped year+field, with `result_url`, nullable when no race was scheduled that year) → `result` (one row per finisher, `time_seconds` NULL for DNF/DNS entries).
- **`scraper/`** — `http.py` (disk-cached, rate-limited fetcher — re-parsing during development never re-hits the network), `parse_events.py` (extracts the 12 target categories from a year's index page), `parse_results.py` (parses a category's finisher table; **column positions are derived from the `<thead>` at runtime, not hardcoded** — some years insert extra 500m/1000m/1500m split columns before the finish time, and some years render an unrelated `.timeteam.home` info widget before the real results table), `pipeline.py` (orchestrates the full multi-year scrape, idempotent per year).
- **`common/time_parse.py`** — shared time string ⇄ seconds conversion, used both for scraped Dutch-format times (`06:02,0`) and user-submitted form input.
- **`webapp/queries.py`** — all SQL and the rank/percentile/nearest-times logic (pooled across all scraped years per field), independent of Flask so it's unit-testable against an in-memory fixture DB.
- **`webapp/`** — Flask app factory (`__init__.py`) + routes (`GET /`, `GET /fields` JSON, `POST /compare`) + Jinja2 templates. Server-rendered, no separate frontend build.

## Git Workflow

- Commit work to git regularly as you go, not just at the end of a task — don't let uncommitted work pile up.
- Write clean, descriptive commit messages that explain why a change was made, not just what changed.
- Push commits to GitHub regularly so work is backed up and never lost to a local-only state.
- Before any destructive git operation (reset --hard, force push, etc.), confirm with the user first.
