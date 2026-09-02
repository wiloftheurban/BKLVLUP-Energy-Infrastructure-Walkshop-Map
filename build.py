#!/usr/bin/env python3
"""Build tour.geojson, STOP_DESCRIPTIONS.md and ROUTES.md from a single source.

Edit STOPS / ROUTES below, then run:  python3 build.py
"""
import json, math, os, shutil, subprocess, time, urllib.request, urllib.error

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- stops
STOPS = [
dict(id=1, name="Brooklyn Public Library, Rugby Branch", address="1000 Utica Ave, Brooklyn, NY 11203",
     lat=40.648656592711426, lon=-73.93037995465203, scale="NEIGHBORHOOD", access="open",
     short="Library and cooling center",
 long="The Rugby Branch has served East Flatbush since 1946, when it opened as a sub-branch in a rented storefront at 749 Linden Avenue with 7,000 volumes and staff supplemented by volunteers from the East Flatbush Council. It moved to a larger store at 875 Utica in 1951, and on April 1, 1957 opened in its own red brick building here with 25,000 volumes, the second library built under the Beame Plan and the result of more than a decade of organizing by neighborhood residents who wanted a real library. Its 1957 interior was described as the most colorful of any library in the metropolitan area. The branch closed in March 2017 for a renovation first scoped in 2005 at about $1 million, and reopened in July 2021 at a final cost of $10.2 million. That work replaced the HVAC system entirely, added new lighting, improved the facade, and installed an antenna that pushes the branch's wifi out into the surrounding blocks. Today it holds roughly 22,000 items, the Rochelle Tenner Reading Garden, and a mural by Brooklyn artist Hellbent. It sits two blocks from the house where Jackie Robinson lived when he won Rookie of the Year. During heat emergencies the branch operates as a cooling center: free air conditioning, seating, wifi, and charging, open to anyone.",
 energy="That $10.2 million renovation is the clearest example of building retrofit anywhere on this walk: mechanical systems, envelope, and lighting done together, on a building that has to serve the public through summers that keep getting hotter. Look for the rooftop equipment and the newer windows; that's the retrofit you're standing in.",
 talk="A cooling center is a public backstop for a private problem: not every household can afford to run air conditioning, and not every building is wired to support it. What would it take for homes in East Flatbush to stay cool without needing this room? And what else could a building like this do? Solar on the roof, battery storage, a charging station that works when the power doesn't.",
 resource="BPL's catalog and the Center for Brooklyn History hold neighborhood records, photographs, and local history on East Flatbush. Library staff can connect you to city services, and the branch runs free programs year-round. Call 718-566-0053 for current hours and cooling-center status."),

dict(id=2, name="A Vacant Lot Reimagined", address="946 Utica Ave, Brooklyn, NY 11203",
     lat=40.649825350752394, lon=-73.93062729428682, scale="NEIGHBORHOOD", access="sidewalk",
     short="Vacant brownfield lot",
 long="A vacant brownfield lot on Utica Avenue, two minutes from the library and near a proposed IBX station. Lots like this one sit empty across East Flatbush, passed every day and rarely looked at. Through our Reimagine Vacant Lots pop-up events, BKLVLUP invites residents to pause, imagine, and redesign the forgotten spaces around them. Using VR and community knowledge, these events document what kinds of spaces and experiences the neighborhood actually wants. Vacant land is one of the few assets a community can still shape, and what goes on it is a decision worth making together.",
 energy="A brownfield is land whose reuse is complicated by real or suspected contamination, common on commercial corridors that carried a century of fuel, solvents, and auto work. That history shapes what can go here and how much site work comes first, and it is one reason lots like this sit idle while the blocks around them fill in. Look at the frontage, the southern exposure, and how close the site is to the library, the bus route, and the proposed IBX station on Utica.",
 talk="This is the stop where the tour asks for something rather than explains something. What do you want on this lot? Who decides, and who benefits when it finally gets built on? What would you have to see to believe the answer came from this neighborhood rather than from outside it?",
 resource="BKLVLUP runs Reimagine Vacant Lots pop-ups here; see bklvlup.org to take part. NYC's Department of City Planning and the Office of Environmental Remediation publish the zoning and brownfield status of individual lots. The MTA's Interborough Express project page carries the current station planning for Utica Avenue."),

dict(id=3, name="East Flatbush Village", address="1011 Utica Ave, Brooklyn, NY 11203",
     lat=40.648371757639055, lon=-73.92968857701426, scale="NEIGHBORHOOD", access="visitor",
     short="Grassroots youth nonprofit",
 long="East Flatbush Village Inc. is a grassroots Brooklyn nonprofit founded in 2008, working with young people and low-income families through sports, mentorship, and anti-violence programming. It reaches over a thousand families a year, and its programs are free and open. Organizations like this one are among the most durable institutions on a commercial strip. They outlast individual businesses, they hold relationships across generations, and they know who lives where and who needs checking on. That makes them infrastructure in a sense that rarely appears on an infrastructure map: when information needs to move through a neighborhood (a heat advisory, a program deadline, a rebate about to expire, a construction notice), it moves through places like this one far more reliably than through a utility mailer.",
 energy="Energy programs consistently underperform their eligibility: hundreds of thousands of New York households qualify for bill discounts they never enroll in. The gap is almost never awareness of the problem. It's the absence of a trusted person to explain the form.",
 talk="Who tells you about things in this neighborhood? If a free program could cut your energy bill, how would you find out it existed? This is also the stop for talking about the COAD, the coalition of local organizations coordinating on emergency preparedness, and which groups in East Flatbush aren't part of it yet.",
 resource="The Flats Rising COAD (Community Organizations Active in Disaster) coordinates local organizations across Flatbush, East Flatbush, and Flatlands. Organizations not yet involved are a priority; ask a BKLVLUP facilitator how to connect."),

dict(id=4, name="Chef's Choice Brooklyn", address="1039 Utica Ave, Brooklyn, NY 11203",
     lat=40.647622057159175, lon=-73.92975378899715, scale="BLOCK", access="customer",
     short="Caribbean wholesale grocer",
 long="Founded in 1987, Chef's Choice Brooklyn has operated for nearly four decades as a wholesale food and paper distributor serving the Caribbean community. It's open seven days a week and sells groceries, meats, and paper goods in bulk to both households and other businesses. Stores like this are the supply chain behind a cultural enclave. They're the reason ingredients for Caribbean cooking are available at a price a family can carry, and they're the wholesale link that keeps smaller shops and restaurants on this corridor stocked. They are also, in energy terms, among the heaviest continuous electricity users on this stretch of Utica Avenue: commercial refrigeration runs twenty-four hours a day, year-round, and its compressors work hardest in exactly the weather that strains the grid.",
 energy="Businesses like this are billed on a commercial rate that can include a demand charge — a fee based not on total consumption but on the highest single spike in a billing period. Look through the glass and note whether the cases have doors or night curtains: covered cases can cut refrigeration energy substantially, but they cost more to install, which is a real barrier for a small business.",
 talk="Decarbonization conversations usually center on homes. What does it mean for the commercial corridor a neighborhood depends on? Efficiency upgrades here lower operating costs and keep prices down. But who pays for the upgrade, and how does a forty-year-old family business access capital for it?",
 resource="Con Edison and NYSERDA both run no-cost energy assessments and equipment rebates for small businesses; refrigeration and lighting typically have the fastest payback. NYC Accelerator provides free energy advising. Con Edison also accepts food spoilage claims after an outage, from both residential and commercial customers."),

dict(id=5, name="Johnson Energy Clinic and Cooperative (former)", address="436 E 53rd St, Brooklyn, NY 11203",
     lat=40.6490951, lon=-73.9274567, scale="HOUSEHOLD", access="sidewalk",
     short="Early NYC solar home (site)",
 long="This house was the home of the Johnson Energy Clinic and Cooperative, an experimental energy home and one of the earliest solar houses in New York City. Decades before rooftop solar became a commercial industry here, this was an ordinary Flatbush residence retrofitted into a working demonstration of what a house could do with sun, insulation, and careful engineering. The house has since been sold and redeveloped, so what stands here now is not the clinic. Visiting is looking at a site, not a building: the address is public, but this is a private home, so please view it from the sidewalk and do not approach the door or photograph the residents.",
 energy="Everything the rest of this tour discusses in the future tense happened here in the past tense. Solar generation, deep retrofit, energy education, cooperative ownership: this house did all four, with none of the incentives, financing, or installer infrastructure that exist today. The technical lesson is that the building envelope comes first: solar on an uninsulated house is expensive electricity poured into a leaky container, and the early experimental homes understood that before the market did.",
 talk="This is the stop that reframes the whole walk. East Flatbush isn't waiting to be introduced to clean energy. It has been doing this work, and the record is thin because nobody was writing it down. Who else here has done something like this? Whose garage, basement, or roof holds knowledge that never got documented? And what would have let this survive: cooperative ownership, technical support, financing that doesn't put the house at risk? That list is the agenda.",
 resource="This is the strongest oral-history opportunity on the route; longtime residents may remember the clinic directly. Community solar is the present-day version of what a cooperative was reaching for: a shared array, subscribers who get bill credits, no roof and no upfront cost required. Solar One's Here Comes Solar program provides free technical support for NYC residents and building owners.",
 todo="VERIFY: founder's name, the years the clinic operated, and the systems installed. Sources: NYT City Room 2011-08-03 (reporting the owner at risk of losing the house) and the YouTube video, both held by BKLVLUP/GROUND3D. The house was subsequently sold and redeveloped; confirm the date and whether anything of the original retrofit survives. The address is public and the stop is marked, but the site is a private home: keep the view-from-the-sidewalk line in the description."),

dict(id=6, name="De Event Room", address="634 Remsen Ave, Brooklyn, NY 11236",
     lat=40.65137199318552, lon=-73.91869743552688, scale="BLOCK", access="booking",
     short="Private event space",
 long="De Event Room is a private event space on Remsen Avenue, on a block where residential buildings and small businesses sit side by side. The indoor space runs over 1,100 square feet across two rooms, with a backyard patio and pool area outside, multiple restrooms, two bar areas, and a buffet-style warming station. It accommodates roughly a hundred people and hosts bridal showers, birthdays, corporate events, pop-ups, workshops, and product launches. Read that amenity list the way an emergency planner would: capacity for a hundred, working restrooms, food service, climate control, outdoor space, and an operator on site who knows the building. That is most of what a neighborhood needs from a refuge.",
 energy="The gap between an event space and a refuge is a backup power source, a cooling strategy, and an agreement reached before an emergency rather than during one. Across the country, the buildings that end up sheltering people are rarely the ones on the official list. They're the halls, basements, and storefronts people already know how to walk into.",
 talk="Does East Flatbush need a new building, or upgrades to the ones it already has? What would it take to make five existing rooms in this neighborhood outage-ready instead of one new one? Who would maintain them?",
 resource="Solar-plus-storage for a building this size is eligible for federal tax credits, NYSERDA incentives, and NYC property tax abatements for solar, which can be stacked. Building owners can get free advising through NYC Accelerator."),

dict(id=7, name="Railroad Playground", address="Ditmas Ave between E 91st and E 92nd St, Brooklyn, NY 11236",
     lat=40.649393652888115, lon=-73.91422443933631, scale="NEIGHBORHOOD", access="open",
     short="1957 park on the rail corridor",
 long="Originally called Ditmas Playground, this park takes its earlier name from the street to the southeast, itself named for the Van Ditmarsen family who settled in the village of Flatbush in the late 17th century. The Canarsie and Rockaway Beach Railroad, a Long Island Rail Road subsidiary whose branch opened in 1865, runs just south of the park, and in the early 20th century it was the most popular route for New Yorkers heading to the amusement park at Canarsie Beach. The same corridor serves the Brooklyn Terminal Market down the block, which historically supplied fresh produce and lodging for upstate and Long Island farmers who couldn't make the return trip in a day. The Parks Department acquired this site in 1954 and opened the park in 1957 with handball and basketball courts, a softball field, a public restroom, a wading pool, a children's play area, and shade trees planted around the entire perimeter. A 1997 renovation costing $735,000 gave the park its train-and-market theme: locomotive-shaped play units, railroad pavement of stone and steel track, and steel panels depicting flowers, watermelon, tomatoes, onions, and grapes. It's open daily, 6am to 9pm, with a wheelchair-accessible restroom and water play features.",
 energy="A park is environmental infrastructure that runs on nothing. Tree canopy and vegetated ground can hold a park meaningfully cooler than the paved blocks around it. Shade blocks solar radiation before it reaches a surface, and plants cool the air directly as they release water. That's passive cooling: no compressor, no meter, no failure mode during an outage. Soil and planting also absorb stormwater that would otherwise run into the sewer. The water play features do the same job a cooling center does, outdoors and for free. The shade trees planted around this perimeter in 1957 are doing work today that no one billed for.",
 talk="Parks are usually filed under recreation. What changes if they're budgeted as cooling infrastructure? East Flatbush and Canarsie have less tree canopy than the city average, and canopy tracks closely with heat vulnerability across New York. Who decides where trees get planted, and how long does it take a new one to do the work an old one already does?",
 resource="NYC Parks takes tree service and new tree requests through 311 and the Forestry Division. Street tree planting is free to residents and property owners. The Parks tree map shows every street tree in the city, including the stormwater and cooling benefit each provides annually."),

dict(id=8, name="Con Edison Gateway Park Substation", address="789 E 91st St, Brooklyn, NY 11236",
     lat=40.648339092431364, lon=-73.91345543431983, scale="REGIONAL", access="sidewalk",
     short="$1.3B Con Edison substation",
 long="Con Edison is building the Gateway Park Substation here at a cost of $1.3 billion. It's an indoor high-voltage transmission substation: a building rather than an open yard of exposed equipment, a more expensive choice made for a dense residential setting. When complete it will serve roughly 52,000 customers across Central and East Brooklyn, primarily Canarsie and Remsen Village. The project includes about 7.5 miles of new underground feeder cable connecting it into the network, part of a larger cable program reported at around 28 miles. Con Edison's stated reasons for building it are capacity, overload prevention, and network resiliency: the company projects Brooklyn's electricity demand will rise roughly 16 percent over the next decade, driven by population growth, new development, and the shift from gas to electric heating, cooking, and vehicles. Power will reach this station through underground transmission from the Brooklyn Clean Energy Hub in Vinegar Hill, an $810 million transmission substation built to accept up to 1,500 megawatts and designed as an interconnection point for offshore wind generated in the New York Bight, roughly 150 miles off the coast of Long Island and New Jersey.",
 energy="A substation is where transmission becomes distribution. Electricity travels long distances at very high voltage because that's efficient, then has to be stepped down to a level that can safely enter streets and buildings. That conversion needs land, access, and physical protection, which is why substations end up beside rail corridors and industrial edges. This one is also a decarbonization asset: the shift away from gas only works if the electric system can carry the load gas used to. Con Edison's public FAQ for the project specifically addresses Railroad Playground across the street, stating the company doesn't anticipate changes to the playground's size.",
 talk="Electrification is the core decarbonization strategy for New York, and it depends on infrastructure like this. So what does the neighborhood hosting it get? Jobs during construction and after? Priority for grid reliability? Community solar or storage connected to it? East Flatbush and Canarsie have experienced outages during past heat waves, including a deliberate shutoff in July 2019 that affected tens of thousands of southeast Brooklyn customers — this station is part of Con Edison's answer to that history. Is it enough, and who decides?",
 resource="Con Edison maintains a public project page for the Gateway Park Substation with a community contact. Major infrastructure projects and rate changes are decided by the New York Public Service Commission, where written public comment becomes part of the official record. Rate cases are when comments carry the most weight."),

dict(id=9, name="National Grid — Canarsie Service Center", address="8424 Ditmas Ave, Brooklyn, NY 11236",
     lat=40.64576668511091, lon=-73.91784006730398, scale="REGIONAL", access="sidewalk",
     short="National Grid gas campus",
 long="This is National Grid's Canarsie Service Center, a working operations campus spanning an address range along Ditmas Avenue with multiple numbered buildings. It's an operational base rather than a customer office, housing crews, equipment, and administration for the gas distribution network across Brooklyn and Queens. New gas service applications for both boroughs are processed through this address. The site also includes a public compressed natural gas fueling station, operated by Clean Energy and open 24 hours at 3,000 and 3,600 PSI, used by CNG fleet vehicles. National Grid's downstate business is the former Brooklyn Union Gas Company, and the utility delivers gas to roughly 1.8 million customers across New York City and Long Island.",
 energy="In New York City the utility split is fixed and worth memorizing: Con Edison delivers electricity to all five boroughs, while National Grid delivers natural gas — and only gas — to Brooklyn, Queens, and Staten Island. Two companies, two bills, two separate emergency numbers, two separate regulatory proceedings. Most households pay both and can't say which does what. That matters practically, because if you smell gas and call the wrong company you lose time you don't have. It also matters structurally: the decarbonization debate is fundamentally about which of these two connections into your home grows and which shrinks.",
 talk="Gas heats and cooks in most of East Flatbush's housing stock. Electrification would change that, swapping heat pumps for boilers and induction for burners, with implications for indoor air quality and childhood asthma, and with real costs and real disruption. What does a fair transition look like for homeowners here, many of them older, many in buildings that need envelope work before any equipment swap makes sense? And what happens to the workers and the network at a site like this one?",
 resource="Gas emergency, 24 hours: 1-800-892-2345. Leave the building first, then call. The Energy Affordability Program discounts bills for income-eligible households at both National Grid and Con Edison, targeting energy costs at or below 6 percent of household income; receiving HEAP generally enrolls you automatically. Under New York's HEFPA law, households including someone 62 or older, blind, or disabled, or with a certified medical condition have shutoff protections that many eligible people never claim. See nyeeap.com."),

dict(id=10, name="Wyckoff House Museum", address="5816 Clarendon Rd, Brooklyn, NY 11203",
     lat=40.64435222474173, lon=-73.92082873529188, scale="HOUSEHOLD", access="appointment",
     short="NY's oldest building, 1652",
 long="The Wyckoff House is the oldest surviving building in New York State and was New York City's first officially designated landmark. Built around 1652 on land taken from the Lenape in the 1630s, it sits on about an acre and a half within Milton Fidler Park. Pieter Claesen Wyckoff arrived in New Netherland in 1637 as an indentured laborer; after completing his indenture he and Grietje van Nes settled in the village of Nieuw Amersfoort, in what is now East Flatbush and Flatlands. The Historic House Trust's account of the site is direct about who worked this land: Dutch-American landowners, enslaved and freed Africans, and later European immigrants farmed some of the most fertile ground in the country here. The property remained a working farm until 1901. Today it's owned by NYC Parks, operated by the Wyckoff House & Association, and runs farm-based and school programs, a working garden, and seasonal markets.",
 energy="This building ran for roughly 249 years with no electric grid, no gas main, and no meter. Everything it did to stay habitable was structural: window placement for cross-ventilation, deep eaves for shade, thick walls that slow heat transfer, a cellar for cold storage, and trees left standing where they'd do the most good. That's passive design, and its defining property is that it doesn't fail during an outage because it never depended on power. Modern high-performance building — Passive House, deep energy retrofits — is largely a rediscovery of these principles with better materials and measurement.",
 talk="This is the stop for elders. Before central air, what did your household actually do in a heat wave? Which room did you sleep in, what did you do with the windows, where did people go during the day? Those answers are passive cooling strategy, held as memory rather than as building code, and no technical report contains them.",
 resource="The museum is open on a limited schedule and some access is by appointment. Call (718) 629-5400 or email info@wyckoffmuseum.org, especially for a group visit. School and farm programs run year-round."),

dict(id=11, name="Footprints Cafe", address="5814 Clarendon Rd, Brooklyn, NY 11203",
     lat=40.64473940909019, lon=-73.9213153001351, scale="BLOCK", access="customer",
     short="Caribbean restaurant",
 long="Footprints is a Caribbean restaurant known for a large menu and a lively room, and it has grown into a small chain with several Brooklyn locations. If the one on your route differs from what's described here, that's expected; this is a general profile rather than a single address. It sits directly beside the Wyckoff House Museum, which makes for an unusual adjacency: a 17th-century farm and a Caribbean kitchen on the same block, three hundred and seventy years apart, both organized around food grown somewhere and cooked here. Restaurants are also among the most energy-intense small businesses per square foot anywhere on a commercial strip.",
 energy="A commercial kitchen runs gas ranges, an exhaust hood pulling conditioned air out of the building during every open hour, walk-in refrigeration, and a dining room that has to stay comfortable while the kitchen behind it runs hot. Kitchen ventilation alone is often the largest single load, because every cubic foot of air the hood removes has to be replaced and re-conditioned. It's also the least visible: you can see a solar panel, but you can't see a hood running at full speed all day.",
 talk="Of everything you saw today, what did you not know this morning? What's on your own block that you'll look at differently? And what should the Green Book include so that someone who never takes this tour still gets the benefit of it?",
 resource="Con Edison and NYSERDA small-business programs cover energy assessments and equipment rebates; for restaurants, refrigeration and kitchen ventilation typically offer the highest return. Con Edison food spoilage claims apply to restaurants after an outage."),
]

