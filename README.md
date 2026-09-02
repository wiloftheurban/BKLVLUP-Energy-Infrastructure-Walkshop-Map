# Ecopower Infrastructure Walk

Maps and content for BKLVLUP's energy infrastructure walking tour of East
Flatbush, Remsen Village and Canarsie, Brooklyn. Part of *The Green Book —
Energy Resilience Edition*.

Produced by [GROUND3D](https://ground3d.com) with BKLVLUP.

Eleven stops. F3 variants. Two deliverables from one dataset: a printed
5×7 postcard map and a public interactive web map.

## Structure

```
build.py                  <- ALL CONTENT LIVES HERE. Edit this, then run it.
data/tour.geojson         <- generated. Never hand-edit.
STOP_DESCRIPTIONS.md      <- generated. Readable stop text for review.
ROUTES.md                 <- generated. The five route variants with distances.
CLAUDE.md                 <- brand spec, rendering rules, build guidance.
web/                      <- MapLibre GL JS interactive map.
static/                   <- Python render script for the print map.
```

## Editing content

Stop descriptions, addresses, coordinates and route orders are all defined in
`build.py`. Change them there and regenerate:

```bash
python3 build.py
```

That rewrites `data/tour.geojson`, `STOP_DESCRIPTIONS.md` and `ROUTES.md`
together, so the three can't drift apart. **Do not hand-edit the GeoJSON.**

## Running the web map

```bash
cp web/config.example.js web/config.js
# add your Mapbox token and style URL to web/config.js
python3 -m http.server 8000
# open http://localhost:8000/web/
```

Requires a Mapbox account. Author the style in Mapbox Studio first — see the
Basemap section of `CLAUDE.md` for the label and colour rules.

## Rendering the print map

```bash
python3 static/render.py v1
```

Outputs SVG and 300dpi PNG at 7×5in. The SVG is a starting point for
hand-finishing in Illustrator, not a final file.

## Content status

All eleven descriptions are drafted and sourced. Before anything is published:

- **Johnson Energy Clinic** (stop 5) — founder's name, operating years, systems
  installed, and post-2011 history still need filling from the NYT City Room
  article and video. It is also a private residence; confirm whether the map
  marks the address or the block.
- **946 Utica Ave** (stop 2) — parcel data from ZoLa and ACRIS.
- **Rugby Library** (stop 1) — confirm current cooling-centre hours with BPL.
- **Chef's Choice, De Event Room, Footprints** — details are from listings, not
  from the businesses. Worth confirming in person before bringing a group.
- **Route geometry** — every LineString is a placeholder straight line between
  stops. Snap to sidewalks before publishing.

## Licence

Content © BKLVLUP and GROUND3D. Code released under MIT unless noted.
