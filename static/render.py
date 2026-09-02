#!/usr/bin/env python3
"""Static 5x7 postcard map for the BKLVLUP Ecopower Infrastructure Walk.

Reads data/tour.geojson (the only place stop data lives — never hand-edit it,
never hardcode stop content here) and renders one route variant as a 7x5in
landscape postcard: numbered pins only, names in a legend strip below the map
band, keyed by pin number using the `short` field. See CLAUDE.md > "Static map —
5x7 postcard" for the layout rationale.

Usage:
    python3 static/render.py full
    python3 static/render.py longview --basemap light
"""
import argparse
import json
import os
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from shapely.geometry import shape
import geopandas as gpd
import contextily as cx

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "tour.geojson"
OUT_DIR = Path(__file__).resolve().parent

# --- Brand (CLAUDE.md > Brand — dark-tuned palette) ----------------------
DARK = dict(
    page="#22232E", card="#292A39", lime="#C0FD47", green="#6CDF67",
    pink="#D85390", violet_map="#9076F7", white="#FDFDFD", muted="#AFB0BF",
    numeral="#22232E", road="#3E3F52",
)
# Deck / light-ground set, darkened data colors per the "Print decision" note.
LIGHT = dict(
    page="#FDFDFD", card="#F1F1F4", lime="#7A9A00", green="#118026",
    pink="#D51470", violet_map="#6844D3", white="#22232E", muted="#5B5C6B",
    numeral="#FDFDFD", road="#FFFFFF",
)

# --- Print geometry --------------------------------------------------------
BLEED_IN = 0.125
TRIM_W_IN, TRIM_H_IN = 7.0, 5.0
PAGE_W_IN, PAGE_H_IN = TRIM_W_IN + 2 * BLEED_IN, TRIM_H_IN + 2 * BLEED_IN  # 7.25 x 5.25
SAFETY_IN = 0.25  # keep pins/legend text this far inside the trim line
MAP_BAND_TRIM_H_IN = 3.30  # within-trim height of the map band
BOTTOM_BAND_TRIM_H_IN = TRIM_H_IN - MAP_BAND_TRIM_H_IN  # 1.70in for title/legend/logo
# 11 legend entries at the 8pt floor need ~0.20in per row plus a title block;
# at the old 1.25in the rows overlapped. See CLAUDE.md > Static map.
BOTTOM_BAND_FULL_H_IN = BOTTOM_BAND_TRIM_H_IN + BLEED_IN  # includes bottom bleed
MAP_BAND_FULL_H_IN = PAGE_H_IN - BOTTOM_BAND_FULL_H_IN  # includes top bleed

DPI = 300
MIN_PIN_NUMERAL_PT = 12.0  # Hard rule: the pin numeral must never drop below 12pt
MIN_LABEL_PT = 8.0  # CLAUDE.md > Type: minimum label size 8pt

# Pin diameter (points) by scale — same encoding as the web map: household
# smallest, block, neighborhood, then regional largest.
SCALE_DIAMETER_PT = {
    "HOUSEHOLD": 18.0,
    "BLOCK": 21.0,
    "NEIGHBORHOOD": 24.0,
    "REGIONAL": 28.0,
}
# Two-digit numerals need a smaller face to stay inside the circle, but the
# 12pt floor is a hard rule -- the numeral is the only identifier on the card.
NUMERAL_PT = 13.0
NUMERAL_PT_2DIGIT = 12.0


def numeral_pt(n):
    return NUMERAL_PT_2DIGIT if len(str(int(n))) > 1 else NUMERAL_PT

# Esri's World Gray Canvas is keyless, unwatermarked and already very quiet:
# pale ground, roads as white line work, no labels at this scale. The dark
# card reuses the same tiles and remaps their luminance onto the brand ground
# (see recolor_basemap), so both themes come from one source.
BASEMAPS = {
    "dark": cx.providers.Esri.WorldGrayCanvas,
    "light": cx.providers.Esri.WorldGrayCanvas,
}
# Opt in to CARTO instead by setting CARTO_API_KEY; matches the web map's
# cartography but CARTO watermarks its raster tiles without a key.
CARTO_BASEMAPS = {
    "dark": cx.providers.CartoDB.DarkMatterNoLabels,
    "light": cx.providers.CartoDB.PositronNoLabels,
}
BASEMAP_ATTRIBUTION = {
    "esri": "Basemap (C) Esri, HERE, Garmin, (C) OpenStreetMap contributors",
    "carto": "(C) OpenStreetMap contributors (C) CARTO",
}


