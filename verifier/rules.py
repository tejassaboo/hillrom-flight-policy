"""The answer key's rules for Hill-Rom Holdings' Global Travel, Meeting & Expense Policy (Corporate Policy 1016,
effective June 1, 2021), as exact integer code. Byte-identical in src/plugin/rules.py and verifier/rules.py; it
imports only modules a verifier may use.

Every rule cites the frozen handbook text (src/plugin/data/policy.txt) by line. Where the text leaves an
answer open, the rule returns FLAG_FOR_APPROVAL with the unclear words, and a scenario may depend on each
unclear phrase at most once (tests/test_scenarios.py). Combinations no scenario needs raise ValueError, so a
new scenario cannot fall silently into untested logic.

The duration hook. The only flight-duration clause is the class-of-service table (lines 424-435): "Class of
service is predicated upon the length of individual flight segment and position in the Company", with the
columns "< 6 hours", "> 6 hours and < 10 hours" and "> 10 hours". It is measured per segment (each flight on
its own scheduled minutes, legs never added, ground time never counted). Its four comparisons are coded as
four duration rules, each clear on its own:

- below-six (">=" 360): a segment is not "< 6 hours" at 360 minutes or more;
- above-six (">" 360): a segment is "> 6 hours" at 361 minutes or more;
- below-ten (">=" 600): a segment is not "< 10 hours" at 600 minutes or more;
- above-ten (">" 600): a segment is "> 10 hours" at 601 minutes or more.

A segment of exactly 360 or exactly 600 minutes is in no column: the table leaves it open (a gap, never a
boundary twin). The gap matters only where the two columns beside it give the position different classes:
at 360 minutes for "Vice Presidents and above" (coach or business), at 600 minutes for "All other employees"
(coach or premium coach). There the answer is a hold over the unclear words; elsewhere both columns agree.

over(rule, offer) asks the rule of every segment of the offer (out and back): True when every segment is
over, False when none is, None when the segments differ (a connection whose flights fall on both sides).
"""

from contract import ApprovalSubject, Approver, Cabin, Clause, Decision, Passenger, Purpose, ReasonCode

from .world import airport, days_between

ROW_NAMES = {"ELT": "an ELT member", "VP": "a Vice President or above", "OTHER": "one of all other employees"}
HANDBOOK = "Hill-Rom Holdings, Global Travel, Meeting & Expense Policy (Corporate Policy 1016), June 1, 2021"

# Each closed-list section and the heading it names in the frozen text (tests check every heading is there).
CLAUSE_HEADINGS = {
    Clause.PURPOSE: "1.1 Purpose",
    Clause.SCOPE: "1.2 Scope",
    Clause.RESPONSIBILITY: "1.3 Responsibility",
    Clause.GENERAL_INFORMATION: "2.0 GENERAL INFORMATION",
    Clause.TRAVEL_CARD: "2.2 Travel Card",
    Clause.ALTERNATIVES_TO_TRAVEL: "2.4 Alternatives to Travel",
    Clause.INTERNATIONAL_PRE_APPROVAL: "2.5 Pre-Approval for International Travel",
    Clause.POLICY_VIOLATIONS: "2.6 Policy Violations",
    Clause.TRAVEL_AGENCIES: "2.7 Use of Preferred Travel Agencies",
    Clause.PREFERRED_VENDORS: "2.8 Use of Preferred Vendors",
    Clause.ADDITIONAL_GUIDELINES: "2.9 Additional Travel Guidelines and Restrictions",
    Clause.SPOUSE_COMPANION: "2.10 Spouse/Companion Travel",
    Clause.AIR_TRAVEL: "3.0 AIR TRAVEL",
    Clause.CLASS_OF_SERVICE: "3.1 Airline Class of Service",
    Clause.LOWEST_LOGICAL_AIRFARE: "3.2 Lowest Logical Airfare",
    Clause.FREQUENT_FLYER: "3.3 Frequent Flyer Program Benefits",
    Clause.CHANGES_CANCELLATION: "3.4 Changes or Cancellation of Travel",
    Clause.KEY_PERSONNEL: "3.5 Key Personnel Air Travel Policy / Employees Traveling Together",
    Clause.GROUND_TRANSPORTATION: "4.0 GROUND TRANSPORTATION",
    Clause.PERSONAL_VEHICLE: "4.9 Personal Vehicle Usage",
    Clause.RAIL_CLASS: "6.1 Class of Service",
    Clause.LODGING: "7.0 LODGING",
    Clause.MEETING_COMPANION: "8.8 Spouse / Companion Travel to Meetings and Events",
    Clause.MEALS: "9.0 MEALS",
    Clause.INTERNET: "12.1 Internet Connections",
    Clause.LUGGAGE: "12.4 Luggage Fees",
    Clause.NON_REIMBURSABLE: "13.0 NON-REIMBURSABLE EXPENSES",
}

