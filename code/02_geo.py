"""Geography: a light world outline file for the page and figures (Natural Earth 1:50m, with the United Kingdom split
into England, Scotland, Wales and Northern Ireland from Natural Earth admin-1, because each has its own football
association), a present-day country and continent for every club, and place names for map labels.

Country of a club: the country (or UK nation) its point falls in, on present-day borders; if it has no point, the
present-day country Wikidata gives (P17), matched to Natural Earth by Wikidata ID. Clubs whose only Wikidata country
is a former state (Soviet Union, German Reich, Czechoslovakia, Austria-Hungary...) and that have no point are left
without a present-day country, except where the successor is unambiguous (East Germany, Kingdom of Italy...)."""
from collections import Counter
from shapely.geometry import shape, mapping, Point
from shapely.ops import unary_union
from shapely.strtree import STRtree
from common import *

UKN = {"England": ("ENG", "England"), "Scotland": ("SCT", "Scotland"), "Wales": ("WLS", "Wales"), "Northern Ireland": ("NIR", "Northern Ireland")}
SUCC = {"Q16957": "DEU", "Q41304": "DEU", "Q172579": "ITA", "Q25": "WLS", "Q26": "NIR", "Q174193": "GBR", "Q29999": "NLD",
        "Q756617": "DNK", "Q1774": "TZA", "Q219060": "PSE", "Q21": "ENG", "Q22": "SCT"}
FORMER = {"Q15180": "Soviet Union", "Q1206012": "German Reich", "Q7318": "German Reich", "Q43287": "German Empire",
          "Q33946": "Czechoslovakia", "Q207272": "Second Polish Republic", "Q34266": "Russian Empire", "Q28513": "Austria-Hungary",
          "Q36704": "Yugoslavia", "Q2305208": "Russian Empire"}


def rnd(c, k=2):
    if isinstance(c, (list, tuple)) and c and isinstance(c[0], (int, float)):
        return [round(c[0], k), round(c[1], k)]
    return [rnd(x, k) for x in c]


iso_of = lambda p: p["ISO_A3_EH"] if p.get("ISO_A3_EH") not in ("-99", None) else p["ADM0_A3"]
W50 = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")
A1 = jload(f"{GEO}/ne_10m_admin_1_states_provinces.geojson")
uk = {}
for f in A1["features"]:
    p = f["properties"]
    if p["adm0_a3"] == "GBR" and p["geonunit"] in UKN:
        uk.setdefault(p["geonunit"], []).append(shape(f["geometry"]).buffer(0))
uk = {UKN[k][0]: unary_union(v) for k, v in uk.items()}

feats, meta = [], {}
for f in W50["features"]:
    p = f["properties"]; iso = iso_of(p)
    parts = [(k, g) for k, g in uk.items()] if iso == "GBR" else [(iso, shape(f["geometry"]))]
    for k, g in parts:
        gs = g.simplify(0.04 if k in uk else 0.06, preserve_topology=True)
        if gs.is_empty:
            continue
        gm = mapping(gs)
        feats.append({"type": "Feature", "properties": {"iso": k}, "geometry": {"type": gm["type"], "coordinates": rnd(gm["coordinates"])}})
        if k in meta and (meta[k]["pop"] or 0) >= (p["POP_EST"] or 0):
            continue
        c = g.representative_point()
        nm = {"ENG": "England", "SCT": "Scotland", "WLS": "Wales", "NIR": "Northern Ireland"}.get(k, p["NAME_EN"] or p["NAME"])
        meta[k] = {"name": nm, "cont": p["CONTINENT"], "sub": p["SUBREGION"], "pop": p["POP_EST"],
                   "lx": round(c.x if k in uk else p["LABEL_X"], 2), "ly": round(c.y if k in uk else p["LABEL_Y"], 2)}
for k in uk:
    meta[k]["pop"] = None          # Natural Earth gives population for the UK as a whole only
meta["GBR"] = {"name": "United Kingdom (nation not known)", "cont": "Europe", "sub": "Northern Europe", "pop": 0, "lx": -2, "ly": 54}
for k in meta:
    meta[k]["name"] = meta[k]["name"].replace("People's Republic of China", "China").replace("United States of America", "United States")
jsave({"type": "FeatureCollection", "features": feats}, f"{DATA}/world.json")

# point in polygon on 10m outlines (UK nations from admin-1)
W10 = jload(f"{GEO}/ne_10m_admin_0_countries.geojson")
QID = {}
geoms = []
for f in W10["features"]:
    p = f["properties"]; iso = iso_of(p)
    if p.get("WIKIDATAID"):
        QID[p["WIKIDATAID"]] = iso
    if iso == "GBR":
        continue
    geoms.append((iso, shape(f["geometry"]).buffer(0)))
geoms += list(uk.items())
QID.update(SUCC)
tree = STRtree([g for _, g in geoms])


def at(lon, lat):
    pt = Point(lon, lat)
    hit = [geoms[i][0] for i in tree.query(pt) if geoms[i][1].covers(pt)]
    if hit:
        return hit[0]
    near = [(geoms[i][1].distance(pt), geoms[i][0]) for i in tree.query(pt.buffer(0.15))]
    near = [x for x in near if x[0] < 0.15]
    return min(near)[1] if near else None


D = jload(f"{WORK}/clubs_raw.json")
how = Counter(); agree = Counter()
for c in D["clubs"]:
    wd = [QID[q] for q in c["cty"] if q in QID]
    iso = at(c["lon"], c["lat"]) if c["lon"] is not None else None
    if iso:
        how["point"] += 1
        if wd:
            ok = iso in wd or (iso in uk and "GBR" in wd)
            agree["same" if ok else "different"] += 1
    elif wd:
        iso = wd[0]; how["wikidata country"] += 1
        if iso == "GBR":
            how["uk nation unknown"] += 1
    else:
        fs = [FORMER[q] for q in c["cty"] if q in FORMER]
        c["former"] = fs[0] if fs else None
        how["former state only" if fs else "none"] += 1
    iso = {"CNM": "CYP", "ESB": "CYP", "WSB": "CYP", "PSX": "PSE"}.get(iso, iso)
    if iso == "GIB" and "GIB" not in meta:
        meta["GIB"] = {"name": "Gibraltar", "cont": "Europe", "sub": "Southern Europe", "pop": 0, "lx": -5.35, "ly": 36.14}
    if iso and iso not in meta:
        how["no outline " + iso] += 1
        iso = None
    c["iso"] = iso
    c["cont"] = meta[iso]["cont"] if iso else None
print("country from", dict(how), "point vs wikidata", dict(agree))
D["how"] = dict(how); D["agree"] = dict(agree)
jsave(D, f"{WORK}/clubs_geo.json")
jsave(meta, f"{WORK}/countries.json")

P = jload(f"{GEO}/ne_10m_populated_places_simple.geojson")
cities = []
for f in P["features"]:
    p = f["properties"]; pop = p.get("pop_max") or 0
    cap = p.get("adm0cap") == 1
    if pop >= 150000 or cap:
        cities.append({"name": re.sub(r"\s+", " ", p["name"]), "lat": round(p["latitude"], 3), "lon": round(p["longitude"], 3), "pop": int(pop)})
cities.sort(key=lambda c: -c["pop"])
jsave(cities, f"{DATA}/cities.json")
print("cities", len(cities), "countries", len(meta), "world", os.path.getsize(f"{DATA}/world.json") // 1024, "KB")
