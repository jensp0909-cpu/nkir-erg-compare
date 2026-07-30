# The 12 individual senior/elite NKIR categories this project tracks.
# key: canonical slug used throughout the DB and app (our own naming, from the user's original request).
# raw_code: the code as it ACTUALLY appears on regatta.time-team.nl (verified against real 2023 HTML).
#   The site uses 'D' for Dames (women) and 'LH'/'LD' for Lichte Heren/Lichte Dames (lightweight men/women),
#   not the 'V'/'LM'/'LV' the user's shorthand used -- confirmed with the user this mapping is correct.
# gender: 'M' or 'V'. weight_class: 'open' or 'light'. age_category: 'Elite' | 'Gevorderde' | 'Senior B'.

FIELDS = [
    {"key": "he", "raw_code": "HE", "display_name": "Heren elite", "gender": "M", "weight_class": "open", "age_category": "Elite"},
    {"key": "hg", "raw_code": "HG", "display_name": "Heren gevorderde", "gender": "M", "weight_class": "open", "age_category": "Gevorderde"},
    {"key": "hsb", "raw_code": "HSB", "display_name": "Heren senioren B", "gender": "M", "weight_class": "open", "age_category": "Senior B"},
    {"key": "ve", "raw_code": "DE", "display_name": "Dames elite", "gender": "V", "weight_class": "open", "age_category": "Elite"},
    {"key": "vg", "raw_code": "DG", "display_name": "Dames gevorderde", "gender": "V", "weight_class": "open", "age_category": "Gevorderde"},
    {"key": "vsb", "raw_code": "DSB", "display_name": "Dames senioren B", "gender": "V", "weight_class": "open", "age_category": "Senior B"},
    {"key": "lme", "raw_code": "LHE", "display_name": "Lichte heren elite", "gender": "M", "weight_class": "light", "age_category": "Elite"},
    {"key": "lmg", "raw_code": "LHG", "display_name": "Lichte heren gevorderde", "gender": "M", "weight_class": "light", "age_category": "Gevorderde"},
    {"key": "lmsb", "raw_code": "LHSB", "display_name": "Lichte heren senioren B", "gender": "M", "weight_class": "light", "age_category": "Senior B"},
    {"key": "lve", "raw_code": "LDE", "display_name": "Lichte dames elite", "gender": "V", "weight_class": "light", "age_category": "Elite"},
    {"key": "lvg", "raw_code": "LDG", "display_name": "Lichte dames gevorderde", "gender": "V", "weight_class": "light", "age_category": "Gevorderde"},
    {"key": "lvsb", "raw_code": "LDSB", "display_name": "Lichte dames senioren B", "gender": "V", "weight_class": "light", "age_category": "Senior B"},
]

FIELDS_BY_CODE = {f["raw_code"]: f for f in FIELDS}
FIELDS_BY_KEY = {f["key"]: f for f in FIELDS}
