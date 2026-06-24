"""Vector redraw of the hydrovoltaic dataset workflow (Figure 1a)."""
from pathlib import Path as FilePath

import matplotlib
matplotlib.rcParams["svg.fonttype"] = "none"
matplotlib.rcParams["font.family"] = ["Arial", "DejaVu Sans"]

import matplotlib.pyplot as plt
from matplotlib.patches import (Circle, Ellipse, FancyArrowPatch, FancyBboxPatch,
                                Polygon, Rectangle, PathPatch)
from matplotlib.path import Path


# --- Reusable visual style -------------------------------------------------
NAVY = "#17324a"; INK = "#090909"; GRAY = "#676b6c"; LIGHT_GRAY = "#d9dcdc"
BLUE = "#3d73a7"; GREEN = "#5c9e51"; ORANGE = "#d48219"; PURPLE = "#87639b"
RED = "#d45549"; TEAL = "#367f7b"; PALE_BLUE = "#e9f1f8"; WATER = "#97c6df"
LW = 1.15
FS = {"title": 14, "panel": 10.5, "body": 8.2, "small": 7.2, "number": 11}


def text(ax, x, y, label, size="body", **kwargs):
    defaults = dict(ha="left", va="center", fontsize=FS[size], color=INK)
    defaults.update(kwargs)
    return ax.text(x, y, label, **defaults)


def round_box(ax, x, y, w, h, edge, face="#ffffff", radius=1.5, lw=LW):
    p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0.01,rounding_size={radius}",
                       linewidth=lw, edgecolor=edge, facecolor=face)
    ax.add_patch(p); return p


def arrow(ax, start, end, color=GRAY, width=1.05, head=1.65, style="Simple"):
    """Compact filled workflow connector with a stable geometry in data units."""
    x1, y1 = start; x2, y2 = end
    ax.add_patch(Polygon([(x1, y1-width/2), (x2-head, y1-width/2),
                          (x2-head, y1-width), (x2, y2),
                          (x2-head, y1+width), (x2-head, y1+width/2),
                          (x1, y1+width/2)], closed=True, facecolor=color,
                         edgecolor="none", zorder=5))


def outline_arrow(ax, start, end, color=NAVY, lw=1.0, ms=9, rad=0):
    a = FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=ms, linewidth=lw,
                        color=color, connectionstyle=f"arc3,rad={rad}")
    ax.add_patch(a); return a


def panel(ax, x, w, color, title, num):
    round_box(ax, x, 32, w, 48, color, "#ffffff", radius=1.5, lw=.85)
    ax.add_patch(Circle((x + 3.8, 77.1), 1.7, facecolor=color, edgecolor="none"))
    text(ax, x + 3.8, 77.1, str(num), "number", color="white", ha="center", fontweight="bold")
    text(ax, x + w/2, 77.3, title, "panel", ha="center", va="top", fontweight="bold", linespacing=1.36)


def draw_paper(ax, x, y):
    for dx, dy in [(2.1, .9), (1.1, .45), (0, 0)]:
        ax.add_patch(Polygon([(x+dx,y+dy),(x+dx+12,y+dy),(x+dx+11,y+dy+14),(x+dx,y+dy+14)],
                             closed=True, facecolor="#fcfcfb", edgecolor="#53585b", linewidth=.8))
    text(ax, x+6, y+11.7, "JOURNAL", "small", color="#777b7e", ha="center", fontweight="bold")
    ax.plot([x+1.5,x+10.2],[y+10.4,y+10.4], color="#8b8e8f", lw=.8)
    ax.add_patch(Rectangle((x+1.6,y+5.3),8.8,5.4,facecolor="#e3f2f3",edgecolor="#8d9e9e",lw=.7))
    # miniature hydrovoltaic-device sketch, matching the illustrated journal inset
    ax.plot([x+3.3,x+3.3],[y+6.0,y+9.7],color="#8aa4a7",lw=.55)
    ax.plot([x+6.1,x+6.1],[y+6.0,y+9.7],color="#8aa4a7",lw=.55)
    ax.plot([x+2.4,x+9.2],[y+7.0,y+7.0],color="#83aeba",lw=.5)
    ax.add_patch(Circle((x+4.0,y+8.0),.45,facecolor="#c9e5ea",edgecolor="#6f99a2",lw=.35))
    ax.add_patch(Circle((x+7.4,y+8.5),.4,facecolor="#c9e5ea",edgecolor="#6f99a2",lw=.35))
    for yy in [4.0, 2.8, 1.6]: ax.plot([x+1.7,x+10],[y+yy,y+yy],color="#4e5658",lw=.8)
    ax.plot([x+1.7,x+5.7],[y+.5,y+.5],color="#4e5658",lw=.8)
    text(ax, x+7, y+17.2, "…", "panel", ha="center")


