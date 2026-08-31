#!/usr/bin/env python3
"""Build tour.geojson, STOP_DESCRIPTIONS.md and ROUTES.md from a single source.

Edit STOPS / ROUTES below, then run:  python3 build.py
"""
import json, math, os

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- stops
STOPS = [
dict(id=1, name="Brooklyn Public Library, Rugby Branch", address="1000 Utica Ave, Brooklyn, NY 11203",
     lat=40.648656592711426, lon=-73.93037995465203, scale="NEIGHBORHOOD", access="open",
     short="Neighborhood library, cooling center, and climate resource",
 long="The Rugby Branch has served East Flatbush since 1946, when it opened as a sub-branch in a rented storefront at 749 Linden Avenue with 7,000 volumes and staff supplemented by volunteers from the East Flatbush Council. It moved to a larger store at 875 Utica in 1951, and on April 1, 1957 opened in its own red brick building here with 25,000 volumes — the second library built under the Beame Plan, and the result of more than a decade of organizing by neighborhood residents who wanted a real library. Its 1957 interior was described as the most colorful of any library in the metropolitan area. The branch closed in March 2017 for a renovation first scoped in 2005 at about $1 million, and reopened in July 2021 at a final cost of $10.2 million — work that replaced the HVAC system entirely, added new lighting, improved the facade, and installed an antenna that pushes the branch's wifi out into the surrounding blocks. Today it holds roughly 22,000 items, the Rochelle Tenner Reading Garden, and a mural by Brooklyn artist Hellbent. It sits two blocks from the house where Jackie Robinson lived when he won Rookie of the Year. During heat emergencies the branch operates as a cooling center: free air conditioning, seating, wifi, and charging, open to anyone.",
 energy="That $10.2 million renovation is the clearest example of building retrofit anywhere on this walk — mechanical systems, envelope, and lighting done together, on a building that has to serve the public through summers that keep getting hotter. Look for the rooftop equipment and the newer windows; that's the retrofit you're standing in.",
 talk="A cooling center is a public backstop for a private problem: not every household can afford to run air conditioning, and not every building is wired to support it. What would it take for homes in East Flatbush to stay cool without needing this room? And what else could a building like this do — solar on the roof, battery storage, a charging station that works when the power doesn't?",
 resource="BPL's catalog and the Center for Brooklyn History hold neighborhood records, photographs, and local history on East Flatbush. Library staff can connect you to city services, and the branch runs free programs year-round. Call 718-566-0053 for current hours and cooling-center status."),

dict(id=2, name="East Flatbush Resilience Hub (proposed site)", address="946 Utica Ave, Brooklyn, NY 11203",
     lat=40.649825350752394, lon=-73.93062729428682, scale="NEIGHBORHOOD", access="sidewalk",
     short="A vacant lot BKLVLUP is scoping for a resilience hub",
 long="Right now this is a vacant lot on Utica Avenue, two minutes' walk from the library. BKLVLUP is scoping it as a potential site for the East Flatbush Resilience Hub. A resilience hub is a community-run building that operates normally most of the time — programming, services, a place to gather — and switches roles during an emergency, becoming a place where people can cool down or warm up, charge medical equipment and phones, get clean water and food, and find reliable information. The distinguishing feature is that it stays operational when the wider grid does not, usually through on-site solar paired with battery storage. The model matters because in an emergency people go where they already trust, not where a plan tells them to go. Hubs in other cities are most often churches, libraries, community centers, and neighborhood organizations — buildings with existing relationships, upgraded to keep working under stress.",
 energy="An empty lot is an unusual opportunity. Most resilience hubs are retrofits, which means working around an existing roof, panel, and floor plan. Building from the ground up means solar orientation, battery siting, envelope performance, and backup circuits can be designed in from the start. Look at the roof area a new building could offer, the southern exposure, and how close the site is to the library and the bus route.",
 talk="This is the stop where the tour asks for something rather than explains something. What should this building do on an ordinary Tuesday, not just during an emergency? Who runs it, and how does it stay funded between crises? What would make you actually come here — and who in your life would need someone to come get them?",
 resource="BKLVLUP is gathering community input on this site now. NYSERDA and city emergency management programs fund community resilience hubs, typically covering solar plus storage. Community solar lets renters and homeowners without suitable roofs subscribe to a shared array and receive credits on their Con Edison bill — no installation, no upfront cost."),

dict(id=3, name="East Flatbush Village", address="1011 Utica Ave, Brooklyn, NY 11203",
     lat=40.648371757639055, lon=-73.92968857701426, scale="NEIGHBORHOOD", access="visitor",
     short="Grassroots nonprofit serving youth and families since 2008",
 long="East Flatbush Village Inc. is a grassroots Brooklyn nonprofit founded in 2008, working with young people and low-income families through sports, mentorship, and anti-violence programming. It reaches over a thousand families a year, and its programs are free and open. Organizations like this one are among the most durable institutions on a commercial strip — they outlast individual businesses, they hold relationships across generations, and they know who lives where and who needs checking on. That makes them infrastructure in a sense that rarely appears on an infrastructure map: when information needs to move through a neighborhood — a heat advisory, a program deadline, a rebate about to expire, a construction notice — it moves through places like this one far more reliably than through a utility mailer.",
 energy="Energy programs consistently underperform their eligibility: hundreds of thousands of New York households qualify for bill discounts they never enroll in. The gap is almost never awareness of the problem. It's the absence of a trusted person to explain the form.",
 talk="Who tells you about things in this neighborhood? If a free program could cut your energy bill, how would you find out it existed? This is also the stop for talking about the COAD — the coalition of local organizations coordinating on emergency preparedness — and which groups in East Flatbush aren't part of it yet.",
 resource="The Flats Rising COAD (Community Organizations Active in Disaster) coordinates local organizations across Flatbush, East Flatbush, and Flatlands. Organizations not yet involved are a priority — ask a BKLVLUP facilitator how to connect."),

dict(id=4, name="Chef's Choice Brooklyn", address="1039 Utica Ave, Brooklyn, NY 11203",
     lat=40.647622057159175, lon=-73.92975378899715, scale="BLOCK", access="customer",
     short="Caribbean wholesale grocer, open since 1987",
 long="Founded in 1987, Chef's Choice Brooklyn has operated for nearly four decades as a wholesale food and paper distributor serving the Caribbean community. It's open seven days a week and sells groceries, meats, and paper goods in bulk to both households and other businesses. Stores like this are the supply chain behind a cultural enclave — they're the reason ingredients for Caribbean cooking are available at a price a family can carry, and they're the wholesale link that keeps smaller shops and restaurants on this corridor stocked. They are also, in energy terms, among the heaviest continuous electricity users on this stretch of Utica Avenue: commercial refrigeration runs twenty-four hours a day, year-round, and its compressors work hardest in exactly the weather that strains the grid.",
 energy="Businesses like this are billed on a commercial rate that can include a demand charge — a fee based not on total consumption but on the highest single spike in a billing period. Look through the glass and note whether the cases have doors or night curtains: covered cases can cut refrigeration energy substantially, but they cost more to install, which is a real barrier for a small business.",
 talk="Decarbonization conversations usually center on homes. What does it mean for the commercial corridor a neighborhood depends on? Efficiency upgrades here lower operating costs and keep prices down — but who pays for the upgrade, and how does a forty-year-old family business access capital for it?",
 resource="Con Edison and NYSERDA both run no-cost energy assessments and equipment rebates for small businesses; refrigeration and lighting typically have the fastest payback. NYC Accelerator provides free energy advising. Con Edison also accepts food spoilage claims after an outage, from both residential and commercial customers."),

dict(id=5, name="Johnson Energy Clinic and Cooperative (former)", address="436 E 53rd St, Brooklyn, NY 11203",
     lat=40.6490951, lon=-73.9274567, scale="HOUSEHOLD", access="sidewalk",
     short="One of New York City's earliest solar homes",
 long="This house was the home of the Johnson Energy Clinic and Cooperative, an experimental energy home and one of the earliest solar houses in New York City. Decades before rooftop solar became a commercial industry here, this was an ordinary Flatbush residence retrofitted into a working demonstration of what a house could do with sun, insulation, and careful engineering — and, as the name says, it was organized as a clinic and a cooperative, not a private experiment. People came to see it. The distinction matters: a clinic teaches, and a cooperative shares ownership. This wasn't one homeowner installing panels. It was an attempt to build local energy knowledge and hold it collectively, on a residential block in a Black neighborhood, long before anyone was calling that energy justice. In August 2011 the New York Times reported that the owner was at risk of losing the house. Please view from the street — this is a private residence.",
 energy="Everything the rest of this tour discusses in the future tense happened here in the past tense. Solar generation, deep retrofit, energy education, cooperative ownership — this house did all four, with none of the incentives, financing, or installer infrastructure that exist today. The technical lesson is that the building envelope comes first: solar on an uninsulated house is expensive electricity poured into a leaky container, and the early experimental homes understood that before the market did.",
 talk="This is the stop that reframes the whole walk. East Flatbush isn't waiting to be introduced to clean energy — it has been doing this work, and the record is thin because nobody was writing it down. Who else here has done something like this? Whose garage, basement, or roof holds knowledge that never got documented? And what infrastructure would have let this survive — cooperative ownership, technical support, financing that doesn't put the house at risk? That list is essentially the case for the resilience hub.",
 resource="This is the strongest oral-history opportunity on the route; longtime residents may remember the clinic directly. Community solar is the present-day version of what a cooperative was reaching for — a shared array, subscribers who get bill credits, no roof and no upfront cost required. Solar One's Here Comes Solar program provides free technical support for NYC residents and building owners.",
 todo="VERIFY: founder's name, years the clinic operated, systems installed, what happened after 2011. Sources: NYT City Room 2011-08-03 and the YouTube video (both held by BKLVLUP/GROUND3D). Also confirm whether the current owner consents to a public map marker."),

dict(id=6, name="De Event Room", address="634 Remsen Ave, Brooklyn, NY 11236",
     lat=40.65137199318552, lon=-73.91869743552688, scale="BLOCK", access="booking",
     short="Private event space, capacity ~100",
 long="De Event Room is a private event space on Remsen Avenue, on a block where residential buildings and small businesses sit side by side. The indoor space runs over 1,100 square feet across two rooms, with a backyard patio and pool area outside, multiple restrooms, two bar areas, and a buffet-style warming station. It accommodates roughly a hundred people and hosts bridal showers, birthdays, corporate events, pop-ups, workshops, and product launches. Read that amenity list the way an emergency planner would — capacity for a hundred, working restrooms, food service, climate control, outdoor space, and an operator on site who knows the building — and it is close to the profile of a resilience hub.",
 energy="The gap between an event space and a refuge is a backup power source, a cooling strategy, and an agreement reached before an emergency rather than during one. Across the country, the buildings that end up sheltering people are rarely the ones on the official list — they're the halls, basements, and storefronts people already know how to walk into.",
 talk="Does East Flatbush need to build a hub, or upgrade the buildings it already has? What would it take to make five existing rooms in this neighborhood outage-ready instead of one new one? Who would maintain them?",
 resource="Solar-plus-storage for a building this size is eligible for federal tax credits, NYSERDA incentives, and NYC property tax abatements for solar, which can be stacked. Building owners can get free advising through NYC Accelerator."),

dict(id=7, name="Railroad Playground", address="Ditmas Ave between E 91st and E 92nd St, Brooklyn, NY 11236",
     lat=40.649393652888115, lon=-73.91422443933631, scale="NEIGHBORHOOD", access="open",
     short="1957 park on the Canarsie rail corridor",
 long="Originally called Ditmas Playground, this park takes its earlier name from the street to the southeast, itself named for the Van Ditmarsen family who settled in the village of Flatbush in the late 17th century. The Canarsie and Rockaway Beach Railroad — a Long Island Rail Road subsidiary whose branch opened in 1865 — runs just south of the park, and in the early 20th century it was the most popular route for New Yorkers heading to the amusement park at Canarsie Beach. The same corridor serves the Brooklyn Terminal Market down the block, which historically supplied fresh produce and lodging for upstate and Long Island farmers who couldn't make the return trip in a day. The Parks Department acquired this site in 1954 and opened the park in 1957 with handball and basketball courts, a softball field, a public restroom, a wading pool, a children's play area, and shade trees planted around the entire perimeter. A 1997 renovation costing $735,000 gave the park its train-and-market theme: locomotive-shaped play units, railroad pavement of stone and steel track, and steel panels depicting flowers, watermelon, tomatoes, onions, and grapes. It's open daily, 6am to 9pm, with a wheelchair-accessible restroom and water play features.",
 energy="A park is environmental infrastructure that runs on nothing. Tree canopy and vegetated ground can hold a park meaningfully cooler than the paved blocks around it — shade blocks solar radiation before it reaches a surface, and plants cool the air directly as they release water. That's passive cooling: no compressor, no meter, no failure mode during an outage. Soil and planting also absorb stormwater that would otherwise run into the sewer. The water play features do the same job a cooling center does, outdoors and for free. The shade trees planted around this perimeter in 1957 are doing work today that no one billed for.",
 talk="Parks are usually filed under recreation. What changes if they're budgeted as cooling infrastructure? East Flatbush and Canarsie have less tree canopy than the city average, and canopy tracks closely with heat vulnerability across New York. Who decides where trees get planted, and how long does it take a new one to do the work an old one already does?",
 resource="NYC Parks takes tree service and new tree requests through 311 and the Forestry Division. Street tree planting is free to residents and property owners. The Parks tree map shows every street tree in the city, including the stormwater and cooling benefit each provides annually."),

dict(id=8, name="Con Edison Gateway Park Substation", address="789 E 91st St, Brooklyn, NY 11236",
     lat=40.648339092431364, lon=-73.91345543431983, scale="REGIONAL", access="sidewalk",
     short="$1.3 billion substation serving 52,000 Brooklyn customers",
 long="Con Edison is building the Gateway Park Substation here at a cost of $1.3 billion. It's an indoor high-voltage transmission substation — a building rather than an open yard of exposed equipment, a more expensive choice made for a dense residential setting. When complete it will serve roughly 52,000 customers across Central and East Brooklyn, primarily Canarsie and Remsen Village. The project includes about 7.5 miles of new underground feeder cable connecting it into the network, part of a larger cable program reported at around 28 miles. Con Edison's stated reasons for building it are capacity, overload prevention, and network resiliency: the company projects Brooklyn's electricity demand will rise roughly 16 percent over the next decade, driven by population growth, new development, and the shift from gas to electric heating, cooking, and vehicles. Power will reach this station through underground transmission from the Brooklyn Clean Energy Hub in Vinegar Hill, an $810 million transmission substation built to accept up to 1,500 megawatts and designed as an interconnection point for offshore wind generated in the New York Bight, roughly 150 miles off the coast of Long Island and New Jersey.",
 energy="A substation is where transmission becomes distribution. Electricity travels long distances at very high voltage because that's efficient, then has to be stepped down to a level that can safely enter streets and buildings. That conversion needs land, access, and physical protection, which is why substations end up beside rail corridors and industrial edges. This one is also a decarbonization asset: the shift away from gas only works if the electric system can carry the load gas used to. Con Edison's public FAQ for the project specifically addresses Railroad Playground across the street, stating the company doesn't anticipate changes to the playground's size.",
 talk="Electrification is the core decarbonization strategy for New York, and it depends on infrastructure like this. So what does the neighborhood hosting it get? Jobs during construction and after? Priority for grid reliability? Community solar or storage connected to it? East Flatbush and Canarsie have experienced outages during past heat waves, including a deliberate shutoff in July 2019 that affected tens of thousands of southeast Brooklyn customers — this station is part of Con Edison's answer to that history. Is it enough, and who decides?",
 resource="Con Edison maintains a public project page for the Gateway Park Substation with a community contact. Major infrastructure projects and rate changes are decided by the New York Public Service Commission, where written public comment becomes part of the official record. Rate cases are when comments carry the most weight."),

dict(id=9, name="National Grid — Canarsie Service Center", address="8424 Ditmas Ave, Brooklyn, NY 11236",
     lat=40.64576668511091, lon=-73.91784006730398, scale="REGIONAL", access="sidewalk",
     short="Gas operations campus and public CNG fueling station",
 long="This is National Grid's Canarsie Service Center, a working operations campus spanning an address range along Ditmas Avenue with multiple numbered buildings. It's an operational base rather than a customer office — crews, equipment, and administration for the gas distribution network across Brooklyn and Queens. New gas service applications for both boroughs are processed through this address. The site also includes a public compressed natural gas fueling station, operated by Clean Energy and open 24 hours at 3,000 and 3,600 PSI, used by CNG fleet vehicles. National Grid's downstate business is the former Brooklyn Union Gas Company, and the utility delivers gas to roughly 1.8 million customers across New York City and Long Island.",
 energy="In New York City the utility split is fixed and worth memorizing: Con Edison delivers electricity to all five boroughs, while National Grid delivers natural gas — and only gas — to Brooklyn, Queens, and Staten Island. Two companies, two bills, two separate emergency numbers, two separate regulatory proceedings. Most households pay both and can't say which does what. That matters practically, because if you smell gas and call the wrong company you lose time you don't have. It also matters structurally: the decarbonization debate is fundamentally about which of these two connections into your home grows and which shrinks.",
 talk="Gas heats and cooks in most of East Flatbush's housing stock. Electrification would change that — heat pumps instead of boilers, induction instead of burners — with implications for indoor air quality and childhood asthma, and with real costs and real disruption. What does a fair transition look like for homeowners here, many of them older, many in buildings that need envelope work before any equipment swap makes sense? And what happens to the workers and the network at a site like this one?",
 resource="Gas emergency, 24 hours: 1-800-892-2345. Leave the building first, then call. The Energy Affordability Program discounts bills for income-eligible households at both National Grid and Con Edison, targeting energy costs at or below 6 percent of household income; receiving HEAP generally enrolls you automatically. Under New York's HEFPA law, households including someone 62 or older, blind, or disabled, or with a certified medical condition have shutoff protections that many eligible people never claim. See nyeeap.com."),

dict(id=10, name="Wyckoff House Museum", address="5816 Clarendon Rd, Brooklyn, NY 11203",
     lat=40.64435222474173, lon=-73.92082873529188, scale="HOUSEHOLD", access="appointment",
     short="New York State's oldest building, c. 1652",
 long="The Wyckoff House is the oldest surviving building in New York State and was New York City's first officially designated landmark. Built around 1652 on land taken from the Lenape in the 1630s, it sits on about an acre and a half within Milton Fidler Park. Pieter Claesen Wyckoff arrived in New Netherland in 1637 as an indentured laborer; after completing his indenture he and Grietje van Nes settled in the village of Nieuw Amersfoort, in what is now East Flatbush and Flatlands. The Historic House Trust's account of the site is direct about who worked this land: Dutch-American landowners, enslaved and freed Africans, and later European immigrants farmed some of the most fertile ground in the country here. The property remained a working farm until 1901. Today it's owned by NYC Parks, operated by the Wyckoff House & Association, and runs farm-based and school programs, a working garden, and seasonal markets.",
 energy="This building ran for roughly 249 years with no electric grid, no gas main, and no meter. Everything it did to stay habitable was structural: window placement for cross-ventilation, deep eaves for shade, thick walls that slow heat transfer, a cellar for cold storage, and trees left standing where they'd do the most good. That's passive design, and its defining property is that it doesn't fail during an outage because it never depended on power. Modern high-performance building — Passive House, deep energy retrofits — is largely a rediscovery of these principles with better materials and measurement.",
 talk="This is the stop for elders. Before central air, what did your household actually do in a heat wave — which room did you sleep in, what did you do with the windows, where did people go during the day? Those answers are passive cooling strategy, held as memory rather than as building code, and no technical report contains them.",
 resource="The museum is open on a limited schedule and some access is by appointment. Call (718) 629-5400 or email info@wyckoffmuseum.org, especially for a group visit. School and farm programs run year-round."),

dict(id=11, name="Footprints Cafe", address="5814 Clarendon Rd, Brooklyn, NY 11203",
     lat=40.64473940909019, lon=-73.9213153001351, scale="BLOCK", access="customer",
     short="Caribbean restaurant next door to the Wyckoff farm",
 long="Footprints is a Caribbean restaurant known for a large menu and a lively room, and it has grown into a small chain with several Brooklyn locations. If the one on your route differs from what's described here, that's expected — this is a general profile rather than a single address. It sits directly beside the Wyckoff House Museum, which makes for an unusual adjacency: a 17th-century farm and a Caribbean kitchen on the same block, three hundred and seventy years apart, both organized around food grown somewhere and cooked here. Restaurants are also among the most energy-intense small businesses per square foot anywhere on a commercial strip.",
 energy="A commercial kitchen runs gas ranges, an exhaust hood pulling conditioned air out of the building during every open hour, walk-in refrigeration, and a dining room that has to stay comfortable while the kitchen behind it runs hot. Kitchen ventilation alone is often the largest single load, because every cubic foot of air the hood removes has to be replaced and re-conditioned. It's also the least visible: you can see a solar panel, but you can't see a hood running at full speed all day.",
 talk="Of everything you saw today, what did you not know this morning? What's on your own block that you'll look at differently? And what should the Green Book include so that someone who never takes this tour still gets the benefit of it?",
 resource="Con Edison and NYSERDA small-business programs cover energy assessments and equipment rebates; for restaurants, refrigeration and kitchen ventilation typically offer the highest return. Con Edison food spoilage claims apply to restaurants after an outage."),
]