def load_data():
    with open(DATA_PATH) as f:
        return json.load(f)


def variant_lookup(data, variant_id):
    variants = data["metadata"]["route_variants"]
    for v in variants:
        if v["id"] == variant_id:
            return v
    ids = ", ".join(v["id"] for v in variants)
    sys.exit(f"Unknown variant {variant_id!r}. Choose from: {ids}")


def walk_sequence(variant):
    """Stop ids in walking order: `order`, then the spur minus its shared first
    stop. Identical to the web map's walkSequence()."""
    seq = list(variant.get("order", []))
    seq += [sid for i, sid in enumerate(variant.get("spur", [])) if i > 0]
    return seq


def stops_and_routes(data, variant):
    seq = walk_sequence(variant)
    pos_by_id = {sid: i + 1 for i, sid in enumerate(seq)}
    stop_ids = set(seq)
    stops = [
        f for f in data["features"]
        if f["properties"]["kind"] == "stop" and f["properties"]["stop_id"] in stop_ids
    ]
    # Pins and legend are numbered by position along THIS walk, so both must be
    # ordered that way -- sorting by stop_id put the card's "1" on whichever
    # stop happened to be first in the source data, not first on the walk.
    stops.sort(key=lambda f: pos_by_id[f["properties"]["stop_id"]])
    for f in stops:
        f["properties"]["walk_pos"] = pos_by_id[f["properties"]["stop_id"]]
    routes = [
        f for f in data["features"]
        if f["properties"]["kind"] == "route" and f["properties"]["variant"] == variant["id"]
    ]
    return stops, routes


def to_gdf(features):
    if not features:
        return None
    gdf = gpd.GeoDataFrame(
        [f["properties"] for f in features],
        geometry=[shape(f["geometry"]) for f in features],
        crs="EPSG:4326",
    )
    return gdf.to_crs(epsg=3857)


def fit_text(fig, ax, x, y, text, max_width_in, fontsize, **kwargs):
    """Draw `text` at (x, y) in ax data coords, truncating with an ellipsis
    if it would exceed max_width_in. Returns (artist, was_truncated)."""
    renderer = fig.canvas.get_renderer()
    artist = ax.text(x, y, text, fontsize=fontsize, **kwargs)
    truncated = False
    while True:
        bbox = artist.get_window_extent(renderer=renderer)
        width_in = bbox.width / fig.dpi
        if width_in <= max_width_in or len(artist.get_text()) <= 4:
            break
        truncated = True
        artist.set_text(artist.get_text()[:-2].rstrip() + "…")
    return artist, truncated


def build_page(palette):
    fig = plt.figure(figsize=(PAGE_W_IN, PAGE_H_IN), dpi=DPI)
    fig.patch.set_facecolor(palette["page"])

    map_ax = fig.add_axes([0, BOTTOM_BAND_FULL_H_IN / PAGE_H_IN, 1, MAP_BAND_FULL_H_IN / PAGE_H_IN])
    bottom_ax = fig.add_axes([0, 0, 1, BOTTOM_BAND_FULL_H_IN / PAGE_H_IN])

    for ax in (map_ax, bottom_ax):
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    bottom_ax.set_xlim(0, PAGE_W_IN)
    bottom_ax.set_ylim(0, BOTTOM_BAND_FULL_H_IN)
    return fig, map_ax, bottom_ax


def pin_color(row_or_props, basemap_key):
    """Scale colour for the basemap in use. Four groups, four distinct hues;
    each carries a dark-ground and a light-ground value (no single hex clears
    4.5:1 on both). See CLAUDE.md > Brand."""
    if basemap_key == "light":
        return row_or_props.get("color_light") or row_or_props["color"]
    return row_or_props["color"]