def draw_screen(ax, x, y):
    ax.add_patch(Rectangle((x,y),11.6,13,facecolor="#fff",edgecolor="#40484a",lw=.9))
    for yy in [10.7,7.8,4.8]:
        text(ax,x+2.5, y+yy,"✓", "panel", color=GREEN, ha="center", fontweight="bold")
        ax.plot([x+4.1,x+9.3],[y+yy+.2,y+yy+.2], color="#686d6e", lw=.9)
    text(ax,x+2.5,y+2.5,"×", "panel",color=RED,ha="center",fontweight="bold")
    ax.plot([x+4.1,x+8.2],[y+2.6,y+2.6],color="#686d6e",lw=.9)
    ax.add_patch(Circle((x+7.4,y+8.4),3.6,facecolor="#edf3f6",edgecolor="#21282b",lw=2.0))
    ax.add_patch(Ellipse((x+6.25,y+9.55),1.35,.58,facecolor="#ffffff",edgecolor="none",alpha=.75))
    for yy in [9.5,8.5,7.3]: ax.plot([x+5.4,x+9.5],[y+yy,y+yy],color="#b5c4ca",lw=.7)
    ax.plot([x+9.9,x+14.4],[y+5.9,y+1.8],color="#303638",lw=2.4,solid_capstyle="round")


def draw_barrel(ax, x, y):
    ax.add_patch(Rectangle((x,y+2),12.4,10.2,facecolor="#9baebb",edgecolor=NAVY,lw=1))
    ax.add_patch(Rectangle((x+.6,y+2.8),1.5,8.7,facecolor="#c8d4d9",edgecolor="none",alpha=.38))
    ax.add_patch(Ellipse((x+6.2,y+12.2),12.4,4.0,facecolor="#b8c5cc",edgecolor=NAVY,lw=1))
    ax.add_patch(Ellipse((x+6.2,y+2),12.4,4.0,facecolor="#9eafb8",edgecolor=NAVY,lw=1))
    ax.plot([x,x+12.4],[y+7.4,y+7.4],color=NAVY,lw=1)
    # Rounded, plump water droplet: a symmetric sequence of cubic Bezier curves.
    drop = Path([
        (x+6.2, y+8.55),
        (x+5.75, y+7.70), (x+3.95, y+6.05), (x+3.95, y+4.85),
        (x+3.95, y+3.55), (x+4.90, y+3.05), (x+6.20, y+3.05),
        (x+7.50, y+3.05), (x+8.45, y+3.55), (x+8.45, y+4.85),
        (x+8.45, y+6.05), (x+6.65, y+7.70), (x+6.20, y+8.55),
        (x+6.20, y+8.55),
    ], [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY])
    ax.add_patch(PathPatch(drop, facecolor="#fbfdfe", edgecolor="#5d8faf", lw=1.05))
    # One quiet, contour-following highlight, kept inside the left shoulder.
    highlight = Path([(x+5.03, y+5.75), (x+4.60, y+5.05), (x+4.72, y+4.10), (x+5.30, y+3.83)],
                     [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4])
    ax.add_patch(PathPatch(highlight, facecolor="none", edgecolor="#c4e2ee", lw=.72, capstyle="round"))