# ---------------------------------------------------------------- routes
ROUTES = [
# List order is switcher order; the first entry is the default on load.
 dict(id="full", name="The Full Walk", order=[6,7,8,9,10,11,5,4,3,1], spur=[1,2],
      gather="De Event Room", end="Brooklyn Public Library, Rugby Branch",
      blurb="This route is the longest and most comprehensive, featuring all 11 stops. Gather "
            "at De Event Room, head east through the playground, the substation, and the gas "
            "campus, then come back along Clarendon and up Utica. It ends at the Brooklyn "
            "Public Library, Rugby Branch, with an optional extension to a local vacant lot.",
      rationale="Private business hosts the reception, supporting a local operator. Opens on infrastructure while energy is high, closes on the Utica community cluster, and lands at the library where there is room to sit and debrief. The vacant lot is the optional last word."),
 dict(id="utica", name="Utica Walkshop", order=[1,2,3,4,5], spur=[],
      gather="Rugby Library", end="Johnson Energy Clinic",
      blurb="The social infrastructure half. This route covers a few sites of social "
            "infrastructure along Utica Avenue: the library, a vacant lot, East Flatbush "
            "Village, Chef's Choice, and one of New York City's earliest solar homes. Short "
            "enough for a lunch hour, a school group, or a walk with elders.",
      rationale="Short community-scale tour. Accessible length; can run in a lunch hour."),
 dict(id="ditmas", name="Ditmas Walkshop", order=[6,7,8,9,10], spur=[10,11],
      gather="De Event Room", end="Wyckoff House Museum",
      blurb="The built infrastructure half. It begins at De Event Room as a gathering space, "
            "and continues on to Railroad Playground, the Con Edison substation, and National "
            "Grid, ending at the Wyckoff House Museum, with an optional extension to grab a "
            "meal at Footprints. Pairs with the Utica Walkshop to cover all eleven stops "
            "across two sessions.",
      rationale="Infrastructure and utilities tour. Pairs with the Utica Walkshop as a two-session series."),
]

