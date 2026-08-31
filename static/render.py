#!/usr/bin/env python3
"""Static 5x7 postcard map for the BKLVLUP Ecopower Infrastructure Walk.

Reads data/tour.geojson (the only place stop data lives — never hand-edit it,
never hardcode stop content here) and renders one route variant as a 7x5in
landscape postcard: numbered pins only, names in a legend strip below the map
band, keyed by stop_id using the `short` field. See CLAUDE.md > "Static map —
5x7 postcard" for the layout rationale.

Usage:
    python3 static/render.py v1
    python3 static/render.py v3 --basemap light
"""
import argparse
import json
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
    numeral="#22232E",
)
# Deck / light-ground set, darkened data colors per the "Print decision" note.
LIGHT = dict(
    page="#FDFDFD", card="#F1F1F4", lime="#7A9A00", green="#118026",
    pink="#D51470", violet_map="#6844D3", white="#22232E", muted="#5B5C6B",
    numeral="#FDFDFD",
)

# --- Print geometry --------------------------------------------------------
BLEED_IN = 0.125
TRIM_W_IN, TRIM_H_IN = 7.0, 5.0
PAGE_W_IN, PAGE_H_IN = TRIM_W_IN + 2 * BLEED_IN, TRIM_H_IN + 2 * BLEED_IN  # 7.25 x 5.25
SAFETY_IN = 0.25  # keep pins/legend text this far inside the trim line
MAP_BAND_TRIM_H_IN = 3.75  # within-trim height of the map band
BOTTOM_BAND_TRIM_H_IN = TRIM_H_IN - MAP_BAND_TRIM_H_IN  # 1.25in for title/legend/logo
BOTTOM_BAND_FULL_H_IN = BOTTOM_BAND_TRIM_H_IN + BLEED_IN  # includes bottom bleed
MAP_BAND_FULL_H_IN = PAGE_H_IN - BOTTOM_BAND_FULL_H_IN  # includes top bleed

DPI = 300
MIN_PIN_NUMERAL_PT = 12.0  # Hard rule: the stop_id numeral must never drop below 12pt
MIN_LABEL_PT = 8.0  # CLAUDE.md > Type: minimum label size 8pt

# Pin diameter (points) by scale — same encoding as the web map: household
# smallest, block, neighborhood, then regional largest.
SCALE_DIAMETER_PT = {
    "HOUSEHOLD": 22.0,
    "BLOCK": 26.0,
    "NEIGHBORHOOD": 30.0,
    "REGIONAL": 36.0,
}
NUMERAL_PT = 13.0  # constant across pin sizes, comfortably above the 12pt floor

