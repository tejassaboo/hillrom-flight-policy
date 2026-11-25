"""Writes the Hill-Rom scenario JSON files (authoring aid; the JSON files are the source of truth).

    python3 tests/build_scenarios.py

Every line number is a line of the frozen handbook (src/plugin/data/policy.txt). Not collected by pytest.
"""

import hashlib
import json
import sys
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(PLUGIN), str(PLUGIN / "src")]

from plugin.world import clock_minutes, day_number, flight_number, utc_offset

POLICY = (PLUGIN / "src/plugin/data/policy.txt").read_text(encoding="utf-8").split("\n")
OUT = PLUGIN / "src/plugin/data/scenarios"


def norm(text):
    return " ".join(text.split())


def keep(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    quote = text if quote is None else quote
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "sha256": hashlib.sha256(text.encode()).hexdigest(), "quote": quote, "why": why}


def near(a, b, quote, why):
    text = norm(" ".join(POLICY[a - 1:b]))
    assert norm(quote) in text, (a, b, quote, text)
    return {"lines": [a, b], "quote": quote, "why": why}


# ----- the clauses the answers rest on -----
TABLE = keep(424, 435, None, "the class of service per segment length and position")
LOGICAL = keep(425, 426, "Employees are to use the lowest logical airfare as defined in Section 3.2.",
               "the lowest logical airfare")
PREF_AIR = keep(400, 401, "Travelers will be required to utilize preferred vendors if the fare offered is equal to "
                "or less than that offered by a non-preferred vendor.", "preferred airline at an equal or lower fare")
PREF_VENDORS = keep(331, 332, "Travelers are required to utilize preferred vendors (airline, lodging, car rental, rail, "
                    "etc.) with whom the Company has negotiated special rates and/or concessions, if equal to or less "
                    "than other options.", "preferred vendors (general information)")
WITHIN = keep(438, 445, None, "the routing tests within a continent")
REFUND = keep(446, 446, "Non-refundable fares may be declined if the cost differential is less than $150.",
              "the refundable margin")
UPGRADES = keep(449, 450, "Upgrades to Business or Premium Economy classes are not reimbursable unless no other seats "
                "are available in your permitted class of service at the time of booking.", "no upgrade")
BETWEEN = keep(451, 455, None, "the routing tests between continents")
ALTERNATES = keep(456, 459, None, "alternate airports such as Gatwick and Heathrow")
FREQUENT = keep(461, 464, "participation in these programs must not influence flight selection, which would result in "
                "incremental cost to the Company beyond the lowest logical airfare available, as defined, or which "
                "results in the use of a non-preferred vendor over a preferred even if the costs are equal.",
                "no non-preferred airline for miles, even at an equal fare")
KEY = keep(490, 494, None, "who may travel together, and the CEO's approval for exceptions")
INTL = keep(288, 290, "International travel (travel between continents) requires pre-travel authorization from the "
            "employee's ELT representative or Regional President. Such approval should be documented in writing",
            "authorization for travel between continents")
SAME_CONTINENT = keep(290, 291, "Pre-travel authorization is not required for travel within the same continent",
                      "no authorization within a continent")
NOT_COVERED = keep(159, 160, "Prior to travel, if a particular situation is not covered by policy, employees should "
                   "contact their manager/supervisor or the Manager of Global Travel for direction.",
                   "who directs a situation the policy does not cover")
SPOUSE = keep(356, 361, None, "companion travel only with a business purpose approved in advance by the ELT member")
SPOUSE_PERSONAL = keep(363, 365, "When a spouse or other individual accompanies an employee at the employee's expense for "
                       "personal reasons, the additional cost must be separated and excluded", "personal companion")
MEET_SPOUSE = keep(865, 867, None, "companion travel to Company meetings")
NONREIMB_SPOUSE = keep(1281, 1281, None, "companion travel is non-reimbursable unless approved")
GAMBLING = keep(343, 345, None, "no gambling trips")
SCOPE = keep(145, 146, "It governs expenses incurred during Company travel", "the policy covers Company travel")
NONREIMB = keep(1237, 1237, None, "nothing not related to business travel")
VACATION = keep(1250, 1251, None, "no vacation or personal days")

# ----- nearby clauses that must not change the answer -----
D_ADVANCE = near(395, 396, "book flights at least 14 days before your trip begins for travel within a continent and at "
                 "least 21 days in advance for travel between continents", "'should': advice, never a refusal")
D_WIFI = near(1216, 1217, "Internet connections during flight may be reimbursed for flight segments greater than six (6) "
              "hours in duration.", "in-flight internet, not the cabin")
D_GROUP = near(487, 488, "it is recommended to avoid planning or creating travel plans that place large employee groups "
               "together in a single aircraft", "a recommendation; the limits count ELT members and officers only")
D_UPGRADE = near(349, 350, "Any upgrades for air, car, hotel, etc. may be made at the traveler's expense or when the "
                 "Company incurs no additional cost.", "an upgrade the company pays for is not one of these")
D_AGENCY = near(310, 311, "If you find lower costs for your travel, contact your agency immediately",
                "the agency books; the listed fares are the agency's")
D_MEETING_SPEND = near(798, 799, "inclusive of flights, rail, car, hotel, venue, meals",
                       "meeting spend, not the traveller's own ticket")

ELT_REP = "Diane Kessler"
SVP_OPS = {"approver_name": ELT_REP, "approver_title": "Senior Vice President, Global Operations"}
RP_EUROPE = {"approver_name": "Henrik Aalto", "approver_title": "Regional President, Europe"}


def trip(**fields):
    base = {
        "traveller_name": "", "traveller_title": "", "elt_member": False, "passenger": "EMPLOYEE", "accompanies": "",
        "home_country": "US", "elt_representative": ELT_REP, "supervisor": "", "origin": "", "destination": "",
        "travel_date": "", "return_date": "", "booking_date": "", "purpose": "", "purpose_kind": "CUSTOMER_VISIT",
        "requested_cabin": "ECONOMY", "prefers_nonstop": False, "requested_refundable": False, "requested_airline": "",
        "requested_airline_why": "", "preferred_airlines": [], "companion_business_purpose": "", "approvals": [],
        "colleagues": [], "notes": [],
    }
    unknown = set(fields) - set(base)
    assert not unknown, unknown
    base.update(fields)
    return base


def sign(who, subject, on):
    return {**who, "subject": subject, "in_writing": True, "given_on": on}


def fl(carrier, depart, minutes, via=None, layovers=None, back=None):
    spec = {"carrier": carrier, "depart": depart, "minutes": minutes}
    if via:
        spec["via"] = via
    if layovers:
        spec["layovers"] = layovers
    if back:
        spec["return"] = back
    return spec


def of(slot, flight, cabin, cents, seats=True, refundable=False):
    data = {"slot": slot, "flight": flight, "cabin": cabin, "fare_cents": cents}
    if not seats:
        data["seats"] = False
    if refundable:
        data["refundable"] = True
    return data


def search(name, origin, destination, date, flights, offers, back="", background=0):
    return {"name": name, "origin": origin, "destination": destination, "date": date, "return_date": back,
            "background": background, "flights": flights, "offers": offers}