def recolor_basemap(map_ax, ground, road):
    """Remap a pale grayscale basemap onto a dark ground.

    World Gray Canvas puts its background around L=0.93 and its road casings at
    white. Compressing [0.85, 1.0] onto [ground, road] keeps the road network
    reading as texture without inverting the image (an inversion would turn the
    open ground black and the roads into a bright web that fights the route)."""
    import numpy as np
    g = np.array([int(ground[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    r = np.array([int(road[i:i + 2], 16) / 255 for i in (1, 3, 5)])
    for im in map_ax.images:
        arr = im.get_array()
        a = np.asarray(arr, dtype=float)
        if a.max() > 1.5:
            a = a / 255.0
        rgb = a[..., :3]
        lum = rgb @ np.array([0.2126, 0.7152, 0.0722])
        t = np.clip((lum - 0.85) / 0.15, 0.0, 1.0)[..., None]
        out = g * (1 - t) + r * t
        if a.shape[-1] == 4:
            out = np.concatenate([out, a[..., 3:]], axis=-1)
        im.set_data(out)


def draw_map(fig, map_ax, gdf_stops, gdf_routes, palette, basemap_key):
    map_ax.set_facecolor(palette["page"])

    # --- extent: fit the variant's stops + route, padded, matched to the
    # map band's own physical aspect ratio (~1.87:1) so it fills the band.
    geoms = list(gdf_stops.geometry)
    if gdf_routes is not None:
        geoms += list(gdf_routes.geometry)
    minx = min(g.bounds[0] for g in geoms)
    miny = min(g.bounds[1] for g in geoms)
    maxx = max(g.bounds[2] for g in geoms)
    maxy = max(g.bounds[3] for g in geoms)
    raw_w, raw_h = maxx - minx, maxy - miny
    pad = 0.16
    w, h = raw_w * (1 + 2 * pad), raw_h * (1 + 2 * pad)
    cx0, cy0 = (minx + maxx) / 2, (miny + maxy) / 2

    target_aspect = (PAGE_W_IN) / MAP_BAND_FULL_H_IN
    if w / h < target_aspect:
        w = h * target_aspect
    else:
        h = w / target_aspect

    xlim = (cx0 - w / 2, cx0 + w / 2)
    ylim = (cy0 - h / 2, cy0 + h / 2)
    map_ax.set_xlim(*xlim)
    map_ax.set_ylim(*ylim)
    map_ax.set_aspect("equal", adjustable="box")

    # --- basemap ---
    # "none" renders a flat ground: no raster at all, which is the cleanest
    # hand-off to Illustrator and sidesteps CARTO's watermark on keyless
    # raster tiles. See the CARTO_API_KEY note in main().
    basemap_ok = True
    if basemap_key == "none":
        basemap_ok = None
        map_ax.set_facecolor(palette["page"])
    else:
        api_key = os.environ.get("CARTO_API_KEY")
        which = "carto" if api_key else "esri"
        source = (CARTO_BASEMAPS if api_key else BASEMAPS)[basemap_key]
        if api_key:
            source = source.copy()
            source["url"] = source["url"] + "?api_key=" + api_key
        try:
            # contextily's own attribution draws black-on-white, which is a
            # bright rectangle on the dark card. Suppress it and set our own
            # in palette colours below.
            cx.add_basemap(
                map_ax, source=source, crs="EPSG:3857",
                attribution=False, reset_extent=False,
            )
            if which == "esri" and basemap_key == "dark":
                recolor_basemap(map_ax, palette["page"], palette["road"])
            map_ax.text(
                0.004, 0.012, BASEMAP_ATTRIBUTION[which], transform=map_ax.transAxes,
                fontsize=4.5, color=palette["muted"], alpha=0.75, ha="left", va="bottom",
                family="DejaVu Sans", zorder=7,
            )
        except Exception as exc:  # network/tile failure — never leave the map blank-white
            basemap_ok = False
            print(f"[render] WARNING: basemap tiles failed to load ({exc!r}); "
                  f"filling map band with the flat page color instead.", file=sys.stderr)
            map_ax.set_facecolor(palette["page"])
        map_ax.set_xlim(*xlim)
        map_ax.set_ylim(*ylim)

    # --- route ---
    if gdf_routes is not None:
        for _, row in gdf_routes.iterrows():
            xs, ys = zip(*list(row.geometry.coords))
            dashed = bool(row.get("optional"))
            map_ax.plot(
                xs, ys, color=palette["violet_map"], linewidth=3.0,
                linestyle=(0, (6, 4)) if dashed else "solid",
                solid_capstyle="round", zorder=3,
            )

    # --- pins ---
    diag = {"out_of_frame": [], "pairs_checked": [], "overlaps": [], "near_touch": [],
            "nudged": []}
    map_w_in = PAGE_W_IN
    map_h_in = MAP_BAND_FULL_H_IN
    xspan = xlim[1] - xlim[0]
    yspan = ylim[1] - ylim[0]
    m_per_in = xspan / map_w_in  # projected metres per inch on the card

    # CLAUDE.md > "Static map": several stops are closer together on the ground
    # than two 12pt pins can sit on a 7in card (Wyckoff -> Footprints is 59 m,
    # about 0.26in). Relax overlapping pins apart just enough to separate them,
    # and report the worst positional error so it is a known, bounded lie.
    nodes = []
    for _, row in gdf_stops.iterrows():
        diam_pt = SCALE_DIAMETER_PT.get(row["scale"], 26.0)
        nodes.append({"row": row, "x": row.geometry.x, "y": row.geometry.y,
                      "x0": row.geometry.x, "y0": row.geometry.y,
                      "r_m": (diam_pt / 72.0 / 2.0) * m_per_in})
    MIN_GAP_M = 0.03 * m_per_in  # 0.03in of clear space between pin edges
    for _ in range(400):
        moved = False
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                a, b = nodes[i], nodes[j]
                dx, dy = b["x"] - a["x"], b["y"] - a["y"]
                d = (dx * dx + dy * dy) ** 0.5 or 1e-6
                need = a["r_m"] + b["r_m"] + MIN_GAP_M
                if d < need:
                    push = (need - d) / 2.0
                    ux, uy = dx / d, dy / d
                    a["x"] -= ux * push; a["y"] -= uy * push
                    b["x"] += ux * push; b["y"] += uy * push
                    moved = True
        if not moved:
            break
    for n in nodes:
        # DejaVu Sans Bold digits run about 0.64em wide; check the numeral fits.
        pos = int(n["row"]["walk_pos"])
        need_pt = len(str(pos)) * numeral_pt(pos) * 0.64
        have_pt = SCALE_DIAMETER_PT.get(n["row"]["scale"], 21.0) - 3.0
        if need_pt > have_pt:
            diag.setdefault("numeral_overflow", []).append(
                (pos, round(need_pt, 1), round(have_pt, 1)))
    for n in nodes:
        err_m = ((n["x"] - n["x0"]) ** 2 + (n["y"] - n["y0"]) ** 2) ** 0.5
        if err_m > 1.0:
            diag["nudged"].append((int(n["row"]["walk_pos"]), round(err_m)))

    placed = []  # (walk_pos, x, y, radius_in)
    for n in nodes:
        row = n["row"]
        x, y = n["x"], n["y"]
        diam_pt = SCALE_DIAMETER_PT.get(row["scale"], 26.0)
        diam_in = diam_pt / 72.0
        radius_in = diam_in / 2.0
        dashed = row["access"] == "sidewalk"
        anchor = row["stop_id"] == 6

        # hairline leader back to the true location when a pin was moved
        if (x - n["x0"]) ** 2 + (y - n["y0"]) ** 2 > (0.5 * m_per_in * 0.04) ** 2:
            map_ax.plot([n["x0"], x], [n["y0"], y], color=palette["white"],
                        linewidth=0.5, alpha=0.5, zorder=4.5, solid_capstyle="butt")

        if anchor:
            map_ax.scatter(
                [x], [y], s=(diam_pt * 1.9 / 2) ** 2 * 3.1416, marker="o",
                facecolor=palette["lime"], edgecolor="none", alpha=0.28, zorder=4,
            )

        map_ax.scatter(
            [x], [y], s=(diam_pt / 2) ** 2 * 3.1416, marker="o",
            facecolor=pin_color(row, basemap_key), edgecolor=palette["white"], linewidths=1.4,
            linestyle=(0, (2, 1.6)) if dashed else "solid", zorder=5,
        )
        map_ax.text(
            x, y, str(int(row["walk_pos"])), fontsize=numeral_pt(row["walk_pos"]),
            color=palette["numeral"],
            ha="center", va="center", fontweight="bold", zorder=6,
            family="DejaVu Sans",
        )

        # frame check (in inches, via display-coordinate round trip)
        disp = map_ax.transData.transform((x, y))
        fig_in = fig.dpi_scale_trans.inverted().transform(disp)
        left_in, bottom_in = map_ax.get_position().x0 * PAGE_W_IN, map_ax.get_position().y0 * PAGE_H_IN
        right_in = map_ax.get_position().x1 * PAGE_W_IN
        top_in = map_ax.get_position().y1 * PAGE_H_IN
        if not (left_in + radius_in <= fig_in[0] <= right_in - radius_in and
                bottom_in + radius_in <= fig_in[1] <= top_in - radius_in):
            diag["out_of_frame"].append(int(row["walk_pos"]))

        placed.append((int(row["walk_pos"]), fig_in[0], fig_in[1], radius_in))

    for i in range(len(placed)):
        for j in range(i + 1, len(placed)):
            a, b = placed[i], placed[j]
            dist_in = ((a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2) ** 0.5
            gap_in = dist_in - (a[3] + b[3])
            diag["pairs_checked"].append((a[0], b[0], round(dist_in, 3), round(gap_in, 3)))
            if gap_in < 0:
                diag["overlaps"].append((a[0], b[0], round(gap_in, 3)))
            elif gap_in < 0.05:
                diag["near_touch"].append((a[0], b[0], round(gap_in, 3)))

    return diag, basemap_ok


def draw_bottom_band(fig, bottom_ax, data, variant, stops, palette, basemap_key):
    bottom_ax.set_facecolor(palette["page"])
    inner_x0 = BLEED_IN + SAFETY_IN
    inner_x1 = PAGE_W_IN - (BLEED_IN + SAFETY_IN)
    inner_y0 = BLEED_IN + SAFETY_IN
    inner_w = inner_x1 - inner_x0

    # A hairline rule separates the map band from the caption block, so the
    # flat ground and the caption ground do not read as one undivided field.
    rule_y = BOTTOM_BAND_FULL_H_IN - 0.02
    bottom_ax.plot([inner_x0, inner_x1], [rule_y, rule_y],
                   color=palette["muted"], linewidth=0.6, alpha=0.35,
                   solid_capstyle="butt", zorder=2)

    # --- title block ---
    TITLE_PT, SUB_PT, STAT_PT, CRED_PT = 13.0, 8.5, 9.5, 7.5
    title_y = rule_y - 0.24
    sub_y = title_y - 0.215
    bottom_ax.text(inner_x0, title_y, "ECOPOWER INFRASTRUCTURE WALK",
                   fontsize=TITLE_PT, color=palette["lime"], fontweight="bold",
                   ha="left", va="center", family="DejaVu Sans")
    bottom_ax.text(inner_x0, sub_y,
                   f"{variant['name']} \u00b7 {variant['gather']} to {variant['end']}",
                   fontsize=SUB_PT, color=palette["muted"], ha="left", va="center",
                   family="DejaVu Sans")
    bottom_ax.text(inner_x1, title_y,
                   f"{variant['walk_miles']} mi  \u00b7  {variant['walk_minutes']} min walk",
                   fontsize=STAT_PT, color=palette["white"], ha="right", va="center",
                   family="DejaVu Sans", fontweight="bold")
    bottom_ax.text(inner_x1, sub_y, "BKLVLUP \u00d7 GROUND3D", fontsize=CRED_PT,
                   color=palette["muted"], ha="right", va="center",
                   family="DejaVu Sans", style="italic")

    # --- legend grid, keyed by pin number (walk position), using `short` ---
    n_cols, n_rows = 3, 4
    GUTTER_IN = 0.18          # clear space between a label and the next swatch
    SWATCH_D_IN = 0.155
    LABEL_GAP_IN = 0.075      # swatch to its own label
    col_w = inner_w / n_cols
    max_w = col_w - SWATCH_D_IN - LABEL_GAP_IN - GUTTER_IN

    legend_top = sub_y - 0.20
    legend_bottom = inner_y0
    avail = legend_top - legend_bottom
    row_h = avail / n_rows
    # Short variants use fewer rows than the 11-stop grid allows; centre the
    # block they do use so the caption does not sit on a dead band of ground.
    rows_used = -(-len(stops) // n_cols)
    legend_top -= (n_rows - rows_used) * row_h / 2.0
    # 8pt is the CLAUDE.md floor; each row needs the cap height plus leading.
    if row_h < MIN_LABEL_PT / 72.0 * 1.55:
        print(f"[render] WARNING: legend rows are {row_h:.3f}in for {MIN_LABEL_PT}pt text; "
              f"raise BOTTOM_BAND_TRIM_H_IN or drop a legend row.", file=sys.stderr)

    truncated_entries = []
    for i, props in enumerate([f["properties"] for f in stops]):
        row_i, col_i = divmod(i, n_cols)
        cx_ = inner_x0 + col_i * col_w
        cy_ = legend_top - (row_i + 0.5) * row_h

        bottom_ax.scatter([cx_ + SWATCH_D_IN / 2], [cy_],
                          s=(SWATCH_D_IN * 72 / 2) ** 2 * 3.1416,
                          facecolor=pin_color(props, basemap_key),
                          edgecolor=palette["white"], linewidths=0.8,
                          linestyle=(0, (1.5, 1.2)) if props["access"] == "sidewalk" else "solid",
                          zorder=5)
        bottom_ax.text(cx_ + SWATCH_D_IN / 2, cy_, str(int(props["walk_pos"])),
                       fontsize=6.5, color=palette["numeral"], ha="center", va="center",
                       fontweight="bold", family="DejaVu Sans", zorder=6)

        artist, truncated = fit_text(
            fig, bottom_ax, cx_ + SWATCH_D_IN + LABEL_GAP_IN, cy_, props["short"],
            max_w, fontsize=MIN_LABEL_PT, color=palette["white"], ha="left",
            va="center", family="DejaVu Sans")
        if truncated:
            truncated_entries.append(props["walk_pos"])

    return truncated_entries


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("variant", help="route variant id: full, library, longview, utica, or ditmas")
    parser.add_argument("--basemap", choices=["dark", "light", "none"], default="dark",
                         help="dark (default), light (print-decision alternate), or none (flat ground, no raster - cleanest hand-off to Illustrator)")
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    args = parser.parse_args()

    data = load_data()
    variant = variant_lookup(data, args.variant)
    stops, routes = stops_and_routes(data, variant)

    gdf_stops = to_gdf(stops)
    gdf_routes = to_gdf(routes)
    palette = LIGHT if args.basemap == "light" else DARK

    fig, map_ax, bottom_ax = build_page(palette)
    diag, basemap_ok = draw_map(fig, map_ax, gdf_stops, gdf_routes, palette, args.basemap)
    truncated = draw_bottom_band(fig, bottom_ax, data, variant, stops, palette, args.basemap)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = out_dir / f"tour-{variant['id']}.svg"
    png_path = out_dir / f"tour-{variant['id']}.png"
    fig.savefig(svg_path, facecolor=fig.get_facecolor())
    fig.savefig(png_path, dpi=DPI, facecolor=fig.get_facecolor())

    print(f"[render] variant {variant['id']} — {len(stops)} stops, "
          f"{'spur ' if variant.get('spur') else ''}basemap="
          f"{'none (flat ground)' if basemap_ok is None else 'OK' if basemap_ok else 'FAILED (flat fill used)'}")
    print(f"[render] wrote {svg_path}")
    print(f"[render] wrote {png_path} ({PAGE_W_IN}x{PAGE_H_IN}in @ {DPI}dpi = "
          f"{int(PAGE_W_IN*DPI)}x{int(PAGE_H_IN*DPI)}px)")

    if diag["out_of_frame"]:
        print(f"[render] CHECK: pins outside the map frame: {diag['out_of_frame']}")
    else:
        print("[render] CHECK: all pins are within the map frame.")

    if diag["overlaps"]:
        print("[render] CHECK: OVERLAPPING pins (negative gap, inches):")
        for a, b, gap in diag["overlaps"]:
            print(f"           stop {a} <-> stop {b}: overlap by {-gap:.3f}in")
    if diag["near_touch"]:
        print("[render] CHECK: pins nearly touching (<0.05in gap):")
        for a, b, gap in diag["near_touch"]:
            print(f"           stop {a} <-> stop {b}: gap {gap:.3f}in")
    if not diag["overlaps"] and not diag["near_touch"]:
        print("[render] CHECK: no overlapping or near-touching pin pairs at this extent.")
    if diag.get("numeral_overflow"):
        print("[render] CHECK: numeral too wide for its pin (pin, needs pt, has pt):")
        for pin, need, have in diag["numeral_overflow"]:
            print(f"           pin {pin}: needs {need}pt, circle allows {have}pt")
    if diag["nudged"]:
        worst = max(diag["nudged"], key=lambda t: t[1])
        print("[render] CHECK: pins nudged apart to stay legible (ground error, metres):")
        for sid, err in sorted(diag["nudged"], key=lambda t: -t[1]):
            print(f"           stop {sid}: {err} m off true position")
        print(f"           worst: stop {worst[0]} at {worst[1]} m. A hairline leader "
              f"marks each true location.")

    if truncated:
        print(f"[render] CHECK: legend text truncated for pin(s): {truncated} "
              f"(short field too long for its grid cell — needs hand-finishing in Illustrator).")
    else:
        print("[render] CHECK: legend text fit without truncation.")


if __name__ == "__main__":
    main()
