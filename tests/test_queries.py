import os
import sqlite3

import pytest

from webapp import queries

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "db", "schema.sql")


@pytest.fixture
def conn():
    c = sqlite3.connect(":memory:")
    c.row_factory = sqlite3.Row
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        c.executescript(f.read())

    c.execute(
        "INSERT INTO field (key, raw_code, display_name, gender, weight_class, age_category) "
        "VALUES ('he', 'HE', 'Heren elite', 'M', 'open', 'Elite')"
    )
    c.execute(
        "INSERT INTO field (key, raw_code, display_name, gender, weight_class, age_category) "
        "VALUES ('empty', 'EMPTY', 'Empty field', 'M', 'open', 'Gevorderde')"
    )
    c.execute(
        "INSERT INTO category (year, field_key, raw_code, raw_label, participant_count, result_url, scraped_at) "
        "VALUES (2023, 'he', 'HE', 'Heren elite', 4, 'http://example/he', '2023-01-01T00:00:00')"
    )
    category_id = c.execute("SELECT id FROM category").fetchone()["id"]

    # Sorted field is [350, 360, 360, 370] -- 360 is a deliberate tie.
    for name, t in [("Fastest", 350.0), ("Tied A", 360.0), ("Tied B", 360.0), ("Slowest", 370.0)]:
        c.execute(
            "INSERT INTO result (category_id, pos, club_code, athlete_name, team_name, time_seconds, time_raw, diff_raw, spm) "
            "VALUES (?, NULL, 'CLB', ?, NULL, ?, NULL, NULL, NULL)",
            (category_id, name, t),
        )
    c.commit()
    return c


def test_list_fields_includes_counts(conn):
    fields = queries.list_fields(conn)
    by_key = {f["key"]: f for f in fields}
    assert by_key["he"]["n"] == 4
    assert by_key["empty"]["n"] == 0


def test_get_pooled_results_sorted_ascending(conn):
    pooled = queries.get_pooled_results(conn, "he")
    assert [r["time_seconds"] for r in pooled] == [350.0, 360.0, 360.0, 370.0]


def test_rank_faster_than_everyone():
    sorted_times = [350.0, 360.0, 360.0, 370.0]
    result = queries.rank_and_percentile(sorted_times, 345.0)
    assert result == {"rank": 1, "total": 4, "percentile_faster_than": 100.0}


def test_rank_slower_than_everyone():
    sorted_times = [350.0, 360.0, 360.0, 370.0]
    result = queries.rank_and_percentile(sorted_times, 999.0)
    assert result == {"rank": 5, "total": 4, "percentile_faster_than": 0.0}


def test_rank_between_entries():
    sorted_times = [350.0, 360.0, 360.0, 370.0]
    result = queries.rank_and_percentile(sorted_times, 355.0)
    assert result == {"rank": 2, "total": 4, "percentile_faster_than": 75.0}


def test_rank_exact_tie():
    # Matching the tied 360.0 time: one entry (350.0) is strictly faster,
    # so rank is 2; the two 360.0 entries don't count as "beaten".
    sorted_times = [350.0, 360.0, 360.0, 370.0]
    result = queries.rank_and_percentile(sorted_times, 360.0)
    assert result == {"rank": 2, "total": 4, "percentile_faster_than": 25.0}


def test_compute_comparison_end_to_end(conn):
    result = queries.compute_comparison(conn, "he", 355.0, k=5)
    assert result["rank"] == 2
    assert result["total"] == 4
    assert result["percentile_faster_than"] == 75.0
    assert [r["athlete_name"] for r in result["nearest_faster"]] == ["Fastest"]
    assert [r["athlete_name"] for r in result["nearest_slower"]] == ["Tied A", "Tied B", "Slowest"]


def test_compute_comparison_empty_field_returns_none(conn):
    assert queries.compute_comparison(conn, "empty", 400.0) is None
