"""House style for static figures: fonts (static instances cut from the variable Fraunces in /home/claude/ref/fonts,
written to WORK), the touchline palette, era and continent colours, and Natural Earth outlines in Equal Earth."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import Polygon as MPoly
import numpy as np
from pyproj import Transformer
from common import *

FD = os.path.join(WORK, "fonts"); os.makedirs(FD, exist_ok=True)
if not os.path.exists(f"{FD}/Fraunces-Black.ttf"):
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer
    for w, nm in ((900, "Black"), (700, "Bold")):
        instancer.instantiateVariableFont(TTFont(f"{FONTS}/FrauncesVar.ttf"), {"wght": w, "opsz": 144, "SOFT": 0, "WONK": 0}).save(f"{FD}/Fraunces-{nm}.ttf")
DISP = fm.FontProperties(fname=f"{FD}/Fraunces-Black.ttf")
DISPB = fm.FontProperties(fname=f"{FD}/Fraunces-Bold.ttf")
SERP = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Regular.ttf")
SERB = fm.FontProperties(fname=f"{FONTS}/SourceSerif4-Semibold.ttf")
for f in ("IBMPlexMono-Regular.ttf", "IBMPlexMono-Medium.ttf"):
    fm.fontManager.addfont(f"{FONTS}/{f}")
MONO = "IBM Plex Mono"
plt.rcParams.update({"font.family": MONO, "font.size": 12, "axes.edgecolor": "#646B66", "axes.labelcolor": "#1E2421",
                     "xtick.color": "#646B66", "ytick.color": "#646B66"})
BG, FG, MUT, LAND, RULE, HOT, PITCH, GOLD = "#F7F4EC", "#1E2421", "#646B66", "#E4DFD1", "#E0DACB", "#9E1B32", "#2E6B3A", "#D99A1E"
ERA = [(1857, "#6E0F2B"), (1880, "#B3261E"), (1900, "#E0702A"), (1925, "#D9A21E"), (1950, "#5E9C3F"), (1975, "#22877F"), (2000, "#2F5DA8"), (2026, "#5B3E96")]
CONT = [("Europe", "#9E1B32"), ("South America", "#D99A1E"), ("North America", "#2D5E9E"), ("Africa", "#2E7D4F"), ("Asia", "#D9622B"), ("Oceania", "#7A5CA8")]
CC = dict(CONT)


def hx(h):
    return np.array([int(h[i:i + 2], 16) for i in (1, 3, 5)]) / 255


def era(y):
    if y <= ERA[0][0]:
        return hx(ERA[0][1])
    for (y0, c0), (y1, c1) in zip(ERA, ERA[1:]):
        if y <= y1:
            t = (y - y0) / (y1 - y0)
            return hx(c0) * (1 - t) + hx(c1) * t
    return hx(ERA[-1][1])


def lighten(c, t):
    c = np.array(c) if not isinstance(c, str) else hx(c)
    return c * (1 - t) + hx(BG) * t


EE = Transformer.from_crs(4326, 8857, always_xy=True)
W = jload(f"{DATA}/world.json")


def rings(geom):
    cs = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
    for poly in cs:
        yield np.array(poly[0])


SHAPES = []
for f in W["features"]:
    for ring in rings(f["geometry"]):
        x, y = EE.transform(np.clip(ring[:, 0], -179.9, 179.9), ring[:, 1])
        SHAPES.append((f["properties"]["iso"], np.column_stack([x, y]), ring))
WORLD_EXT = (-12.3e6, 15.6e6, -5.9e6, 8.6e6)


def world(ax, colour_of=lambda iso: None, lw=.3, ext=WORLD_EXT, ec="#FFFFFF", land=LAND, z=1):
    for iso, p, _ in SHAPES:
        c = colour_of(iso)
        ax.add_patch(MPoly(p, closed=True, fc=land if c is None else c, ec=ec, lw=lw, zorder=z))
    ax.set_xlim(ext[0], ext[1]); ax.set_ylim(ext[2], ext[3]); ax.set_aspect("equal"); ax.axis("off")


def proj(lon, lat):
    return EE.transform(np.asarray(lon), np.asarray(lat))


def save(fig, name, dpi=200):
    fig.savefig(name, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)


def points():
    P = jload(f"{DATA}/points.json")["rows"]
    return np.array([[p[0], p[1], p[2], p[3]] for p in P], dtype=float), P
