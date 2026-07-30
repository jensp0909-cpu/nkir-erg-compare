from bs4 import BeautifulSoup

from common.time_parse import parse_dutch_time


def _find_results_table(soup):
    """Pick the actual results table. Some years render an extra
    <table class='timeteam home'> info widget (weigh-in notices, etc.)
    before the real results table -- both carry the 'timeteam' class, so a
    plain '.timeteam' selector can grab the wrong one. The real results
    table is the one with a <thead>."""
    for table in soup.select("table.timeteam"):
        if table.find("thead"):
            return table
    return None


def _column_start_index(header_row, predicate):
    """Find the 0-indexed td position where a header column (identified by
    predicate) starts, accounting for colspan on earlier columns. Column
    layouts vary by year (some years add 500m/1000m/1500m split columns
    before 'finish'), so positions must be derived from the header rather
    than hardcoded."""
    idx = 0
    for th in header_row.find_all("th"):
        if predicate(th):
            return idx
        idx += int(th.get("colspan", 1))
    return None


def _is_finish_column(th):
    classes = th.get("class") or []
    return "finish" in classes or "finish" in th.get_text(strip=True).lower()


def _is_verschil_column(th):
    classes = th.get("class") or []
    return "number" in classes or "verschil" in th.get_text(strip=True).lower()


def parse_category_page(html):
    """Parse a category result page into a list of finisher dicts.

    Each finisher is rendered as a <tbody> containing two <tr>s: a "main"
    row (pos / club code / athlete name / ... / finish time / ... /
    verschil) and a 'smallrow' detail row (team name / ... / stroke rate).
    The detail row always has exactly one fewer column than the main row
    (it omits the trailing rowspan'd chart-link cell), so team name sits at
    a fixed index (2) and stroke rate is always the last cell. See
    tests/fixtures for real captured examples.
    """
    soup = BeautifulSoup(html, "lxml")
    table = _find_results_table(soup)
    if table is None:
        return []

    header_row = table.find("thead").find("tr")
    finish_idx = _column_start_index(header_row, _is_finish_column)
    verschil_idx = _column_start_index(header_row, _is_verschil_column)
    if finish_idx is None or verschil_idx is None:
        return []

    rows = []
    for tbody in table.find_all("tbody"):
        trs = tbody.find_all("tr")
        if not trs:
            continue

        main_tds = trs[0].find_all("td")
        if len(main_tds) <= max(finish_idx, verschil_idx):
            continue

        pos_text = main_tds[0].get_text(strip=True).rstrip(".")
        pos = int(pos_text) if pos_text.isdigit() else None

        club_link = main_tds[1].find("a")
        club_code = (club_link.get_text(strip=True) if club_link else main_tds[1].get_text(strip=True)) or None

        name_link = main_tds[2].find("a")
        athlete_name = (name_link.get_text(strip=True) if name_link else main_tds[2].get_text(strip=True))
        if not athlete_name:
            continue

        time_raw = main_tds[finish_idx].get_text(strip=True) or None
        diff_raw = main_tds[verschil_idx].get_text(strip=True) or None

        team_name = None
        spm = None
        if len(trs) > 1:
            detail_tds = trs[1].find_all("td")
            if len(detail_tds) >= 3:
                team_name = detail_tds[2].get_text(strip=True) or None
            if detail_tds:
                spm_text = detail_tds[-1].get_text(strip=True)
                spm_value = spm_text.split("spm")[0].strip() if "spm" in spm_text else spm_text
                try:
                    spm = float(spm_value) if spm_value else None
                except ValueError:
                    spm = None

        try:
            time_seconds = parse_dutch_time(time_raw)
        except ValueError:
            time_seconds = None

        rows.append(
            {
                "pos": pos,
                "club_code": club_code,
                "athlete_name": athlete_name,
                "team_name": team_name,
                "time_seconds": time_seconds,
                "time_raw": time_raw,
                "diff_raw": diff_raw,
                "spm": spm,
            }
        )

    return rows