def draw_cell(ax, x, y):
    # electrolyte cell: outlined vessel, faint liquid layers, electrodes and ions
    ax.add_patch(Rectangle((x,y),15.5,6,facecolor="#fbfbf8",edgecolor="#41484a",lw=1.0))
    ax.add_patch(Rectangle((x+1.0,y+3.25),13.5,2.45,facecolor="#a8d0e3",edgecolor="#4d8197",lw=.65))
    ax.add_patch(Rectangle((x+1.0,y+5.05),13.5,.65,facecolor="#d4edf3",edgecolor="none"))
    ax.plot([x+1,x+14.5],[y+4.5,y+4.5],color="#73a7bd",lw=.45,alpha=.7)
    for xx, yy in [(2.1,4.25),(3.9,4.65),(5.8,4.2),(7.6,4.7),(9.55,4.2),(11.2,4.65),(13.0,4.2)]:
        ax.add_patch(Circle((x+xx,y+yy),.52,facecolor="#5d9ac0",edgecolor="#2e6284",lw=.42))
        ax.add_patch(Circle((x+xx-.14,y+yy+.16),.12,facecolor="#cfeaf3",edgecolor="none"))
    ax.add_patch(Rectangle((x+1.0,y+4.05),1.1,6.8,facecolor="#e9d6b7",edgecolor="#775f46",lw=.8))
    ax.add_patch(Rectangle((x+1.18,y+4.2),.25,6.45,facecolor="#f6ead2",edgecolor="none"))
    ax.add_patch(Rectangle((x+13.4,y+4.05),1.1,6.8,facecolor="#edc7bd",edgecolor="#914d43",lw=.8))
    ax.add_patch(Rectangle((x+13.58,y+4.2),.22,6.45,facecolor="#fae0da",edgecolor="none"))
    for xx, lab in [(3.5,"H⁺"),(7.5,"Na⁺"),(11.5,"Cl⁻")]:
        ax.add_patch(Circle((x+xx,y+16.1),1.15,facecolor="#cde6ef" if lab!="Cl⁻" else "#cae5c9",edgecolor="#4c788d",lw=.7))
        text(ax,x+xx,y+16.1,lab,"small",ha="center",fontweight="bold")
        outline_arrow(ax,(x+xx,y+14.5),(x+xx,y+11.2),color="#3d7eae",ms=7)
    # external circuit and voltmeter
    ax.add_patch(Circle((x+7.7,y-.1),1.4,facecolor="white",edgecolor="#333",lw=1.05))
    text(ax,x+7.7,y-.1,"V","panel",ha="center",fontstyle="italic")


def draw_iv(ax, x, y):
    ax.plot([x,x],[y,y+10.6],color=INK,lw=.8); ax.plot([x,x+14.5],[y,y],color=INK,lw=.8)
    outline_arrow(ax,(x,y),(x,y+10.9),color=INK,ms=6); outline_arrow(ax,(x,y),(x+14.8,y),color=INK,ms=6)
    ax.plot([x+.6,x+12.6],[y+10.1,y+.5],color="#2e69aa",lw=1.1)
    ax.plot([x+6,x+6],[y,y+5.35],color=INK,lw=.75,ls=(0,(3,2))); ax.plot([x,x+6],[y+5.35,y+5.35],color=INK,lw=.75,ls=(0,(3,2)))
    ax.add_patch(Circle((x+6,y+5.35),.58,facecolor=RED,edgecolor="none"))
    text(ax, x-.2, y+11.6,"J", "small",ha="right",fontstyle="italic")
    text(ax,x+15,y-.8,"V", "small",fontstyle="italic")
    text(ax,x-1.0,y+9.6,"J$_{sc}$", "small",ha="center",fontweight="bold")
    text(ax,x+12.6,y-1.9,"V$_{oc}$", "small",ha="center",fontweight="bold")
    text(ax,x+6,y-1.9,"V$_{oc}$/2", "small",ha="center")
    text(ax,x-2.1,y+5.35,"J$_{sc}$\n―\n2", "small",ha="center",linespacing=.6)