# Four scale groups, four distinct hues — no two groups share a swatch.
# Each carries a dark-ground and a light-ground value; no single hex clears
# 4.5:1 against both #22232E and a near-white basemap. See CLAUDE.md > Brand.
SCALE_COLOR       = {"HOUSEHOLD": "#4FD8E8", "BLOCK": "#D85390",
                     "NEIGHBORHOOD": "#6CDF67", "REGIONAL": "#9076F7"}
SCALE_COLOR_LIGHT = {"HOUSEHOLD": "#0E7C8C", "BLOCK": "#D51470",
                     "NEIGHBORHOOD": "#118026", "REGIONAL": "#6844D3"}

SCALE_LABEL = {"HOUSEHOLD": "Household", "BLOCK": "Block + small business",
               "NEIGHBORHOOD": "Neighborhood", "REGIONAL": "Regional"}

SCALE_DESC = {
  "HOUSEHOLD": "A single home. The Johnson Energy Clinic and the Wyckoff House.",
  "BLOCK": "Where energy shows up as a bill. The wholesale grocer, the event space, the restaurant kitchen.",
  "NEIGHBORHOOD": "What we hold in common. The library, the playground, the nonprofit, and a vacant lot on Utica.",
  "REGIONAL": "Systems built at a scale no single block decides. Con Edison's electricity, National Grid's gas.",
}