# The class table's comparisons (lines 428-431), one duration rule each (module docstring).
DURATION_RULES = (
    {"name": "below-six", "minutes": 360, "operator": ">=", "lines": [428, 431], "quote": "< 6 hours"},
    {"name": "above-six", "minutes": 360, "operator": ">", "lines": [428, 431], "quote": "> 6 hours and < 10"},
    {"name": "below-ten", "minutes": 600, "operator": ">=", "lines": [428, 431], "quote": "and < 10 hours"},
    {"name": "above-ten", "minutes": 600, "operator": ">", "lines": [428, 431], "quote": "> 10 hours"},
)
LIMITS = {rule["name"]: rule["minutes"] for rule in DURATION_RULES}
OPERATORS = {rule["name"]: rule["operator"] for rule in DURATION_RULES}

# Handbook-specific conventions shown by booking_requirements, beyond the template's (none here).
CONVENTIONS = ()

# Lines 432-435: the class per position and column ("< 6", "> 6 and < 10", "> 10").
TABLE = {
    "ELT": (Cabin.BUSINESS, Cabin.BUSINESS, Cabin.BUSINESS),
    "VP": (Cabin.ECONOMY, Cabin.BUSINESS, Cabin.BUSINESS),
    "OTHER": (Cabin.ECONOMY, Cabin.ECONOMY, Cabin.PREMIUM_ECONOMY),
}
RANK = {Cabin.ECONOMY: 1, Cabin.PREMIUM_ECONOMY: 2, Cabin.BUSINESS: 3, Cabin.FIRST: 4}
VP_TITLES = ("Vice President", "Senior Vice President", "Executive Vice President")
# The unclear words of each gap (lines 429-431, as the table's header reads once its lines are joined).
GAP_PHRASES = {360: "< 6 hours > 6 hours", 600: "< 10 hours > 10 hours"}

# Lines 287-288: "International travel (travel between continents)". Countries the scenarios use, by continent.
CONTINENTS = {
    "US": "North America", "CA": "North America", "MX": "North America",
    "GB": "Europe", "IE": "Europe", "FR": "Europe", "NL": "Europe", "DE": "Europe", "CH": "Europe", "ES": "Europe",
    "IT": "Europe", "DK": "Europe",
    "JP": "Asia", "KR": "Asia", "CN": "Asia", "HK": "Asia", "SG": "Asia", "IN": "Asia",
}

# Lines 438-455: the lowest logical airfare's routing tests, per (between continents?): the most minutes a
# routing may add to the one-way elapsed time ("by more than two hours" / "three (3) hours") and the least
# saving it must bring ("at least $250 of the round-trip coach/economy fare" / "at least $1,000").
ROUTING = {False: (120, 25_000), True: (180, 100_000)}
# Line 446: "Non-refundable fares may be declined if the cost differential is less than $150."
REFUNDABLE_MARGIN_CENTS = 15_000

