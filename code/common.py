"""Shared paths and helpers for the football-origins project.

Raw inputs (read in place, never modified):
  /home/claude/newdata/raw2/clubs.tsv   QLever query result on Wikidata (CC0), retrieved 2026: every item that is an
      instance of association football club (Q476028) or a subclass, with columns
      ?c item, ?l English label, ?inc inception (P571), ?dis dissolved (P576), ?coord own coordinates (P625),
      ?vcoord coordinates of its home venue (P115), ?country (P17), ?sl number of sitelinks, ?type instance of (P31).
      One row per combination, so a club can repeat.
  /home/claude/newdata/raw/geo/ne_50m_admin_0_countries.geojson, ne_10m_admin_0_countries.geojson,
      ne_10m_admin_1_states_provinces.geojson, ne_10m_populated_places_simple.geojson (Natural Earth, public domain)
  /home/claude/newdata/raw2/engsoccerdata/data/england_club_data.rda (engsoccerdata, used only as a check)
"""
import json, gzip, os, re, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = os.environ.get("FOOT_RAW", "/home/claude/newdata/raw2")
GEO = os.environ.get("FOOT_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("FOOT_FONTS", "/home/claude/ref/fonts")
DATA = os.path.join(ROOT, "data")
WORK = os.path.join(os.environ.get("FOOTTMP", "/dev/shm/football"), "work")   # intermediates live in memory, not in the repo
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "football-origins"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
DOI = "{{DOI}}"            # filled in by the publisher
BLOG = "https://blog.tristanhotham.com/2026/10/31/football-origins/"      # filled in by the publisher
RETRIEVED = "2026"
START = 1857               # Sheffield FC; the animation starts here
END = 2026
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")
WD = "http://www.wikidata.org/entity/"


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def dash(v):
    """Remove em and en dashes and double hyphens from text taken from Wikidata (house style)."""
    if isinstance(v, str):
        v = re.sub(r"(\d)\s*[–—]\s*(\d)", r"\1 to \2", v)
        v = v.replace(" — ", ", ").replace("—", ", ").replace(" – ", ", ").replace("–", "-")
        while "--" in v:
            v = v.replace("--", "-")
        return v
    if isinstance(v, list):
        return [dash(x) for x in v]
    if isinstance(v, dict):
        return {k: dash(x) for k, x in v.items()}
    return v


def jsave(obj, path, indent=None):
    if os.path.abspath(path).startswith(DATA):
        obj = dash(obj)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def norm(s):
    s = unicodedata.normalize("NFKD", str(s))
    s = "".join(ch for ch in s if not unicodedata.combining(ch)).lower()
    return re.sub(r"[\W_]+", " ", s).strip()


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "f1": return f"{float(v):.1f}"
    raise ValueError(f)