SCALE_NOTE = ("Every stop is colored by where it sits in the energy system, and sized to "
              "match: smallest for a single home, largest for the utilities.")

# ---------------------------------------------------------------- helpers
def haversine(a, b):
    R = 6371000
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp = p2 - p1
    dl = math.radians(b["lon"] - a["lon"])
    x = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(x))

BY_ID = {s["id"]: s for s in STOPS}

# ---------------------------------------------------------------- walk routing
# CLAUDE.md > "Route geometry": the LineStrings must follow the real pedestrian
# network, not cut through blocks. Each variant's stop sequence is snapped to
# OSM sidewalk/footway data via the public OSRM foot profile. Responses are
# cached to data/route_cache.json so rebuilds are deterministic and work
# offline; delete that file to re-route. Set TOUR_NO_ROUTING=1 to force the
# straight-line fallback (flagged routed=False in the output).
OSRM_URL = "https://routing.openstreetmap.de/routed-foot/route/v1/foot/"
CACHE_PATH = os.path.join(OUT, "data", "route_cache.json")
WALK_SPEED_MS = 1.35  # m/s (~3.0 mph) — used only for the straight-line fallback
ROUTING = os.environ.get("TOUR_NO_ROUTING") != "1"

try:
    with open(CACHE_PATH) as _f:
        _CACHE = json.load(_f)