# Lines 490-494: the officers of whom no more than two may travel together, by the titles the trip records use,
# and the CEO whose advance approval an exception needs.
OFFICERS = ("President and CEO", "Chief Financial Officer", "SVP Corporate Secretary & Chief Legal Officer")
CEO_TITLE = "President and CEO"
MOST_ELT_TOGETHER, MOST_OFFICERS_TOGETHER = 4, 2

LOW_CLAUSES = [Clause.AIR_TRAVEL, Clause.CLASS_OF_SERVICE, Clause.LOWEST_LOGICAL_AIRFARE]
VENDOR_CLAUSES = [Clause.AIR_TRAVEL, Clause.LOWEST_LOGICAL_AIRFARE, Clause.PREFERRED_VENDORS]
# Line 159-160: a situation the policy does not cover goes to the manager/supervisor or the Manager of Global
# Travel; lines 133-134 send concerns about the policy to the Corporate Controller or Director of Global Travel.
GAP_APPROVERS = [Approver.NOT_NAMED, Approver.SUPERVISOR, Approver.GLOBAL_TRAVEL, Approver.CORPORATE_CONTROLLER]
TRIP_SIGNERS = [Approver.ELT_REPRESENTATIVE, Approver.REGIONAL_PRESIDENT]


def segment_over(rule, minutes):
    """Whether one segment of ``minutes`` is over ``rule`` (its operator: ">" strict, ">=" inclusive)."""
    limit = LIMITS[rule]
    return minutes > limit if OPERATORS[rule] == ">" else minutes >= limit


def segments_of(offer):
    return [*offer.segments, *offer.return_segments]


def over(rule, offer):
    """True, False or None (unclear): whether every segment of ``offer`` is over ``rule`` (module docstring)."""
    verdicts = {segment_over(rule, segment.scheduled_minutes) for segment in segments_of(offer)}
    if verdicts == {True}:
        return True
    if verdicts == {False}:
        return False
    return None


def column(minutes):
    """The table column (0, 1, 2) of one segment, or None for exactly 360 or 600 minutes (the gaps)."""
    if not segment_over("below-six", minutes):
        return 0
    if segment_over("above-six", minutes) and not segment_over("below-ten", minutes):
        return 1
    if segment_over("above-ten", minutes):
        return 2
    return None


def position(trip):
    """The table row (lines 432-435): the ELT, "Vice Presidents and above", or "All other employees"."""
    if trip.elt_member:
        return "ELT"
    if trip.traveller_title.startswith(VP_TITLES):
        return "VP"
    if "President" in trip.traveller_title or "Chief" in trip.traveller_title:
        raise ValueError(f"the row of {trip.traveller_title!r} is not modelled")
    return "OTHER"


def segment_class(row, minutes):
    """(class, gap minutes): the class one segment earns, or (None, gap) when the segment falls in a gap whose
    neighbouring columns give this row different classes."""
    place = column(minutes)
    if place is not None:
        return TABLE[row][place], 0
    left, right = (0, 1) if minutes == LIMITS["above-six"] else (1, 2)
    if TABLE[row][left] == TABLE[row][right]:
        return TABLE[row][left], 0
    return None, minutes


def entitlement(trip, offers):
    """(class, gap) every offer on the route earns, segment by segment (out and back): the class, or None with
    the gap minutes. Offers whose segments earn different classes are not modelled."""
    row = position(trip)
    results = {segment_class(row, segment.scheduled_minutes) for offer in offers for segment in segments_of(offer)}
    if len(results) != 1:
        raise ValueError(f"segments earning different classes are not modelled: {sorted(map(str, results))}")
    return results.pop()


def by_value(items):
    return sorted(set(items), key=lambda item: item.value)


def answer(decision, offers, reasons, approvers, clauses, why, phrase=""):
    return {
        "decision": decision,
        "offer_ids": sorted(offer.offer_id for offer in offers),
        "cabins": by_value(offer.cabin for offer in offers) or [Cabin.NONE],
        "reason_codes": by_value(reasons),
        "approvers": by_value(approvers),
        "clauses": by_value(clauses),
        "unclear_phrase": phrase,
        "explanation": why,
    }