def draw_laptop(ax, x, y):
    # clean laptop silhouette with screen bezel, chart, and subtly keyed base
    round_box(ax,x+1.8,y+4.4,13.6,9.2,"#181b1c","#242729",radius=.7,lw=.9)
    ax.add_patch(Rectangle((x+2.6,y+5.2),12.0,7.7,facecolor="#f8f9f7",edgecolor="#090a0a",lw=.75))
    for xx, yy in [(5,8),(7,7),(9,9),(11,7.5),(12.3,10),(6.6,10.7),(10.5,6.4),(4.7,6.6)]: ax.add_patch(Circle((x+xx,y+yy),.33,facecolor="#2e66a7",edgecolor="none"))
    for xx, yy in [(11,10),(12.5,8.7),(10,8.4),(12,6.8),(8.8,7.2)]: ax.add_patch(Circle((x+xx,y+yy),.3,facecolor="#d87962",edgecolor="none"))
    ax.plot([x+4.2,x+12.5],[y+6.4,y+11.0],color="#3975ae",lw=.9,ls=(0,(2,2)))
    ax.plot([x+9.3,x+13.0],[y+7.1,y+10.8],color="#d36b56",lw=.9,ls=(0,(2,2)))
    ax.add_patch(Polygon([(x+1.1,y+4.2),(x+16.2,y+4.2),(x+18.2,y+1.2),(x-.7,y+1.2)],facecolor="#596063",edgecolor="#161a1b",lw=1))
    ax.add_patch(Polygon([(x+1.6,y+3.85),(x+15.8,y+3.85),(x+16.4,y+2.85),(x+1.0,y+2.85)],facecolor="#6c7476",edgecolor="none",alpha=.45))
    for row, yy in enumerate([3.45,3.15]):
        for col in range(7):
            xx=x+4.4+col*1.05+(row*.18)
            ax.add_patch(Rectangle((xx,yy),.68,.16,facecolor="#41484a",edgecolor="none"))
    ax.add_patch(Polygon([(x+7.5,y+2.0),(x+11.0,y+2.0),(x+10.4,y+2.7),(x+8.0,y+2.7)],facecolor="#c2c5c4",edgecolor="#242829",lw=.5))


def draw_ml_icon(ax, x, y, kind):
    """Four compact vector icons used in the descriptor-learning stage."""
    c = "#4a7894"
    if kind == "bars":
        for i, h in enumerate([1.5, 2.4, 1.8]):
            ax.add_patch(Rectangle((x+i*1.05,y),.62,h,facecolor="#a6c9df",edgecolor=c,lw=.7))
        ax.plot([x-.15,x+3.0],[y,y],color=c,lw=.6)
    elif kind == "grid":
        for i in range(3):
            for j in range(3):
                ax.add_patch(Rectangle((x+i*.82,y+j*.82),.76,.76,facecolor="#d0e4ef" if (i+j)%2 else "#a5cadf",edgecolor=c,lw=.35))
    elif kind == "network":
        pts=[(x+1.25,y+1.65),(x+.25,y+.25),(x+2.25,y+.25),(x+1.25,y-.55)]
        for a,b in [(0,1),(0,2),(0,3)]: ax.plot([pts[a][0],pts[b][0]],[pts[a][1],pts[b][1]],color=c,lw=.7)
        for px,py in pts: ax.add_patch(Circle((px,py),.42,facecolor="#8fbad2",edgecolor="#315e7b",lw=.55))
    else:
        ax.add_patch(Circle((x+1.0,y+1.25),1.05,facecolor="#edf5f8",edgecolor="#465e6c",lw=1.0))
        ax.plot([x+1.75,x+2.85],[y+.5,y-.6],color="#465e6c",lw=1.5,solid_capstyle="round")
        ax.plot([x+.32,x+1.52],[y+1.25,y+1.25],color="#91b8ca",lw=.5)
        ax.plot([x+1.0,x+1.0],[y+.65,y+1.85],color="#91b8ca",lw=.5)