except (OSError, ValueError):
    _CACHE = {}
_CACHE_DIRTY = False


def _cache_key(ids):
    return ">".join(str(i) for i in ids)


def _http_get(url):
    """GET a URL, returning parsed JSON. Tries urllib, then falls back to the
    curl binary — the stock macOS python links an old LibreSSL that fails the
    TLS handshake with some hosts, but the system curl does not."""
    ua = "BKLVLUP-ecopower-walk/1.0 (map build script)"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua})
        with urllib.request.urlopen(req, timeout=25) as resp:
            return json.load(resp)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        if not shutil.which("curl"):
            raise
        print(f"    (urllib failed: {exc}; retrying with curl)")
        out = subprocess.run(
            ["curl", "-sS", "--max-time", "25", "-A", ua, url],
            capture_output=True, text=True, timeout=30)
        if out.returncode != 0:
            raise RuntimeError(out.stderr.strip() or f"curl exit {out.returncode}")
        return json.loads(out.stdout)


def _osrm_foot(ids):
    """Walking path through the given stop ids on the OSM pedestrian network.
    Returns dict(routed, coords, legs_m, total_m, duration_s) or None on failure."""
    pts = ";".join(f"{BY_ID[i]['lon']:.6f},{BY_ID[i]['lat']:.6f}" for i in ids)
    url = OSRM_URL + pts + "?overview=full&geometries=geojson&steps=false&annotations=false"
    try:
        doc = _http_get(url)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"  routing {_cache_key(ids)}: request failed ({exc})")
        return None
    if doc.get("code") != "Ok" or not doc.get("routes"):
        print(f"  routing {_cache_key(ids)}: no route (code {doc.get('code')})")
        return None
    rt = doc["routes"][0]
    coords = [[x, y] for x, y in rt["geometry"]["coordinates"]]
    # OSRM snaps each waypoint to the nearest footway; stitch the exact stop
    # coordinate onto the ends so the drawn line meets the start/end pins.
    ends = ((ids[0], 0), (ids[-1], -1))
    for sid, idx in ends:
        snap = {"lon": coords[idx][0], "lat": coords[idx][1]}
        if haversine(snap, BY_ID[sid]) > 3:
            pt = [BY_ID[sid]["lon"], BY_ID[sid]["lat"]]
            coords.insert(0, pt) if idx == 0 else coords.append(pt)
    coords = [[round(x, 6), round(y, 6)] for x, y in coords]
    return {"routed": True, "coords": coords,
            "legs_m": [round(l["distance"], 1) for l in rt["legs"]],
            "total_m": round(rt["distance"], 1),
            "duration_s": round(rt["duration"], 1)}