def number(carrier, origin, destination, date, depart):
    """The flight number the world gives a nonstop pinned flight (world.flight_number)."""
    start = day_number(date) * 1440 + clock_minutes(depart) - utc_offset(origin)
    return flight_number(carrier, origin, destination, start)


def expected(decision, slots, cabins, reasons, approvers, clauses, phrase=""):
    return {"decision": decision, "offer_slots": sorted(slots), "cabins": sorted(cabins), "reason_codes": sorted(reasons),
            "approvers": sorted(approvers), "clauses": sorted(clauses), "unclear_phrase": phrase}


LOW = ["AIR_TRAVEL", "CLASS_OF_SERVICE", "LOWEST_LOGICAL_AIRFARE"]
VENDOR = ["AIR_TRAVEL", "LOWEST_LOGICAL_AIRFARE", "PREFERRED_VENDORS"]
GAP = ["CORPORATE_CONTROLLER", "GLOBAL_TRAVEL", "NOT_NAMED", "SUPERVISOR"]
DENIED = ["LONG_FLIGHT_CONDITION_NOT_MET", "UPGRADE_NOT_ELIGIBLE"]
BIZ = ["SEGMENT_CLASS_ENTITLEMENT", "SENIOR_ROLE_ENTITLEMENT"]
PREM = ["PREMIUM_ECONOMY_ALLOWED", "SEGMENT_CLASS_ENTITLEMENT"]
S = []


def scenario(id, category, overlays, request, trip_, searches, exp, must_keep, notes, twin_of="", twin_fact="",
             flag_twins=(), ambiguity="none", distractors=()):
    S.append({
        "id": id, "category": category, "overlays": overlays, "twin_of": twin_of, "twin_fact": twin_fact,
        "flag_twins": list(flag_twins), "ambiguity_note": ambiguity, "request": request, "trip": trip_,
        "world": {"searches": searches}, "expected": exp, "must_keep": must_keep, "distractors": list(distractors),
        "design_notes": notes,
    })


# ============================== easy ==============================
scenario(
    "alder-bight", "easy", [],
    "I'm flying to Atlanta on December 9 to visit the Emory hospital account the next morning. Economy, please - "
    "whatever fits policy.",
    trip(traveller_name="Rachel Owens", traveller_title="Senior Account Manager", supervisor="Paul Grady, Area Director",
         origin="ORD", destination="ATL", travel_date="2026-12-09", booking_date="2026-11-30",
         purpose="Account review at a hospital customer in Atlanta",
         preferred_airlines=["United Airlines", "American Airlines"]),
    [search("out", "ORD", "ATL", "2026-12-09",
            {"dl": fl("DL", "07:05", [120]), "ua": fl("UA", "09:40", [115]), "aa": fl("AA", "12:15", [115])},
            [of("dl-economy", "dl", "ECONOMY", 21400), of("ua-economy", "ua", "ECONOMY", 21400),
             of("aa-economy", "aa", "ECONOMY", 22800)])],
    expected("BOOK", ["ua-economy"], ["ECONOMY"], ["LOWEST_FARE", "PREFERRED_CARRIER_REQUIRED"], ["NONE"], VENDOR),
    [TABLE, LOGICAL, PREF_AIR, SAME_CONTINENT],
    "A 115-120 minute segment: coach for all other employees (424-435). Delta and United tie at the lowest fare; "
    "the preferred airline is required at an equal fare (400-401). Within a continent no pre-travel authorization "
    "is needed (290-291), so no sign-off: NONE.")

scenario(
    "bramble-tor", "easy", ["dearer_option"],
    "Please book me business class to San Francisco on December 11 for the West region leadership offsite, which "
    "starts the next day.",
    trip(traveller_name="Gloria Benton", traveller_title="Senior Vice President, Human Resources", elt_member=True,
         supervisor="Marcus Hale, President and CEO", origin="ORD", destination="SFO", travel_date="2026-12-11",
         booking_date="2026-11-30", purpose="West region leadership offsite", purpose_kind="INTERNAL_MEETING",
         requested_cabin="BUSINESS"),
    [search("out", "ORD", "SFO", "2026-12-11",
            {"ua": fl("UA", "08:00", [270]), "aa": fl("AA", "10:30", [275])},
            [of("ua-economy", "ua", "ECONOMY", 29800), of("ua-business", "ua", "BUSINESS", 91000),
             of("aa-economy", "aa", "ECONOMY", 31200), of("aa-business", "aa", "BUSINESS", 88500)])],
    expected("BOOK", ["aa-business"], ["BUSINESS"], BIZ, ["NONE"], ["CLASS_OF_SERVICE"]),
    [TABLE],
    "An ELT member flies Standard Business in every column (432), even on a 270-275 minute segment; the cheaper "
    "business fare.")

scenario(
    "cinder-fell", "easy", ["date_arithmetic", "month_end", "outside_air_section"],
    "I fly out to Frankfurt on December 10 for the distributor training there on December 12. Economy is fine. Diane "
    "already approved the trip by email.",
    trip(traveller_name="Kevin Marsh", traveller_title="Clinical Education Manager",
         supervisor="Mark Ellison, Director, Clinical Education", origin="ORD", destination="FRA",
         travel_date="2026-12-10", booking_date="2026-11-28", purpose="Distributor training in Frankfurt",
         purpose_kind="TRAINING", approvals=[sign(SVP_OPS, "TRIP", "2026-11-26")]),
    [search("out", "ORD", "FRA", "2026-12-10",
            {"ua": fl("UA", "17:40", [530]), "lh": fl("LH", "20:15", [535])},
            [of("ua-economy", "ua", "ECONOMY", 84500), of("lh-economy", "lh", "ECONOMY", 81900),
             of("ua-premium", "ua", "PREMIUM_ECONOMY", 152000)])],
    expected("BOOK", ["lh-economy"], ["ECONOMY"], ["LOWEST_FARE"], ["ELT_REPRESENTATIVE", "NONE"],
             [*LOW, "INTERNATIONAL_PRE_APPROVAL"]),
    [TABLE, LOGICAL, INTL],
    "Travel between continents with the ELT representative's written authorization on file (288-290). 530-535 "
    "minutes: coach for all other employees. Booked 12 days ahead across the month end: line 395-396 says "
    "'should', so it changes nothing.",
    twin_of="finch-holt", twin_fact="the trip sign-off is the ELT representative's or only the supervisor's",
    distractors=[D_ADVANCE])

scenario(
    "drumlin-sedge", "easy", [],
    "Economy to Dallas on December 8, please, for the Baylor Scott & White installation review the next day.",
    trip(traveller_name="Dana Whitfield", traveller_title="Field Service Manager",
         supervisor="Craig Lund, Director, Field Service", origin="ORD", destination="DFW", travel_date="2026-12-08",
         booking_date="2026-12-01", purpose="Installation review at a hospital customer in Dallas"),
    [search("out", "ORD", "DFW", "2026-12-08",
            {"aa-early": fl("AA", "06:30", [150]), "ua": fl("UA", "09:15", [155]), "aa-noon": fl("AA", "13:40", [150])},
            [of("early-economy", "aa-early", "ECONOMY", 17900, seats=False), of("ua-economy", "ua", "ECONOMY", 19400),
             of("noon-economy", "aa-noon", "ECONOMY", 21900)], background=2)],
    expected("BOOK", ["ua-economy"], ["ECONOMY"], ["LOWEST_FARE"], ["NONE"], LOW),
    [TABLE, LOGICAL],
    "The cheapest listed fare is sold out, so the lowest fare that can be bought; coach (424-435).")