BASEMAPS = {
    "dark": cx.providers.CartoDB.DarkMatterNoLabels,
    "light": cx.providers.CartoDB.PositronNoLabels,
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


def stops_and_routes(data, variant):
    stop_ids = set(variant.get("order", [])) | set(variant.get("spur", []))
    stops = [
        f for f in data["features"]
        if f["properties"]["kind"] == "stop" and f["properties"]["stop_id"] in stop_ids
    ]
    stops.sort(key=lambda f: f["properties"]["stop_id"])
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


def build_page():
    fig = plt.figure(figsize=(PAGE_W_IN, PAGE_H_IN), dpi=DPI)
    fig.patch.set_facecolor(DARK["page"])

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
    basemap_ok = True
    try:
        cx.add_basemap(
            map_ax, source=BASEMAPS[basemap_key], crs="EPSG:3857",
            attribution="(C) OpenStreetMap contributors (C) CARTO",
            attribution_size=5, reset_extent=False,
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
    diag = {"out_of_frame": [], "pairs_checked": [], "overlaps": [], "near_touch": []}
    placed = []  # (stop_id, x, y, radius_in)
    map_w_in = PAGE_W_IN
    map_h_in = MAP_BAND_FULL_H_IN
    xspan = xlim[1] - xlim[0]
    yspan = ylim[1] - ylim[0]

    for _, row in gdf_stops.iterrows():
        x, y = row.geometry.x, row.geometry.y
        diam_pt = SCALE_DIAMETER_PT.get(row["scale"], 26.0)
        diam_in = diam_pt / 72.0
        radius_in = diam_in / 2.0
        dashed = row["access"] == "sidewalk"
        anchor = row["stop_id"] == 6

        if anchor:
            map_ax.scatter(
                [x], [y], s=(diam_pt * 1.9 / 2) ** 2 * 3.1416, marker="o",
                facecolor=palette["lime"], edgecolor="none", alpha=0.28, zorder=4,
            )

        map_ax.scatter(
            [x], [y], s=(diam_pt / 2) ** 2 * 3.1416, marker="o",
            facecolor=row["color"], edgecolor=palette["white"], linewidths=1.4,
            linestyle=(0, (2, 1.6)) if dashed else "solid", zorder=5,
        )
        map_ax.text(
            x, y, str(row["stop_id"]), fontsize=NUMERAL_PT, color=palette["numeral"],
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
            diag["out_of_frame"].append(int(row["stop_id"]))

        placed.append((int(row["stop_id"]), fig_in[0], fig_in[1], radius_in))

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


def draw_bottom_band(fig, bottom_ax, data, variant, stops, palette):
    bottom_ax.set_facecolor(palette["page"])
    inner_x0 = BLEED_IN + SAFETY_IN
    inner_x1 = PAGE_W_IN - (BLEED_IN + SAFETY_IN)
    inner_y0 = BLEED_IN + SAFETY_IN
    top_y = BOTTOM_BAND_FULL_H_IN - 0.06  # just under the map band, small gap only

    # --- title row ---
    title_y = top_y - 0.16
    bottom_ax.text(
        inner_x0, title_y, "ECOPOWER INFRASTRUCTURE WALK",
        fontsize=13, color=palette["lime"], fontweight="bold",
        ha="left", va="center", family="DejaVu Sans",
    )
    bottom_ax.text(
        inner_x0, title_y - 0.20, f"{variant['name']}  —  {variant['gather']} to {variant['end']}",
        fontsize=8, color=palette["muted"], ha="left", va="center", family="DejaVu Sans",
    )
    stats = f"{variant['walk_miles']} mi  ·  {variant['walk_minutes']} min walk"
    bottom_ax.text(
        inner_x1, title_y, stats, fontsize=9, color=palette["white"],
        ha="right", va="center", family="DejaVu Sans", fontweight="bold",
    )
    bottom_ax.text(
        inner_x1, title_y - 0.20, "BKLVLUP × GROUND3D", fontsize=7.5,
        color=palette["muted"], ha="right", va="center", family="DejaVu Sans", style="italic",
    )

    # --- legend grid: 2 rows x 6 cols, keyed by stop_id, using `short` ---
    legend_top = title_y - 0.42
    legend_bottom = inner_y0
    n_cols = 4
    n_rows = 3
    col_w = (inner_x1 - inner_x0) / n_cols
    row_h = (legend_top - legend_bottom) / n_rows

    truncated_entries = []
    for i, feature_props in enumerate([f["properties"] for f in stops]):
        row_i, col_i = divmod(i, n_cols)
        cx_ = inner_x0 + col_i * col_w
        cy_ = legend_top - row_i * row_h - row_h / 2

        swatch_d_in = 0.15
        bottom_ax.scatter(
            [cx_ + swatch_d_in / 2], [cy_], s=(swatch_d_in * 72 / 2) ** 2 * 3.1416,
            facecolor=feature_props["color"], edgecolor=palette["white"], linewidths=0.8,
            linestyle=(0, (1.5, 1.2)) if feature_props["access"] == "sidewalk" else "solid",
            zorder=5,
        )
        bottom_ax.text(
            cx_ + swatch_d_in / 2, cy_, str(feature_props["stop_id"]),
            fontsize=6.5, color=palette["numeral"], ha="center", va="center",
            fontweight="bold", family="DejaVu Sans", zorder=6,
        )

        text_x = cx_ + swatch_d_in + 0.06
        max_w = col_w - swatch_d_in - 0.10
        artist, truncated = fit_text(
            fig, bottom_ax, text_x, cy_, feature_props["short"], max_w,
            fontsize=MIN_LABEL_PT, color=palette["white"], ha="left", va="center",
            family="DejaVu Sans",
        )
        if truncated:
            truncated_entries.append(feature_props["stop_id"])

    return truncated_entries


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("variant", help="route variant id: v1, v2, v3, v4a, or v4b")
    parser.add_argument("--basemap", choices=["dark", "light"], default="dark",
                         help="dark (default, matches the digital palette) or light (print-decision alternate)")
    parser.add_argument("--out-dir", default=str(OUT_DIR))
    args = parser.parse_args()

    data = load_data()
    variant = variant_lookup(data, args.variant)
    stops, routes = stops_and_routes(data, variant)

    gdf_stops = to_gdf(stops)
    gdf_routes = to_gdf(routes)
    palette = DARK if args.basemap == "dark" else LIGHT

    fig, map_ax, bottom_ax = build_page()
    diag, basemap_ok = draw_map(fig, map_ax, gdf_stops, gdf_routes, palette, args.basemap)
    truncated = draw_bottom_band(fig, bottom_ax, data, variant, stops, palette)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    svg_path = out_dir / f"tour-{variant['id']}.svg"
    png_path = out_dir / f"tour-{variant['id']}.png"
    fig.savefig(svg_path, facecolor=fig.get_facecolor())
    fig.savefig(png_path, dpi=DPI, facecolor=fig.get_facecolor())

    print(f"[render] variant {variant['id']} — {len(stops)} stops, "
          f"{'spur ' if variant.get('spur') else ''}basemap={'OK' if basemap_ok else 'FAILED (flat fill used)'}")
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

    if truncated:
        print(f"[render] CHECK: legend text truncated for stop_id(s): {truncated} "
              f"(short field too long for its grid cell — needs hand-finishing in Illustrator).")
    else:
        print("[render] CHECK: legend text fit without truncation.")


if __name__ == "__main__":
    main()