def walk_path(ids):
    """Routed pedestrian geometry + stats for a stop sequence, with a
    straight-line fallback (routed=False) when OSRM is unavailable."""
    global _CACHE_DIRTY
    key = _cache_key(ids)
    hit = _CACHE.get(key) if ROUTING else None
    if hit is None and ROUTING:
        hit = _osrm_foot(ids)
        if hit:
            _CACHE[key] = hit
            _CACHE_DIRTY = True
            time.sleep(1.0)  # be polite to the shared OSRM instance
    if hit is None:
        legs_m = [round(haversine(BY_ID[ids[i]], BY_ID[ids[i + 1]]), 1)
                  for i in range(len(ids) - 1)]
        total_m = round(sum(legs_m), 1)
        hit = {"routed": False,
               "coords": [[BY_ID[i]["lon"], BY_ID[i]["lat"]] for i in ids],
               "legs_m": legs_m, "total_m": total_m,
               "duration_s": round(total_m / WALK_SPEED_MS, 1)}
    return hit


# Resolve every variant's geometry once, up front.
PATHS = {}
for r in ROUTES:
    print(f"routing {r['id']} …")
    PATHS[r["id"]] = {"main": walk_path(r["order"]),
                      "spur": walk_path(r["spur"]) if r["spur"] else None}
if _CACHE_DIRTY:
    with open(CACHE_PATH, "w") as _f:
        json.dump(_CACHE, _f, indent=2)

ANY_FALLBACK = any(
    not p["main"]["routed"] or (p["spur"] and not p["spur"]["routed"])
    for p in PATHS.values())


def miles(m):
    return round(m / 1609.34, 2)


def minutes(path):
    return round(path["duration_s"] / 60)