def draw_design(ax, x, y):
    # Classic bulb envelope, with a rounded crown and a gentle transition into the neck.
    bulb = Path([
        (x+5.95,y+8.55),
        (x+5.65,y+9.65),(x+4.25,y+11.05),(x+4.25,y+13.15),
        (x+4.25,y+15.55),(x+5.47,y+16.90),(x+7.00,y+16.90),
        (x+8.53,y+16.90),(x+9.75,y+15.55),(x+9.75,y+13.15),
        (x+9.75,y+11.05),(x+8.35,y+9.65),(x+8.05,y+8.55),
        (x+5.95,y+8.55),
    ], [Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4,
        Path.CURVE4,Path.CURVE4,Path.CURVE4,
        Path.CURVE4,Path.CURVE4,Path.CURVE4,
        Path.CURVE4,Path.CURVE4,Path.CURVE4,Path.CLOSEPOLY])
    ax.add_patch(PathPatch(bulb,facecolor="#ffe5a0",edgecolor="#8c7141",lw=.95))
    ax.add_patch(Ellipse((x+5.75,y+14.35),.92,1.82,facecolor="#fff4c9",edgecolor="none",alpha=.62))
    for ang in range(0,360,45):
        import math
        a=math.radians(ang); ax.plot([x+7+4.25*math.cos(a),x+7+5.35*math.cos(a)],[y+13.25+4.25*math.sin(a),y+13.25+5.35*math.sin(a)],color="#333",lw=.82)
    # Fine filament and supports keep the interior technical rather than clip-art-like.
    ax.plot([x+6.28,x+6.28],[y+8.72,y+12.05],color="#725d32",lw=.62)
    ax.plot([x+7.72,x+7.72],[y+8.72,y+12.05],color="#725d32",lw=.62)
    ax.plot([x+6.28,x+6.58,x+7.00,x+7.42,x+7.72],[y+12.05,y+11.38,y+12.28,y+11.38,y+12.05],color="#725d32",lw=.68)
    ax.add_patch(Polygon([(x+5.95,y+8.72),(x+8.05,y+8.72),(x+7.72,y+7.15),(x+6.28,y+7.15)],facecolor="#f1c65e",edgecolor="#4b4b44",lw=.8))
    ax.add_patch(Rectangle((x+5.78,y+6.22),2.44,.92,facecolor="#737779",edgecolor="#383c3c",lw=.8))
    ax.plot([x+5.93,x+8.07],[y+6.53,y+6.53],color="#aeb4b4",lw=.35)
    for i in range(4):
        ax.add_patch(Polygon([(x+1,y+1.2+i*1.2),(x+10,y-1+i*1.2),(x+14,y+.5+i*1.2),(x+5,y+2.7+i*1.2)],facecolor="#719bb4",edgecolor=NAVY,lw=.7))
        ax.plot([x+1.6,x+10],[y+1.35+i*1.2,y-.55+i*1.2],color="#a7c6d5",lw=.4)
    for xx, sign, col in [(2,"+", "#e88575"),(12,"+","#e88575"),(14.7,"+","#e88575"),(-.5,"+","#9ecbe1"),(16.5,"+","#9ecbe1")]:
        ax.add_patch(Circle((x+xx,y+8),1.0,facecolor=col,edgecolor=NAVY,lw=.55)); text(ax,x+xx,y+8,"+","small",ha="center",fontweight="bold")
    for xx in [2,7,12]: outline_arrow(ax,(x+xx,y+5.3),(x+xx,y+9.1),color=RED,ms=8)


