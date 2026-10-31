"""Place clubs that have no coordinates of their own or of their ground, where the club's English name contains the
name of a town or city in the same country (Natural Earth populated places, 1:10m). Such points are approximate (the
town, not the ground) and are flagged as 'town in name'. A UK club placed this way also gets its UK nation.
Also checks Wikidata points for English clubs against the engsoccerdata club table (Curley, GPL-3; used only as a check,
nothing from it is redistributed)."""
import math
from collections import Counter
from shapely.geometry import Point
from common import *

STOP = set("""union victoria real sporting athletic atletico santa san santo inter united city rovers town nacional independiente
olympic olimpia progreso concordia liberty hope unity star stars royal racing club deportivo deportes national central capital
colon libertad general esperanza paz progress florida america americano junior juniors rangers celtic hearts wanderers villa
alliance phoenix dynamo dinamo spartak lokomotiv torpedo zenit shakhtar metalurg energetik avangard trinidad mercedes rosario
victory federal guarani palmeira palmeiras corinthians porto vitoria belem natal bonito pilar lima""".split())
D = jload(f"{WORK}/clubs_geo.json")
P = jload(f"{GEO}/ne_10m_populated_places_simple.geojson")["features"]
UKN = {"ENG", "SCT", "WLS", "NIR"}
idx = {}
for f in P:
    p = f["properties"]; nm = norm(p["nameascii"] or p["name"])
    if len(nm) < 4 or nm in STOP:
        continue
    iso = p["adm0_a3"]
    key = (iso, nm)
    if key not in idx or (p["pop_max"] or 0) > idx[key][2]:
        idx[key] = (round(p["longitude"], 4), round(p["latitude"], 4), p["pop_max"] or 0, p["name"])
bycty = {}
for (iso, nm), v in idx.items():
    bycty.setdefault(iso, {})[nm] = v
from shapely.geometry import shape
from shapely.ops import unary_union
A1 = jload(f"{GEO}/ne_10m_admin_1_states_provinces.geojson")
nat = {}
for f in A1["features"]:
    p = f["properties"]
    if p["adm0_a3"] == "GBR":
        k = {"England": "ENG", "Scotland": "SCT", "Wales": "WLS", "Northern Ireland": "NIR"}.get(p["geonunit"])
        if k: nat.setdefault(k, []).append(shape(f["geometry"]).buffer(0))
nat = {k: unary_union(v) for k, v in nat.items()}


def uk_nation(lon, lat):
    pt = Point(lon, lat)
    best = min((g.distance(pt), k) for k, g in nat.items())
    return best[1] if best[0] < .2 else None


# Hong Kong and Macau clubs that Wikidata files under China only, with no point
for c in D["clubs"]:
    if c["iso"] == "CHN" and c["lon"] is None and c["n"]:
        if "hong kong" in norm(c["n"]): c["iso"] = "HKG"
        elif "macau" in norm(c["n"]) or "macao" in norm(c["n"]): c["iso"] = "MAC"
placed = Counter()
for c in D["clubs"]:
    if c["lon"] is not None or not c["n"] or not c["iso"]:
        continue
    look = "GBR" if c["iso"] in UKN or c["iso"] == "GBR" else c["iso"]
    cand = bycty.get(look)
    if not cand:
        continue
    toks = norm(c["n"]).split()
    best = None
    for i in range(len(toks)):
        for j in (3, 2, 1):
            nm = " ".join(toks[i:i + j])
            if nm in cand and (best is None or cand[nm][2] > best[2]):
                best = cand[nm]
    if best:
        c["lon"], c["lat"], c["src"], c["town"] = best[0], best[1], "town", best[3]
        if look == "GBR":
            n = uk_nation(best[0], best[1])
            if c["iso"] == "GBR" and n:
                c["iso"] = n
            elif c["iso"] in UKN and n and n != c["iso"]:
                c["lon"] = c["lat"] = c["src"] = c["town"] = None
                continue
        placed[c["iso"]] += 1
print("placed by town in name", sum(placed.values()), placed.most_common(12))
print("points by source", dict(Counter(c["src"] for c in D["clubs"])))

# check: Wikidata points of English clubs against engsoccerdata
try:
    import pyreadr
    E = pyreadr.read_r(f"{RAW}/engsoccerdata/data/england_club_data.rda")["england_club_data"]
    ref = {norm(t): (float(lo), float(la)) for t, la, lo in zip(E["team"], E["lat"], E["lon"]) if la == la}
    dist = []
    for c in D["clubs"]:
        if c["iso"] != "ENG" or c["src"] not in ("own", "venue") or not c["n"]:
            continue
        k = norm(re.sub(r"\b(F\.?C\.?|A\.?F\.?C\.?)$", "", c["n"]).strip())
        if k in ref:
            lo, la = ref[k]
            dist.append(6371 * math.acos(min(1, math.sin(math.radians(la)) * math.sin(math.radians(c["lat"])) + math.cos(math.radians(la)) * math.cos(math.radians(c["lat"])) * math.cos(math.radians(lo - c["lon"])))))
    dist.sort()
    D["eng_check"] = {"n": len(dist), "median_km": round(dist[len(dist) // 2], 1), "within10": sum(d <= 10 for d in dist)}
    print("engsoccerdata check", D["eng_check"])
except Exception as e:
    print("engsoccerdata check skipped", e)
jsave(D, f"{WORK}/clubs.json")