ROUTED_NOTE = "Geometry follows the OSM pedestrian network (OSRM foot profile)."
FALLBACK_NOTE = ("PLACEHOLDER straight-line geometry — routing was unavailable "
                 "at build time. Re-run build.py with network access before publishing.")

# ---------------------------------------------------------------- geojson
features = []
for r in ROUTES:
    mp = PATHS[r["id"]]["main"]
    features.append({
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": mp["coords"]},
        "properties": {"kind": "route", "variant": r["id"], "segment": "main",
                       "label": r["name"], "optional": False,
                       "stop_order": r["order"], "routed": mp["routed"],
                       "walk_miles": miles(mp["total_m"]), "walk_minutes": minutes(mp),
                       "note": ROUTED_NOTE if mp["routed"] else FALLBACK_NOTE}})
    sp = PATHS[r["id"]]["spur"]
    if sp:
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString", "coordinates": sp["coords"]},
            "properties": {"kind": "route", "variant": r["id"], "segment": "spur",
                           "label": r["name"] + " (optional extension)", "optional": True,
                           "stop_order": r["spur"], "routed": sp["routed"],
                           "walk_miles": miles(sp["total_m"]),
                           "note": ("Render dashed. " +
                                    (ROUTED_NOTE if sp["routed"] else FALLBACK_NOTE))}})

for s in STOPS:
    p = {"kind": "stop", "stop_id": s["id"], "name": s["name"], "address": s["address"],
         "short": s["short"], "long": s["long"],
         "scale": s["scale"], "access": s["access"],
         "color": SCALE_COLOR[s["scale"]], "color_light": SCALE_COLOR_LIGHT[s["scale"]],
         "energy_connection": s["energy"], "conversation": s["talk"], "resource": s["resource"]}
    if s.get("todo"):
        p["todo"] = s["todo"]
    features.append({"type": "Feature",
                     "geometry": {"type": "Point", "coordinates": [s["lon"], s["lat"]]},
                     "properties": p})

geo = {
 "type": "FeatureCollection",
 "name": "BKLVLUP Ecopower Infrastructure Walk",
 "metadata": {
   "version": "v4",
   "title": "Ecopower Infrastructure Walk",
   "edition": "The Green Book — Energy Resilience Edition",
   "partners": "BKLVLUP × GROUND3D",
   "neighborhood": "East Flatbush / Remsen Village / Canarsie, Brooklyn",
   "description": [
     "BKLVLUP is a community development + social impact lab nonprofit that uses art and "
     "technology to build lasting community wealth in East Flatbush, Flatbush, and "
     "Flatlands, Brooklyn.",

     "This map supports our Energy Infrastructure Walking Tour: eleven stops across East "
     "Flatbush, Remsen Village, and Canarsie. It's built for self-guided walking, with "
     "turn-by-turn directions along the route, so you can take it at your own pace, alone "
     "or with your block.",

     "Energy infrastructure runs all throughout this neighborhood, mostly out of sight. This "
     "tour makes it visible: the $1.3 billion substation going up on the Canarsie rail line, "
     "the gas campus on Ditmas, the library that operates as a cooling center during heat "
     "emergencies, the grocer's coolers that never shut off, and a house on East 53rd that "
     "ran on solar before anyone called it clean energy. Along the way we connect residents' "
     "daily experiences with energy, from utility bills to power outages to the summers that "
     "keep getting hotter, back to the systems behind them.",

     "New York State is planning the Interborough Express, a light rail along an existing "
     "freight line connecting Brooklyn to Queens, with three stations planned in our area "
     "including one on Utica Avenue. Transit like that brings investment and pressure at the "
     "same time. We're preparing to meet it on purpose by using transit-oriented development "
     "to build community-owned energy resilient infrastructure, while the community is still "
     "ours to shape.",
   ],
   "credits": ("Produced by GROUND3D in collaboration with the BKLVLUP EcoPower '26 Summer "
               "Fellows. Map authored by GROUND3D. Route drawn on the OpenStreetMap sidewalk "
               "network."),
   "center": [-73.9219, 40.6478],
   "popup_fields": ["name", "address", "long"],
   "popup_note": "INTERACTIVE MAP POPUPS RENDER ONLY name, address AND long. The energy_connection, conversation and resource fields are facilitator material for the printed Green Book and the walkshop script — do NOT render them in map popups.",
   "static_map_note": "Static map shows NUMBERED PINS ONLY. No inline labels. Names go in a legend strip keyed to stop_id, using the short field.",
   "color_note": "Pin fill from properties.color on a dark basemap, properties.color_light on a light one. Pin outline encodes access. See CLAUDE.md > Brand.",
   "scale_note": SCALE_NOTE,
   "scale_groups": {k: {"label": SCALE_LABEL[k], "description": SCALE_DESC[k],
                        "color": SCALE_COLOR[k], "color_light": SCALE_COLOR_LIGHT[k]}
                    for k in ("HOUSEHOLD", "BLOCK", "NEIGHBORHOOD", "REGIONAL")},
   "access_values": {"open": "open to anyone", "visitor": "open as a visitor",
                     "customer": "open as a customer", "booking": "open by booking",
                     "appointment": "open by appointment", "sidewalk": "view from the sidewalk only"},
   "route_variants": [{"id": r["id"], "name": r["name"], "gather": r["gather"], "end": r["end"],
                       "order": r["order"], "spur": r["spur"],
                       "routed": PATHS[r["id"]]["main"]["routed"],
                       "walk_miles": miles(PATHS[r["id"]]["main"]["total_m"]),
                       "walk_minutes": minutes(PATHS[r["id"]]["main"]),
                       "spur_miles": (miles(PATHS[r["id"]]["spur"]["total_m"])
                                      if PATHS[r["id"]]["spur"] else None),
                       "stop_count": len(set(r["order"]) | set(r["spur"])),
                       "blurb": r["blurb"],
                       "rationale": r["rationale"]} for r in ROUTES],
   "note": ("Route LineStrings follow the OSM pedestrian network (OSRM foot profile); "
            "walk_miles and walk_minutes are the routed distance and time. "
            "Verify against a site walk before publishing."
            if not ANY_FALLBACK else
            "WARNING: one or more route LineStrings are PLACEHOLDER straight lines — "
            "routing was unavailable at build time. Re-run build.py with network access "
            "before publishing.")
 },
 "features": features}

