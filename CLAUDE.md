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
   Names live in a legend strip keyed to the pin number, using `short`.
   See "Static map — 5×7 postcard" below; the geometry does not permit labels.
4. Features split on `properties.kind`: `route` or `stop`.
5. Routes carry `properties.variant` (`full`, `utica`, `ditmas`). Render
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

Pins are coloured by `properties.scale`, which answers "at what level does this
sit in the energy system." **Four groups, four distinct hues — no two groups
share a swatch.** Colour comes pre-resolved on each stop feature: `color` for a
dark ground, `color_light` for a light one.

| Scale | Dark (`color`) | on #22232E | Light (`color_light`) | on Positron | Stops |
|---|---|---|---|---|---|
| HOUSEHOLD | `#4FD8E8` | 9.14:1 | `#0E7C8C` | 4.70:1 | Johnson Energy Clinic, Wyckoff House |
| BLOCK | `#D85390` | 4.12:1 | `#D51470` | 4.83:1 | Chef's Choice, De Event Room, Footprints |
| NEIGHBORHOOD | `#6CDF67` | 9.19:1 | `#118026` | 4.86:1 | Library, vacant lot, EF Village, Railroad Pgd |
| REGIONAL | `#9076F7` | 4.54:1 | `#6844D3` | 5.99:1 | Con Ed Gateway, National Grid |

**Each group needs a dark/light pair — a single hex cannot serve both.** To
clear 4.5:1 on `#22232E` a colour needs relative luminance ≥ 0.253; to clear it
on a near-white basemap it needs ≤ 0.168. There is no overlap. Any new data
colour must therefore ship as a pair, and both halves must be checked.

Scale is *also* encoded by diameter — smallest for household through largest
for regional — so size and hue reinforce each other rather than hue carrying
the load alone.

Household cyan was chosen over amber because it separates from the other three
on the **blue–yellow axis**, which both protanopes and deuteranopes retain.
Amber collapses toward green under deuteranopia at nearly identical lightness.
Cyan and violet both read blue, but differ in lightness by ~2.2x.

CVD-checked under protanopia and deuteranopia: every pair clears dE 45+.

**Both maps number pins by position along the active variant's walk**, 1..N,
restarting at 1 for each variant. The card and the web map must always agree:
they derive from the same sequence (`order`, then `spur` minus its shared first
stop), implemented as `walkSequence()` in `web/index.html` and `walk_sequence()`
in `static/render.py`. Change one, change the other.

This is deliberately *not* `stop_id`. A card carried on the walk has to count
the walk: numbering by `stop_id` put "1" on the Rugby Library, which is where
The Full Walk *ends*, and started the route at "6".

`stop_id` remains the stable internal identity — it keys the data, the popups,
the list/pin sync, and `STOP_DESCRIPTIONS.md` — but it is never the number a
reader sees. On the static map the numeral is the *only* identifier, so it must
never be dropped or shrunk below 12pt, and it keys the legend strip.

### Access — pin outline, not fill

`properties.access` is a second channel, drawn as the pin's stroke:

```
open / visitor / customer / booking / appointment  -> solid outline
sidewalk                                           -> dashed outline
```

Four stops are sidewalk-only: Con Ed, National Grid, the vacant lot, and the
Johnson Energy Clinic. On a public map that persists, a stranger needs to know
whether they can actually go in.

**The Johnson Energy Clinic is a private residence.** The address is public and
the exact point is marked, but the house was sold and redeveloped, so the stop
is a *site*, not a building. Its description says so and carries a
view-from-the-sidewalk line asking visitors not to approach the door or
photograph residents. Keep both when editing that stop.

### Active pin

Lime `#C0FD47` fill, `#22232E` numeral, 12.90 : 1 both ways. On dark, lime is
already the headline color, so this reads as continuity rather than an
exception — lime means "the thing you are looking at."

### Route

`#9076F7`, 4px. **No white casing** — on a dark basemap the line separates on
its own. Optional spur: same color, dashed `8 6`.

### Basemap

**Web: MapLibre GL JS + a custom Mapbox style.** Not Leaflet, not off-the-shelf
tiles. Two reasons, both functional:

1. **Exact brand match.** Land set to `#22232E` means the map and the page
   frame are the same dark. Off-the-shelf dark tiles are a neutral near-black
   and sit inside a blue-black frame as a visible seam.
2. **Label control.** A walking tour needs street names and nothing else.
   Stock styles are all-or-nothing; a custom style keeps street labels and
   drops POI, transit, and business labels that compete with the pins.