scenario(
    "egret-shale", "easy", ["upgrade_not_taken", "outside_air_section"],
    "I'm flying to London on December 15 for the NHS tender meeting on December 17. Economy is fine for me; Henrik "
    "signed off.",
    trip(traveller_name="Laura Pierce", traveller_title="Vice President, International Sales",
         supervisor="Henrik Aalto, Regional President, Europe", origin="JFK", destination="LHR", travel_date="2026-12-15",
         booking_date="2026-12-01", purpose="NHS tender meeting in London",
         approvals=[sign(RP_EUROPE, "TRIP", "2026-11-30")]),
    [search("out", "JFK", "LHR", "2026-12-15",
            {"ba": fl("BA", "18:30", [420]), "aa": fl("AA", "21:10", [415])},
            [of("ba-economy", "ba", "ECONOMY", 68000), of("ba-business", "ba", "BUSINESS", 412000),
             of("aa-economy", "aa", "ECONOMY", 64500), of("aa-business", "aa", "BUSINESS", 398000)])],
    expected("BOOK", ["aa-economy"], ["ECONOMY"], ["LOWEST_FARE"], ["NONE", "REGIONAL_PRESIDENT"],
             [*LOW, "INTERNATIONAL_PRE_APPROVAL"]),
    [TABLE, LOGICAL, INTL],
    "A Vice President on 415-420 minute segments may fly business (433), but asks for economy: a permission, not an "
    "obligation; the lowest fare. The Regional President's authorization is on file (288).")

scenario(
    "fernwick-cove", "easy", [],
    "Book me economy London to Frankfurt on December 7, please, for the EMEA service meeting the next day.",
    trip(traveller_name="Oliver Grant", traveller_title="Service Sales Manager, UK", home_country="GB",
         supervisor="Sophie Lang, Director, EMEA Service", origin="LHR", destination="FRA", travel_date="2026-12-07",
         booking_date="2026-11-30", purpose="EMEA service meeting in Frankfurt", purpose_kind="INTERNAL_MEETING"),
    [search("out", "LHR", "FRA", "2026-12-07",
            {"ba": fl("BA", "07:20", [95]), "lh": fl("LH", "10:05", [100])},
            [of("ba-economy", "ba", "ECONOMY", 18800), of("lh-economy", "lh", "ECONOMY", 17600)], background=2)],
    expected("BOOK", ["lh-economy"], ["ECONOMY"], ["LOWEST_FARE"], ["NONE"], [*LOW, "INTERNATIONAL_PRE_APPROVAL"]),
    [TABLE, LOGICAL, SAME_CONTINENT],
    "London to Frankfurt is within one continent, so no pre-travel authorization (290-291); coach, lowest fare.")

# ============================== boundary twins ==============================
for name, minutes, twin in (("gannet-sill", 359, "heather-knap"), ("heather-knap", 361, "gannet-sill")):
    over_six = minutes > 360
    scenario(
        name, "boundary_twin", ["dearer_option"] if over_six else [],
        "I'm flying to Seattle on December 14 for the Providence health system review. Business class, please.",
        trip(traveller_name="Thomas Reyes", traveller_title="Vice President, Global Marketing",
             supervisor=f"{ELT_REP}, Senior Vice President, Global Operations", origin="JFK", destination="SEA",
             travel_date="2026-12-14", booking_date="2026-12-01", purpose="Health system review in Seattle",
             requested_cabin="BUSINESS"),
        [search("out", "JFK", "SEA", "2026-12-14",
                {"dl": fl("DL", "08:10", [minutes]), "aa": fl("AA", "14:05", [minutes])},
                [of("dl-economy", "dl", "ECONOMY", 42000), of("dl-business", "dl", "BUSINESS", 128000),
                 of("aa-economy", "aa", "ECONOMY", 44500), of("aa-business", "aa", "BUSINESS", 131000)])],
        expected("BOOK", ["dl-business"], ["BUSINESS"], BIZ, ["NONE"], ["CLASS_OF_SERVICE"]) if over_six else
        expected("BOOK", ["dl-economy"], ["ECONOMY"], DENIED, ["NONE"], ["CLASS_OF_SERVICE"]),
        [TABLE],
        f"A Vice President on a {minutes}-minute nonstop: "
        + ("'> 6 hours', Standard Business (433)." if over_six else "'< 6 hours', Coach / Economy (433)."),
        twin_of=twin, twin_fact="nonstop scheduled minutes 359 or 361")

for name, minutes, twin in (("iris-combe", 599, "jackdaw-scar"), ("jackdaw-scar", 601, "iris-combe")):
    over_ten = minutes > 600
    scenario(
        name, "boundary_twin", ["dearer_option", "outside_air_section"] if over_ten else ["outside_air_section"],
        "I'm going to Tokyo on January 12 for the Japan distributor launch. Premium economy, please - Diane has "
        "approved the trip.",
        trip(traveller_name="Kevin Cho", traveller_title="Director, Asia Pacific Marketing",
             supervisor="Laura Pierce, Vice President, International Sales", origin="SFO", destination="NRT",
             travel_date="2027-01-12", booking_date="2026-12-01", purpose="Japan distributor launch in Tokyo",
             requested_cabin="PREMIUM_ECONOMY", approvals=[sign(SVP_OPS, "TRIP", "2026-11-27")]),
        [search("out", "SFO", "NRT", "2027-01-12",
                {"ua": fl("UA", "11:20", [minutes]), "nh": fl("NH", "13:05", [minutes])},
                [of("ua-economy", "ua", "ECONOMY", 89000), of("ua-premium", "ua", "PREMIUM_ECONOMY", 165000),
                 of("nh-economy", "nh", "ECONOMY", 94000), of("nh-premium", "nh", "PREMIUM_ECONOMY", 171000)])],
        expected("BOOK", ["ua-premium"], ["PREMIUM_ECONOMY"], PREM, ["ELT_REPRESENTATIVE", "NONE"],
                 ["CLASS_OF_SERVICE", "INTERNATIONAL_PRE_APPROVAL"]) if over_ten else
        expected("BOOK", ["ua-economy"], ["ECONOMY"], DENIED, ["ELT_REPRESENTATIVE", "NONE"],
                 ["CLASS_OF_SERVICE", "INTERNATIONAL_PRE_APPROVAL"]),
        [TABLE, INTL],
        f"A Director (all other employees) on a {minutes}-minute nonstop: "
        + ("'> 10 hours', Premium Coach / Economy Plus (434-435)." if over_ten
           else "'> 6 hours and < 10 hours', Coach / Economy (434)."),
        twin_of=twin, twin_fact="nonstop scheduled minutes 599 or 601")