with open(os.path.join(OUT, "data", "tour.geojson"), "w") as f:
    json.dump(geo, f, indent=2, ensure_ascii=False)

# ---------------------------------------------------------------- descriptions md
L = ["# Ecopower Infrastructure Walk — Stop Descriptions (v4)", "",
     "**The Green Book — Energy Resilience Edition** · BKLVLUP × GROUND3D", "",
     "Eleven stops in East Flatbush, Remsen Village and Canarsie.", "",
     "**Description** is the only field that appears in interactive map popups. **Energy connection**, "
     "**Conversation** and **Resource** are facilitator material for the printed Green Book and the "
     "walkshop script — they are stored in the data but not rendered on the map.", "", "---", ""]
for s in STOPS:
    L += [f"## {s['id']}. {s['name']}",
          f"*{s['address']}* · scale: **{s['scale'].title()}** · access: {s['access']} · map label: **{s['short']}**",
          "", "**Description** *(shown in map popups)*", "", s["long"], "",
          "**Energy connection**", "", s["energy"], "",
          "**Conversation**", "", s["talk"], "",
          "**Resource**", "", s["resource"], ""]
    if s.get("todo"):
        L += [f"> **{s['todo']}**", ""]
    L += ["---", ""]
with open(os.path.join(OUT, "STOP_DESCRIPTIONS.md"), "w") as f:
    f.write("\n".join(L))

# ---------------------------------------------------------------- routes md
R = ["# Route variants", "",
     "Distances and times are routed on the OSM pedestrian network (OSRM foot profile) — "
     "the LineStrings in `data/tour.geojson` follow the same paths.",
     "Add roughly 5 minutes per stop for narration and discussion.", ""]
if ANY_FALLBACK:
    R += ["> **Some variants below fell back to straight-line geometry (routing "
          "unavailable at build time). Re-run `build.py` with network access before publishing.**", ""]
R += ["---", ""]
for r in ROUTES:
    mp = PATHS[r["id"]]["main"]
    order, legs = r["order"], mp["legs_m"]
    worst = max(range(len(legs)), key=lambda k: legs[k]) if legs else None
    est = "" if mp["routed"] else "  _(straight-line estimate — routing unavailable)_"
    total_stops = len(set(order) | set(r["spur"]))
    R += [f"## {r['name']}", "",
          f"`{r['id']}` · **Gather:** {r['gather']} · **End:** {r['end']}",
          f"**{total_stops} stops · {miles(mp['total_m'])} mi · ~{minutes(mp)} min walking**{est}", "",
          r["blurb"], "",
          f"*Facilitator note:* {r['rationale']}", "", "| # | Stop | Leg |", "|---|---|---|"]
    for n, sid in enumerate(order, 1):
        leg = "" if n == 1 else f"{legs[n-2]:.0f} m"
        R += [f"| {n} | {BY_ID[sid]['name']} | {leg} |"]
    sp = PATHS[r["id"]]["spur"]
    if sp:
        R += ["", f"*Optional extension (+{miles(sp['total_m'])} mi):* " +
              " → ".join(BY_ID[i]["name"] for i in r["spur"][1:])]
    if worst is not None:
        a, b = order[worst], order[worst + 1]
        R += ["", f"Longest leg: **{legs[worst]:.0f} m** ({BY_ID[a]['name']} → {BY_ID[b]['name']})"]
    R += ["", "---", ""]
with open(os.path.join(OUT, "ROUTES.md"), "w") as f:
    f.write("\n".join(R))

print(f"built: {len(STOPS)} stops, {len(ROUTES)} route variants, {len(features)} features")
for r in ROUTES:
    mp = PATHS[r["id"]]["main"]
    tag = "routed" if mp["routed"] else "STRAIGHT-LINE FALLBACK"
    n = len(set(r["order"]) | set(r["spur"]))
    print(f"  {r['id']:8s} {n:2d} stops  {miles(mp['total_m']):4.2f} mi  "
          f"{minutes(mp):3.0f} min  [{tag}]")