**The web map ships both themes with a toggle, and defaults to LIGHT.** This
is a field-legibility decision, not a brand one: the tour is walked in July, and
a dark screen in direct sun sits behind a layer of glare. The dark theme is
retained for evening and indoor planning use, and the choice persists in
`localStorage`. Every data colour therefore needs its dark/light pair (see
Brand > Data colors), and every UI colour is a CSS custom property redefined
under `:root[data-theme="dark"]` — never hardcode a hex in a rule.

Two Studio styles, one per theme, in `web/config.js` as `STYLE_URL_LIGHT` and
`STYLE_URL_DARK`; either may be `null`, in which case that theme falls back to
the token-free CARTO style (Positron / Dark Matter).

**Author them from a CLASSIC Studio template, never Mapbox Standard.** This is
the one hard constraint on the styles, and it is easy to trip: Studio's default
"new style" flow now produces a **Mapbox Standard (v3)** style, whose JSON has
`"layers": []` and puts all cartography behind
`"imports": [{"url": "mapbox://styles/mapbox/standard"}]`. `imports` is a
Mapbox GL JS v3 feature that **MapLibre does not implement**, so such a style
renders as an empty map. Standard styles also write `"terrain": null`, which
MapLibre's validator rejects outright with `terrain: object expected, null
found` — that error is the usual first symptom.

Pick a classic template instead (Streets v12, Light v11, Dark v11, or a
duplicate of one) so the style ships real `layers`. To check a style before
wiring it up:

```
curl -s "https://api.mapbox.com/styles/v1/<user>/<id>?access_token=<pk>" \
  | python3 -c "import sys,json; d=json.load(sys.stdin); \
    print('layers', len(d.get('layers',[])), '| imports', bool(d.get('imports')))"
```

`layers 0 | imports True` means MapLibre cannot render it. `index.html` builds
the map on the CARTO fallback first and only then upgrades to the custom style,
stripping null `terrain`/`fog`/`sky` and refusing a style with `imports` or no
layers — so a bad style degrades to the fallback with a named reason in the
console rather than blanking the map.

Label rules for both styles:
```
street labels      keep, muted     #5B5C6B light / #AFB0BF dark, reduced opacity
POI / business     remove
transit labels     remove
park / water fill  keep, very low contrast against the page colour
road casing        subtle - roads read as texture, not structure
```

**Static: contextily + Esri World Gray Canvas.** Do not use Mapbox for the
print map.

**Not CARTO.** CARTO now stamps "API KEY REQUIRED" diagonally across its
keyless *raster* tiles, which is what contextily fetches. (The web map is
unaffected: it uses CARTO's *vector* styles, which are still open.) Esri's
World Gray Canvas is keyless, unwatermarked, and already meets the brief:
pale ground, roads as fine line work, no labels at this scale.

One source serves both cards. `--basemap light` uses the tiles as they come;
`--basemap dark` passes them through `recolor_basemap()`, which compresses
luminance `[0.85, 1.0]` onto `[page, road]`. That is deliberately *not* an
inversion: inverting turns the open ground black and the road grid into a
bright web that competes with the route line. Compression keeps roads reading
as texture.

Also available:
- `--basemap none` renders a flat page-colour ground, route and pins only.
- Set `CARTO_API_KEY` to use CARTO instead, matching the web map's cartography.

contextily's built-in attribution draws black-on-white, a bright rectangle on
a dark card. `render.py` suppresses it and sets its own in palette colours;
keep that if you change providers, and keep the attribution.

**Offline check before committing to Mapbox.** Vector tiles require a network
request at load. If the map ever needs to run on a kiosk, in a low-signal
location, or embedded somewhere that blocks external requests, self-hosted
tiles or a raster fallback change this decision. Confirm with BKLVLUP.

### Mapbox setup

```
web/config.js        <- MAPBOX_TOKEN + STYLE_URL_LIGHT/DARK, gitignored
web/config.example.js <- committed, placeholder values
```

Never commit a real token. Use a **URL-restricted public token** (`pk.`),
scoped to the deployment domain plus `localhost` — not the default token.
Client-side exposure is normal for Mapbox and expected; URL restriction is what
makes it safe. Free tier is generous and a community map will not approach it.

### Type

| Role | Print | Web |
|---|---|---|
| Display / titles | Bebas Neue Pro Expanded Bold | Syne ExtraBold |
| Body | Urbanist Regular | Urbanist Regular |
| Handwritten accent | Mansalva | Mansalva |

Bebas Neue Pro is licensed, not a free webfont. Syne, Urbanist and Mansalva
are on Google Fonts.

### Voice

**Go easy on em dashes.** They had taken over the copy; prefer a colon, a
semicolon, a comma, parentheses, or a full stop. Keep one only where it is
doing work no other mark can. Same rule for new stop descriptions and blurbs.

Minimum label size 8pt. On dark, set body text one notch heavier than you
would on light — light-on-dark type optically thins, and Urbanist Regular at
small sizes on `#22232E` starts to break up.

