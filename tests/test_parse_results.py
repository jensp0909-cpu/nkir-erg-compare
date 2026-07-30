import os

from scraper.parse_results import parse_category_page

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "category_2023_he.html")


def _load():
    with open(FIXTURE, "r", encoding="utf-8") as f:
        return f.read()


def test_parses_known_winning_row():
    rows = parse_category_page(_load())
    assert len(rows) == 8  # HE 2023 had 8 entries

    first = rows[0]
    assert first["pos"] == 1
    assert first["club_code"] == "NER"
    assert first["athlete_name"] == "Isak Verkaik"
    assert first["team_name"] == "Nereus 2"
    assert first["time_raw"] == "06:02,0"
    assert first["time_seconds"] == 362.0
    assert first["spm"] == 37.0


def test_all_rows_have_names_and_times():
    rows = parse_category_page(_load())
    for row in rows:
        assert row["athlete_name"]
        assert row["time_seconds"] is not None


FIXTURE_2021_SPLITS = os.path.join(os.path.dirname(__file__), "fixtures", "category_2021_he_with_splits.html")


def test_parses_finish_time_not_split_time_when_extra_columns_present():
    # 2021 pages insert 500m/1000m/1500m split columns before 'finish',
    # and also render an unrelated '.timeteam.home' table before the real
    # results table -- both must be handled correctly.
    with open(FIXTURE_2021_SPLITS, "r", encoding="utf-8") as f:
        rows = parse_category_page(f.read())

    assert len(rows) == 10
    first = rows[0]
    assert first["athlete_name"] == "Pieter van Veen"
    assert first["club_code"] == "TRI"
    assert first["team_name"] == "Triton"
    assert first["time_raw"] == "05:58,6"
    assert first["time_seconds"] == 358.6
    assert first["spm"] == 38.2
