# BKLVLUP Ecopower Infrastructure Walk — Maps

Two map deliverables, one source of truth.

- `data/tour.geojson` — **the only place stop data lives**
- `static/render.py` → print map: SVG (for Illustrator) + 300dpi PNG
- `web/index.html` → Leaflet map with toggleable route + detailed pins

Client: BKLVLUP (Brooklyn Level Up). Produced by GROUND3D.
Neighborhood: East Flatbush / Canarsie, Brooklyn.

## Hard rules

0. **Read `web/config.example.js` and the Basemap section before writing web
   code.** The web map is MapLibre GL JS with a custom Mapbox style, not
   Leaflet. Never commit `web/config.js` or a real token.
1. **Never hardcode stop data in a renderer.** Both maps read `data/tour.geojson`.
   Content is edited in `build.py`, which regenerates the GeoJSON,
   `STOP_DESCRIPTIONS.md` and `ROUTES.md`. Never hand-edit the GeoJSON.
2. **Interactive map popups render ONLY `name`, `address` and `long`.**
   `energy_connection`, `conversation` and `resource` are facilitator material
   for the printed Green Book and the walkshop script. They live in the data
   so one file stays the source of truth, but they must not appear in a popup.
   `metadata.popup_fields` states this explicitly — read it rather than
   iterating over every property.
3. **Static map shows numbered pins only.** No inline labels, no leader lines.
   Names live in a legend strip keyed to `stop_id`, using `short`.
   See "Static map — 5×7 postcard" below; the geometry does not permit labels.
4. Features split on `properties.kind`: `route` or `stop`.
5. Routes carry `properties.variant` (`v1`, `v2`, `v3`, `v4a`, `v4b`). Render
   one variant at a time; on the web map offer a variant switcher.
   `properties.optional: true` renders dashed.
6. Basemap stays quiet. The route is figure, the city is ground.

## Brand

Sampled from the Summer 2026 "Four projects, one summer" slide. **This is the
dark-tuned palette and it supersedes the values in the intro deck** — BKLVLUP
already shifted every hue for a dark ground. Do not mix the two sets.

```
--page:        #22232E   /* map + page background */
--card:        #292A39   /* panel / popup surface */
--lime:        #C0FD47   /* headline + active pin */
--green:       #6CDF67
--pink:        #D85390
--violet:      #6C4AF4   /* display type ONLY - see below */
--violet-map:  #9076F7   /* lifted for map use */
--white:       #FDFDFD
--muted:       #AFB0BF
```

Deck values (`#B8FF00`, `#42E661`, `#EF529D`, `#7E52FF`) are the light-ground
set. Keep them only if a light print variant is produced.

### Contrast on #22232E

| Color | Ratio | Verdict |
|---|---|---|
| lime `#C0FD47` | 12.90 : 1 | strongest element available |
| green `#6CDF67` | 9.19 : 1 | pass |
| pink `#D85390` | 4.12 : 1 | pass for graphics, marginal for body text |
| violet `#6C4AF4` | **2.91 : 1** | **fails 3.0 threshold** |
| white `#FDFDFD` | 15.32 : 1 | body text |
| muted `#AFB0BF` | 7.26 : 1 | secondary text |

Violet only works on the slide because the numerals are huge display type. At
map scale — a 4px line, a 16px pin number — it disappears. Use `--violet-map
#9076F7` (same hue, 4.54 : 1) for anything on the map. Reserve `#6C4AF4` for
display type at 40px+.

Card surface `#292A39` is only 1.10 : 1 against the page. That is deliberate
surface separation, not a contrast relationship — never rely on it to
distinguish content. Popups need a border or the map beneath them will bleed
through visually.

### Data colors — grouped by scale

**Light is the default theme, for both the web map and print.** Pins are
coloured by `properties.scale`. Colour comes pre-resolved: `properties.color`
is the light value, `properties.color_dark` is the alternate.

| Group | **Light (default)** | On paper | Dark alternate |
|---|---|---|---|
| REGIONAL | `#6844D3` | 6.15 : 1 | `#9076F7` |
| NEIGHBORHOOD | `#118026` | 4.99 : 1 | `#6CDF67` |
| HOUSEHOLD | `#D51470` | 4.96 : 1 | `#D85390` |
| BLOCK | `#D51470` | 4.96 : 1 | `#D85390` |

Household and block share a hue and separate by **pin size** — scale is also
encoded by diameter, smallest for household through largest for regional. That
keeps the palette to three colours while carrying four categories, which
matters on a 5x7 card where a fourth hue would crowd the legend.

Never use `#C0FD47` or `#6CDF67` on a light background: 1.19 : 1 and 1.62 : 1,
effectively invisible. Those are dark-theme values only.

CVD-checked under protanopia and deuteranopia: every pair clears comfortably in
both themes.

**Numbers carry identity, colour is secondary.** Every pin shows its `stop_id`,
1–11. On the static map the number is the *only* identifier, so it must never
be dropped or shrunk below 12pt.

### Access — pin outline, not fill

`properties.access` is a second channel, drawn as the pin's stroke:

```
open / visitor / customer / booking / appointment  -> solid outline
sidewalk                                           -> dashed outline
```

Four stops are sidewalk-only: Con Ed, National Grid, the Hub site, and the
Johnson Energy Clinic. On a public map that persists, a stranger needs to know
whether they can actually go in.

**The Johnson Energy Clinic is a private residence.** Its description carries a
view-from-the-street line. Before publishing, decide whether to mark the exact
address or the block, and ideally contact the current owner.

### Active pin

**Light (default):** `#22232E` disc, lime `#C0FD47` numeral. 15.32 : 1 against
paper, 12.90 : 1 inside. Lime never touches a light background directly — only
the inside of the dark disc.

**Dark alternate:** inverted — lime `#C0FD47` disc, `#22232E` numeral.

In both themes the active pin is the single highest-contrast element on the
map, and lime is always attached to it. Lime means "the thing you are looking
at" and is used for nothing else.

### Route

**Light (default):** `#6844D3`, 4px, over a 6px `#FDFDFD` casing. The casing is
required — without it the line disappears crossing road fills.

**Dark alternate:** `#9076F7`, 4px, no casing. On dark the line separates on
its own.

Optional spur in both themes: same colour, dashed `8 6`.

### Basemap

**Light is the default for both outputs.** Web map and print map use the same
Mapbox light style, so the two deliverables read as one family and the palette
does not have to be maintained twice.

The deciding factor is reading conditions. This is a July walking tour: a dark
map on a phone held in direct sunlight, or a dark 5x7 card held in one hand,
is harder to read than a light one — glare sits on top of dense ink instead of
being absorbed. Screen and paper differ less than sun and shade do.

Web uses **MapLibre GL JS** with the Mapbox style, not Leaflet. Two reasons:
exact brand match (land set to `#FDFDFD` means map and page frame agree), and
label control (a walking tour needs street names and nothing else; stock styles
are all-or-nothing).

A **dark-mode toggle is optional and secondary.** If built, it swaps
`STYLE_DARK` plus every `properties.color` for `properties.color_dark`, and
drops the route casing. Do not build it before the light map works.

**Offline check.** Vector tiles need a network request at load. If the map ever
runs on a kiosk or in a low-signal location, self-hosted tiles or a raster
fallback change this. Confirm with BKLVLUP.

### Mapbox setup

Account: **wiljones**. Two published Standard styles, both Monochrome, POI
labels / landmark icons / admin boundaries off, road labels and pedestrian
paths on.

```
STYLE_DARK   web map            land #22232E, roads brightness 0.25
STYLE_LIGHT  print basemap      land #FDFDFD, roads brightness 0.15
             mapbox://styles/wiljones/cmth7gjh500d201s04i6j0wa3
```

Token and style URLs live in `web/config.js`, copied from
`web/config.example.js`. `config.js` is gitignored.

Use a **URL-restricted public token** (`pk.`) scoped to `localhost:*` and
`wiloftheurban.github.io/*`. Client-side exposure of a public token is normal
and expected for Mapbox; URL restriction is the actual control. Never commit
an `sk.` secret token.

Note the account/repo mismatch: Mapbox is **wiljones**, GitHub is
**wiloftheurban**. The token restriction uses the GitHub Pages domain.

Both styles are **Mapbox Standard**, not classic. MapLibre's Standard support
is newer than its classic support. If the style fails to load in MapLibre,
suspect this first — the fix is rebuilding both from classic Light/Dark
templates. `FALLBACK_STYLE` in config keeps the map usable meanwhile.

### Type

| Role | Print | Web |
|---|---|---|
| Display / titles | Bebas Neue Pro Expanded Bold | Syne ExtraBold |
| Body | Urbanist Regular | Urbanist Regular |
| Handwritten accent | Mansalva | Mansalva |

Bebas Neue Pro is licensed, not a free webfont. Syne, Urbanist and Mansalva
are on Google Fonts.

Minimum label size 8pt. On dark, set body text one notch heavier than you
would on light — light-on-dark type optically thins, and Urbanist Regular at
small sizes on `#22232E` starts to break up.

### Print decision — settled

Light, for both web and print. At $400 for 100 booklets this is digital
printing, which prices per impression, so coverage does not affect cost — the
argument was never about ink. It is about field legibility in July sun, and
about not maintaining two palettes.

## Geometry

Center: `40.6478, -73.9219`. Extent 1,449 m E–W x 781 m N–S — **1.86:1 landscape**.

Eleven stops. Five route variants, defined in `metadata.route_variants` and
documented in `ROUTES.md`:

| Variant | Gather | End | Stops | Distance |
|---|---|---|---|---|
| v1 | Rugby Library | National Grid (+ spur to Footprints) | 9 (+2) | 1.92 mi |
| v2 | De Event Room | Resilience Hub site | 11 | 2.05 mi |
| v3 | Footprints / Wyckoff | Resilience Hub site | 10 | 2.24 mi |
| v4a | Rugby Library | Johnson Energy Clinic | 5 | 0.50 mi |
| v4b | De Event Room | Footprints Cafe | 6 | 1.08 mi |

