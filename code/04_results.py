"""All numbers (data/results.json), the reusable tables in data/, and the page data (data/site.json embedded in the
page; data/points.json loaded by it)."""
import csv, math, statistics
from collections import Counter, defaultdict
from common import *

D = jload(f"{WORK}/clubs.json"); M = jload(f"{WORK}/countries.json")
CONT = ["Europe", "South America", "North America", "Africa", "Asia", "Oceania"]
SEAS = {"MDV": "Asia", "IOT": "Asia"}


def cont(c):
    k = c.get("cont")
    if k == "Seven seas (open ocean)":
        return SEAS.get(c["iso"], "Africa")
    return k if k in CONT else None


SHEF = (-1.4659, 53.3811)


def km(lon, lat, o=SHEF):
    a = math.radians
    s = math.sin(a(lat)) * math.sin(a(o[1])) + math.cos(a(lat)) * math.cos(a(o[1])) * math.cos(a(lon - o[0]))
    return 6371 * math.acos(max(-1, min(1, s)))


clubs = []
bad_future = []
for c in D["clubs"]:
    if c["y"] and c["y"] > END:
        bad_future.append(c["n"]); c["y"] = None
    if c["d"] and c["y"] and c["d"] < c["y"]:
        c["d_bad"] = True
    c["k"] = cont(c)
    c["early"] = bool(c["y"] and c["y"] < START)
    clubs.append(c)
N = len(clubs)
dated = [c for c in clubs if c["y"]]
okd = [c for c in dated if not c["early"]]            # dated 1857 or later: used for every time analysis
pts = [c for c in clubs if c["lon"] is not None]
lab = lambda c: c["n"] or f"(no English label) {c['q']}"
R = {"meta": {"slug": SLUG, "page": PAGE, "repo": REPO, "doi": DOI, "blog": BLOG, "retrieved": RETRIEVED, "start": START, "end": END}}
src = Counter(c["src"] for c in clubs)
R["source"] = {"n_rows": D["n_rows"], "n_items": D["n_items"], "dropped": D["dropped"], "n_dropped": sum(D["dropped"].values()),
               "n": N, "n_dated": len(dated), "dated_pct": 100 * len(dated) / N, "n_ok": len(okd), "n_early": sum(c["early"] for c in clubs),
               "n_future": len(bad_future), "yonly_pct": 100 * sum(c["yonly"] for c in dated) / len(dated),
               "n_point": len(pts), "point_pct": 100 * len(pts) / N, "n_own": src["own"], "n_venue": src["venue"], "n_town": src["town"],
               "n_dated_point": sum(1 for c in okd if c["lon"] is not None),
               "n_country": sum(1 for c in clubs if c["iso"]), "n_no_country": sum(1 for c in clubs if not c["iso"]),
               "n_former": sum(1 for c in clubs if c.get("former")), "n_uk_unknown": sum(1 for c in clubs if c["iso"] == "GBR"),
               "n_nolabel": sum(1 for c in clubs if not c["n"]),
               "agree_pct": 100 * D["agree"]["same"] / (D["agree"]["same"] + D["agree"]["different"]), "n_agree_checked": D["agree"]["same"] + D["agree"]["different"],
               "eng_check": D.get("eng_check")}
R["source"]["early"] = [{"n": lab(c), "y": c["y"], "iso": c["iso"], "q": c["q"]} for c in sorted([c for c in clubs if c["early"]], key=lambda c: c["y"])]

# spot checks of famous clubs
SPOT = [("Q18491", "Sheffield F.C.", 1857), ("Q1257402", "Hallam F.C.", 1860), ("Q19598", "Notts County F.C.", 1862), ("Q18736", "Stoke City F.C.", 1863),
        ("Q18529", "Wrexham A.F.C.", 1864), ("Q19490", "Nottingham Forest F.C.", 1865), ("Q852753", "Queen's Park F.C.", 1867),
        ("Q1257402", "Hallam F.C.", 1860)]
byq = {c["q"]: c for c in clubs}
byname = defaultdict(list)
for c in clubs:
    byname[c["n"]].append(c)


def find(name):
    v = [c for c in byname.get(name, []) if c["y"]]
    return max(v, key=lambda c: c["sl"]) if v else None


