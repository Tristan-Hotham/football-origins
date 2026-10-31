"""Blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
{{DOI}}, {{DOI_URL}} and https://blog.tristanhotham.com/2026/10/31/football-origins/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Where_Football_Clubs_Come_From"

# facts stated in words in the blog (alt text included); the page build checks the rest
import importlib.util
spec = importlib.util.spec_from_file_location("b", os.path.join(ROOT, "code", "05_build_site.py")); spec.loader.exec_module(importlib.util.module_from_spec(spec))
spot = {s["n"]: s["y"] for s in R["spot"]}
assert spot["Sheffield F.C."] == 1857 and spot["Notts County F.C."] == 1862 and spot["Club Atlético Peñarol"] == 1891 and spot["Genoa CFC"] == 1893
assert R["dis"]["y1945"] == 174
top4 = [r["iso"] for r in R["coverage"]["top"][:4]]
assert top4 == ["CYP", "LTU", "NLD", "EST"] and all(r["per_m"] > 150 for r in R["coverage"]["top"][:4])
assert [r["iso"] for r in R["coverage"]["bottom"][-3:]] == ["PAK", "CHN", "IND"] and all(r["per_m"] < 1 for r in R["coverage"]["bottom"][-3:])
F = {f["iso"]: f["y"] for f in R["first"]["list"]}
assert F["MNG"] >= 1990 and F["LAO"] >= 1990 and max(F[i] for i in ("PER", "BRA", "ARG", "USA", "IND", "AUS")) < 1890

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG|DOI_URL|BLOG_URL|DOI\}\})([^}|]+)(\|(\w+))?\}\}", lambda m: fmt(get(R, m.group(1)), m.group(3)), post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
meta = {"title": "Where football clubs come from: from Sheffield in 1857 to every corner of the world",
        "slug": "football-origins",
        "excerpt": f"I put {R['source']['n']:,} football clubs from Wikidata on one animated map, in the order they were founded: from Sheffield FC in 1857 to {R['first']['n']} countries and territories, with the oldest club in each and the clubs that folded.",
        "seo_description": "An animated map of football clubs by founding year, from Sheffield FC in 1857 to today: first clubs in every country, waves of founding and clubs that died.",
        "tags": ["football", "soccer", "sport history", "maps", "data visualisation", "Wikidata", "diffusion"],
        "header_alt": f"Title card reading 'Where football clubs come from' in black, green and claret on cream, beside a world map with countries shaded by the year of their first football club and dots for clubs coloured from dark red (1857) to purple (2026). Text: {R['source']['n']:,} clubs in Wikidata, from Sheffield FC in 1857 to {R['first']['n']} countries and territories."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/football-origins_data_and_code.zip"
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for d in ("code", "data"):
        for fn in sorted(os.listdir(os.path.join(ROOT, d))):
            if fn.endswith(".pyc") or fn == "__pycache__":
                continue
            z.write(os.path.join(ROOT, d, fn), f"football-origins/{d}/{fn}")
    for fn in ("README.md", "LICENSE"):
        if os.path.exists(os.path.join(ROOT, fn)):
            z.write(os.path.join(ROOT, fn), f"football-origins/{fn}")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&")
zmeta = {"title": "Where Football Clubs Come From: Founding Years of Association Football Clubs in Wikidata, from Sheffield FC in 1857 to Today",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {BLOG}.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["football", "soccer", "association football clubs", "sport history", "diffusion", "Wikidata", "open data", "maps"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": "https://www.wikidata.org/", "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
s = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in s and "\u2013" not in s and "--" not in s
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