### Print decision — still open

Dark is right for screen. For the printed Green Book it is a real decision,
and the deciding factor is not ink cost. At $400 for 100 booklets this is
digital printing, which prices per impression, so heavy coverage does not cost
more. The actual risks are:

- **Field legibility.** This is a July walking tour. A dark page in direct
  sunlight is harder to read than a light one — glare sits on top of the ink
  instead of being absorbed by the paper.
- **Toner cracking at the fold** on a dark flood, and rub-off on uncoated stock.

If the printed edition goes light, invert to the deck palette and the darkened
data colors (`#6844D3` / `#118026` / `#D51470` on Positron). Test a real proof
outdoors before committing either way.

## Geometry

Center: `40.6478, -73.9219`. Extent 1,449 m E–W x 781 m N–S — **1.86:1 landscape**.

Eleven stops. Three route variants, defined in `metadata.route_variants` and
documented in `ROUTES.md`:

Switcher order is the order of `ROUTES` in `build.py`; the first entry is the
default on load.

| id | Name | Gather | End | Stops | Distance |
|---|---|---|---|---|---|
| `full` | The Full Walk *(default)* | De Event Room | Rugby Library (+ vacant lot) | 11 | 2.35 mi |
| `utica` | Utica Walkshop | Rugby Library | Johnson Energy Clinic | 5 | 0.56 mi |
| `ditmas` | Ditmas Walkshop | De Event Room | Wyckoff House (+ Footprints) | 6 | 1.33 mi |

Stop counts include the optional extension; `walk_miles` covers the main
`order` only, with the spur reported separately as `spur_miles`.

Distances are the routed walking distance (see below), not straight-line.
`ROUTES.md` carries the per-leg breakdown and walk times. Utica and Ditmas are a
matched pair: two shorter walkshops covering the full eleven stops between
them.

Each variant carries a `blurb` (reader-facing, shown in the sidebar) and a
`rationale` (facilitator-facing, ROUTES.md only). **Never put a distance or
stop count in the blurb prose** — those render from the computed values, and
hardcoding them reintroduces drift between the sidebar and ROUTES.md.

### Route geometry — IMPORTANT

`build.py` snaps every route LineString to the OSM pedestrian network via the
public OSRM foot profile, caching the result in `data/route_cache.json` so
rebuilds are deterministic and work offline (delete that file to re-route; set
`TOUR_NO_ROUTING=1` to force the straight-line fallback). Each route feature
carries `properties.routed` — `false` means the build fell back to straight
lines and the geometry still cuts through blocks.

This is machine routing on OSM data, not a verified walk. Before publishing,
check the paths against the ground — OSRM can miss a closed cut-through, a
missing curb ramp, or a safer crossing — by walking them, or refining in
geojson.io / QGIS against OSM sidewalk data. A tour map that routes people
through a building, or across an ungraded rail cut, is worse than no map.

## Static map — 5x7 postcard

Trim 7 x 5 in landscape, 300 dpi (2100 x 1500 px), 0.125 in bleed. Keep pins
and legend text 0.25 in inside the trim; postcard trimming drifts.

The route bbox is 1.86:1 and the card is 1.4:1, so the map cannot fill the
face. The map band is **3.30 in** tall within the trim, leaving **1.70 in** for
the title block and legend strip.

That split is set by the legend, not the map. Eleven entries at the 8pt floor
need four rows of about 0.19 in plus a title block; the band was originally
1.25 in and the rows overlapped. `render.py` warns if row height ever drops
below the 8pt floor again, so raise the band rather than shrinking the type.

**Why labels are impossible here.** At 7 in wide the scale is ~223 m/inch. A
numbered pin needs 12pt (0.167 in) for the numeral to read. Tightest pairs:

| Pair | Ground | On card |
|---|---|---|
| Wyckoff -> Footprints | 59 m | 0.26 in |
| Chef's Choice -> EF Village | 84 m | 0.38 in |
| Library -> vacant lot | 132 m | 0.59 in |
| Railroad Pgd -> Con Ed | 134 m | 0.60 in |

Two 12pt pins need ~0.20 in centre-to-centre before any text. There is no room
for labels at any of these. Hence: **numbered pins only, names in a legend
strip**, keyed by the pin number and using `short`. This makes `short`
load-bearing: it is the only stop text the card carries.

Wyckoff and Footprints at 0.26 in will nearly touch. `render.py` resolves this
with a **relaxation pass**: overlapping pins are pushed apart until each pair
has 0.03 in of clear space, a hairline leader is drawn back to each pin's true
location, and the run prints the ground error per stop. On The Full Walk the
worst is about 44 m. Treat that as a bounded, declared inaccuracy: if a run
ever reports a figure large enough to mislead, tighten the extent or drop a
stop rather than letting the nudge grow.