def bullet_list(ax, x, y, lines, dy=3.15, size="body"):
    for i, line in enumerate(lines): text(ax,x,y-i*dy,"•  "+line,size)


def draw_exclusion(ax):
    # lower exclusion strip
    round_box(ax,4,9,112,17.3,"#9ac475","#fbfdf7",radius=1.5,lw=.8)
    text(ax,60,27,"Excluded from the dataset", "body",color=GREEN,ha="center",fontweight="bold")
    groups=[(15,"Droplet triboelectric /\ncontact electrification\nsystems"),(43,"Salinity-gradient\nosmotic membrane\npower systems"),(72,"Active-electrode /\nredox-dominant\nsystems"),(101,"Galvanic / battery-like\nconfigurations dominated\nby electrode reactions")]
    for i,(cx,label) in enumerate(groups):
        text(ax,cx,24.1,label,"body",ha="center",va="top",fontweight="bold",linespacing=1.35)
        if i<3: ax.plot([cx+12.6,cx+12.6],[11.5,23.2],color="#c2dca6",lw=.8)
        # consistent red exclusion mark, deliberately lighter than the title text
        xx, yy = cx+10.5, 15
        ax.plot([xx-.95,xx+.95],[yy-.95,yy+.95],color="#df5c4c",lw=2.05,solid_capstyle="butt")
        ax.plot([xx-.95,xx+.95],[yy+.95,yy-.95],color="#df5c4c",lw=2.05,solid_capstyle="butt")
    # small excluded-system illustrations
    # triboelectric droplet, sharing the main-panel droplet's continuous rounded contour
    small_drop = Path([
        (13.2,17.8),
        (12.75,16.85), (10.75,14.65), (10.75,13.30),
        (10.75,11.90), (11.80,11.20), (13.15,11.20),
        (14.55,11.20), (15.55,11.95), (15.55,13.30),
        (15.55,14.65), (13.65,16.85), (13.20,17.80),
        (13.20,17.80),
    ], [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CURVE4, Path.CURVE4, Path.CURVE4,
        Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY])
    ax.add_patch(PathPatch(small_drop, facecolor="#b7dcea",edgecolor="#5b8ba8",lw=.9))
    small_highlight = Path([(12.05,14.1),(11.55,13.30),(11.75,12.45),(12.35,12.15)],
                           [Path.MOVETO,Path.CURVE4,Path.CURVE4,Path.CURVE4])
    ax.add_patch(PathPatch(small_highlight,facecolor="none",edgecolor="#d7edf4",lw=.58,capstyle="round"))
    # A single, crisp lightning bolt tucked behind the droplet's right shoulder.
    bolt = Path([(16.65,18.20),(18.18,18.25),(16.72,15.58),
                 (18.38,15.66),(14.48,11.03),(15.72,14.67),
                 (14.13,14.64),(16.65,18.20)],
                [Path.MOVETO,Path.LINETO,Path.LINETO,Path.LINETO,
                 Path.LINETO,Path.LINETO,Path.LINETO,Path.CLOSEPOLY])
    ax.add_patch(PathPatch(bolt,facecolor="#edf0ef",edgecolor="#687578",lw=.78,joinstyle="miter"))
    ax.add_patch(Rectangle((7.1,10.8),10.4,1.5,facecolor="#d5d6d1",edgecolor="#999",lw=.5))
    ax.add_patch(Rectangle((36.5,10.7),11.8,6.7,facecolor="#d5edf5",edgecolor="#548ba6",lw=.9)); ax.add_patch(Rectangle((36.5,15.8),11.8,1.6,facecolor="#edf8fb",edgecolor="none")); ax.add_patch(Rectangle((42.0,10.7),.9,8.0,facecolor="#e6d5a6",edgecolor="#765e36",lw=.7))
    for xx,yy in [(38,15),(40,13),(45,15),(46,12.5),(39,12)]: ax.add_patch(Circle((xx,yy),.48,facecolor="#76b5d2",edgecolor="#34769b",lw=.45))
    text(ax,34.5,14,"High\nsalinity","small",color="#28669a",ha="center",fontweight="bold"); text(ax,50,14,"Low\nsalinity","small",color="#28669a",ha="center",fontweight="bold")
    outline_arrow(ax,(39.8,14),(44.1,14),color="#6d6558",ms=7)
    ax.add_patch(Ellipse((65,12.8),6.8,2.6,facecolor="#5e8bc1",edgecolor=NAVY,lw=.9)); ax.add_patch(Ellipse((74,12.8),6.8,2.6,facecolor="#e98b78",edgecolor="#994b42",lw=.9))
    ax.add_patch(Ellipse((64.1,13.35),3.1,.45,facecolor="#9fc3df",edgecolor="none",alpha=.6)); ax.add_patch(Ellipse((73.1,13.35),3.1,.45,facecolor="#f2b1a3",edgecolor="none",alpha=.65))
    outline_arrow(ax,(65,15),(74,15),color="#56636b",ms=8,rad=-.6); outline_arrow(ax,(74,15),(65,15),color="#56636b",ms=8,rad=-.6); text(ax,69.5,17.8,"e⁻","body",ha="center",fontstyle="italic")
    ax.add_patch(Rectangle((93.8,10.5),12.8,5.1,facecolor="#c6e6f0",edgecolor="#568092",lw=.9)); ax.add_patch(Rectangle((93.8,14.25),12.8,1.35,facecolor="#e9f6f8",edgecolor="none")); ax.plot([93.8,106.6],[y for y in [14.2,14.2]],color="#5b8ca0",lw=.7)
    ax.add_patch(Rectangle((96,11),1.3,5.8,facecolor="#6f7477",edgecolor="#333",lw=.5)); ax.add_patch(Rectangle((102.8,11),1.3,5.8,facecolor="#cc776b",edgecolor="#7d3934",lw=.5))
    outline_arrow(ax,(97,17),(103.4,17),color="#56636b",ms=7,rad=-.55); text(ax,100.2,17.6,"e⁻","body",ha="center",fontstyle="italic")


