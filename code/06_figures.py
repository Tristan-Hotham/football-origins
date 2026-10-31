"""Header card, blog figures (release/blog/b_*.png) and paper figures (release/paper/f_*.png)."""
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from figstyle import *

R = jload(f"{DATA}/results.json"); SITE = jload(f"{DATA}/site.json")
A, P = points()
BL = os.path.join(ROOT, "release", "blog"); PA = os.path.join(ROOT, "release", "paper")
os.makedirs(BL, exist_ok=True); os.makedirs(PA, exist_ok=True)
FIRST = {f["iso"]: f["y"] for f in R["first"]["list"]}
dated = A[A[:, 2] > 0]
order = np.argsort(-dated[:, 2])          # newest drawn first, oldest on top
dated = dated[order]
X, Y = proj(dated[:, 0], dated[:, 1])
SX, SY = proj(-1.4659, 53.3811)


def both(fig, name):
    fig.savefig(os.path.join(PA, "f_" + name + ".png"), dpi=200, facecolor=fig.get_facecolor())
    fig.savefig(os.path.join(BL, "b_" + name + ".png"), dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)


def era_bar(fig, rect, label=True):
    ax = fig.add_axes(rect)
    ys = np.arange(1857, 2027)
    ax.imshow(np.array([[era(y) for y in ys]]), aspect="auto", extent=(1857, 2026, 0, 1))
    ax.set_yticks([]); ax.set_xticks([1857, 1900, 1950, 2000, 2026]); ax.tick_params(labelsize=10, length=0)
    for s in ax.spines.values(): s.set_visible(False)
    if label: ax.set_title("year founded", fontsize=10, color=MUT, loc="left", pad=3)
    return ax