# ---------------------------------------------------------------- routes
ROUTES = [
 dict(id="v1", name="V1 — Library start", order=[1,2,3,4,5,6,7,8,9], spur=[9,10,11],
      gather="Rugby Library", end="National Grid (or Footprints via spur)",
      rationale="Civic gathering space with room for a presentation. Opens on the library's own retrofit story, meets the proposed hub site two minutes later, and builds from community scale out to utility scale."),
 dict(id="v2", name="V2 — De Event Room start", order=[6,7,8,9,10,11,5,4,3,1,2], spur=[],
      gather="De Event Room", end="Resilience Hub site",
      rationale="Private business hosts the reception, supporting a local operator. Opens on infrastructure while energy is high, closes on the Utica community cluster and ends on the ask at the hub site."),
 dict(id="v3", name="V3 — Wyckoff / Footprints start", order=[11,10,7,8,9,5,4,3,1,2], spur=[],
      gather="Footprints Cafe or Wyckoff House Museum", end="Resilience Hub site",
      rationale="Historical framing first — a pre-grid building — then the present-day infrastructure that replaced it, then the community response. Skips De Event Room."),
 dict(id="v4a", name="V4a — Utica walkshop", order=[1,2,3,4,5], spur=[],
      gather="Rugby Library", end="Johnson Energy Clinic",
      rationale="Short community-scale tour. Library, hub site, nonprofit, wholesale grocer, historic solar home. Accessible length; can run in a lunch hour."),
 dict(id="v4b", name="V4b — Ditmas walkshop", order=[6,7,8,9,10,11], spur=[],
      gather="De Event Room", end="Footprints Cafe",
      rationale="Infrastructure and utilities tour. Event space, park, substation, gas campus, then the historic house and a meal. Pairs with V4a as a two-session series."),
]