def draw_outcome(ax):
    round_box(ax,120,9,30,17.3,"#b8c8db",PALE_BLUE,radius=1.5,lw=.8)
    text(ax,135,23.8,"Outcome","body",color="#345397",ha="center",fontweight="bold")
    # clipboard
    round_box(ax,123.1,13.8,7,7.5,"#4d5b66","#fbfbfa",radius=.4,lw=1)
    ax.add_patch(Rectangle((123.45,14.15),6.3,6.8,facecolor="#fdfdfb",edgecolor="none"))
    ax.add_patch(Circle((126.6,21.4),.6,facecolor="#66727c",edgecolor="#4d5b66",lw=.5)); ax.add_patch(Rectangle((125.7,20.8),1.8,.8,facecolor="#66727c",edgecolor="#4d5b66",lw=.4))
    for yy in [18.9,17.3,15.7]:
        text(ax,125.1,yy,"✓","small",color="#4b8595",ha="center",fontweight="bold")
        ax.plot([126.3,129.2],[yy,yy],color="#555",lw=.6)
        ax.plot([126.3,128.0],[yy-.3,yy-.3],color="#c5ced1",lw=.4)
    bullet_list(ax,132.6,19.9,["Curated dataset","Descriptor set","ML models","Design insights"],dy=2.65)


