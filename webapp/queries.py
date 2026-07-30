import bisect
import sqlite3

import config

_AGE_ORDER = {"Elite": 0, "Gevorderde": 1, "Senior B": 2}


def get_connection():
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def list_fields(conn):
    """All 12 fields with how many comparable (timed) results each has,
    sorted for a sensible dropdown grouping: gender, then weight class,
    then age category (Elite -> Gevorderde -> Senior B)."""
    rows = conn.execute(
        """
        SELECT f.key, f.display_name, f.gender, f.weight_class, f.age_category,
               COUNT(r.id) AS n
        FROM field f
        LEFT JOIN category c ON c.field_key = f.key
        LEFT JOIN result r ON r.category_id = c.id AND r.time_seconds IS NOT NULL
        GROUP BY f.key
        """
    ).fetchall()
    fields = [dict(r) for r in rows]
    fields.sort(key=lambda f: (f["gender"], f["weight_class"], _AGE_ORDER.get(f["age_category"], 99)))
    return fields


def get_field(conn, field_key):
    row = conn.execute("SELECT * FROM field WHERE key = ?", (field_key,)).fetchone()
    return dict(row) if row else None


def get_pooled_results(conn, field_key):
    """All timed results for a field, pooled across every scraped year,
    sorted fastest first."""
    rows = conn.execute(
        """
        SELECT r.time_seconds, r.athlete_name, r.club_code, r.team_name, c.year
        FROM result r
        JOIN category c ON c.id = r.category_id
        WHERE c.field_key = ? AND r.time_seconds IS NOT NULL
        ORDER BY r.time_seconds ASC
        """,
        (field_key,),
    ).fetchall()
    return [dict(r) for r in rows]


def rank_and_percentile(sorted_times, user_seconds):
    """sorted_times: ascending list of seconds. Competition-style rank (ties
    share the count of strictly-faster times); percentile is the share of
    the field strictly slower than the user (ties don't count as beaten)."""
    total = len(sorted_times)
    if total == 0:
        return None
    rank = bisect.bisect_left(sorted_times, user_seconds) + 1
    slower_count = total - bisect.bisect_right(sorted_times, user_seconds)
    return {
        "rank": rank,
        "total": total,
        "percentile_faster_than": (slower_count / total) * 100,
    }


def nearest(sorted_rows, user_seconds, k=5):
    """k closest results faster than, and k closest slower than/equal to,
    user_seconds. sorted_rows must already be sorted ascending by
    time_seconds (as returned by get_pooled_results)."""
    times = [r["time_seconds"] for r in sorted_rows]
    idx = bisect.bisect_left(times, user_seconds)
    return {
        "faster": sorted_rows[max(0, idx - k):idx],
        "slower": sorted_rows[idx:idx + k],
    }


def compute_comparison(conn, field_key, user_seconds, k=5):
    pooled = get_pooled_results(conn, field_key)
    if not pooled:
        return None
    times = [r["time_seconds"] for r in pooled]
    result = rank_and_percentile(times, user_seconds)
    nb = nearest(pooled, user_seconds, k=k)
    result["nearest_faster"] = nb["faster"]
    result["nearest_slower"] = nb["slower"]
    return result