for name, cents, twin in (("kittiwake-holm", 36800, "lupin-wold"), ("lupin-wold", 36900, "kittiwake-holm")):
    enough = 61800 - cents >= 25000
    scenario(
        name, "boundary_twin", ["multi_leg"] + ([] if enough else ["dearer_option"]),
        "Round trip to Seattle, out December 8 and back December 11, for the Swedish Medical install. I'd like the "
        "nonstop both ways if policy allows; economy.",
        trip(traveller_name="Nina Patel", traveller_title="Implementation Specialist",
             supervisor="Craig Lund, Director, Field Service", origin="ORD", destination="SEA", travel_date="2026-12-08",
             return_date="2026-12-11", booking_date="2026-11-24", purpose="Equipment installation at a Seattle hospital",
             prefers_nonstop=True),
        [search("round", "ORD", "SEA", "2026-12-08",
                {"ua": fl("UA", "08:00", [250], back={"depart": "16:00", "minutes": [225]}),
                 "dl": fl("DL", "07:15", [70, 190], via=["MSP"], layovers=[80],
                          back={"depart": "15:10", "minutes": [180, 75], "via": ["MSP"], "layovers": [60]})},
                [of("nonstop-economy", "ua", "ECONOMY", 61800), of("connection-economy", "dl", "ECONOMY", cents)],
                back="2026-12-11")],
        expected("BOOK", ["connection-economy"], ["ECONOMY"], ["COST_SAVINGS", "LOWEST_FARE"], ["NONE"],
                 ["LOWEST_LOGICAL_AIRFARE"]) if enough else
        expected("BOOK", ["nonstop-economy"], ["ECONOMY"], ["ALTERNATE_ROUTE_WITHIN_MARGIN", "SAVINGS_BELOW_THRESHOLD"],
                 ["NONE"], ["LOWEST_LOGICAL_AIRFARE"]),
        [WITHIN, LOGICAL],
        f"The one-stop round trip via Minneapolis adds 90 minutes each way (within two hours) and saves "
        f"{61800 - cents} cents on the round-trip fare: "
        + ("'at least $250', so it is the lowest logical airfare (438-445)." if enough
           else "less than $250, so the requested nonstop."),
        twin_of=twin, twin_fact="connection round-trip fare 36800 or 36900 cents against 61800")

for name, cents, twin in (("mallow-crag", 42300, "nettle-brae"), ("nettle-brae", 42400, "mallow-crag")):
    within = cents - 27400 < 15000
    scenario(
        name, "boundary_twin", ["dearer_option"] if within else [],
        "Denver on December 9 for the UCHealth demo - the date may still move, so a refundable economy fare please.",
        trip(traveller_name="Ben Alvarez", traveller_title="Clinical Sales Specialist",
             supervisor="Paul Grady, Area Director", origin="ORD", destination="DEN", travel_date="2026-12-09",
             booking_date="2026-11-30", purpose="Product demonstration at a hospital customer in Denver",
             requested_refundable=True),
        [search("out", "ORD", "DEN", "2026-12-09",
                {"ua": fl("UA", "08:20", [165]), "aa": fl("AA", "11:45", [170])},
                [of("ua-saver", "ua", "ECONOMY", 27400), of("ua-flex", "ua", "ECONOMY", cents, refundable=True),
                 of("aa-saver", "aa", "ECONOMY", 29900)])],
        expected("BOOK", ["ua-flex"], ["ECONOMY"], ["REFUNDABLE_WITHIN_MARGIN"], ["NONE"], ["LOWEST_LOGICAL_AIRFARE"])
        if within else
        expected("BOOK", ["ua-saver"], ["ECONOMY"], ["REFUNDABLE_FARE_NOT_ALLOWED"], ["NONE"],
                 ["LOWEST_LOGICAL_AIRFARE"]),
        [REFUND, LOGICAL],
        f"The refundable fare costs {cents - 27400} cents more than the non-refundable one on the same flight: "
        + ("less than $150, so it may be booked (446)." if within else "not less than $150, so the non-refundable fare."),
        twin_of=twin, twin_fact="refundable fare 14900 or 15000 cents above the non-refundable one")

# ============================== multi-rule ==============================
CFO = {"traveller_name": "Alan Brooks", "traveller_title": "Chief Financial Officer", "elt_member": True,
           "supervisor": "Marcus Hale, President and CEO", "origin": "ORD", "destination": "LGA", "travel_date": "2026-12-09",
           "booking_date": "2026-12-01", "purpose": "Quarterly board meeting in New York", "purpose_kind": "BOARD_MEETING"}
X = number("UA", "ORD", "LGA", "2026-12-09", "07:00")
CEO_C = {"name": "Marcus Hale", "title": "President and CEO", "elt_member": True, "flights": [X]}
CLO_C = {"name": "Joan Whitaker", "title": "SVP Corporate Secretary & Chief Legal Officer", "elt_member": True,
         "flights": [X]}
BOARD_FLIGHTS = {"ua": fl("UA", "07:00", [125]), "aa": fl("AA", "08:30", [130])}
BOARD_OFFERS = [of("ua-economy", "ua", "ECONOMY", 21800), of("ua-business", "ua", "BUSINESS", 64000),
                of("aa-economy", "aa", "ECONOMY", 24600), of("aa-business", "aa", "BUSINESS", 66000)]
REQ_BOARD = ("Book me to LaGuardia on December 9 for the board meeting. Economy is fine - the earlier flight the rest "
             "of the leadership team is on would be ideal.")

scenario(
    "osprey-dene", "multi_rule", ["multi_traveller", "dearer_option", "upgrade_not_taken"], REQ_BOARD,
    trip(**CFO, colleagues=[CEO_C, CLO_C], notes=[f"The CEO and the Chief Legal Officer are booked on {X}.", "The board meets at 13:00."]),
    [search("out", "ORD", "LGA", "2026-12-09", BOARD_FLIGHTS, BOARD_OFFERS)],
    expected("BOOK", ["aa-economy"], ["ECONOMY"], ["KEY_OFFICERS_TOGETHER", "TRAVELLER_LIMIT_PER_FLIGHT"], ["NONE"],
             ["KEY_PERSONNEL"]),
    [KEY, TABLE],
    f"The CEO and the Chief Legal Officer are on {X}; the CFO would make three of the named officers on one flight "
    "(493-494), so the other flight. The ELT may fly business (432) but she asks for economy.",
    twin_of="plover-ghyll", twin_fact="the Chief Legal Officer is or is not on the earlier flight",
    distractors=[D_GROUP])

scenario(
    "plover-ghyll", "multi_rule", ["multi_traveller", "upgrade_not_taken"], REQ_BOARD,
    trip(**CFO, colleagues=[CEO_C], notes=[f"The CEO is booked on {X}.", "The board meets at 13:00."]),
    [search("out", "ORD", "LGA", "2026-12-09", BOARD_FLIGHTS, BOARD_OFFERS)],
    expected("BOOK", ["ua-economy"], ["ECONOMY"], ["LOWEST_FARE"], ["NONE"], [*LOW, "KEY_PERSONNEL"]),
    [KEY, TABLE, LOGICAL],
    f"Only the CEO is on {X}: with the CFO that is two of the named officers, which is allowed (493-494); the lowest "
    "fare.",
    twin_of="osprey-dene", twin_fact="the Chief Legal Officer is or is not on the earlier flight")