def refuse(reasons, clauses, why):
    return answer(Decision.REFUSE, [], reasons, [Approver.NONE], clauses, why)


def cheapest(offers):
    if not offers:
        return []
    low = min(offer.fare_cents for offer in offers)
    return [offer for offer in offers if offer.fare_cents == low]


def city(code):
    return airport(code).city


def return_day(offer):
    return offer.return_segments[0].depart_local[:10] if offer.return_segments else ""


def on_route(trip, offers):
    """Offers from the trip's origin city to its destination city (any airport of each: lines 456-459), flying
    back on the trip's return date ("" one way)."""
    start, end = city(trip.origin.code), city(trip.destination.code)
    return [offer for offer in offers
            if city(offer.segments[0].origin) == start and city(offer.segments[-1].destination) == end
            and return_day(offer) == trip.return_date]


def continent(code):
    country = airport(code).country
    if country not in CONTINENTS:
        raise ValueError(f"the continent of {country} is not modelled")
    return CONTINENTS[country]


def signed(trip, subject):
    """The sign-offs on file for ``subject``, each in writing and given on or before today."""
    records = [record for record in trip.approvals if record.subject == subject]
    for record in records:
        if not record.in_writing or days_between(record.given_on, trip.booking_date) < 0:
            raise ValueError("a spoken or later sign-off is not modelled")
    return records


def trip_signers(trip):
    """Lines 287-290: who of those on file may authorize travel between continents: the employee's ELT
    representative or a Regional President. Another signer (the supervisor) does not count."""
    roles = []
    for record in signed(trip, ApprovalSubject.TRIP):
        if record.approver_name == trip.elt_representative:
            roles.append(Approver.ELT_REPRESENTATIVE)
        elif record.approver_title.startswith("Regional President"):
            roles.append(Approver.REGIONAL_PRESIDENT)
        elif not trip.supervisor.startswith(record.approver_name):
            raise ValueError("a trip sign-off from someone other than the supervisor or the line 288 roles")
    return roles


def solve(trip, offers, hidden):
    """The answer key for one trip and the offers of every search its scenario pins: the decision, and every
    accepted offer id, cabin, reason, approver and section. ``hidden`` (answer_key_inputs) is unused."""
    if hidden:
        raise ValueError("this handbook's scenarios carry no answer_key_inputs")
    if trip.purpose_kind == Purpose.PERSONAL:
        return refuse([ReasonCode.PERSONAL_TRAVEL_NOT_COVERED, ReasonCode.OUTSIDE_POLICY_SCOPE],
                      [Clause.NON_REIMBURSABLE, Clause.SCOPE, Clause.PURPOSE],
                      "Lines 143-146 and 1237: the policy governs Company travel, and any expense not directly "
                      "related to business travel is not permitted; lines 1250-1251 exclude vacation and personal "
                      "days.")
    if trip.purpose_kind == Purpose.ENTERTAINMENT:
        if "casino" not in trip.purpose.lower():
            raise ValueError("entertainment other than gambling is not modelled")
        return refuse([ReasonCode.GAMBLING_TRIP_NOT_PERMITTED, ReasonCode.OUTSIDE_POLICY_SCOPE],
                      [Clause.ADDITIONAL_GUIDELINES],
                      "Lines 343-345: the Company will not take employees or customers gambling; gambling trips "
                      "are not to be planned as part of customer visits.")
    if trip.passenger == Passenger.SPOUSE_OR_COMPANION:
        return companion(trip, on_route(trip, offers))
    return employee(trip, on_route(trip, offers))


