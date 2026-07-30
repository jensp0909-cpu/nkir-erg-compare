from urllib.parse import urljoin

from bs4 import BeautifulSoup

from db.fields import FIELDS_BY_CODE


def parse_events_page(html, year, page_url):
    """Parse an events.php index page into a list of dicts, one per row
    matching one of our 12 target category codes (raw_code in db/fields.py).

    Row structure on the source site: a "main" row (nr / code / participant
    count, each cell possibly wrapping an <a href> to the results page) is
    immediately followed by a 'smallrow' row holding the full Dutch label in
    a single colspan cell. Categories with no scheduled race have no <a
    href> (rendered as plain gray text) and an empty count cell.
    """
    soup = BeautifulSoup(html, "lxml")
    matched = []

    for table in soup.select("table.timeteam"):
        rows = table.find_all("tr")
        i = 0
        while i < len(rows):
            row = rows[i]
            classes = row.get("class") or []
            if "smallrow" in classes or row.find("th"):
                i += 1
                continue

            tds = row.find_all("td")
            if len(tds) < 3:
                i += 1
                continue

            code = tds[1].get_text(strip=True)
            field = FIELDS_BY_CODE.get(code)

            label = None
            consumed = 1
            if i + 1 < len(rows) and "smallrow" in (rows[i + 1].get("class") or []):
                label_td = rows[i + 1].find("td", colspan=True)
                if label_td:
                    label = label_td.get_text(strip=True)
                consumed = 2
            i += consumed

            if field is None:
                continue

            count_text = tds[2].get_text(strip=True)
            participant_count = int(count_text) if count_text.isdigit() else 0

            link = tds[1].find("a") or tds[0].find("a")
            href = link.get("href") if link else None
            result_url = urljoin(page_url, href) if href else None

            matched.append(
                {
                    "year": year,
                    "field_key": field["key"],
                    "raw_code": code,
                    "raw_label": label or "",
                    "participant_count": participant_count,
                    "result_url": result_url,
                }
            )

    return matched
