import hashlib
import os
import re
import time
from urllib.parse import urlsplit

import requests

import config

_session = None


def _get_session():
    global _session
    if _session is None:
        _session = requests.Session()
        _session.headers.update({"User-Agent": config.USER_AGENT})
    return _session


def events_cache_path(year):
    return os.path.join(config.RAW_HTML_DIR, str(year), "events.php.html")


def category_cache_path(year, url):
    basename = os.path.basename(urlsplit(url).path)
    if not re.fullmatch(r"[A-Za-z0-9_.\-]+", basename or ""):
        basename = hashlib.md5(url.encode("utf-8")).hexdigest() + ".html"
    return os.path.join(config.RAW_HTML_DIR, str(year), "categories", basename)


def fetch(url, cache_path):
    """Fetch a URL's HTML, using an on-disk cache so re-parsing during
    development never re-hits the network. Only sleeps/requests over the
    network on an actual cache miss."""
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            return f.read()

    session = _get_session()
    time.sleep(config.REQUEST_DELAY_SECONDS)

    last_error = None
    for attempt in range(2):
        try:
            resp = session.get(url, timeout=config.REQUEST_TIMEOUT_SECONDS)
            resp.raise_for_status()
            break
        except requests.RequestException as e:
            last_error = e
            if attempt == 0:
                time.sleep(config.REQUEST_DELAY_SECONDS)
    else:
        raise last_error

    resp.encoding = resp.encoding or "utf-8"
    text = resp.text

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(text)

    return text
