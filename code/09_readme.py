"""README.md, LICENSE and reddit/post.md, with numbers from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
s, f, w, d, c = R["source"], R["first"], R["waves"], R["dis"], R["coverage"]
N = lambda v: f"{round(v):,}"
readme = f"""# Where football clubs come from

An animated world map of {N(s['n'])} association football clubs in Wikidata, from Sheffield FC in 1857 to today: the oldest club Wikidata records in each country, founding waves by decade and continent, the "first club" diffusion front, and the clubs that folded.

Interactive page: {PAGE}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}

## Headline results

- Spread: the oldest dated club in Wikidata is Sheffield FC (1857). {f['by_1900']} countries and territories had a dated club before 1900, {f['by_1950']} before 1950 and {f['n']} today. First clubs founded before 1900 lie a median {N(f['median_km_pre1900'])} km from Sheffield, those after 1950 {N(f['median_km_post1950'])} km; Peru (Lima Cricket and Football Club, 1859), Argentina, Uruguay, India and Australia all have clubs before Hungary, Poland or Russia.
- British Isles: {R['uk']['pre1880']} of the {R['uk']['pre1880_all']} clubs dated before 1880 are in the United Kingdom. First clubs: Sheffield FC (England, 1857), Wrexham (Wales, 1864), Queen's Park (Scotland, 1867), Cliftonville (Northern Ireland, 1879).
- Waves: {round(w['share_by_period']['1857-1899']['Europe'])}% of clubs founded before 1900 are European; the busiest year is {w['peak_year']} ({w['peak_year_n']} clubs), Europe's busiest decade the 1920s, every other continent's the 2000s. Since 2000 Europe's share of new clubs is {round(w['share_by_period']['2000-2026']['Europe'])}%.
- Clubs that died: {N(d['n'])} clubs have a dissolution date. The worst year is {d['peak_year']} ({d['y1945']} clubs, {d['y1945_german']} of them German); {round(d['since2000_pct'])}% of recorded dissolutions are since 2000.
- Coverage: the Netherlands has {N(c['nld_per_m'])} clubs per million people in Wikidata, Nigeria {c['nga_per_m']:.1f}. Europe holds {round(c['europe_pct'])}% of clubs with a country, Africa {round(c['africa_pct'])}%. Read the maps as a record of what has been catalogued.
- Not in the data: Wikidata does not record founders' nationality, so nothing here measures the share of clubs founded by British workers, sailors or expatriates.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; page data embedded, `data/points.json` loaded by the page). |
| `header.png` | Social card, 1200 x 630. |
| `data/clubs.csv` | All {N(s['n'])} clubs: Wikidata ID, name, founded (year, and full date where one is given), dissolved, present-day country, continent, point and where it came from, sitelinks, flags. |
| `data/first_clubs.csv` | The oldest dated club in each of {f['n']} countries and territories, with distance from Sheffield. |
| `data/decades_by_continent.csv` | Clubs founded per decade by continent, and clubs dissolved per decade. |
| `data/countries.csv` | Per country: clubs, dated, with a point, dissolved, first year, population estimate, clubs per million. |
| `data/results.json` | Every number used in the page, paper, blog and collage. |
| `data/points.json`, `data/site.json`, `data/world.json`, `data/cities.json` | Page data (club points, per-country counts, outlines, city labels). |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper PDF and LaTeX source with figures (`paper/`), blog post, figures and meta (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots of the page at desktop and phone widths. |

## Method in brief

- Clubs: every Wikidata item that is an instance of association football club (Q476028) or a subclass, from one QLever query ({N(s['n_rows'])} rows, {N(s['n_items'])} items). One record per item. Left out: national and representative teams, beach soccer and futsal, reserve, B and under-age teams, and Australian clubs whose names mark them as Australian rules clubs ({N(s['n_dropped'])} in all).
- Dates: founding year = earliest inception (P571) year; 1 January dates are treated as year only ({round(s['yonly_pct'])}% of dates). {s['n_early']} clubs dated before 1857 (older sports societies and errors) are kept with a flag but left out of the timeline. Dissolution = latest P576 year.
- Places: own coordinates, else home ground's, else a Natural Earth town named in the club's English label (approximate). Country = present-day country of the point, else Wikidata's country; the UK is split into England, Scotland, Wales and Northern Ireland.
- First clubs: the oldest club with a year from 1857 in each country; distance from Sheffield is great-circle distance.
- Caveats: Wikidata is incomplete and very uneven by country; first dates may be those of a parent multi-sport society, or wrong; town-matched points are approximate; nothing identifies founders.

## How to rerun

Needs Python 3 with numpy, shapely, pyproj, matplotlib, fontTools and pyreadr, xelatex and pdftotext. Raw inputs are read in place (paths in `code/common.py`): `/home/claude/newdata/raw2/clubs.tsv` (the QLever result, retrieved {RETRIEVED}), Natural Earth files in `/home/claude/newdata/raw/geo/`, and `engsoccerdata/data/england_club_data.rda` (check only). Intermediate files go to `/dev/shm/football/work` (set `FOOTTMP` to change).

```
python3 code/01_parse.py        # one record per club, exclusions
python3 code/02_geo.py          # outlines, countries and continents
python3 code/03_place.py        # points from town names; engsoccerdata check
python3 code/04_results.py      # results.json, data tables, page data
python3 code/05_build_site.py   # index.html
python3 code/06_figures.py      # header, blog and paper figures
python3 code/07_paper.py        # paper PDF
python3 code/09_readme.py       # README, LICENSE, Reddit post
python3 code/08_release.py      # blog post, Zenodo files
python3 reddit/collage.py       # collage
```

## Sources and licences

- Wikidata, via QLever (https://qlever.cs.uni-freiburg.de/wikidata). CC0.
- Natural Earth countries, states and provinces, and populated places (https://www.naturalearthdata.com/). Public domain.
- engsoccerdata (James Curley, https://github.com/jalapic/engsoccerdata, GPL-3): used only to check the points of English clubs; nothing from it is redistributed.
- Base map tiles on the page: © Esri.

## Citation

Hotham, T. (2026) Where football clubs come from: founding years of {N(s['n'])} association football clubs in Wikidata, from Sheffield FC in 1857 to today. Zenodo. https://doi.org/{DOI}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
lic = """MIT License

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


This licence covers the code in code/, reddit/collage.py and the page scripts.
The text of the page, paper and blog post, the figures and the derived data
files in data/ are released under CC BY 4.0. They are derived from Wikidata
(CC0) and Natural Earth (public domain).
"""
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
post = f"""## Title

[OC] Where football clubs come from: {N(s['n_dated'])} clubs in Wikidata by founding year, from Sheffield FC in 1857 to {f['n']} countries and territories

## Body

I mapped every association football club in Wikidata with a founding year and shaded each country by the year of the oldest club it records. Football leaves Sheffield in 1857 and spreads by sea: Peru (Lima Cricket and Football Club, 1859), Argentina, Uruguay, India and Australia all have clubs in the record before Hungary, Poland or Russia. Before 1900, {round(w['share_by_period']['1857-1899']['Europe'])}% of new clubs were European; since 2000 it is {round(w['share_by_period']['2000-2026']['Europe'])}%. The busiest year for new clubs was {w['peak_year']} ({w['peak_year_n']}); the worst for dissolutions was {d['peak_year']} ({d['y1945']}, mostly German). Caveat: Wikidata is very uneven (the Netherlands has {N(c['nld_per_m'])} clubs per million people in it, Nigeria {c['nga_per_m']:.1f}), and many "first clubs" are older cricket, rowing or gymnastics societies. Animated version with a time slider: {PAGE}

## Source comment

Source: Wikidata via QLever, every item that is an association football club or a subclass (CC0), 2026; Natural Earth outlines and populated places (public domain). National, reserve, youth, beach soccer and futsal teams and probable Australian rules clubs removed; 1 January founding dates treated as year only.

Tools: Python (shapely, pyproj, matplotlib); Leaflet for the interactive map.

Interactive version: {PAGE}
Paper: https://doi.org/{DOI}
Blog post: {BLOG}
"""
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
for t in (readme, post):
    for bad in ("—", "–", "--"):
        assert bad not in t.replace("|---|---|", ""), bad
print("README", len(readme.split()), "words; post", len(post.split()))
