"""Build index.html from code/page_template.html. Every number in the text is a {{path|format}} token filled from
data/results.json; page data (site.json, world.json, cities) is embedded; data/points.json is loaded by the page.
Facts stated in words are checked here. The full-screen map snippet (code/fullscreen_snippet.html) is pasted before </body>."""
import json
from common import *

R = jload(f"{DATA}/results.json")
SITE = jload(f"{DATA}/site.json")
F = {f["iso"]: f for f in R["first"]["list"]}

# facts stated in words (page, blog, paper)
assert F["ENG"]["club"] == "Sheffield F.C." and F["ENG"]["y"] == 1857
assert F["WLS"]["club"].startswith("Wrexham") and F["SCT"]["club"].startswith("Queen's Park") and F["NIR"]["club"].startswith("Cliftonville")
assert F["WLS"]["y"] < F["SCT"]["y"] < F["NIR"]["y"]
assert R["first"]["first_by_cont"]["South America"]["club"] == "Lima Cricket and Football Club"
assert F["CHE"]["club"].startswith("Lausanne Football and Cricket") and "Rowing" in F["URY"]["club"]
assert F["NOR"]["club"] == "Drammens TF" and F["ITA"]["club"].startswith("Bentegodi") and F["DEU"]["y"] == 1858
assert max(F[i]["y"] for i in ("PER", "ARG", "URY", "IND", "AUS")) < min(F[i]["y"] for i in ("HUN", "POL", "RUS"))
assert F["IND"]["y"] < F["HUN"]["y"]
assert R["waves"]["peak_by_cont"]["Europe"] == 1920 and all(R["waves"]["peak_by_cont"][k] == 2000 for k in ("South America", "North America", "Africa", "Asia"))
assert R["waves"]["peak_year"] == 1919
assert R["dis"]["peak_year"] == 1945 and R["dis"]["y1945_german"] > R["dis"]["y1945"] / 2
assert R["dis"]["oldest_dead"][0]["n"] == "Wanderers F.C."
assert R["dis"]["since2000_pct"] > 50
assert R["coverage"]["nld"] > R["coverage"]["deu"]
assert R["first"]["last"]["iso"] == "GIB"
top = [r["iso"] for r in R["coverage"]["top"][:12]]
assert {"NLD", "SWE", "BEL", "LTU", "CYP", "EST", "LVA"} <= set(top), top
assert R["source"]["n_early"] > 0 and R["decades"][-1]["dec"] == 2020
eng_early = [c["n"] for c in R["spot"] if c["iso"] == "ENG" and c["y"] < 1870]
assert {"Sheffield F.C.", "Hallam F.C.", "Notts County F.C.", "Stoke City F.C.", "Nottingham Forest F.C."} <= set(eng_early), eng_early


def build():
    tpl = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
    html = re.sub(r"\{\{([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(R, m.group(1)), m.group(3)), tpl)
    assert "{{" not in html.replace("{{DOI}}", "").replace("https://blog.tristanhotham.com/2026/10/31/football-origins/", "")
    J = lambda o: json.dumps(o, ensure_ascii=False, separators=(",", ":"))
    html = html.replace("/*RESULTS*/", J(R)).replace("/*SITE*/", J(SITE))
    html = html.replace("/*WORLD*/", open(f"{DATA}/world.json", encoding="utf-8").read())
    html = html.replace("/*CITIES*/", J([{"name": x["name"], "lat": x["lat"], "lon": x["lon"], "pop": x["pop"]} for x in jload(f"{DATA}/cities.json")]))
    html = html.replace("/*FULLSCREEN*/", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
    vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", html, flags=re.S)
    vis = re.sub(r"<[^>]+>", " ", vis)
    for bad in ("—", "–", "--"):
        assert bad not in vis, bad
    for scr in re.findall(r"<script>(.*?)</script>", html, flags=re.S):
        for bad in ("—", "–"):
            assert bad not in scr, bad
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(html)
    print("index.html", len(html.encode()) // 1024, "KB")


if __name__ == "__main__":
    build()
