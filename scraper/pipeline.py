import argparse
import sqlite3
from datetime import datetime, timezone

import config
from db.fields import FIELDS_BY_KEY
from scraper.http import category_cache_path, events_cache_path, fetch
from scraper.parse_events import parse_events_page
from scraper.parse_results import parse_category_page


def get_connection():
    conn = sqlite3.connect(config.DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def scrape_year(conn, year):
    page_url = f"{config.BASE_URL}/{year}/results/events.php"
    try:
        html = fetch(page_url, events_cache_path(year))
    except Exception as e:
        print(f"[{year}] FAILED to fetch events page: {e}")
        return {"scraped": 0, "missing": sorted(FIELDS_BY_KEY)}

    categories = parse_events_page(html, year, page_url)
    found_keys = {c["field_key"] for c in categories}
    missing = sorted(set(FIELDS_BY_KEY) - found_keys)
    if missing:
        print(f"[{year}] missing codes: {missing}")

    # Idempotent: clear this year's existing rows before inserting fresh ones
    # (result rows cascade-delete via category_id FK).
    conn.execute("DELETE FROM category WHERE year = ?", (year,))

    scraped = 0
    for c in categories:
        cur = conn.execute(
            """
            INSERT INTO category (year, field_key, raw_code, raw_label, participant_count, result_url, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                c["year"],
                c["field_key"],
                c["raw_code"],
                c["raw_label"],
                c["participant_count"],
                c["result_url"],
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        category_id = cur.lastrowid

        if not c["result_url"]:
            continue

        try:
            result_html = fetch(c["result_url"], category_cache_path(year, c["result_url"]))
        except Exception as e:
            print(f"[{year}] {c['field_key']} FAILED to fetch results: {e}")
            continue

        rows = parse_category_page(result_html)
        for r in rows:
            conn.execute(
                """
                INSERT OR IGNORE INTO result
                    (category_id, pos, club_code, athlete_name, team_name, time_seconds, time_raw, diff_raw, spm)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    category_id,
                    r["pos"],
                    r["club_code"],
                    r["athlete_name"],
                    r["team_name"],
                    r["time_seconds"],
                    r["time_raw"],
                    r["diff_raw"],
                    r["spm"],
                ),
            )
        scraped += 1
        if len(rows) != c["participant_count"]:
            print(f"[{year}] {c['field_key']}: parsed {len(rows)} rows, expected {c['participant_count']}")

    conn.commit()
    return {"scraped": scraped, "missing": missing}


def run(years):
    conn = get_connection()
    try:
        summary = {}
        for year in years:
            print(f"--- scraping {year} ---")
            summary[year] = scrape_year(conn, year)
    finally:
        conn.close()
    return summary


def _parse_year_range(s):
    if "-" in s:
        start, end = s.split("-")
        return range(int(start), int(end) + 1)
    return [int(s)]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", type=str, default="2014-2023", help="e.g. 2014-2023 or a single year like 2019")
    args = parser.parse_args()

    result = run(_parse_year_range(args.years))

    print("\n=== summary ===")
    for year, info in result.items():
        print(f"{year}: scraped {info['scraped']}/12 categories, missing {info['missing']}")