SCALE_COLOR = {"HOUSEHOLD":"#D85390","BLOCK":"#D85390","NEIGHBORHOOD":"#6CDF67","REGIONAL":"#9076F7"}

# ---------------------------------------------------------------- helpers
def haversine(a, b):
    R = 6371000
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp = p2 - p1
    dl = math.radians(b["lon"] - a["lon"])
    x = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(x))

BY_ID = {s["id"]: s for s in STOPS}

def leg_stats(order):
    total = sum(haversine(BY_ID[order[i]], BY_ID[order[i+1]]) for i in range(len(order)-1))
    legs = [(order[i], order[i+1], haversine(BY_ID[order[i]], BY_ID[order[i+1]])) for i in range(len(order)-1)]
    return total, legs

def fmt(total):
    return round(total*1.25/1609.34, 2), round(total*1.25/1.35/60)

# ---------------------------------------------------------------- geojson
features = []
for r in ROUTES:
    full = r["order"] + r["spur"][1:] if r["spur"] else r["order"]
    total, legs = leg_stats(r["order"])
    miles, mins = fmt(total)
    features.append({
        "type": "Feature",
        "geometry": {"type": "LineString",
                     "coordinates": [[BY_ID[i]["lon"], BY_ID[i]["lat"]] for i in r["order"]]},
        "properties": {"kind": "route", "variant": r["id"], "segment": "main",
                       "label": r["name"], "optional": False,
                       "stop_order": r["order"], "walk_miles": miles, "walk_minutes": mins,
                       "note": "PLACEHOLDER straight-line geometry. Snap to sidewalks before publishing."}})
    if r["spur"]:
        st, _ = leg_stats(r["spur"])
        features.append({
            "type": "Feature",
            "geometry": {"type": "LineString",
                         "coordinates": [[BY_ID[i]["lon"], BY_ID[i]["lat"]] for i in r["spur"]]},
            "properties": {"kind": "route", "variant": r["id"], "segment": "spur",
                           "label": r["name"] + " (optional extension)", "optional": True,
                           "stop_order": r["spur"], "walk_miles": fmt(st)[0],
                           "note": "PLACEHOLDER straight-line geometry. Render dashed."}})