def build_figure():
    fig, ax = plt.subplots(figsize=(16, 10.2), dpi=160)
    ax.set_xlim(0, 155.5); ax.set_ylim(6, 89); ax.axis("off")
    # Figure heading
    text(ax,2,86.8,"A", "title",fontweight="bold")
    text(ax,7.2,86.8,"Overall workflow for building the hydrovoltaic dataset\nand conducting descriptor-learning analysis", "title",fontweight="bold",va="top",linespacing=1.35)
    xs=[1.5,23.5,45.5,64.5,87.5,111,135]; ws=[20,20,18,22,22,21,20]
    specs=[(BLUE,"Literature\ncollection"),(GREEN,"Scope screening\nand exclusion"),("#efba57","Curated\nnon-galvanic\ndataset"),("#b59ac7","Output and\ndescriptor\nextraction"),("#eb9d91","Standardized\ntarget\nconstruction"),("#6686ad","Descriptor-based\nML analysis"),("#79afae","Virtual design\nand design rules")]
    for i,(x,w,(c,t)) in enumerate(zip(xs,ws,specs),1): panel(ax,x,w,c,t,i)
    for x1,x2 in zip([21.5,43.5,61.5,84.5,108.5,132],[23.5,45.5,64.5,87.5,111,135]): arrow(ax,(x1,61.2),(x2,61.2))
    # Stage 1
    draw_paper(ax,4.2,54.4); bullet_list(ax,3.6,49,["2016–2025\n   publications","Hydrovoltaic\n   devices"],dy=5.1)
    # Stage 2
    draw_screen(ax,27.1,55.8); bullet_list(ax,25.5,49,["Hydrovoltaic\n   scope definition","Remove\n   non-comparable\n   systems"],dy=5.0)
    # Stage 3
    draw_barrel(ax,48.8,53.8); bullet_list(ax,47,49,["Non-galvanic\n   hydrovoltaic\n   devices","Standardized\n   units"],dy=6.7)
    # Stage 4
    # Lowered slightly to give the descriptor title and ion labels independent space.
    draw_cell(ax,67,52.5); text(ax,66,48.5,"Extract from each study:","body",fontweight="bold")
    bullet_list(ax,66,46.0,["V$_{oc}$, J$_{sc}$, (P reported)","Internal resistance (R)","Structure_class","Ion type / electrolyte","Mechanism label","Other reported\n   information"],dy=2.05)
    # Stage 5
    round_box(ax,89.8,63,17.8,6.5,"#e05849","#fffafa",radius=.8,lw=.9)
    text(ax,98.7,66.2,r"P$_{est}$ $\approx$ $\frac{V_{oc}\,J_{sc}}{4}$", "panel",ha="center",fontstyle="italic")
    draw_iv(ax,92.7,50); bullet_list(ax,89.2,42.8,["Linear I–V assumption","Log-transform of P$_{est}$\n   for modeling"],dy=4.7)
    # Stage 6
    draw_laptop(ax,113.2,57.5)
    icons=[("bars","Model comparison"),("grid","Feature ablation"),("network","Permutation / SHAP\nanalysis"),("lens","Descriptor\ninterpretation")]
    for i,(ico,lab) in enumerate(icons):
        yy=54.0-i*4.25
        draw_ml_icon(ax,112.9,yy-1.0,ico)
        text(ax,118.2,yy,lab,"body",fontweight="bold" if i<2 else "normal")
    # Stage 7
    draw_design(ax,136,55.5); bullet_list(ax,137,49,["Resistance regime\n   analysis","Virtual design\n   mapping","Design ranking\n   and guidance"],dy=5.0)
    ax.plot([33,33],[32,26.2],color=GREEN,lw=1.2,ls=(0,(4,3))); outline_arrow(ax,(33,26.2),(33,25.0),color=GREEN,ms=8)
    draw_exclusion(ax); draw_outcome(ax)
    return fig


def main():
    root = FilePath(__file__).resolve().parents[1]
    out = root / "figures"; out.mkdir(exist_ok=True)
    fig = build_figure()
    fig.savefig(out / "fig_1a_redrawn.svg", format="svg", bbox_inches="tight", transparent=True)
    fig.savefig(out / "fig_1a_redrawn.png", format="png", bbox_inches="tight", transparent=True, dpi=320)
    plt.close(fig)


if __name__ == "__main__":
    main()
