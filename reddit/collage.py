"""r/dataisbeautiful collage for football-origins: 2400 x 3000 px, light background. Numbers from data/results.json."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
from figstyle import *
from matplotlib.patches import Patch

R = jload(f"{DATA}/results.json"); SITE = jload(f"{DATA}/site.json")
A, P = points()
F = {f["iso"]: f for f in R["first"]["list"]}
BGc = "#F6F3EA"
fig = plt.figure(figsize=(12, 15), dpi=200, facecolor=BGc)
fig.text(.045, .972, "Where football clubs come from", fontproperties=DISP, fontsize=50, color=FG, va="top")
fig.text(.045, .917, f"Every association football club in Wikidata with a founding year, from Sheffield FC in 1857 to today.\nCountries are shaded by the year of the oldest club Wikidata records there; dots are {R['source']['n_dated_point']:,} clubs by year founded.",
         fontproperties=SERP, fontsize=15, color=FG, va="top", linespacing=1.45)

ax = fig.add_axes([0, .47, 1, .40])
ext = (-12.3e6, 15.6e6, -5.9e6, 8.6e6)
world(ax, lambda iso: lighten(era(F[iso]["y"]), .45) if iso in F else None, lw=.35, ext=ext, ec=BGc, land="#E2DED2")
d = A[A[:, 2] > 0]; d = d[np.argsort(-d[:, 2])]
x, y = proj(d[:, 0], d[:, 1])
ax.scatter(x, y, s=1.4, c=[era(v) for v in d[:, 2]], lw=0, zorder=3, rasterized=True)
LAB = [("ENG", "England 1857\nSheffield FC", -32, 50), ("PER", "Peru 1859", -102, -14), ("BRA", "Brazil 1872", -22, -19),
       ("ARG", "Argentina 1870", -100, -40), ("URY", "Uruguay 1874", -26, -32), ("CAN", "Canada 1879", -47, 40),
       ("USA", "United States 1883", -112, 6), ("ZAF", "South Africa 1882", -4, -44), ("IND", "India 1880", 76, -6),
       ("AUS", "Australia 1880", 90, -36), ("NZL", "New Zealand 1887", 128, -45), ("RUS", "Russia 1894", 62, 79),
       ("JPN", "Japan 1912", 162, 37), ("CHN", "China 1925", 143, 19), ("NGA", "Nigeria 1950", -26, 2)]
for iso, txt, lx, ly in LAB:
    f = F[iso]
    assert txt.split("\n")[0].endswith(str(f["y"])), (iso, f["y"])
    x0, y0 = proj(f["lon"], f["lat"]); x1, y1 = proj(lx, ly)
    ax.annotate(txt, xy=(x0, y0), xytext=(x1, y1), fontsize=10.5, color=FG, ha="center", va="center", family=MONO, linespacing=1.15,
                arrowprops=dict(arrowstyle="-", color=FG, lw=.7, shrinkA=4, shrinkB=1), zorder=6,
                bbox=dict(boxstyle="round,pad=.25", fc=BGc, ec="none", alpha=.92))
    ax.plot([x0], [y0], "o", ms=3, mfc="#fff", mec=FG, mew=.9, zorder=7)
# legend: era ramp
cax = fig.add_axes([.045, .452, .5, .014]); ys = np.arange(1857, 2027)
cax.imshow(np.array([[era(v) for v in ys]]), aspect="auto", extent=(1857, 2026, 0, 1)); cax.set_yticks([])
cax.set_xticks([1857, 1880, 1900, 1925, 1950, 1975, 2000, 2026]); cax.tick_params(labelsize=10, length=0, colors=FG)
for s_ in cax.spines.values(): s_.set_visible(False)
fig.text(.57, .443, "Shading: year of each country's first club.\nDots: year each club was founded.\nGrey: no dated club in Wikidata.", fontsize=10, color=MUT, va="center", linespacing=1.35)

nums = [(f"{R['first']['by_1900']}", HOT, f"countries and territories\nhad a club in the record\nbefore 1900 ({R['first']['n']} today)"),
        (f"{R['waves']['share_by_period']['1857-1899']['Europe']:.0f}%", "#2D5E9E", "of clubs founded before\n1900 were European;\nsince 2000: " + f"{R['waves']['share_by_period']['2000-2026']['Europe']:.0f}%"),
        (f"{R['waves']['peak_year_n']}", GOLD, f"clubs founded in\n{R['waves']['peak_year']}, the busiest\nyear on record"),
        (f"{R['dis']['y1945']}", "#5B3E96", f"clubs dissolved in\n{R['dis']['peak_year']}, {R['dis']['y1945_german']} of them\nGerman: the worst year")]
for i, (big, col, small) in enumerate(nums):
    xx = .045 + i * .235
    fig.text(xx, .41, big, fontproperties=DISP, fontsize=44, color=col, va="top")
    fig.text(xx, .358, small, family=MONO, fontsize=11.5, color=FG, va="top", linespacing=1.45)

# bottom left: waves
D = [w for w in R["decades"] if w["dec"] >= 1850]
a1 = fig.add_axes([.07, .085, .42, .16]); a1.set_facecolor(BGc)
b = np.zeros(len(D)); xs = np.arange(len(D))
for k, c in CONT + [("Unknown", "#B5AFA3")]:
    v = np.array([w[k] for w in D]); a1.bar(xs, v, bottom=b, color=c, width=.82); b += v
a1.set_xticks(xs[::3]); a1.set_xticklabels([f"{w['dec']}s" for w in D][::3], fontsize=9.5)
a1.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}")); a1.tick_params(labelsize=9.5)
for s_ in ("top", "right"): a1.spines[s_].set_visible(False)
a1.set_title("Clubs founded per decade, by continent", family=MONO, fontsize=12.5, color=FG, loc="left", pad=8)
# bottom right: front
a2 = fig.add_axes([.58, .085, .38, .16]); a2.set_facecolor(BGc)
for k, c in CONT:
    s = [f for f in R["first"]["list"] if f["cont"] == k]
    a2.scatter([f["y"] for f in s], [f["km"] / 1000 for f in s], s=16, c=c, alpha=.9, lw=.3, edgecolor="#fff")
a2.set_xlim(1850, 2030); a2.set_ylim(-.5, 19.5); a2.tick_params(labelsize=9.5)
a2.set_ylabel("thousand km from Sheffield", fontsize=9.5)
for s_ in ("top", "right"): a2.spines[s_].set_visible(False)
a2.set_title("Each country's first club: year and distance", family=MONO, fontsize=12.5, color=FG, loc="left", pad=8)
LEGP = SERP.copy(); LEGP.set_size(12)
fig.legend(handles=[Patch(fc=c, ec="none", label=k) for k, c in CONT] + [Patch(fc="#B5AFA3", ec="none", label="No present-day country")],
           loc="upper left", bbox_to_anchor=(.04, .292), ncol=7, frameon=False, prop=LEGP, handlelength=1, columnspacing=1.1)
fig.text(.045, .018, "Source: Wikidata (CC0) via QLever, every item that is an association football club, 2026; Natural Earth (public domain). National, reserve,\n"
         "beach and futsal teams removed. Coverage is very uneven between countries; a first club is the oldest one Wikidata dates, often a multi-sport society.\n"
         "Analysis and chart: Tristan Hotham, with Python and matplotlib  ·  maps.tristanhotham.com/football-origins", family=MONO, fontsize=9, color=MUT, linespacing=1.55, va="bottom")
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "where_football_clubs_come_from.png")
fig.savefig(out, facecolor=BGc, dpi=200)
print("ok", out)
