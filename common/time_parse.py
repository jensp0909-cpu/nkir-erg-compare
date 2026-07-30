import re

# Matches "M:SS", "MM:SS", "H:MM:SS", optionally with a ",D" or ".D" fractional
# seconds suffix -- covers both the site's scraped Dutch format ("06:02,0")
# and user-typed input ("6:02.0", "6:02,0", "6:02").
_TIME_RE = re.compile(
    r"^\s*(?:(?P<h>\d+):)?(?P<m>\d{1,2}):(?P<s>\d{2})(?:[.,](?P<frac>\d+))?\s*$"
)


def parse_time(raw):
    """Parse a time string into total seconds (float). Returns None for a
    blank/missing value. Raises ValueError if raw is non-empty but doesn't
    match a recognized time format (e.g. 'DNF')."""
    if raw is None:
        return None
    raw = raw.strip()
    if not raw:
        return None

    match = _TIME_RE.match(raw)
    if not match:
        raise ValueError(f"Unrecognized time format: {raw!r}")

    hours = int(match.group("h")) if match.group("h") else 0
    minutes = int(match.group("m"))
    seconds = int(match.group("s"))
    frac = match.group("frac")
    fraction = int(frac) / (10 ** len(frac)) if frac else 0.0

    return hours * 3600 + minutes * 60 + seconds + fraction


# Alias kept for readability at scraper call sites -- same format/behavior.
parse_dutch_time = parse_time


def format_seconds(total_seconds):
    """Format seconds as 'M:SS.D' for display."""
    if total_seconds is None:
        return ""
    total_seconds = float(total_seconds)
    minutes = int(total_seconds // 60)
    seconds = total_seconds - minutes * 60
    return f"{minutes}:{seconds:04.1f}"
