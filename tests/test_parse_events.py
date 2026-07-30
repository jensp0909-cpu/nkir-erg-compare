import os

from db.fields import FIELDS_BY_KEY
from scraper.parse_events import parse_events_page

FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "events_2023.html")
PAGE_URL = "https://regatta.time-team.nl/nkir/2023/results/events.php"


def _load():
    with open(FIXTURE, "r", encoding="utf-8") as f:
        return f.read()


def test_matches_all_12_target_fields():
    rows = parse_events_page(_load(), 2023, PAGE_URL)
    found_keys = {r["field_key"] for r in rows}
    assert found_keys == set(FIELDS_BY_KEY)


def test_resolves_absolute_result_url():
    rows = parse_events_page(_load(), 2023, PAGE_URL)
    he = next(r for r in rows if r["field_key"] == "he")
    assert he["result_url"] == (
        "https://regatta.time-team.nl/nkir/2023/results/"
        "ebd0a8963-c6d4-4ffc-aff4-549b637afe35.php"
    )
    assert he["participant_count"] == 8


def test_unscheduled_category_has_no_url():
    rows = parse_events_page(_load(), 2023, PAGE_URL)
    lme = next(r for r in rows if r["field_key"] == "lme")
    assert lme["result_url"] is None
    assert lme["participant_count"] == 0