# 1. snapshots
YRS = [1870, 1890, 1910, 1930, 1960, 2026]
fig = plt.figure(figsize=(12, 9.6), facecolor=BG)
for k, yr in enumerate(YRS):
    ax = fig.add_axes([.01 + (k % 2) * .495, .655 - (k // 2) * .292, .48, .25])
    world(ax, lambda iso: lighten(era(FIRST[iso]), .55) if iso in FIRST and FIRST[iso] <= yr else None, lw=.2)
    m = dated[:, 2] <= yr
    alive = m & ~((dated[:, 3] > 0) & (dated[:, 3] <= yr))
    ax.scatter(X[alive], Y[alive], s=2.2 if yr > 1930 else 4, c=[era(y) for y in dated[alive, 2]], lw=0, zorder=3, rasterized=True)
    n = sum(v for kk, v in SITE["all_y"].items() if int(kk) <= yr); nc = sum(1 for v in FIRST.values() if v <= yr)
    ax.text(.04, 1.02, f"{yr}", transform=ax.transAxes, fontproperties=DISP, fontsize=24, color=FG, va="bottom")
    ax.text(.25, 1.035, f"{n:,} dated clubs · {nc} countries", transform=ax.transAxes, fontsize=10.5, color=MUT, va="bottom")
era_bar(fig, [.3, .04, .4, .022])
both(fig, "snapshots")

# 2. first club map
fig = plt.figure(figsize=(12, 6.6), facecolor=BG)
ax = fig.add_axes([0, .1, 1, .9])
world(ax, lambda iso: era(FIRST[iso]) if iso in FIRST else None, lw=.3)
ax.plot([SX], [SY], "o", ms=7, mfc="#fff", mec=FG, mew=1.6, zorder=5)
ax.annotate("Sheffield FC, 1857", xy=(SX, SY), xytext=(-2.4e6, 3.7e6), fontsize=11, color=FG, ha="center",
            arrowprops=dict(arrowstyle="-", color=FG, lw=.8), zorder=6)
era_bar(fig, [.3, .085, .4, .028])
fig.text(.5, .012, ha="center", s= "Countries coloured by the founding year of the oldest dated club Wikidata records there; grey: none.", fontsize=9.5, color=MUT)
both(fig, "first_map")

# 3. diffusion front scatter
F = R["first"]["list"]
fig, ax = plt.subplots(figsize=(11, 6.2), facecolor=BG); ax.set_facecolor(BG)
for k, c in CONT:
    s = [f for f in F if f["cont"] == k]
    ax.scatter([f["y"] for f in s], [f["km"] for f in s], s=34, c=c, alpha=.88, lw=.5, edgecolor="#fff", label=k, zorder=3)
LAB = {"ENG": "Sheffield FC", "PER": "Lima Cricket and FC", "AUS": "Wanderers, Sydney", "NZL": "New Zealand", "ARG": "Argentina", "IND": "India",
       "USA": "United States", "JPN": "Japan", "NGA": "Nigeria", "GIB": "Gibraltar", "MNG": "Mongolia", "BRA": "Brazil", "EGY": "Egypt"}
for f in F:
    if f["iso"] in LAB:
        r = f["y"] > 2005
        ax.annotate(LAB[f["iso"]], (f["y"], f["km"]), xytext=(-6 if r else 6, 5), textcoords="offset points", fontsize=9.5, ha="right" if r else "left", color=FG)
ax.set_xlim(1852, 2028); ax.set_ylim(-400, 19500)
ax.set_ylabel("km from Sheffield"); ax.grid(color=RULE, lw=.8); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.legend(frameon=False, ncol=6, loc="upper center", bbox_to_anchor=(.5, -.07), fontsize=10, handletextpad=.3, columnspacing=1.2)
fig.tight_layout()
both(fig, "front")

# 4. waves
D = [d for d in R["decades"] if d["dec"] >= 1850]
fig, ax = plt.subplots(figsize=(11, 5.6), facecolor=BG); ax.set_facecolor(BG)
b = np.zeros(len(D)); xs = np.arange(len(D))
for k, c in CONT + [("Unknown", "#B5AFA3")]:
    v = np.array([d[k] for d in D]); ax.bar(xs, v, bottom=b, color=c, width=.82, label=k if k != "Unknown" else "No country"); b += v
ax.set_xticks(xs[::2]); ax.set_xticklabels([f"{d['dec']}s" for d in D][::2], fontsize=10)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
ax.grid(axis="y", color=RULE); ax.set_axisbelow(True)
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.legend(frameon=False, ncol=4, fontsize=10, loc="upper left")
ax.set_ylabel("clubs founded")
ax.text(len(D) - 1, b[-1] + 60, "to 2026", ha="center", fontsize=9, color=MUT)
fig.tight_layout()
both(fig, "waves")

# 5. British Isles to 1890
fig = plt.figure(figsize=(8, 9.2), facecolor=BG)
ax = fig.add_axes([0, 0, 1, 1]); ext = (-10.8, 2.1, 49.7, 59.2)
k = np.cos(np.radians(54.5))
for iso, _, ring in SHAPES:
    lo, la = ring[:, 0], ring[:, 1]
    if lo.max() < ext[0] or lo.min() > ext[1] or la.max() < ext[2] or la.min() > ext[3]:
        continue
    fc = lighten(era(FIRST[iso]), .6) if iso in FIRST and FIRST[iso] <= 1890 else LAND
    ax.add_patch(MPoly(np.column_stack([lo * k, la]), closed=True, fc=fc, ec="#fff", lw=1))
m = (A[:, 2] > 0) & (A[:, 2] <= 1890) & (A[:, 0] > ext[0]) & (A[:, 0] < ext[1]) & (A[:, 1] > ext[2]) & (A[:, 1] < ext[3])
s = A[m]; s = s[np.argsort(-s[:, 2])]
dead = (s[:, 3] > 0)
ax.scatter(s[~dead, 0] * k, s[~dead, 1], s=26, c=[era(y) for y in s[~dead, 2]], lw=.5, edgecolor="#fff", zorder=3)
ax.scatter(s[dead, 0] * k, s[dead, 1], s=26, facecolor=[era(y) for y in s[dead, 2]], lw=1.2, edgecolor=FG, zorder=3)
for nm, lo, la, tx, ty in (("Sheffield FC 1857", -1.4659, 53.3811, 1.0, 54.75), ("Queen's Park 1867", -4.252, 55.826, -8.6, 57.7),
                           ("Wrexham 1864", -3.004, 53.052, -5.6, 53.55), ("Cliftonville 1879", -5.947, 54.62, -8.4, 55.75)):
    ax.annotate(nm, (lo * k, la), xytext=(tx * k, ty), fontsize=11, color=FG, ha="center", arrowprops=dict(arrowstyle="-", color=FG, lw=.8), zorder=6,
                bbox=dict(boxstyle="round,pad=.2", fc=BG, ec="none", alpha=.9))
ax.set_xlim(ext[0] * k, ext[1] * k); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal"); ax.axis("off")
ax.text(ext[0] * k + .1, 58.9, f"Clubs founded by 1890", fontproperties=DISPB, fontsize=20, color=FG, va="top")
ax.text(ext[0] * k + .1, 58.45, f"{int(m.sum()):,} clubs with a point; ringed: later dissolved", fontsize=10, color=MUT, va="top")
era_bar(fig, [.06, .05, .4, .022])
both(fig, "british_isles")

# 6. dissolved
Dd = [d for d in R["dis"]["by_dec"] if d["dec"] >= 1860]
fig, ax = plt.subplots(figsize=(11, 4.8), facecolor=BG); ax.set_facecolor(BG)
ax.bar(range(len(Dd)), [d["n"] for d in Dd], color=[HOT if d["dec"] == 1940 else "#8A877F" for d in Dd], width=.8)
ax.set_xticks(range(len(Dd))[::2]); ax.set_xticklabels([f"{d['dec']}s" for d in Dd][::2], fontsize=10)
ax.grid(axis="y", color=RULE); ax.set_axisbelow(True); ax.set_ylabel("clubs dissolved")
for s in ("top", "right"): ax.spines[s].set_visible(False)
i40 = [d["dec"] for d in Dd].index(1940)
ax.annotate(f"{R['dis']['y1945']} in {R['dis']['peak_year']} alone", (i40, Dd[i40]["n"]), xytext=(i40, Dd[i40]["n"] + 260), ha="center", fontsize=10, color=HOT, arrowprops=dict(arrowstyle="-", color=HOT, lw=.8))
fig.tight_layout()
both(fig, "dissolved")

# 7. coverage
rows = R["coverage"]["top"][:10] + R["coverage"]["bottom"][-10:]
fig, ax = plt.subplots(figsize=(10, 7.4), facecolor=BG); ax.set_facecolor(BG)
ys = np.arange(len(rows))[::-1]
ax.barh(ys, [r["per_m"] for r in rows], color=[PITCH] * 10 + [GOLD] * 10, height=.72)
ax.set_xscale("log"); ax.set_yticks(ys); ax.set_yticklabels([r["name"].replace("Democratic Republic of the Congo", "DR Congo") for r in rows], fontsize=10)
for y, r in zip(ys, rows):
    ax.text(r["per_m"] * 1.08, y, f"{r['per_m']:.0f}" if r["per_m"] >= 10 else f"{r['per_m']:.1f}", va="center", fontsize=9.5)
ax.axhline(9.5, color=MUT, lw=.8, ls=(0, (3, 3)))
ax.set_xlabel("football clubs in Wikidata per million people (log scale)")
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}"))
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout()
both(fig, "coverage")

# header card 1200 x 630
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=BG)
ax = fig.add_axes([.33, .02, .68, .96])
world(ax, lambda iso: lighten(era(FIRST[iso]), .62) if iso in FIRST else None, lw=.25, ext=(-12.0e6, 15.0e6, -5.5e6, 8.4e6))
ax.scatter(X, Y, s=1.3, c=[era(y) for y in dated[:, 2]], lw=0, zorder=3, rasterized=True)
ax.plot([SX], [SY], "o", ms=6, mfc="#fff", mec=FG, mew=1.4, zorder=5)
fig.text(.045, .86, "Where", fontproperties=DISP, fontsize=50, color=FG, va="top")
fig.text(.045, .73, "football", fontproperties=DISP, fontsize=50, color=PITCH, va="top")
fig.text(.045, .60, "clubs come", fontproperties=DISP, fontsize=50, color=FG, va="top")
fig.text(.045, .47, "from", fontproperties=DISP, fontsize=50, color=HOT, va="top")
fig.text(.045, .325, f"{R['source']['n']:,} clubs in Wikidata, from Sheffield FC\nin 1857 to {R['first']['n']} countries and territories.", fontproperties=SERP, fontsize=15.5, color=FG, va="top", linespacing=1.3)
cax = fig.add_axes([.045, .115, .25, .022]); ys = np.arange(1857, 2027)
cax.imshow(np.array([[era(y) for y in ys]]), aspect="auto", extent=(1857, 2026, 0, 1)); cax.set_yticks([]); cax.set_xticks([1857, 1900, 1950, 2026]); cax.tick_params(labelsize=9.5, length=0, colors=MUT)
for s_ in cax.spines.values(): s_.set_visible(False)
fig.text(.045, .158, "dots: clubs, coloured by year founded", fontsize=9.5, color=MUT)
fig.text(.045, .025, "maps.tristanhotham.com/football-origins", fontsize=11, color=MUT)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=BG)
plt.close(fig)
print("figures done", sorted(os.listdir(BL)), sorted(x for x in os.listdir(PA) if x.endswith(".png")))