scenario(
    "quince-firth", "multi_rule", ["multi_leg", "date_arithmetic", "outside_air_section"],
    "Round trip to Mexico City, out December 9 and back December 12, for the distributor kickoff. Nonstop both ways "
    "if policy allows; economy.",
    trip(traveller_name="Marco Ruiz", traveller_title="Distributor Sales Manager, Latin America",
         supervisor="Laura Pierce, Vice President, International Sales", origin="ORD", destination="MEX",
         travel_date="2026-12-09", return_date="2026-12-12", booking_date="2026-11-24",
         purpose="Latin America distributor kickoff in Mexico City", prefers_nonstop=True),
    [search("round", "ORD", "MEX", "2026-12-09",
            {"ua": fl("UA", "08:30", [220], back={"depart": "14:00", "minutes": [220]}),
             "aa": fl("AA", "07:00", [120, 135], via=["DFW"], layovers=[75],
                      back={"depart": "13:10", "minutes": [135, 120], "via": ["DFW"], "layovers": [75]})},
            [of("nonstop-economy", "ua", "ECONOMY", 78000), of("connection-economy", "aa", "ECONOMY", 52000)],
            back="2026-12-12")],
    expected("BOOK", ["connection-economy"], ["ECONOMY"], ["COST_SAVINGS", "LOWEST_FARE"], ["NONE"],
             ["INTERNATIONAL_PRE_APPROVAL", "LOWEST_LOGICAL_AIRFARE"]),
    [INTL, SAME_CONTINENT, WITHIN],
    "Chicago to Mexico City is within North America, so no pre-travel authorization (288-291) and the within-continent "
    "tests apply (438-445): the connection adds 110 minutes each way and saves 26000 cents, so it is the lowest logical "
    "airfare. The between-continents $1,000 test would wrongly keep the nonstop. Booked 15 days ahead: 14 days is "
    "advice for within a continent anyway.",
    distractors=[D_ADVANCE])

scenario(
    "rowan-skerry", "multi_rule", ["multi_leg", "outside_air_section"],
    "Round trip to Frankfurt, out January 18 and back January 22, for the European service review. Nonstop if policy "
    "allows; economy. Diane approved the trip.",
    trip(traveller_name="Sarah Lindqvist", traveller_title="Director, Global Service Operations",
         supervisor=f"{ELT_REP}, Senior Vice President, Global Operations", origin="ORD", destination="FRA",
         travel_date="2027-01-18", return_date="2027-01-22", booking_date="2026-12-02",
         purpose="European service review in Frankfurt", purpose_kind="INTERNAL_MEETING", prefers_nonstop=True,
         approvals=[sign(SVP_OPS, "TRIP", "2026-12-01")]),
    [search("round", "ORD", "FRA", "2027-01-18",
            {"lh": fl("LH", "17:30", [530], back={"depart": "11:00", "minutes": [590]}),
             "ua": fl("UA", "15:20", [125, 465], via=["EWR"], layovers=[110],
                      back={"depart": "08:40", "minutes": [515, 145], "via": ["EWR"], "layovers": [100]})},
            [of("nonstop-economy", "lh", "ECONOMY", 236000), of("connection-economy", "ua", "ECONOMY", 132000)],
            back="2027-01-22")],
    expected("BOOK", ["connection-economy"], ["ECONOMY"], ["COST_SAVINGS", "LOWEST_FARE"],
             ["ELT_REPRESENTATIVE", "NONE"], ["INTERNATIONAL_PRE_APPROVAL", "LOWEST_LOGICAL_AIRFARE"]),
    [BETWEEN, INTL, TABLE],
    "Between continents the tests are three hours and $1,000 (451-455): the connection via Newark adds 170 minutes each "
    "way and saves 104000 cents, so it is the lowest logical airfare. The within-continent two-hour test would wrongly "
    "keep the nonstop. Every segment is coach for a Director (125-590 minutes, none at 360 or 600).")

COMPANION = {"traveller_name": "Elena Novak", "traveller_title": "Spouse of Robert Novak", "passenger": "SPOUSE_OR_COMPANION",
                 "accompanies": "Robert Novak, Vice President, Sales North America",
                 "supervisor": f"{ELT_REP}, Senior Vice President, Global Operations", "origin": "ORD", "destination": "MCO",
                 "travel_date": "2027-02-22", "booking_date": "2026-12-03", "purpose_kind": "CUSTOMER_EVENT"}
COMPANION_SEARCH = [search("out", "ORD", "MCO", "2027-02-22",
                           {"ua": fl("UA", "07:45", [165]), "wn": fl("WN", "10:20", [170]),
                            "aa": fl("AA", "13:05", [165])},
                           [of("ua-economy", "ua", "ECONOMY", 23800), of("wn-economy", "wn", "ECONOMY", 21900),
                            of("aa-economy", "aa", "ECONOMY", 24400)])]

scenario(
    "sorrel-haugh", "multi_rule", ["multi_traveller", "outside_air_section"],
    "Please book my wife Elena to Orlando on February 22 for the customer partners' event that opens the next day - "
    "she's hosting the partners' program, and Diane approved it last week.",
    trip(**COMPANION, purpose="Hosting the partners' program at the customer partners' event in Orlando",
         companion_business_purpose="Hosts the program for customers' partners at the Company's partners' event",
         approvals=[sign(SVP_OPS, "COMPANION_TICKET", "2026-11-26")]),
    COMPANION_SEARCH,
    expected("BOOK", ["wn-economy"], ["ECONOMY"], ["COMPANION_BUSINESS_PURPOSE_APPROVED", "LOWEST_FARE"],
             ["ELT_MEMBER", "ELT_REPRESENTATIVE", "NONE"],
             ["LOWEST_LOGICAL_AIRFARE", "MEETING_COMPANION", "SPOUSE_COMPANION"]),
    [SPOUSE, MEET_SPOUSE],
    "A bona fide business purpose and the ELT member's advance written approval (356-361, 865-871): the companion's "
    "ticket at the lowest fare.",
    twin_of="aster-fold", twin_fact="a business purpose and the ELT member's approval are or are not on file")