FAMOUS = ["Sheffield F.C.", "Hallam F.C.", "Notts County F.C.", "Stoke City F.C.", "Wrexham A.F.C.", "Nottingham Forest F.C.", "Queen's Park F.C.",
          "Cliftonville F.C.", "Lima Cricket and Football Club", "Royal Antwerp F.C.", "Grasshopper Club Zürich", "Hamburger SV", "Quilmes Atlético Club",
          "Club Atlético Peñarol", "Recreativo de Huelva", "Genoa CFC", "Sparta Rotterdam", "AC Sparta Prague", "Club Nacional de Football",
          "Al Ahly SC", "Mohun Bagan AC", "Accra Hearts of Oak SC", "Maccabi Tel Aviv F.C.", "Club Olimpia", "AS Monaco FC"]
R["spot"] = []
for nm in FAMOUS:
    c = find(nm)
    if c:
        R["spot"].append({"n": nm, "y": c["y"], "iso": c["iso"], "q": c["q"], "src": c["src"]})
spot = {s["n"]: s["y"] for s in R["spot"]}
print("spot", spot)
assert spot["Sheffield F.C."] == 1857 and spot["Notts County F.C."] == 1862 and spot["Hallam F.C."] == 1860 and spot["Queen's Park F.C."] == 1867
assert spot.get("Genoa CFC") == 1893, spot.get("Genoa CFC")
assert spot["Wrexham A.F.C."] == 1864 and spot["Club Atlético Peñarol"] == 1891 and spot["Recreativo de Huelva"] == 1889

# founding waves by decade and continent
decs = list(range(1850, 2030, 10))
wave = {d: Counter() for d in decs}
for c in okd:
    wave[(c["y"] // 10) * 10][c["k"] or "Unknown"] += 1
R["decades"] = [{"dec": d, "n": sum(wave[d].values()), **{k: wave[d][k] for k in CONT + ["Unknown"]}} for d in decs]
tot = {k: sum(w[k] for w in R["decades"]) for k in CONT + ["Unknown"]}
peak = max(R["decades"], key=lambda w: w["n"])
R["waves"] = {"peak_dec": peak["dec"], "peak_n": peak["n"], "by_cont": tot,
              "peak_by_cont": {k: max(R["decades"], key=lambda w: w[k])["dec"] for k in CONT},
              "pre1900": sum(1 for c in okd if c["y"] < 1900), "pre1900_europe_pct": 100 * sum(1 for c in okd if c["y"] < 1900 and c["k"] == "Europe") / sum(1 for c in okd if c["y"] < 1900),
              "pre1900_uk_pct": 100 * sum(1 for c in okd if c["y"] < 1900 and c["iso"] in ("ENG", "SCT", "WLS", "NIR", "GBR")) / sum(1 for c in okd if c["y"] < 1900),
              "post1990_pct": 100 * sum(1 for c in okd if c["y"] >= 1990) / len(okd),
              "europe_pct_all": 100 * sum(1 for c in okd if c["k"] == "Europe") / len(okd),
              "share_by_period": {}}
for a, b in ((1857, 1899), (1900, 1949), (1950, 1999), (2000, 2026)):
    s = [c for c in okd if a <= c["y"] <= b and c["k"]]
    R["waves"]["share_by_period"][f"{a}-{b}"] = {k: 100 * sum(1 for c in s if c["k"] == k) / len(s) for k in CONT}
UKS = ("ENG", "SCT", "WLS", "NIR", "GBR")
R["waves"]["n_1870"] = sum(1 for c in okd if c["y"] <= 1870)
R["waves"]["uk_pct_1870"] = 100 * sum(1 for c in okd if c["y"] <= 1870 and c["iso"] in UKS) / R["waves"]["n_1870"]
y1900 = Counter(c["y"] for c in okd)
R["waves"]["peak_year"] = max(y1900, key=lambda y: y1900[y]); R["waves"]["peak_year_n"] = y1900[R["waves"]["peak_year"]]

# oldest club in each country (dated 1857 or later)
first = {}
for c in sorted([c for c in okd if c["iso"] and c["iso"] != "GBR"], key=lambda c: (c["y"], -c["sl"])):
    first.setdefault(c["iso"], []).append(c)
F = []
for iso, v in first.items():
    c = v[0]; ties = [x for x in v if x["y"] == c["y"]]
    lon, lat = (c["lon"], c["lat"]) if c["lon"] is not None else (M[iso]["lx"], M[iso]["ly"])
    F.append({"iso": iso, "name": M[iso]["name"], "cont": c["k"], "y": c["y"], "club": lab(c), "q": c["q"], "ties": len(ties) - 1,
              "km": round(km(lon, lat)), "pt": c["lon"] is not None, "n": sum(1 for x in clubs if x["iso"] == iso),
              "n_dated": len(v), "lon": round(lon, 3), "lat": round(lat, 3)})
F.sort(key=lambda f: (f["y"], f["km"]))
R["first"] = {"n": len(F), "by_1880": sum(f["y"] < 1880 for f in F), "by_1900": sum(f["y"] < 1900 for f in F), "by_1914": sum(f["y"] < 1914 for f in F),
              "by_1950": sum(f["y"] < 1950 for f in F), "after_1960": sum(f["y"] >= 1960 for f in F),
              "median_by_cont": {k: statistics.median([f["y"] for f in F if f["cont"] == k]) for k in CONT},
              "first_by_cont": {k: min([f for f in F if f["cont"] == k], key=lambda f: (f["y"], f["km"])) for k in CONT},
              "last": F[-1], "list": F}
# diffusion front: how far from Sheffield the furthest first club had reached, by decade
front = []
for d in range(1850, 2030, 10):
    s = [f for f in F if f["y"] < d + 10]
    front.append({"dec": d, "countries": len(s), "max_km": max([f["km"] for f in s] or [0]), "median_km": statistics.median([f["km"] for f in s]) if s else 0})
R["front"] = front
early = [f for f in F if f["y"] < 1900]; late = [f for f in F if f["y"] >= 1950]
R["first"]["median_km_pre1900"] = statistics.median([f["km"] for f in early]); R["first"]["median_km_post1950"] = statistics.median([f["km"] for f in late])
xs = [f["y"] for f in F]; ys = [f["km"] for f in F]
mx, my = statistics.mean(xs), statistics.mean(ys)
R["first"]["corr_year_km"] = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))

