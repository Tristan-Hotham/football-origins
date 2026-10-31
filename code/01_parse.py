"""Parse the QLever TSV of Wikidata football clubs into one record per club.

Rules
- One record per Wikidata item (?c). Rows repeat per type, venue and country; values are pooled.
- Inception: the earliest parsable year. A date of 1 January is treated as year only (Wikidata stores a bare year that way).
- Dissolved: the latest parsable year.
- Point: the club's own coordinates (P625) if any, else its home venue's (the first venue in the query result).
- Left out: probable Australian rules football clubs in Australia (see AUSRULES), national and regional representative teams, beach soccer and futsal sides, and reserve, youth, academy and
  'B' teams, which are teams of a club rather than clubs (they would repeat the parent's founding year).
"""
import csv, sys
from collections import defaultdict, Counter
from common import *

csv.field_size_limit(sys.maxsize)
POINT = re.compile(r"POINT\(([-\d.eE+]+) ([-\d.eE+]+)\)")
DATE = re.compile(r'^"?(-?\+?\d{1,4})-(\d\d)-(\d\d)T')


def val(v):
    v = (v or "").strip()
    if v.startswith("<" + WD):
        return v[len(WD) + 1:-1]
    m = re.match(r'^"(.*)"(@[\w-]+|\^\^<[^>]+>)?$', v, re.S)
    if m:
        return m.group(1).replace('\\"', '"').replace("\\\\", "\\")
    return v


def date(v):
    m = DATE.match(v or "")
    if not m:
        return None
    y = int(m.group(1).lstrip("+"))
    if y < 1000:
        return None
    return y, m.group(2), m.group(3)


def point(v):
    m = POINT.search(v or "")
    if not m:
        return None
    lon, lat = float(m.group(1)), float(m.group(2))
    if not (-180 <= lon <= 180 and -90 <= lat <= 90):
        return None
    return round(lon, 4), round(lat, 4)


EXCL = [
    ("national team", re.compile(r"\bnational\b.*\bteam\b|\bnational (association )?football|\bnational under|\bselecci[oó]n\b|\bXI\b", re.I)),
    ("beach or futsal", re.compile(r"beach soccer|\(beach|futsal|\bfutebol de praia\b", re.I)),
    ("reserve or youth team", re.compile(r"\breserves?\b|development squad|\bunder[- ]?\d\d\b|\bU-?\d\ds?\b|and academy|\bB team\b|(?<!^Willem)\s(II|B|C|2)$", re.I)),
]
# Wikidata types many Australian rules football clubs as association football clubs; in Australia a spelt-out
# 'Football Club', 'Football Netball Club' or 'Australian Football Club' without a soccer word is treated as Australian rules.
AUSRULES = re.compile(r"Football (Netball|and Netball|& Netball) Club|Football Club$|\bFNC\b|Australian Football", re.I)
SOCCERW = re.compile(r"soccer|united|city|rangers|wanderers|olympic|hellas|juventus|\bS\.?C\.?\b|\bF\.?C\.?\b|A\.?F\.?C|women", re.I)
EXCL_TYPES = {"Q135408445": "national team", "Q116953048": "beach or futsal"}

rows = list(csv.reader(open(f"{RAW}/clubs.tsv", encoding="utf-8"), delimiter="\t", quoting=csv.QUOTE_NONE))
head = [h.lstrip("?") for h in rows[0]]
C = defaultdict(lambda: {"l": "", "inc": [], "dis": [], "pt": None, "vpt": [], "cty": [], "sl": 0, "types": set()})
for r in rows[1:]:
    r = dict(zip(head, [val(x) for x in r + [""] * (len(head) - len(r))]))
    c = C[r["c"]]
    if r["l"] and not c["l"]:
        c["l"] = r["l"]
    d = date(r["inc"])
    if d: c["inc"].append(d)
    d = date(r["dis"])
    if d: c["dis"].append(d)
    p = point(r["coord"])
    if p and not c["pt"]: c["pt"] = p
    p = point(r["vcoord"])
    if p and p not in c["vpt"]: c["vpt"].append(p)
    if r["country"] and r["country"] not in c["cty"]: c["cty"].append(r["country"])
    c["sl"] = max(c["sl"], int(r["sl"] or 0))
    c["types"].add(r["type"])
print("rows", len(rows) - 1, "items", len(C))

out, drop = [], Counter()
for q, c in C.items():
    why = next((EXCL_TYPES[t] for t in c["types"] if t in EXCL_TYPES and len(c["types"]) == 1), None)
    if not why and c["l"]:
        why = next((k for k, rx in EXCL if rx.search(c["l"])), None)
    if not why and "Q408" in c["cty"] and c["l"] and AUSRULES.search(c["l"]) and not SOCCERW.search(c["l"]):
        why = "probable Australian rules club"
    if why:
        drop[why] += 1
        continue
    inc = min(c["inc"]) if c["inc"] else None
    dis = max(c["dis"]) if c["dis"] else None
    pt, src = (c["pt"], "own") if c["pt"] else ((c["vpt"][0], "venue") if c["vpt"] else (None, None))
    out.append({"q": q, "n": c["l"], "y": inc[0] if inc else None, "yonly": bool(inc and inc[1:] == ("01", "01")),
                "date": f"{inc[0]}-{inc[1]}-{inc[2]}" if inc and inc[1:] != ("01", "01") else None,
                "d": dis[0] if dis else None, "lon": pt[0] if pt else None, "lat": pt[1] if pt else None, "src": src,
                "cty": c["cty"], "sl": c["sl"], "types": sorted(c["types"])})
print("kept", len(out), "dropped", dict(drop))
jsave({"n_rows": len(rows) - 1, "n_items": len(C), "dropped": dict(drop), "clubs": out}, f"{WORK}/clubs_raw.json")
