import os

BASE_URL = "https://regatta.time-team.nl/nkir"
# 2018-2023 inclusive. Years before 2018 use inconsistent/legacy category
# naming and page templates (verified by inspecting real scraped HTML across
# 2014-2023; see scraper/pipeline.py run history) -- 2018 is where the
# modern HE/DE/HG/DG/HSB/DSB (+ LH/LD lightweight) naming and page template
# become stable across all 12 target fields.
YEARS = range(2018, 2024)

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "nkir.db")
RAW_HTML_DIR = os.path.join(DATA_DIR, "raw_html")

REQUEST_DELAY_SECONDS = 1.5
USER_AGENT = "nkir-ergo-compare/0.1 (personal hobby project; contact: jensp0909@gmail.com)"
REQUEST_TIMEOUT_SECONDS = 15
