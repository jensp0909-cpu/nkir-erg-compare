import argparse

import config
from db.fields import FIELDS_BY_KEY
from scraper.http import category_cache_path, events_cache_path, fetch
from scraper.parse_events import parse_events_page
from scraper.parse_results import parse_category_page


def inspect_year(year):
    page_url = f"{config.BASE_URL}/{year}/results/events.php"
    html = fetch(page_url, events_cache_path(year))
    categories = parse_events_page(html, year, page_url)
    by_key = {c["field_key"]: c for c in categories}

    print(f"\n=== NKIR {year}: {len(categories)} of 12 target fields found ===\n")
    print(f"{'key':6} {'code':6} {'label':30} {'n':>4}  result_url")
    for key in FIELDS_BY_KEY:
        c = by_key.get(key)
        if c is None:
            print(f"{key:6} {'MISSING':6}")
            continue
        print(f"{key:6} {c['raw_code']:6} {c['raw_label']:30} {c['participant_count']:>4}  {c['result_url'] or '(no scheduled race)'}")

    missing = set(FIELDS_BY_KEY) - set(by_key)
    if missing:
        print(f"\n!! MISSING target codes for {year}: {sorted(missing)} -- check for a code alias.")

    print("\n--- sample parse of each scheduled category's results table ---")
    for key, c in by_key.items():
        if not c["result_url"]:
            print(f"{key}: no scheduled race, skipped")
            continue
        result_html = fetch(c["result_url"], category_cache_path(year, c["result_url"]))
        rows = parse_category_page(result_html)
        ok = len(rows) == c["participant_count"]
        flag = "" if ok else "  ** row count mismatch vs participant_count **"
        print(f"{key}: parsed {len(rows)} rows (expected {c['participant_count']}){flag}")
        if rows:
            r0 = rows[0]
            print(f"    winner: {r0['athlete_name']!r} ({r0['club_code']}) {r0['time_raw']} -> {r0['time_seconds']}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2023)
    args = parser.parse_args()
    inspect_year(args.year)