# ============================== hidden clause ==============================
scenario(
    "thistle-moraine", "hidden_clause", ["multi_leg"],
    "I'm headed to Anchorage on December 10 for the Alaska Native Medical Center visit the next day. It's well over "
    "seven hours of flying through Seattle, so business class please.",
    trip(traveller_name="Thomas Reyes", traveller_title="Vice President, Global Marketing",
         supervisor=f"{ELT_REP}, Senior Vice President, Global Operations", origin="ORD", destination="ANC",
         travel_date="2026-12-10", booking_date="2026-12-01", purpose="Customer visit at a medical center in Anchorage",
         requested_cabin="BUSINESS"),
    [search("out", "ORD", "ANC", "2026-12-10",
            {"dl": fl("DL", "07:30", [230, 195], via=["SEA"], layovers=[70]),
             "as": fl("AS", "09:10", [235, 200], via=["SEA"], layovers=[85])},
            [of("dl-economy", "dl", "ECONOMY", 46200), of("dl-business", "dl", "BUSINESS", 118000),
             of("as-economy", "as", "ECONOMY", 44900), of("as-business", "as", "BUSINESS", 112000)])],
    expected("BOOK", ["as-economy"], ["ECONOMY"], DENIED, ["NONE"], ["CLASS_OF_SERVICE"]),
    [TABLE],
    "Class is by 'the length of individual flight segment' (426): every segment is under six hours (195-235 minutes), "
    "so a Vice President flies coach on each, although the flying time adds up to over seven hours.")

scenario(
    "umber-carse", "hidden_clause", ["outside_air_section"],
    "I fly to London on January 19 for the NHS Supply Chain negotiation on January 21 - business class one way, "
    "please. Henrik approved the trip.",
    trip(traveller_name="Laura Pierce", traveller_title="Vice President, International Sales",
         supervisor="Henrik Aalto, Regional President, Europe", origin="ORD", destination="LHR", travel_date="2027-01-19",
         booking_date="2026-12-02", purpose="Supply contract negotiation in central London", requested_cabin="BUSINESS",
         approvals=[sign(RP_EUROPE, "TRIP", "2026-12-01")],
         notes=["Central London is served by London Gatwick (LGW) as well as London Heathrow (LHR)."]),
    [search("heathrow", "ORD", "LHR", "2027-01-19",
            {"ba": fl("BA", "18:10", [470]), "aa": fl("AA", "20:05", [465])},
            [of("lhr-ba-economy", "ba", "ECONOMY", 92000), of("lhr-ba-business", "ba", "BUSINESS", 560000),
             of("lhr-aa-economy", "aa", "ECONOMY", 95000), of("lhr-aa-business", "aa", "BUSINESS", 575000)]),
     search("gatwick", "ORD", "LGW", "2027-01-19",
            {"ba-g": fl("BA", "18:45", [475])},
            [of("lgw-ba-economy", "ba-g", "ECONOMY", 90500), of("lgw-ba-business", "ba-g", "BUSINESS", 428000)])],
    expected("BOOK", ["lgw-ba-business"], ["BUSINESS"],
             ["ALTERNATE_AIRPORT_LOWER_FARE", "COST_SAVINGS", "SEGMENT_CLASS_ENTITLEMENT", "SENIOR_ROLE_ENTITLEMENT"],
             ["NONE", "REGIONAL_PRESIDENT"], ["CLASS_OF_SERVICE", "INTERNATIONAL_PRE_APPROVAL", "LOWEST_LOGICAL_AIRFARE"]),
    [TABLE, ALTERNATES, BETWEEN, INTL],
    "A Vice President over six hours: business (433). Alternate airports are considered, Gatwick for Heathrow by name "
    "(456-459), and the trip record names Gatwick as serving central London: Gatwick business saves 132000 cents (at "
    "least $1,000) and adds 5 minutes, so every reading books it.")

scenario(
    "vetch-linn", "hidden_clause", ["synonym"],
    "Boston on December 16 for the Mass General meeting the next day. Put me on American - I'm close to Platinum, "
    "and it's the same price as United anyway. If American isn't possible, book what the policy allows. Economy.",
    trip(traveller_name="Megan Shaw", traveller_title="Regional Sales Manager", supervisor="Paul Grady, Area Director",
         origin="ORD", destination="BOS", travel_date="2026-12-16", booking_date="2026-12-02",
         purpose="Meeting at a hospital customer in Boston", requested_airline="American Airlines",
         requested_airline_why="Close to the next elite status level", preferred_airlines=["United Airlines"]),
    [search("out", "ORD", "BOS", "2026-12-16",
            {"aa": fl("AA", "07:40", [145]), "ua": fl("UA", "09:05", [140]), "dl": fl("DL", "11:30", [145])},
            [of("aa-economy", "aa", "ECONOMY", 31400), of("ua-economy", "ua", "ECONOMY", 31400),
             of("dl-economy", "dl", "ECONOMY", 33900)])],
    expected("BOOK", ["ua-economy"], ["ECONOMY"],
             ["LOYALTY_PROGRAM_PREFERENCE", "PREFERRED_CARRIER_REQUIRED"], ["NONE"],
             ["FREQUENT_FLYER", *VENDOR]),
    [FREQUENT, PREF_AIR, PREF_VENDORS],
    "Equal fares: the preferred airline is required (400-401, 331-332), and frequent-flyer programs must not lead to a "
    "non-preferred vendor 'even if the costs are equal' (463-464).",
    twin_of="wren-scaur", twin_fact="United's fare equal to American's or 100 cents above")

# ============================== distractors ==============================
scenario(
    "wren-scaur", "distractor", [],
    "Boston on December 16 for the Mass General meeting the next day. Put me on American - I'm close to Platinum, "
    "and it's a dollar cheaper than United anyway. If American isn't possible, book what the policy allows. Economy.",
    trip(traveller_name="Megan Shaw", traveller_title="Regional Sales Manager", supervisor="Paul Grady, Area Director",
         origin="ORD", destination="BOS", travel_date="2026-12-16", booking_date="2026-12-02",
         purpose="Meeting at a hospital customer in Boston", requested_airline="American Airlines",
         requested_airline_why="Close to the next elite status level", preferred_airlines=["United Airlines"]),
    [search("out", "ORD", "BOS", "2026-12-16",
            {"aa": fl("AA", "07:40", [145]), "ua": fl("UA", "09:05", [140]), "dl": fl("DL", "11:30", [145])},
            [of("aa-economy", "aa", "ECONOMY", 31400), of("ua-economy", "ua", "ECONOMY", 31500),
             of("dl-economy", "dl", "ECONOMY", 33900)])],
    expected("BOOK", ["aa-economy"], ["ECONOMY"], ["LOWEST_FARE", "LOYALTY_PROGRAM_PREFERENCE"], ["NONE"],
             ["FREQUENT_FLYER", *VENDOR]),
    [PREF_AIR, PREF_VENDORS, LOGICAL],
    "The preferred airline is required only when its fare is equal to or less (400-401); United is 100 cents dearer, "
    "so American, the lowest fare, which the frequent-flyer clause (461-464) does not forbid.",
    twin_of="vetch-linn", twin_fact="United's fare equal to American's or 100 cents above",
    distractors=[near(461, 463, "participation in these programs must not influence flight selection",
                      "no incremental cost here: the requested airline is the cheapest")])

