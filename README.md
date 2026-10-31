# Where football clubs come from

An animated world map of 45,931 association football clubs in Wikidata, from Sheffield FC in 1857 to today: the oldest club Wikidata records in each country, founding waves by decade and continent, the "first club" diffusion front, and the clubs that folded.

Interactive page: https://maps.tristanhotham.com/football-origins/
Paper: https://doi.org/10.5281/zenodo.23844505
Blog post: https://blog.tristanhotham.com/2026/10/31/football-origins/

## Headline results

- Spread: the oldest dated club in Wikidata is Sheffield FC (1857). 55 countries and territories had a dated club before 1900, 173 before 1950 and 222 today. First clubs founded before 1900 lie a median 1,966 km from Sheffield, those after 1950 6,894 km; Peru (Lima Cricket and Football Club, 1859), Argentina, Uruguay, India and Australia all have clubs before Hungary, Poland or Russia.
- British Isles: 258 of the 314 clubs dated before 1880 are in the United Kingdom. First clubs: Sheffield FC (England, 1857), Wrexham (Wales, 1864), Queen's Park (Scotland, 1867), Cliftonville (Northern Ireland, 1879).
- Waves: 93% of clubs founded before 1900 are European; the busiest year is 1919 (475 clubs), Europe's busiest decade the 1920s, every other continent's the 2000s. Since 2000 Europe's share of new clubs is 38%.
- Clubs that died: 4,091 clubs have a dissolution date. The worst year is 1945 (174 clubs, 143 of them German); 52% of recorded dissolutions are since 2000.
- Coverage: the Netherlands has 165 clubs per million people in Wikidata, Nigeria 0.6. Europe holds 61% of clubs with a country, Africa 8%. Read the maps as a record of what has been catalogued.
- Not in the data: Wikidata does not record founders' nationality, so nothing here measures the share of clubs founded by British workers, sailors or expatriates.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; page data embedded, `data/points.json` loaded by the page). |
| `header.png` | Social card, 1200 x 630. |
| `data/clubs.csv` | All 45,931 clubs: Wikidata ID, name, founded (year, and full date where one is given), dissolved, present-day country, continent, point and where it came from, sitelinks, flags. |
| `data/first_clubs.csv` | The oldest dated club in each of 222 countries and territories, with distance from Sheffield. |
| `data/decades_by_continent.csv` | Clubs founded per decade by continent, and clubs dissolved per decade. |
| `data/countries.csv` | Per country: clubs, dated, with a point, dissolved, first year, population estimate, clubs per million. |
| `data/results.json` | Every number used in the page, paper, blog and collage. |
| `data/points.json`, `data/site.json`, `data/world.json`, `data/cities.json` | Page data (club points, per-country counts, outlines, city labels). |
| `code/` | Scripts, run in order (below), and the page, paper and blog templates. |
| `release/` | Paper PDF and LaTeX source with figures (`paper/`), blog post, figures and meta (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |
| `qa/` | Screenshots of the page at desktop and phone widths. |

## Method in brief

- Clubs: every Wikidata item that is an instance of association football club (Q476028) or a subclass, from one QLever query (48,286 rows, 46,993 items). One record per item. Left out: national and representative teams, beach soccer and futsal, reserve, B and under-age teams, and Australian clubs whose names mark them as Australian rules clubs (1,062 in all).
- Dates: founding year = earliest inception (P571) year; 1 January dates are treated as year only (86% of dates). 20 clubs dated before 1857 (older sports societies and errors) are kept with a flag but left out of the timeline. Dissolution = latest P576 year.
- Places: own coordinates, else home ground's, else a Natural Earth town named in the club's English label (approximate). Country = present-day country of the point, else Wikidata's country; the UK is split into England, Scotland, Wales and Northern Ireland.
- First clubs: the oldest club with a year from 1857 in each country; distance from Sheffield is great-circle distance.
- Caveats: Wikidata is incomplete and very uneven by country; first dates may be those of a parent multi-sport society, or wrong; town-matched points are approximate; nothing identifies founders.

## How to rerun

Needs Python 3 with numpy, shapely, pyproj, matplotlib, fontTools and pyreadr, xelatex and pdftotext. Raw inputs are read in place (paths in `code/common.py`): `/home/claude/newdata/raw2/clubs.tsv` (the QLever result, retrieved 2026), Natural Earth files in `/home/claude/newdata/raw/geo/`, and `engsoccerdata/data/england_club_data.rda` (check only). Intermediate files go to `/dev/shm/football/work` (set `FOOTTMP` to change).

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

Hotham, T. (2026) Where football clubs come from: founding years of 45,931 association football clubs in Wikidata, from Sheffield FC in 1857 to today. Zenodo. https://doi.org/10.5281/zenodo.23844505

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