# UK nations
R["uk"] = {}
for iso in ("ENG", "SCT", "WLS", "NIR"):
    R["uk"][iso] = {"n": sum(1 for c in clubs if c["iso"] == iso), "first": next(f for f in F if f["iso"] == iso)}
R["uk"]["unknown"] = R["source"]["n_uk_unknown"]
R["uk"]["n_all"] = sum(1 for c in clubs if c["iso"] in ("ENG", "SCT", "WLS", "NIR", "GBR"))
R["uk"]["pre1880"] = sum(1 for c in okd if c["y"] < 1880 and c["iso"] in ("ENG", "SCT", "WLS", "NIR", "GBR"))
R["uk"]["pre1880_all"] = sum(1 for c in okd if c["y"] < 1880)

# clubs that died
dis = [c for c in clubs if c["d"] and not c.get("d_bad")]
dd = Counter((c["d"] // 10) * 10 for c in dis); dy = Counter(c["d"] for c in dis)
life = [c["d"] - c["y"] for c in dis if c["y"] and not c["early"]]
y45 = [c for c in dis if c["d"] == 1945]
R["dis"] = {"n": len(dis), "pct": 100 * len(dis) / N, "n_bad": sum(1 for c in clubs if c.get("d_bad")),
            "by_dec": [{"dec": d, "n": dd[d]} for d in range(1850, 2030, 10)], "peak_year": max(dy, key=lambda y: dy[y]), "peak_n": dy[max(dy, key=lambda y: dy[y])],
            "y1945": len(y45), "y1945_german": sum(1 for c in y45 if c["iso"] == "DEU" or c.get("former") in ("German Reich", "German Empire") or any(q in ("Q1206012", "Q7318", "Q183") for q in c["cty"])),
            "since2000": sum(1 for c in dis if c["d"] >= 2000), "since2000_pct": 100 * sum(1 for c in dis if c["d"] >= 2000) / len(dis),
            "median_life": statistics.median(life), "n_life": len(life), "short5": sum(1 for x in life if x <= 5),
            "top_countries": [{"iso": i, "name": M[i]["name"], "n": n} for i, n in Counter(c["iso"] for c in dis if c["iso"]).most_common(8)],
            "oldest_dead": [{"n": lab(c), "y": c["y"], "d": c["d"], "iso": c["iso"], "q": c["q"]} for c in sorted([c for c in dis if c["y"] and not c["early"]], key=lambda c: c["y"])[:8]],
            "dec_2010": dd[2010]}

# coverage
pop = {k: v["pop"] for k, v in M.items()}
cn = Counter(c["iso"] for c in clubs if c["iso"])
uk_pop = sum(pop[k] or 0 for k in ("ENG", "SCT", "WLS", "NIR"))
per = []
for iso, n in cn.items():
    if iso == "GBR":
        continue
    p = pop.get(iso) or 0
    if p >= 1e6:
        per.append({"iso": iso, "name": M[iso]["name"], "n": n, "pop_m": round(p / 1e6, 1), "per_m": n / (p / 1e6)})
ukn = sum(n for i, n in cn.items() if i in ("ENG", "SCT", "WLS", "NIR", "GBR"))
ukp = None
for f in jload(f"{GEO}/ne_50m_admin_0_countries.geojson")["features"]:
    if f["properties"]["ADM0_A3"] == "GBR":
        ukp = f["properties"]["POP_EST"]
per.append({"iso": "GBR", "name": "United Kingdom (all four nations)", "n": ukn, "pop_m": round(ukp / 1e6, 1), "per_m": ukn / (ukp / 1e6)})
per.sort(key=lambda r: -r["per_m"])
bycont = Counter(c["k"] for c in clubs if c["k"])
R["coverage"] = {"top": per[:12], "bottom": [r for r in per if r["pop_m"] >= 20][-12:], "n_countries": len([k for k in cn if k != "GBR"]),
                 "by_cont": [{"cont": k, "n": bycont[k], "pct": 100 * bycont[k] / sum(bycont.values()), "dated_pct": 100 * sum(1 for c in clubs if c["k"] == k and c["y"]) / bycont[k],
                              "point_pct": 100 * sum(1 for c in clubs if c["k"] == k and c["lon"] is not None) / bycont[k]} for k in CONT],
                 "top_countries": [{"iso": i, "name": M[i]["name"], "n": n} for i, n in cn.most_common(12)],
                 "nld": cn["NLD"], "deu": cn["DEU"], "nga": cn.get("NGA", 0), "chn": cn.get("CHN", 0), "ind": cn.get("IND", 0), "bra": cn["BRA"],
                 "nld_per_m": next(r["per_m"] for r in per if r["iso"] == "NLD"), "nga_per_m": next(r["per_m"] for r in per if r["iso"] == "NGA"),
                 "sl1_pct": 100 * sum(1 for c in clubs if c["sl"] <= 1) / N, "median_sl": statistics.median([c["sl"] for c in clubs])}
R["coverage"]["africa_pct"] = next(r["pct"] for r in R["coverage"]["by_cont"] if r["cont"] == "Africa")
R["coverage"]["europe_pct"] = next(r["pct"] for r in R["coverage"]["by_cont"] if r["cont"] == "Europe")
jsave(R, f"{DATA}/results.json", indent=1)

# ---------- reusable tables ----------
with open(f"{DATA}/clubs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["wikidata", "name", "founded", "founded_date", "dissolved", "country_code", "country", "continent", "lon", "lat", "point_from", "town_matched", "sitelinks", "flag"])
    for c in sorted(clubs, key=lambda c: (c["y"] or 9999, c["n"])):
        flag = "founded before 1857: parent society or date error" if c["early"] else ("dissolved before founded" if c.get("d_bad") else "")
        w.writerow([c["q"], dash(c["n"]), c["y"] or "", c["date"] or "", c["d"] or "", c["iso"] or "", M[c["iso"]]["name"] if c["iso"] else (c.get("former") or ""),
                    c["k"] or "", c["lon"] if c["lon"] is not None else "", c["lat"] if c["lat"] is not None else "", c["src"] or "", c.get("town", ""), c["sl"], flag])
with open(f"{DATA}/first_clubs.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["country_code", "country", "continent", "first_year", "oldest_club", "wikidata", "other_clubs_same_year", "km_from_sheffield", "clubs_in_wikidata", "dated_clubs"])
    for x in F:
        w.writerow([x["iso"], x["name"], x["cont"], x["y"], dash(x["club"]), x["q"], x["ties"], x["km"], x["n"], x["n_dated"]])
with open(f"{DATA}/decades_by_continent.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["decade"] + CONT + ["Unknown", "total", "dissolved"])
    for r in R["decades"]:
        w.writerow([r["dec"]] + [r[k] for k in CONT + ["Unknown"]] + [r["n"], dd[r["dec"]]])
with open(f"{DATA}/countries.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f); w.writerow(["country_code", "country", "continent", "clubs", "dated", "with_point", "dissolved", "first_year", "population_est", "clubs_per_million"])
    fy = {x["iso"]: x["y"] for x in F}
    for iso, n in cn.most_common():
        p = pop.get(iso) or 0
        w.writerow([iso, M[iso]["name"], M[iso]["cont"] if M[iso]["cont"] in CONT else cont({"cont": M[iso]["cont"], "iso": iso}) or "", n,
                    sum(1 for c in clubs if c["iso"] == iso and c["y"]), sum(1 for c in clubs if c["iso"] == iso and c["lon"] is not None),
                    sum(1 for c in dis if c["iso"] == iso), fy.get(iso, ""), int(p), round(n / (p / 1e6), 1) if p >= 1e5 else ""])

# ---------- page data ----------
# points: every club with a point and a founding year from 1857 (cumulative/decade animation), plus undated clubs with a point
P = []
names = []
for c in sorted([c for c in clubs if c["lon"] is not None], key=lambda c: (c["y"] or 9999, -c["sl"])):
    y = c["y"] if c["y"] and not c["early"] else 0
    P.append([round(c["lon"], 3), round(c["lat"], 3), y, c["d"] or 0, {"own": 0, "venue": 1, "town": 2}[c["src"]], c["sl"], c["iso"] or "", c["n"] or "", c["q"]])
jsave({"cols": ["lon", "lat", "founded (0 = no year or before 1857)", "dissolved (0 = none)", "point from (0 own, 1 ground, 2 town in name)", "sitelinks", "country", "name", "wikidata"], "rows": P}, f"{DATA}/points.json")
# per country: clubs by year (for the counter and the side panel) including clubs without a point
cy = defaultdict(Counter); cdis = Counter(); cund = Counter()
for c in clubs:
    if not c["iso"]:
        continue
    if c["y"] and not c["early"]:
        cy[c["iso"]][c["y"]] += 1
    else:
        cund[c["iso"]] += 1
    if c["d"]:
        cdis[c["iso"]] += 1
top = defaultdict(list)
for c in sorted(okd, key=lambda c: (c["y"], -c["sl"])):
    if c["iso"] and len(top[c["iso"]]) < 8:
        top[c["iso"]].append([lab(c), c["y"], c["d"] or 0, c["q"]])
SITE = {"cname": {k: v["name"] for k, v in M.items()}, "cont": {k: (cont({"cont": v["cont"], "iso": k}) or "") for k, v in M.items()},
        "cpos": {k: [v["lx"], v["ly"], v["pop"] or 0] for k, v in M.items()},
        "c": {iso: {"y": {str(y): n for y, n in sorted(cy[iso].items())}, "u": cund[iso], "d": cdis[iso], "t": top[iso]} for iso in set(cy) | set(cund)},
        "first": {x["iso"]: [x["y"], x["club"], x["q"], x["ties"]] for x in F},
        "all_y": {str(y): n for y, n in sorted(Counter(c["y"] for c in okd).items())},
        "all_d": {str(y): n for y, n in sorted(Counter(c["d"] for c in dis).items())},
        "pt_y": {str(y): n for y, n in sorted(Counter(p[2] for p in P if p[2]).items())}}
jsave(SITE, f"{DATA}/site.json")
print("results", N, "dated", len(dated), "points page", len(P), "points.json", os.path.getsize(f"{DATA}/points.json") // 1024, "KB; site", os.path.getsize(f"{DATA}/site.json") // 1024, "KB")
