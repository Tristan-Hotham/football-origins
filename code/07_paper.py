"""Build the paper: fill code/paper_template.tex from data/results.json, add tables, compile with xelatex.
Output: release/paper/<NAME>.pdf and .tex (figures f_*.png sit beside them)."""
import subprocess
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Where_Football_Clubs_Come_From"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "pc": return f"{round(float(v))}\\%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    return tex(str(v))


s = R["source"]
TP = ("\\begin{table}[tbp]\\centering\\small\\caption{From query to data.}\\label{tab:pipe}"
      "\\begin{tabular}{p{9.5cm}r}\\toprule Step & Items\\\\\\midrule\n"
      f"Rows returned by the query & {s['n_rows']:,}\\\\\n"
      f"Distinct Wikidata items & {s['n_items']:,}\\\\\n"
      f"Left out: national teams, beach and futsal, reserve and youth teams, Australian rules clubs & {s['n_dropped']:,}\\\\\n"
      f"Clubs kept & {s['n']:,}\\\\\n"
      f"\\quad with a founding year & {s['n_dated']:,}\\\\\n"
      f"\\quad\\quad of which from 1857 (used for the timeline) & {s['n_ok']:,}\\\\\n"
      f"\\quad with a point (own {s['n_own']:,}; ground {s['n_venue']:,}; town in name {s['n_town']:,}) & {s['n_point']:,}\\\\\n"
      f"\\quad with a founding year from 1857 and a point (on the animated map) & {s['n_dated_point']:,}\\\\\n"
      f"\\quad with a present-day country & {s['n_country']:,}\\\\\n"
      f"\\quad with a dissolution year & {R['dis']['n'] + R['dis']['n_bad']:,}\\\\\n"
      "\\bottomrule\\end{tabular}\\end{table}")
CONT = ["Europe", "South America", "North America", "Africa", "Asia", "Oceania"]
rows = ""
for k in CONT:
    f = R["first"]["first_by_cont"][k]
    n = sum(1 for x in R["first"]["list"] if x["cont"] == k)
    rows += f"{k} & {n} & {tex(f['name'])} & {tex(f['club'])} & {f['y']} & {R['first']['median_by_cont'][k]:.0f}\\\\\n"
TC = ("\\begin{table}[tbp]\\centering\\small\\caption{First clubs by continent: number of countries and territories with a dated club, the earliest, and the median year of countries' first clubs.}\\label{tab:cont}\\setlength{\\tabcolsep}{4pt}"
      "\\begin{tabular}{lr>{\\raggedright\\arraybackslash}p{2.6cm}>{\\raggedright\\arraybackslash}p{4.8cm}rr}\\toprule Continent & Countries & Earliest & Club & Year & Median\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for f in R["first"]["list"][:36]:
    rows += f"{f['y']} & {tex(f['name'])} & {tex(f['club'])} & {f['km']:,}\\\\\n"
TF = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{The earliest first clubs: the oldest dated club Wikidata records in each country or territory, first 36 (all are in data/first\\_clubs.csv).}\\label{tab:first}"
      "\\begin{tabular}{rl>{\\raggedright\\arraybackslash}p{7.2cm}r}\\toprule Year & Country & Club & km from Sheffield\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
rows = ""
for c in R["coverage"]["by_cont"]:
    rows += f"{c['cont']} & {c['n']:,} & {c['pct']:.1f}\\% & {c['dated_pct']:.0f}\\% & {c['point_pct']:.0f}\\%\\\\\n"
TV = ("\\begin{table}[tbp]\\centering\\small\\caption{Clubs by continent: share of clubs with a country, and the share of each continent's clubs with a founding year and with a point.}\\label{tab:cov}"
      "\\begin{tabular}{lrrrr}\\toprule Continent & Clubs & Share & With a year & With a point\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
for k in ("page", "repo"):
    t = t.replace("\\url{{{meta.%s}}}" % k, "\\url{%s}" % R["meta"][k])
t = re.sub(r"\{\{(?!TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
t = t.replace("{{TABLE_PIPELINE}}", TP).replace("{{TABLE_CONT}}", TC).replace("{{TABLE_FIRST}}", TF).replace("{{TABLE_COV}}", TV)
assert "{{" not in t.replace("{{DOI}}", "") and "--" not in t and "\u2014" not in t and "\u2013" not in t
# the DOI placeholder stays literal for the publisher; LaTeX needs its braces escaped
t = t.replace("{{DOI}}", "\\{\\{DOI\\}\\}")
t = t.replace("\\href{https://doi.org/\\{\\{DOI\\}\\}}", "\\href{https://doi.org/}").replace("\\url{https://doi.org/\\{\\{DOI\\}\\}}", "https://doi.org/\\{\\{DOI\\}\\}")
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(2):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("\u2014") + txt.count("\u2013") + txt.count("--"))