scenario(
    "yew-strand", "distractor", ["outside_air_section"],
    "Anchorage on December 15 for the Providence Alaska go-live. It's nearly seven hours and I need to work online the "
    "whole way - in-flight wifi is reimbursable on flights that long - so please book business.",
    trip(traveller_name="Priya Nair", traveller_title="Director, Clinical Informatics",
         supervisor="Thomas Reyes, Vice President, Global Marketing", origin="JFK", destination="ANC",
         travel_date="2026-12-15", booking_date="2026-12-01", purpose="Software go-live at a hospital in Anchorage",
         requested_cabin="BUSINESS"),
    [search("out", "JFK", "ANC", "2026-12-15",
            {"dl": fl("DL", "08:45", [415]), "as": fl("AS", "16:30", [420])},
            [of("dl-economy", "dl", "ECONOMY", 51800), of("dl-business", "dl", "BUSINESS", 142000),
             of("as-economy", "as", "ECONOMY", 53900), of("as-business", "as", "BUSINESS", 139000)])],
    expected("BOOK", ["dl-economy"], ["ECONOMY"], ["UPGRADE_NOT_ELIGIBLE"], ["NONE"], ["CLASS_OF_SERVICE"]),
    [TABLE, UPGRADES],
    "A Director on a 415-420 minute segment: Coach / Economy (434). Line 1216-1217 lets in-flight internet be "
    "reimbursed on segments over six hours, which has nothing to do with the cabin.",
    distractors=[D_WIFI])

Y = number("UA", "ORD", "LGA", "2026-12-10", "07:00")
ELT_GROUP = [
    {"name": "Gloria Benton", "title": "Senior Vice President, Human Resources", "elt_member": True, "flights": [Y]},
    {"name": ELT_REP, "title": "Senior Vice President, Global Operations", "elt_member": True, "flights": [Y]},
    {"name": "Victor Hayes", "title": "Senior Vice President, Strategy", "elt_member": True, "flights": [Y]},
    {"name": "Ruth Okafor", "title": "Senior Vice President, Quality", "elt_member": True, "flights": [Y]},
    {"name": "Sam Ito", "title": "Director, Investor Relations", "elt_member": False, "flights": [Y]},
]
scenario(
    "zephyr-mire", "distractor", ["multi_traveller"],
    "Please put me on the 7 a.m. United flight to LaGuardia on December 10 with the leadership team for the investor "
    "day. Economy.",
    trip(traveller_name="Julia Fenwick", traveller_title="Director, Corporate Communications",
         supervisor="Gloria Benton, Senior Vice President, Human Resources", origin="ORD", destination="LGA",
         travel_date="2026-12-10", booking_date="2026-12-01", purpose="Investor day in New York",
         purpose_kind="INTERNAL_MEETING", colleagues=ELT_GROUP,
         notes=[f"Four ELT members and one other employee are booked on {Y}."]),
    [search("out", "ORD", "LGA", "2026-12-10",
            {"ua": fl("UA", "07:00", [125]), "aa": fl("AA", "08:30", [130])},
            [of("ua-economy", "ua", "ECONOMY", 22600), of("aa-economy", "aa", "ECONOMY", 25100)])],
    expected("BOOK", ["ua-economy"], ["ECONOMY"], ["LOWEST_FARE"], ["NONE"], [*LOW, "KEY_PERSONNEL"]),
    [KEY, TABLE, LOGICAL],
    f"Four ELT members are on {Y}; the traveller is not on the ELT and is none of the three named officers, so no "
    "limit of lines 492-494 is reached; the advice against large groups (487-488) is a recommendation. The lowest fare.",
    distractors=[D_GROUP])

# ============================== refusals ==============================
scenario(
    "aster-fold", "refusal", ["multi_traveller", "personal_travel", "outside_air_section"],
    "Please book my wife Elena on a flight to Orlando on February 22 too - she'll enjoy the parks while I'm at the "
    "customer partners' event that opens the next day.",
    trip(**COMPANION, purpose="Sightseeing in Orlando while her husband attends a customer partners' event"),
    COMPANION_SEARCH,
    expected("REFUSE", [], ["NONE"], ["COMPANION_NOT_COVERED", "PERSONAL_TRAVEL_NOT_COVERED"], ["NONE"],
             ["MEETING_COMPANION", "NON_REIMBURSABLE", "SPOUSE_COMPANION"]),
    [SPOUSE, SPOUSE_PERSONAL, NONREIMB_SPOUSE],
    "No bona fide business purpose for the spouse (356-358): the Company does not permit or pay her travel; a companion "
    "for personal reasons is at the employee's expense (363-365, 1281).",
    twin_of="sorrel-haugh", twin_fact="a business purpose and the ELT member's approval are or are not on file")

scenario(
    "bittern-hythe", "refusal", ["outside_air_section"],
    "Book me to Las Vegas on January 15. We're taking the Midwest Health purchasing team for a weekend at the casinos "
    "to say thanks for the renewal.",
    trip(traveller_name="Derek Coleman", traveller_title="Key Account Director", supervisor="Paul Grady, Area Director",
         origin="ORD", destination="LAS", travel_date="2027-01-15", booking_date="2026-12-02",
         purpose="A casino weekend with a customer's purchasing team", purpose_kind="ENTERTAINMENT"),
    [search("out", "ORD", "LAS", "2027-01-15",
            {"ua": fl("UA", "09:00", [230]), "wn": fl("WN", "11:40", [235])},
            [of("ua-economy", "ua", "ECONOMY", 26300), of("wn-economy", "wn", "ECONOMY", 24800)], background=2)],
    expected("REFUSE", [], ["NONE"], ["GAMBLING_TRIP_NOT_PERMITTED", "OUTSIDE_POLICY_SCOPE"], ["NONE"],
             ["ADDITIONAL_GUIDELINES"]),
    [GAMBLING],
    "Lines 343-345: the Company will not take employees or customers gambling, and gambling trips are not to be planned "
    "as part of customer visits: no ticket.")

scenario(
    "corrie-wynd", "refusal", ["personal_travel", "outside_air_section"],
    "Can you book my flight to Orlando on December 23 for our family Christmas trip? I'll sort out paying it back on "
    "my expense report.",
    trip(traveller_name="Hannah Brooks", traveller_title="Product Manager", supervisor="Victor Hayes, Senior Vice "
         "President, Strategy", origin="ORD", destination="MCO", travel_date="2026-12-23", booking_date="2026-12-02",
         purpose="Family Christmas vacation in Orlando", purpose_kind="PERSONAL"),
    [search("out", "ORD", "MCO", "2026-12-23",
            {"ua": fl("UA", "08:10", [165]), "wn": fl("WN", "12:30", [170])},
            [of("ua-economy", "ua", "ECONOMY", 31800), of("wn-economy", "wn", "ECONOMY", 28900)], background=2)],
    expected("REFUSE", [], ["NONE"], ["OUTSIDE_POLICY_SCOPE", "PERSONAL_TRAVEL_NOT_COVERED"], ["NONE"],
             ["NON_REIMBURSABLE", "PURPOSE", "SCOPE"]),
    [SCOPE, NONREIMB, VACATION],
    "The policy governs Company travel (145-146); any expense not directly related to business travel is not permitted "
    "and vacation days are personal (1237, 1250-1251): the Company buys no ticket.")