for s in STOPS:
    p = {"kind": "stop", "stop_id": s["id"], "name": s["name"], "address": s["address"],
         "short": s["short"], "long": s["long"],
         "scale": s["scale"], "access": s["access"], "color": SCALE_COLOR[s["scale"]],
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
   "edition": "The Green Book — Energy Resilience Edition",
   "partners": "BKLVLUP × GROUND3D",
   "neighborhood": "East Flatbush / Remsen Village / Canarsie, Brooklyn",
   "center": [-73.9219, 40.6478],
   "popup_fields": ["name", "address", "long"],
   "popup_note": "INTERACTIVE MAP POPUPS RENDER ONLY name, address AND long. The energy_connection, conversation and resource fields are facilitator material for the printed Green Book and the walkshop script — do NOT render them in map popups.",
   "static_map_note": "Static map shows NUMBERED PINS ONLY. No inline labels. Names go in a legend strip keyed to stop_id, using the short field.",
   "color_note": "Pin fill from properties.color (derived from scale). Pin outline encodes access. See CLAUDE.md > Brand.",
   "scale_groups": {"HOUSEHOLD": "a single home", "BLOCK": "a business or block",
                    "NEIGHBORHOOD": "shared neighborhood assets", "REGIONAL": "utility-scale systems"},
   "access_values": {"open": "open to anyone", "visitor": "open as a visitor",
                     "customer": "open as a customer", "booking": "open by booking",
                     "appointment": "open by appointment", "sidewalk": "view from the sidewalk only"},
   "route_variants": [{"id": r["id"], "name": r["name"], "gather": r["gather"], "end": r["end"],
                       "order": r["order"], "spur": r["spur"],
                       "walk_miles": fmt(leg_stats(r["order"])[0])[0],
                       "walk_minutes": fmt(leg_stats(r["order"])[0])[1],
                       "rationale": r["rationale"]} for r in ROUTES],
   "note": "Route LineStrings are PLACEHOLDER straight lines. Snap to sidewalks before publishing."
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
     "All distances are straight-line × 1.25 to approximate sidewalk routing, at 1.35 m/s.",
     "Add roughly 5 minutes per stop for narration and discussion.", "", "---", ""]
