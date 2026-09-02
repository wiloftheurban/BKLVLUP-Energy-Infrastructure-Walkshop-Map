# BKLVLUP Energy Infrastructure Walking Tour — Maps

Maps for BKLVLUP's Energy Infrastructure Walking Tour: eleven stops across East
Flatbush, Remsen Village, and Canarsie, Brooklyn. Produced by GROUND3D in
collaboration with the BKLVLUP EcoPower '26 Summer Fellows.

Two deliverables, one source of truth.

| | What it is | Built by |
|---|---|---|
| **Web map** | Self-guided MapLibre map with a route switcher, stop list, and per-stop walking directions | `web/index.html` |
| **Print map** | 5×7 postcard, SVG for Illustrator plus a 300dpi PNG | `static/render.py` |

Both read `data/tour.geojson`. Neither hardcodes stop content.

## Layout

```
build.py                 the ONLY place stop + route content is edited
data/tour.geojson        generated — never hand-edit
data/route_cache.json    cached OSRM walking routes, committed for reproducible builds
STOP_DESCRIPTIONS.md     generated — readable stop copy + verification notes
ROUTES.md                generated — per-leg distances for each variant
web/index.html           MapLibre map (single file)
web/config.js            Mapbox token + style URLs — gitignored, never commit
web/config.example.js    committed template
static/render.py         print postcard renderer
CLAUDE.md                design rules, brand, and the reasoning behind both maps
```

## Build

Everything downstream is generated. Edit `build.py`, then:

```bash
python3 build.py
```

This regenerates `data/tour.geojson`, `STOP_DESCRIPTIONS.md`, and `ROUTES.md`.
No third-party packages required.

Route geometry is snapped to the OpenStreetMap pedestrian network via the
public OSRM foot profile and cached in `data/route_cache.json`, so rebuilds are
deterministic and work offline. Delete that file to re-route; set
`TOUR_NO_ROUTING=1` to force the straight-line fallback.

## Web map

```bash
cp web/config.example.js web/config.js   # then add your Mapbox token
python3 -m http.server
# open http://localhost:8000/web/
```

`web/config.js` is gitignored. Use a **URL-restricted public token** (`pk.`)
scoped to your deploy domain plus `localhost`.

Custom Studio styles go in `STYLE_URL_LIGHT` / `STYLE_URL_DARK`; either may be
`null` to use the token-free CARTO fallback. **Author them from a classic
Studio template, not Mapbox Standard** — Standard (v3) styles keep all
cartography in `imports`, which MapLibre cannot render. See CLAUDE.md ›
Basemap for how to check a style before wiring it up.

The map defaults to the light theme for legibility outdoors in summer; the
toggle persists per browser.

## Print map

Needs `geopandas`, `contextily`, `matplotlib`, `shapely`:

```bash
python3 -m venv .venv && .venv/bin/pip install geopandas contextily matplotlib shapely
.venv/bin/python static/render.py full
.venv/bin/python static/render.py utica
.venv/bin/python static/render.py ditmas
```

Writes `static/tour-<variant>.svg` and `.png` (7.25×5.25in at 300dpi, including
bleed). Outputs are gitignored; typography is hand-finished in Illustrator.

The basemap is Esri World Gray Canvas — keyless and unwatermarked. `--basemap
dark` (default) remaps its luminance onto the brand ground; `--basemap light`
uses it as-is; `--basemap none` drops it for a flat ground. **Do not use
CARTO without a key** — it now watermarks its raster tiles — but if you have
one, `CARTO_API_KEY=... .venv/bin/python static/render.py full` uses it
instead.

Each run self-checks and prints pins outside the frame, overlapping pins, how
far any pin was nudged from its true position, and legend text that didn't fit.
Read that output before sending a card to print.

## Routes

Three variants, defined in `build.py` and documented with per-leg distances in
`ROUTES.md`.

| id | Name | Stops | Distance |
|---|---|---|---|
| `full` | The Full Walk *(default)* | 11 | 2.35 mi · ~50 min |
| `utica` | Utica Walkshop | 5 | 0.56 mi · ~12 min |
| `ditmas` | Ditmas Walkshop | 6 | 1.33 mi · ~29 min |

Stop counts include each route's optional extension. Distances are routed
walking distance, not straight-line.

## Before changing anything

Read `CLAUDE.md`. It carries the hard rules that are easy to break by accident:

- Stop content lives **only** in `build.py`; the GeoJSON is generated.
- Map popups render `name`, `address`, and `long` only. The
  `energy_connection`, `conversation`, and `resource` fields are facilitator
  material for the printed Green Book, not for the map.
- **Both maps number pins by position along the selected route**, restarting at
  1 for each variant, and must always agree. The sequence is built by
  `walkSequence()` in `web/index.html` and `walk_sequence()` in
  `static/render.py`; change one, change the other. `stop_id` is the internal
  identity only, never the number a reader sees.
- The static map is **numbered pins only**, keyed to a legend strip.
- Mobile is the baseline: design and verify at a 390px viewport.

## Status

- Route geometry is machine-routed on OSM data and has **not** been walked.
  Verify on the ground before publishing.
- Items flagged `VERIFY` in `STOP_DESCRIPTIONS.md` must be confirmed before
  anything goes to print.
- The Johnson Energy Clinic is a private residence that has since been sold and
  redeveloped. The stop marks a site, not a building.