`short` is sized for this card. Keep it **under ~28 characters** or it will be
ellipsised in the legend grid; the run reports truncation per stop_id. The
legend is 3 columns; short variants centre their rows in the band.

The back of the card is a QR code to the interactive map. Eleven stops x four
content fields cannot fit on a 5x7; the card orients, the web map informs.

## Build

### Web — `web/index.html`

MapLibre GL JS, single file, plus `web/config.js` for the token and style URL
(copy from `web/config.example.js`; `config.js` is gitignored).

Left sidebar (collapsible — "Hide tour stops"):
- Kicker + title + description, all from `metadata` (`edition`, `title`,
  `description`) — never hardcode the copy in the HTML
- Route variant switcher reading `metadata.route_variants` — never a hardcoded list
- "Show walking route" button (route is **hidden by default**) + stop-pins toggle
- Stop list in walking order for the active variant: numbered badge, `name`,
  `short`. Spur stops are tagged "optional"; first/last carry a Start / Finish
  tag. Clicking an item flies to the pin and opens its popup; clicking a pin
  highlights the list row.

**Pin numbers are the position along the active variant's walk (1..N), not
`stop_id`** — see Brand > Numbers. The static card uses the same numbering, so
the two maps always agree. Internally the web code still tracks stops by
`stop_id` (popups, active state, list ↔ pin sync); only the displayed badge is
the walk position.

Start and end of each variant get a flag marker above the pin — green
"⚑ Start" on `order[0]`, pink "⚑ Finish" on the last stop of `order` (the spur
is the optional extension and carries no Finish flag).

Layer structure:
- Route line for the active variant (toggleable, off by default)
- Optional spur, dashed (toggleable; `full` and `ditmas` have one)
- Stop pins (toggleable)

Popups render `name`, `address`, `long` and nothing else. See Hard rule 2.
The stop list carries `name` + `short` only — the facilitator fields stay off
the web map everywhere, list included. The one addition popups may carry is a
**Directions link** to the *next* stop in the walk (Google Maps universal URL,
`travelmode=walking`), because the overview promises turn-by-turn use.

Only one popup is open at a time — opening a stop closes the rest — and opening
one eases the map so the pin sits in the upper part of the viewport, leaving
room for the popup below it.

If a theme's `STYLE_URL_*` fails to load, fall back to that theme's
`FALLBACK_STYLE_*` and log it rather than rendering a blank map.

### Mobile is the baseline, not the fallback

This is a walking-tour map, so **design to a 390px viewport and verify there
before reporting done.** Rules, all enforced in `web/index.html`:

- **Never `100vh`** — mobile browser chrome breaks it. Use `height: 100vh`
  followed by `height: 100dvh` so the fallback loses to the correct value.
- **Body copy ≥16px, line-height 1.5, max-width 65ch.** Under 16px on a form
  control triggers iOS auto-zoom on tap; `#variant-select` especially.
  Small sizes are for labels and kickers only, never running text.
- **Tap targets ≥44×44px** — the select, buttons, checkboxes, the popup close
  button, and pins. Pins keep their scale-encoded *visual* diameter (22–36px)
  inside a fixed 44×44 transparent `.pin` box that is the actual hit area.
- **Body copy never lighter than `--ink-2`** (`#6E6E7A` light / `#C6C7D4` dark).
  `--label` is for labels only; do not set running text in it.
- **The sidebar becomes a bottom sheet under 680px** — 64dvh tall, collapsing
  down to its header bar as a grab handle rather than sliding fully off, so the
  map is never hidden behind a full-width panel.
- The ~270-word overview collapses behind a **"What is this?"** toggle:
  expanded on desktop, collapsed on mobile.

**Never set `position` on `.pin`.** `.pin` and MapLibre's own
`.maplibregl-marker { position: absolute }` have equal specificity, and this
stylesheet loads after MapLibre's — so declaring it wins, detaches markers from
their coordinates, and they drift on zoom. Verify by checking that the pixel
distance between two pins doubles for each zoom level.

Serve with `python -m http.server` and verify in a browser before reporting
done.

### Static — `static/render.py`

GeoPandas + contextily + matplotlib. Takes the variant id as a CLI argument.
Exports SVG first (for Illustrator) and 300dpi PNG second. The script owns
geometry and basemap; final typography is hand-finished, so do not fight
matplotlib's text rendering. Do not use Mapbox here.

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

Content status: all eleven descriptions rewritten (content v4; stop 2 replaced
in v5 — "A Vacant Lot Reimagined"). See
`STOP_DESCRIPTIONS.md` for the readable version and the verification notes.
Do not invent facts. Items flagged "needs local confirmation" there must be
checked before anything goes to print.