for r in ROUTES:
    total, legs = leg_stats(r["order"])
    miles, mins = fmt(total)
    worst = max(legs, key=lambda x: x[2])
    R += [f"## {r['name']}", "",
          f"**Gather:** {r['gather']} · **End:** {r['end']}",
          f"**{len(r['order'])} stops · {miles} mi · ~{mins} min walking**", "",
          r["rationale"], "", "| # | Stop | Leg |", "|---|---|---|"]
    for n, sid in enumerate(r["order"], 1):
        leg = "" if n == 1 else f"{legs[n-2][2]:.0f} m"
        R += [f"| {n} | {BY_ID[sid]['name']} | {leg} |"]
    if r["spur"]:
        st, sl = leg_stats(r["spur"])
        R += ["", f"*Optional extension (+{fmt(st)[0]} mi):* " +
              " → ".join(BY_ID[i]["name"] for i in r["spur"][1:])]
    R += ["", f"Longest leg: **{worst[2]:.0f} m** ({BY_ID[worst[0]]['name']} → {BY_ID[worst[1]]['name']})", "", "---", ""]
with open(os.path.join(OUT, "ROUTES.md"), "w") as f:
    f.write("\n".join(R))

print(f"built: {len(STOPS)} stops, {len(ROUTES)} route variants, {len(features)} features")
for r in ROUTES:
    t, _ = leg_stats(r["order"]); m, mn = fmt(t)
    print(f"  {r['id']:4s} {len(r['order']):2d} stops  {m:4.2f} mi  {mn:3.0f} min")