def companion(trip, route):
    """Lines 355-361 and 864-871: no spouse/companion travel unless there is a bona fide business purpose and
    it is approved in advance, in writing, by the employee's ELT member."""
    if not trip.companion_business_purpose:
        return refuse([ReasonCode.COMPANION_NOT_COVERED, ReasonCode.PERSONAL_TRAVEL_NOT_COVERED],
                      [Clause.SPOUSE_COMPANION, Clause.MEETING_COMPANION, Clause.NON_REIMBURSABLE],
                      "Lines 355-358 and 1281: no bona fide business purpose for the companion, so no ticket; "
                      "lines 363-365: a companion for personal reasons is at the employee's expense.")
    if trip.requested_cabin != Cabin.ECONOMY:
        raise ValueError("a companion asking for a cabin above economy is not modelled")
    records = [record for record in signed(trip, ApprovalSubject.COMPANION_TICKET)
               if record.approver_name == trip.elt_representative]
    if not records:
        raise ValueError("a companion with a business purpose but no ELT approval is not modelled")
    low, reasons, _, why = lowest(trip, [offer for offer in route if offer.cabin == Cabin.ECONOMY])
    return answer(Decision.BOOK, low, [ReasonCode.COMPANION_BUSINESS_PURPOSE_APPROVED, *reasons],
                  [Approver.ELT_MEMBER, Approver.ELT_REPRESENTATIVE, Approver.NONE],
                  [Clause.SPOUSE_COMPANION, Clause.MEETING_COMPANION],
                  "Lines 358-361: a bona fide business purpose, approved in advance in writing by the employee's "
                  f"ELT member. {why}")


def lowest(trip, offers):
    """Lines 400-401, 331-332 and 447-448: the lowest fare that can be bought, non-refundable; on a tie, the
    preferred airlines ("if the fare offered is equal to or less"). Returns (offers, reasons, clauses, why)."""
    sellable = [offer for offer in offers if offer.seats_available]
    if any(offer.refundable for offer in sellable):
        raise ValueError("a refundable offer without a request for one is not modelled")
    low = cheapest(sellable)
    if not low:
        raise ValueError("no offer in the class can be bought")
    preferred = [offer for offer in low if offer.carrier in trip.preferred_airlines]
    if preferred and len(preferred) < len(low):
        return (preferred, [ReasonCode.PREFERRED_CARRIER_REQUIRED, ReasonCode.LOWEST_FARE], VENDOR_CLAUSES,
                f"Lines 400-401: equal lowest fares ({low[0].fare_cents} cents), so the preferred airline.")
    return low, [ReasonCode.LOWEST_FARE], LOW_CLAUSES, f"The lowest logical airfare ({low[0].fare_cents} cents)."


def together(trip, offer):
    """Lines 490-494: (too many ELT members, too many named officers) on any flight of ``offer`` once the
    traveller joins the colleagues already booked on it."""
    numbers = {segment.flight_number for segment in segments_of(offer)}
    aboard = [colleague for colleague in trip.colleagues if set(colleague.flights) & numbers]
    elt = sum(colleague.elt_member for colleague in aboard) + trip.elt_member
    officers = sum(colleague.title in OFFICERS for colleague in aboard) + (trip.traveller_title in OFFICERS)
    return elt > MOST_ELT_TOGETHER, officers > MOST_OFFICERS_TOGETHER