v4a and v4b are a matched pair — two shorter walkshops covering the full
eleven stops between them.

### Route geometry — IMPORTANT

Every LineString is a **placeholder straight line between stops**. They cut
through blocks and buildings. Replace before publishing: draw by hand at
geojson.io, snap with a walking routing API, or trace OSM sidewalk data in
QGIS. A tour map that routes people through a building is worse than no map.

## Static map — 5x7 postcard

Trim 7 x 5 in landscape, 300 dpi (2100 x 1500 px), 0.125 in bleed. Keep pins
and legend text 0.25 in inside the trim; postcard trimming drifts.

The route bbox is 1.86:1 and the card is 1.4:1, so the map cannot fill the
face. At full 7 in width the map band is about 3.75 in tall, leaving ~1.25 in
for title, legend strip and logo.

**Why labels are impossible here.** At 7 in wide the scale is ~223 m/inch. A
numbered pin needs 12pt (0.167 in) for the numeral to read. Tightest pairs:

| Pair | Ground | On card |
|---|---|---|
| Wyckoff -> Footprints | 59 m | 0.26 in |
| Chef's Choice -> EF Village | 84 m | 0.38 in |
| Library -> Hub site | 132 m | 0.59 in |
| Railroad Pgd -> Con Ed | 134 m | 0.60 in |

Two 12pt pins need ~0.20 in centre-to-centre before any text. There is no room
for labels at any of these. Hence: **numbered pins only, names in a legend
strip**, keyed by `stop_id` and using `short`. This makes `short` load-bearing
— it is the only stop text the card carries.

Wyckoff and Footprints at 0.26 in will nearly touch. Either nudge them apart
optically and accept slight positional error, or print a variant that omits
the optional spur.

The back of the card is a QR code to the interactive map. Eleven stops x four
content fields cannot fit on a 5x7; the card orients, the web map informs.

## Build

### Web — `web/index.html`

MapLibre GL JS, single file, plus `web/config.js` for the token and style URL
(copy from `web/config.example.js`; `config.js` is gitignored).

Layer structure:
- Route line for the active variant (toggleable)
- Optional spur, dashed (toggleable, v1 only)
- Stop pins (toggleable)
- Variant switcher reading `metadata.route_variants` — never a hardcoded list

Popups render `name`, `address`, `long` and nothing else. See Hard rule 2.

If `STYLE_URL` fails to load, fall back to `FALLBACK_STYLE` and log it rather
than rendering a blank map.

Serve with `python -m http.server` and verify in a browser before reporting
done.

### Static — `static/render.py`

Takes the variant id as a CLI argument. Exports SVG and 300dpi PNG at
7 x 5 in landscape. Uses the **light** palette throughout — see "Light theme —
data colors". Do not reuse the dark pin colors here.

**Basemap: Mapbox Static Images API with `STYLE_LIGHT`.** This supersedes
earlier contextily guidance. The Static Images API renders the brand-matched
light style directly, which contextily cannot do, and at @2x a 1280px request
returns 2560px — comfortably above the 2100px needed for 7 in at 300 dpi.

Request the image once, cache it to `static/cache/`, and composite pins, route
and legend over it in matplotlib. Do not re-request on every run; it burns
quota and slows iteration.

Read the token from `web/config.js` or an env var. Never hardcode it in the
script.

If the Static Images request fails, fall back to contextily with CartoDB
Positron and log clearly that the basemap is not brand-matched.

The script owns geometry and basemap; final typography is hand-finished in
Illustrator, so do not fight matplotlib's text rendering.

Run the script and open the PNG before reporting done. Check for pins outside
the frame, overlapping pins, and legend fit.

### Verifying visual output

If the Playwright MCP server is connected, use it: navigate to the local
server, screenshot, and inspect. Report what you actually saw, not what the
code should produce. If it is not connected, say so and ask for a screenshot
rather than guessing.

Set up with:
```
claude mcp add playwright -- npx -y @playwright/mcp@latest \
  --browser chromium --viewport-size "1280,900"
```

A fixed viewport keeps screenshots comparable between runs, which matters when
iterating on pin sizes.

## Editorial frame

This walk is a session in the Green Book — Energy Resilience Edition, in the
lineage of the Negro Motorist Green Book, with an Afrofuturist through-line
connecting elders' memory to younger residents' discovery. Youth, elders, and
organizations not yet in the COAD are explicit priorities.

Spine of the tour: **July 2019 is the wound. The Gateway Park Substation is
the response. The question is who was in the room when it was decided.**

Stop 6 is the thesis. Give it visual weight on both maps — it should read as
the anchor, not as one pin among nine. Stops 5 and 6 are a matched pair (Con
Edison's own FAQ names Railroad Playground); consider drawing that relationship
explicitly rather than leaving it to the reader.

Content status: all nine descriptions rewritten (v3). See
`STOP_DESCRIPTIONS.md` for the readable version and the verification notes.
Do not invent facts. Items flagged "needs local confirmation" there must be
checked before anything goes to print.