# ============================== flags ==============================
scenario(
    "dunlin-esker", "flag", ["unclear_phrase"],
    "I'm flying to Seattle on December 14 for the Providence health system review. Business class, please.",
    trip(traveller_name="Thomas Reyes", traveller_title="Vice President, Global Marketing",
         supervisor=f"{ELT_REP}, Senior Vice President, Global Operations", origin="JFK", destination="SEA",
         travel_date="2026-12-14", booking_date="2026-12-01", purpose="Health system review in Seattle",
         requested_cabin="BUSINESS"),
    [search("out", "JFK", "SEA", "2026-12-14",
            {"dl": fl("DL", "08:10", [360]), "aa": fl("AA", "14:05", [360])},
            [of("dl-economy", "dl", "ECONOMY", 42000), of("dl-business", "dl", "BUSINESS", 128000),
             of("aa-economy", "aa", "ECONOMY", 44500), of("aa-business", "aa", "BUSINESS", 131000)])],
    expected("FLAG_FOR_APPROVAL", ["dl-business", "dl-economy"], ["BUSINESS", "ECONOMY"],
             ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"], GAP,
             ["CLASS_OF_SERVICE", "RESPONSIBILITY"], "< 6 hours > 6 hours"),
    [TABLE, NOT_COVERED],
    "A Vice President on a nonstop of exactly 360 minutes: the table's columns are '< 6 hours' (coach) and '> 6 hours "
    "and < 10 hours' (business); exactly six hours is in neither. A situation the policy does not cover goes to the "
    "manager/supervisor or the Manager of Global Travel (159-160).",
    flag_twins=["gannet-sill", "heather-knap"],
    ambiguity={"phrase": "< 6 hours > 6 hours",
               "readings": ["Six hours is not more than six hours, so the segment is not '> 6 hours': coach.",
                            "Six hours is not less than six hours, so the segment is not '< 6 hours': business."]})

scenario(
    "eider-rigg", "flag", ["unclear_phrase", "outside_air_section"],
    "I'm going to Tokyo on January 12 for the Japan distributor launch. Premium economy, please - Diane has approved "
    "the trip.",
    trip(traveller_name="Kevin Cho", traveller_title="Director, Asia Pacific Marketing",
         supervisor="Laura Pierce, Vice President, International Sales", origin="SFO", destination="NRT",
         travel_date="2027-01-12", booking_date="2026-12-01", purpose="Japan distributor launch in Tokyo",
         requested_cabin="PREMIUM_ECONOMY", approvals=[sign(SVP_OPS, "TRIP", "2026-11-27")]),
    [search("out", "SFO", "NRT", "2027-01-12",
            {"ua": fl("UA", "11:20", [600]), "nh": fl("NH", "13:05", [600])},
            [of("ua-economy", "ua", "ECONOMY", 89000), of("ua-premium", "ua", "PREMIUM_ECONOMY", 165000),
             of("nh-economy", "nh", "ECONOMY", 94000), of("nh-premium", "nh", "PREMIUM_ECONOMY", 171000)])],
    expected("FLAG_FOR_APPROVAL", ["ua-economy", "ua-premium"], ["ECONOMY", "PREMIUM_ECONOMY"],
             ["APPROVAL_REQUIRED", "UNCLEAR_POLICY_TEXT"], GAP, ["CLASS_OF_SERVICE", "RESPONSIBILITY"], "< 10 hours > 10 hours"),
    [TABLE, NOT_COVERED, INTL],
    "A Director on a nonstop of exactly 600 minutes: '> 6 hours and < 10 hours' gives coach, '> 10 hours' premium "
    "coach; exactly ten hours is in neither (434-435). The trip itself is authorized (288).",
    flag_twins=["iris-combe", "jackdaw-scar"],
    ambiguity={"phrase": "< 10 hours > 10 hours",
               "readings": ["Ten hours is not more than ten hours, so the segment is not '> 10 hours': coach.",
                            "Ten hours is not less than ten hours, so the segment is not '< 10 hours': premium coach."]})

scenario(
    "finch-holt", "flag", ["approval_required", "outside_air_section"],
    "I fly out to Frankfurt on December 10 for the distributor training there on December 12. Economy is fine. My "
    "manager Mark already signed off on the trip by email.",
    trip(traveller_name="Kevin Marsh", traveller_title="Clinical Education Manager",
         supervisor="Mark Ellison, Director, Clinical Education", origin="ORD", destination="FRA",
         travel_date="2026-12-10", booking_date="2026-11-28", purpose="Distributor training in Frankfurt",
         purpose_kind="TRAINING",
         approvals=[sign({"approver_name": "Mark Ellison", "approver_title": "Director, Clinical Education"}, "TRIP",
                         "2026-11-26")]),
    [search("out", "ORD", "FRA", "2026-12-10",
            {"ua": fl("UA", "17:40", [530]), "lh": fl("LH", "20:15", [535])},
            [of("ua-economy", "ua", "ECONOMY", 84500), of("lh-economy", "lh", "ECONOMY", 81900),
             of("ua-premium", "ua", "PREMIUM_ECONOMY", 152000)])],
    expected("FLAG_FOR_APPROVAL", ["lh-economy"], ["ECONOMY"], ["APPROVAL_REQUIRED", "INTERCONTINENTAL_PRE_APPROVAL"],
             ["ELT_REPRESENTATIVE", "REGIONAL_PRESIDENT"], ["INTERNATIONAL_PRE_APPROVAL"]),
    [INTL, TABLE, LOGICAL],
    "Travel between continents needs pre-travel authorization from the employee's ELT representative or Regional "
    "President (288-290); only the Director's email is on file, which is not that. Hold the lowest coach fare.",
    flag_twins=["cinder-fell", "quince-firth"],
    ambiguity="none: a sign-off is missing; the text is clear")

scenario(
    "gorse-haven", "flag", ["multi_traveller", "approval_required", "upgrade_not_taken"], REQ_BOARD,
    trip(**CFO, colleagues=[CEO_C, CLO_C], notes=[f"The CEO and the Chief Legal Officer are booked on {X}.",
                                                 ("The board meets at 13:00. The CFO cannot leave Chicago before the "
                                                  "morning of December 9, and no other flight that morning is listed.")]),
    [search("out", "ORD", "LGA", "2026-12-09", {"ua": fl("UA", "07:00", [125])},
            [of("ua-economy", "ua", "ECONOMY", 21800), of("ua-business", "ua", "BUSINESS", 64000)])],
    expected("FLAG_FOR_APPROVAL", ["ua-economy"], ["ECONOMY"],
             ["APPROVAL_REQUIRED", "KEY_OFFICERS_TOGETHER", "TRAVELLER_LIMIT_PER_FLIGHT"], ["CEO"], ["KEY_PERSONNEL"]),
    [KEY, TABLE],
    f"The only flight, {X}, already carries the CEO and the Chief Legal Officer; the CFO would be the third named "
    "officer (493-494). An exception needs the CEO's advance approval (490-491), which is not on file: hold it.",
    flag_twins=["plover-ghyll", "osprey-dene"],
    ambiguity="none: a sign-off is missing; the text is clear")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for path in OUT.glob("*.json"):
        path.unlink()
    for data in S:
        (OUT / f"{data['id']}.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(S)} scenarios")


if __name__ == "__main__":
    main()