def employee(trip, route):
    between = continent(trip.origin.code) != continent(trip.destination.code)
    signers = trip_signers(trip) if between else []
    if not between and trip.approvals:
        raise ValueError("a sign-off on file within a continent is not modelled")
    cabin_class, gap = entitlement(trip, route)
    requested = trip.requested_cabin
    sellable = [offer for offer in route if offer.seats_available]
    if gap:
        return gap_hold(trip, sellable, requested, gap, between, signers)
    denied = RANK[requested] > RANK[cabin_class]
    cabin = cabin_class if denied else requested
    pool = [offer for offer in sellable if offer.cabin == cabin]
    if not pool:
        raise ValueError("no seats in the class to book are not modelled")
    limited, pool, hold = personnel(trip, pool)
    if hold:
        return hold
    chosen, reasons, clauses, why = choose(trip, pool, between)
    if denied:
        if reasons != [ReasonCode.LOWEST_FARE]:
            raise ValueError("a refused upgrade together with another fare rule is not modelled")
        row = TABLE[position(trip)]
        reasons = [ReasonCode.UPGRADE_NOT_ELIGIBLE]
        if requested in row:
            reasons.append(ReasonCode.LONG_FLIGHT_CONDITION_NOT_MET)
        clauses = [Clause.CLASS_OF_SERVICE]
        why = (f"Lines 424-435: {ROW_NAMES[position(trip)]} earns {cabin_class.value} on these segments "
               f"(per segment), not {requested.value}; lines 449-450: upgrades are not reimbursable. {why}")
    elif cabin != Cabin.ECONOMY:
        extra = [code for code in reasons if code != ReasonCode.LOWEST_FARE]
        reasons = [ReasonCode.SEGMENT_CLASS_ENTITLEMENT, *extra,
                   ReasonCode.SENIOR_ROLE_ENTITLEMENT if cabin == Cabin.BUSINESS else ReasonCode.PREMIUM_ECONOMY_ALLOWED]
        clauses = [Clause.CLASS_OF_SERVICE] + ([] if clauses == LOW_CLAUSES else clauses)
        why = f"Lines 424-435: {ROW_NAMES[position(trip)]} earns {cabin.value} on every segment. {why}"
    if limited:
        reasons = [ReasonCode.TRAVELLER_LIMIT_PER_FLIGHT, *limited]
        clauses = [Clause.KEY_PERSONNEL]
        why = f"Lines 490-494: the cheaper flight would break the limit ({limited[0].value}); {why}"
    elif trip.colleagues:
        clauses = [*clauses, Clause.KEY_PERSONNEL]
        why = f"Lines 490-494: no limit is broken on this flight. {why}"
    if trip.origin.country != trip.destination.country:
        clauses = [*clauses, Clause.INTERNATIONAL_PRE_APPROVAL]
    if between and not signers:
        return answer(Decision.FLAG_FOR_APPROVAL, chosen,
                      [ReasonCode.APPROVAL_REQUIRED, ReasonCode.INTERCONTINENTAL_PRE_APPROVAL], TRIP_SIGNERS,
                      [Clause.INTERNATIONAL_PRE_APPROVAL],
                      "Lines 288-290: travel between continents needs pre-travel authorization from the "
                      f"employee's ELT representative or Regional President, and none is on file. Hold: {why}")
    if signers:
        why = f"{why} Lines 287-290: the trip between continents is authorized in writing ({signers[0].value})."
    approvers = [*signers, Approver.NONE]  # amendment 4': a sign-off already on file is accepted beside NONE
    return answer(Decision.BOOK, chosen, reasons, approvers, clauses, why)


def gap_hold(trip, sellable, requested, gap, between, signers):
    """A segment in a gap of the table (exactly 360 or 600 minutes) where the neighbouring columns differ for
    this traveller: hold the cheapest offer of each of the two classes."""
    if between and not signers:
        raise ValueError("a gap together with a missing authorization is not modelled")
    row = TABLE[position(trip)]
    left, right = (row[0], row[1]) if gap == LIMITS["above-six"] else (row[1], row[2])
    if requested != right:
        raise ValueError("a gap is modelled only for a request of the higher class")
    held = []
    for cabin in (left, right):
        held += cheapest([offer for offer in sellable if offer.cabin == cabin and not offer.refundable])
    return answer(Decision.FLAG_FOR_APPROVAL, held, [ReasonCode.UNCLEAR_POLICY_TEXT], GAP_APPROVERS,
                  [Clause.CLASS_OF_SERVICE, Clause.RESPONSIBILITY],
                  f"Lines 428-435: a segment of exactly {gap} minutes is in no column of the table, and the columns "
                  f"beside it give {left.value} and {right.value}; line 159-160: a situation the policy does not "
                  "cover goes to the manager/supervisor or the Manager of Global Travel.",
                  phrase=GAP_PHRASES[gap])


def personnel(trip, pool):
    """Lines 490-494: drop offers that would put more than four ELT members, or more than two of the named
    officers, on one flight. (limit codes, offers left, a hold or None)."""
    if signed(trip, ApprovalSubject.SHARED_FLIGHT):
        raise ValueError("a CEO exception on file is not modelled")
    left, codes = [], []
    for offer in pool:
        elt, officers = together(trip, offer)
        if elt:
            codes.append(ReasonCode.ELT_MEMBERS_TOGETHER)
        if officers:
            codes.append(ReasonCode.KEY_OFFICERS_TOGETHER)
        if not (elt or officers):
            left.append(offer)
    codes = by_value(codes)
    if len(left) == len(pool):
        return [], pool, None
    if left:
        if cheapest(pool)[0] in left:
            raise ValueError("a blocked offer that is not the cheapest is not modelled")
        return codes, left, None
    held = cheapest(pool)
    return codes, [], answer(Decision.FLAG_FOR_APPROVAL, held,
                             [ReasonCode.APPROVAL_REQUIRED, ReasonCode.TRAVELLER_LIMIT_PER_FLIGHT, *codes],
                             [Approver.CEO], [Clause.KEY_PERSONNEL],
                             "Lines 490-494: every flight would break the limit "
                             f"({', '.join(code.value for code in codes)}), and an exception needs the CEO's "
                             "advance approval, which is not on file.")


def choose(trip, pool, between):
    """The offer among ``pool`` (one class, seats left) under lines 400-401 and 437-466."""
    if trip.requested_airline:
        return loyalty(trip, pool)
    if trip.requested_refundable:
        return refundable(trip, pool, between)
    if trip.prefers_nonstop:
        return routing(trip, pool, between)
    if any(offer.segments[-1].destination != trip.destination.code for offer in pool):
        return alternate(trip, pool, between)
    return lowest(trip, pool)


def loyalty(trip, pool):
    """Lines 461-464: frequent-flyer programs must not lead to a dearer fare, nor to a non-preferred airline
    over a preferred one "even if the costs are equal"."""
    low, reasons, _, why = lowest(trip, pool)
    clauses = [Clause.FREQUENT_FLYER, *VENDOR_CLAUSES]
    asked = cheapest([offer for offer in pool if offer.carrier == trip.requested_airline])
    if not asked or trip.requested_airline in trip.preferred_airlines:
        raise ValueError("a requested airline that is preferred or not on the route is not modelled")
    if ReasonCode.PREFERRED_CARRIER_REQUIRED in reasons and asked[0].fare_cents == low[0].fare_cents:
        return (low, [ReasonCode.PREFERRED_CARRIER_REQUIRED, ReasonCode.LOYALTY_PROGRAM_PREFERENCE], clauses,
                f"Lines 463-464: not a non-preferred airline over a preferred one at an equal fare. {why}")
    if low == asked:
        return (low, [ReasonCode.LOWEST_FARE, ReasonCode.LOYALTY_PROGRAM_PREFERENCE], clauses,
                f"The requested airline is the lowest fare, below the preferred one (lines 400-401). {why}")
    raise ValueError("a dearer requested airline is not modelled")


def refundable(trip, pool, between):
    """Line 446 (within a continent): "Non-refundable fares may be declined if the cost differential is less
    than $150"."""
    if between:
        raise ValueError("a refundable fare between continents is not modelled")
    fixed = cheapest([offer for offer in pool if not offer.refundable])
    free = cheapest([offer for offer in pool if offer.refundable])
    if not fixed or not free:
        raise ValueError("a refundable request needs both kinds of fare")
    differential = free[0].fare_cents - fixed[0].fare_cents
    numbers = f"{free[0].fare_cents} against {fixed[0].fare_cents} cents, {differential} more"
    if differential < REFUNDABLE_MARGIN_CENTS:
        return (free, [ReasonCode.REFUNDABLE_WITHIN_MARGIN], [Clause.LOWEST_LOGICAL_AIRFARE],
                f"Line 446: the refundable fare costs less than $150 more ({numbers}), so it may be booked.")
    return (fixed, [ReasonCode.REFUNDABLE_FARE_NOT_ALLOWED, ReasonCode.LOWEST_FARE], [Clause.LOWEST_LOGICAL_AIRFARE],
            f"Line 446: the refundable fare costs $150 or more extra ({numbers}), so the non-refundable one.")


def added_minutes(slow, fast):
    """The most minutes ``slow`` adds to ``fast``'s one-way elapsed time, out or back (lines 441-442, 453)."""
    added = slow.elapsed_minutes - fast.elapsed_minutes
    if slow.return_segments:
        added = max(added, slow.return_elapsed_minutes - fast.return_elapsed_minutes)
    return added


def routing(trip, pool, between):
    """Lines 438-455: a traveller who asks for a nonstop gets it unless a connection (one each way) adds no more
    than the limit to the elapsed time each way and saves at least the threshold."""
    if not between and not trip.return_date:
        raise ValueError("the saving 'of the round-trip coach/economy fare' is modelled on round trips only")
    nonstops = cheapest([offer for offer in pool if offer.stops == 0 and len(offer.return_segments) <= 1])
    connections = cheapest([offer for offer in pool if offer.stops == 1 and len(offer.return_segments) in (0, 2)])
    if not nonstops or not connections or len(nonstops) > 1 or len(connections) > 1:
        raise ValueError("one cheapest nonstop and one cheapest connection are needed")
    nonstop, connection = nonstops[0], connections[0]
    saving, added = nonstop.fare_cents - connection.fare_cents, added_minutes(connection, nonstop)
    limit, threshold = ROUTING[between]
    numbers = f"saving {saving} cents, adding up to {added} minutes each way (limits {threshold} and {limit})"
    if saving <= 0 or added > limit:
        raise ValueError(f"this routing is not modelled ({numbers})")
    lines = "451-455" if between else "438-445"
    if saving >= threshold:
        return ([connection], [ReasonCode.COST_SAVINGS, ReasonCode.LOWEST_FARE], [Clause.LOWEST_LOGICAL_AIRFARE],
                f"Lines {lines}: the connection is the lowest logical airfare ({numbers}).")
    return ([nonstop], [ReasonCode.SAVINGS_BELOW_THRESHOLD, ReasonCode.ALTERNATE_ROUTE_WITHIN_MARGIN],
            [Clause.LOWEST_LOGICAL_AIRFARE],
            f"Lines {lines}: the saving does not offset the inconvenience ({numbers}), so the requested nonstop.")


def alternate(trip, pool, between):
    """Lines 456-459: alternate airports are considered (London Gatwick for Heathrow); modelled only when the
    alternate also clears the routing tests of lines 451-455 (saving and added time)."""
    usual = cheapest([offer for offer in pool if offer.segments[-1].destination == trip.destination.code])
    other = cheapest([offer for offer in pool if offer.segments[-1].destination != trip.destination.code])
    if not usual or not other or len(usual) > 1 or len(other) > 1:
        raise ValueError("one cheapest offer to each airport is needed")
    saving, added = usual[0].fare_cents - other[0].fare_cents, added_minutes(other[0], usual[0])
    limit, threshold = ROUTING[between]
    if saving < threshold or added > limit:
        raise ValueError("an alternate airport that does not clear the routing tests is not modelled")
    return (other, [ReasonCode.ALTERNATE_AIRPORT_LOWER_FARE, ReasonCode.COST_SAVINGS, ReasonCode.LOWEST_FARE],
            [Clause.LOWEST_LOGICAL_AIRFARE],
            (f"Lines 456-459: the alternate airport {other[0].segments[-1].destination} saves {saving} cents and "
             f"adds {added} minutes (lines 453-455: limits {threshold} and {limit})."))
