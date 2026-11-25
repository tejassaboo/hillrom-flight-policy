"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only.

The first part is the original-handbook template's shared contract and is the same in every plugin made from
it. The HANDBOOK-SPECIFIC part in the middle is filled per handbook: the scenario ids, the closed lists of
approvers and sections, and the trip record; the shared inputs and outputs after it refer to those names.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output

# ---------------------------------------------------------------------------------------------------------
# SHARED (template): keep identical across plugins, except the agent task's id in Task.BOOK_FLIGHT.
# ---------------------------------------------------------------------------------------------------------


class Tool(Enum):
    BOOKING_REQUIREMENTS = "booking_requirements"
    GET_TRIP = "get_trip"
    SEARCH_FLIGHTS = "search_flights"
    SOLVE_BOOKING = "solve_booking"


class Task(Enum):
    BOOKING_REQUIREMENTS = "booking-requirements"
    SEARCH_FLIGHTS = "search-flights"
    BOOK_FLIGHT = "book-hillrom-flight"


class Decision(Enum):
    BOOK = "BOOK"
    REFUSE = "REFUSE"
    FLAG_FOR_APPROVAL = "FLAG_FOR_APPROVAL"


class Cabin(Enum):
    ECONOMY = "ECONOMY"
    PREMIUM_ECONOMY = "PREMIUM_ECONOMY"
    BUSINESS = "BUSINESS"
    FIRST = "FIRST"
    NONE = "NONE"


class ReasonCode(Enum):
    """Why the decision was made. The list is shared by every handbook plugin, so it also holds reasons
    that a given handbook never uses."""

    LOWEST_FARE = "LOWEST_FARE"
    UPGRADE_NOT_ELIGIBLE = "UPGRADE_NOT_ELIGIBLE"
    CLIENT_REIMBURSABLE = "CLIENT_REIMBURSABLE"
    UPGRADE_WITHIN_FARE_MARGIN = "UPGRADE_WITHIN_FARE_MARGIN"
    MEDICAL_NEED = "MEDICAL_NEED"
    COST_SAVINGS = "COST_SAVINGS"
    NO_ECONOMY_SEATS_URGENT = "NO_ECONOMY_SEATS_URGENT"
    TRAVELER_PAYS_UPGRADE = "TRAVELER_PAYS_UPGRADE"
    LONG_FLIGHT_APPROVED = "LONG_FLIGHT_APPROVED"
    LONG_FLIGHT_CONDITION_NOT_MET = "LONG_FLIGHT_CONDITION_NOT_MET"
    PREMIUM_ECONOMY_ALLOWED = "PREMIUM_ECONOMY_ALLOWED"
    UPGRADE_COST_NOT_NOMINAL = "UPGRADE_COST_NOT_NOMINAL"
    ALTERNATE_ROUTE_WITHIN_MARGIN = "ALTERNATE_ROUTE_WITHIN_MARGIN"
    ALTERNATE_ROUTE_TOO_EXPENSIVE = "ALTERNATE_ROUTE_TOO_EXPENSIVE"
    LOYALTY_PROGRAM_PREFERENCE = "LOYALTY_PROGRAM_PREFERENCE"
    COMPANION_NOT_COVERED = "COMPANION_NOT_COVERED"
    PERSONAL_TRAVEL_NOT_COVERED = "PERSONAL_TRAVEL_NOT_COVERED"
    OUTSIDE_POLICY_SCOPE = "OUTSIDE_POLICY_SCOPE"
    NO_COMPLIANT_OFFER = "NO_COMPLIANT_OFFER"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"
    UNCLEAR_POLICY_TEXT = "UNCLEAR_POLICY_TEXT"
    ADVANCE_PURCHASE_TOO_LATE = "ADVANCE_PURCHASE_TOO_LATE"
    DISTANCE_BELOW_MINIMUM = "DISTANCE_BELOW_MINIMUM"
    DRIVING_EXPECTED = "DRIVING_EXPECTED"
    RAIL_PREFERRED = "RAIL_PREFERRED"
    REFUNDABLE_FARE_NOT_ALLOWED = "REFUNDABLE_FARE_NOT_ALLOWED"
    PREFERRED_CARRIER_REQUIRED = "PREFERRED_CARRIER_REQUIRED"
    CONNECTION_TOO_LONG = "CONNECTION_TOO_LONG"
    OVERNIGHT_STOP_REQUIRED = "OVERNIGHT_STOP_REQUIRED"
    NATIONAL_CARRIER_REQUIRED = "NATIONAL_CARRIER_REQUIRED"
    SENIOR_ROLE_ENTITLEMENT = "SENIOR_ROLE_ENTITLEMENT"
    INTERNATIONAL_LONG_FLIGHT = "INTERNATIONAL_LONG_FLIGHT"
    TRAVELLER_LIMIT_PER_FLIGHT = "TRAVELLER_LIMIT_PER_FLIGHT"
    # HANDBOOK-SPECIFIC reason codes go below this line; keep every shared one above.
    SEGMENT_CLASS_ENTITLEMENT = "SEGMENT_CLASS_ENTITLEMENT"
    SAVINGS_BELOW_THRESHOLD = "SAVINGS_BELOW_THRESHOLD"
    REFUNDABLE_WITHIN_MARGIN = "REFUNDABLE_WITHIN_MARGIN"
    ALTERNATE_AIRPORT_LOWER_FARE = "ALTERNATE_AIRPORT_LOWER_FARE"
    INTERCONTINENTAL_PRE_APPROVAL = "INTERCONTINENTAL_PRE_APPROVAL"
    KEY_OFFICERS_TOGETHER = "KEY_OFFICERS_TOGETHER"
    ELT_MEMBERS_TOGETHER = "ELT_MEMBERS_TOGETHER"
    COMPANION_BUSINESS_PURPOSE_APPROVED = "COMPANION_BUSINESS_PURPOSE_APPROVED"
    GAMBLING_TRIP_NOT_PERMITTED = "GAMBLING_TRIP_NOT_PERMITTED"
    NO_SEATS_IN_PERMITTED_CLASS = "NO_SEATS_IN_PERMITTED_CLASS"
    UPGRADE_NO_ADDITIONAL_COST = "UPGRADE_NO_ADDITIONAL_COST"
    # Decoys: codes for rules of other handbooks that this one lacks, so the list hints at none of its own rules.
    WEEKEND_TRAVEL_HOME = "WEEKEND_TRAVEL_HOME"
    WEEKEND_TRIP_NOT_EARNED = "WEEKEND_TRIP_NOT_EARNED"
    NEXT_OF_KIN_TRAVEL = "NEXT_OF_KIN_TRAVEL"
    FLY_AMERICA_US_CARRIER_REQUIRED = "FLY_AMERICA_US_CARRIER_REQUIRED"
    OPEN_SKIES_AGREEMENT = "OPEN_SKIES_AGREEMENT"
    CREATIVE_TICKETING = "CREATIVE_TICKETING"
    EXTENDED_TRAVEL_SAVINGS = "EXTENDED_TRAVEL_SAVINGS"
    DENIED_BOARDING_NOT_ALLOWED = "DENIED_BOARDING_NOT_ALLOWED"
    CHANCELLOR_WRITTEN_AUTHORIZATION = "CHANCELLOR_WRITTEN_AUTHORIZATION"
    DOUBLE_BOOKING_PROHIBITED = "DOUBLE_BOOKING_PROHIBITED"
    PRIVATE_AIRCRAFT_NOT_APPROVED = "PRIVATE_AIRCRAFT_NOT_APPROVED"
    SAME_CLASS_AS_CUSTOMER = "SAME_CLASS_AS_CUSTOMER"


class TripType(Enum):
    ONE_WAY = "ONE_WAY"
    ROUND_TRIP = "ROUND_TRIP"


class Topic(Enum):
    ALL = "ALL"
    FIELDS = "FIELDS"
    AIRPORTS = "AIRPORTS"


CODE = "An IATA airport code, e.g. JFK"


@dataclass
class Airport(Output):
    code: Annotated[str, CODE]
    name: Annotated[str, "The airport's name"]
    city: Annotated[str, "The city it serves"]
    country: Annotated[str, "Its country, as an ISO code"]


@dataclass
class Segment(Output):
    flight_number: Annotated[str, "The airline's flight number, e.g. BA 117"]
    origin: Annotated[str, CODE]
    destination: Annotated[str, CODE]
    depart_local: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, local time at that airport"]
    arrive_local: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, local time at that airport"]
    depart_utc: Annotated[str, "When it leaves: YYYY-MM-DD HH:MM, UTC"]
    arrive_utc: Annotated[str, "When it lands: YYYY-MM-DD HH:MM, UTC"]
    scheduled_minutes: Annotated[int, "Its scheduled time from departure to arrival, in minutes"]


@dataclass
class Offer(Output):
    offer_id: Annotated[str, "The offer's id, to submit when booking or holding it"]
    carrier: Annotated[str, "The airline"]
    trip_type: Annotated[TripType, "ONE_WAY, or ROUND_TRIP when the fare covers the flights out and back"]
    cabin: Annotated[Cabin, "The cabin sold on every flight of the offer"]
    fare_cents: Annotated[int, "The whole fare for one passenger, in cents of the search's currency"]
    seats_available: Annotated[bool, "False when this cabin is sold out on these flights: it is listed but cannot be bought"]
    refundable: Annotated[bool, "Whether the fare can be refunded or changed without a fee"]
    stops: Annotated[int, "Connections on the way out; zero for a nonstop"]
    segments: Annotated[list[Segment], "The flights out, in order"]
    layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights out"]
    stopover_nights: Annotated[list[bool], "Per connection out: true when it is a ticketed stopover with a hotel night booked"]
    flying_minutes: Annotated[int, "The flights' scheduled minutes out added together, ground time left out"]
    elapsed_minutes: Annotated[int, "Minutes from the first departure out to the last arrival, ground time included"]
    return_segments: Annotated[list[Segment], "For a round trip, the flights back, in order; empty otherwise"]
    return_layover_minutes: Annotated[list[int], "Minutes on the ground between consecutive flights back"]
    return_stopover_nights: Annotated[list[bool], "Per connection back: true for a ticketed stopover with a hotel night"]
    return_flying_minutes: Annotated[int, "The flights' scheduled minutes back added together; zero one way"]
    return_elapsed_minutes: Annotated[int, "Minutes from the first departure back to the last arrival; zero one way"]


# ---------------------------------------------------------------------------------------------------------
# HANDBOOK-SPECIFIC: Hill-Rom Holdings, Global Travel, Meeting & Expense Policy (Corporate Policy 1016).
# ---------------------------------------------------------------------------------------------------------


class Scenario(Enum):
    ALDER_BIGHT = "alder-bight"
    ASTER_FOLD = "aster-fold"
    BITTERN_HYTHE = "bittern-hythe"
    BRAMBLE_TOR = "bramble-tor"
    CINDER_FELL = "cinder-fell"
    CORRIE_WYND = "corrie-wynd"
    DRUMLIN_SEDGE = "drumlin-sedge"
    DUNLIN_ESKER = "dunlin-esker"
    EGRET_SHALE = "egret-shale"
    EIDER_RIGG = "eider-rigg"
    FERNWICK_COVE = "fernwick-cove"
    FINCH_HOLT = "finch-holt"
    GANNET_SILL = "gannet-sill"
    GORSE_HAVEN = "gorse-haven"
    HEATHER_KNAP = "heather-knap"
    IRIS_COMBE = "iris-combe"
    JACKDAW_SCAR = "jackdaw-scar"
    KITTIWAKE_HOLM = "kittiwake-holm"
    LUPIN_WOLD = "lupin-wold"
    MALLOW_CRAG = "mallow-crag"
    NETTLE_BRAE = "nettle-brae"
    OSPREY_DENE = "osprey-dene"
    PLOVER_GHYLL = "plover-ghyll"
    QUINCE_FIRTH = "quince-firth"
    ROWAN_SKERRY = "rowan-skerry"
    SORREL_HAUGH = "sorrel-haugh"
    THISTLE_MORAINE = "thistle-moraine"
    UMBER_CARSE = "umber-carse"
    VETCH_LINN = "vetch-linn"
    WREN_SCAUR = "wren-scaur"
    YEW_STRAND = "yew-strand"
    ZEPHYR_MIRE = "zephyr-mire"


class Approver(Enum):
    """Roles that may sign off. NONE: the decision relies on no one's sign-off, given or awaited (one for
    something else may be on file). NOT_NAMED: one is needed, but the handbook names no role."""

    NONE = "NONE"
    NOT_NAMED = "NOT_NAMED"
    SUPERVISOR = "SUPERVISOR"
    ELT_REPRESENTATIVE = "ELT_REPRESENTATIVE"
    REGIONAL_PRESIDENT = "REGIONAL_PRESIDENT"
    ELT_MEMBER = "ELT_MEMBER"
    CEO = "CEO"
    GLOBAL_TRAVEL = "GLOBAL_TRAVEL"
    CORPORATE_CONTROLLER = "CORPORATE_CONTROLLER"
    GLOBAL_COMPLIANCE_OFFICE = "GLOBAL_COMPLIANCE_OFFICE"
    FINANCE_LEADER = "FINANCE_LEADER"
    CFO = "CFO"
    VICE_PRESIDENT = "VICE_PRESIDENT"
    DEPARTMENT_HEAD = "DEPARTMENT_HEAD"
    HUMAN_RESOURCES = "HUMAN_RESOURCES"
    TRAVEL_AGENCY = "TRAVEL_AGENCY"


class Clause(Enum):
    """The handbook's sections, by heading."""

    PURPOSE = "PURPOSE"
    SCOPE = "SCOPE"
    RESPONSIBILITY = "RESPONSIBILITY"
    GENERAL_INFORMATION = "GENERAL_INFORMATION"
    TRAVEL_CARD = "TRAVEL_CARD"
    ALTERNATIVES_TO_TRAVEL = "ALTERNATIVES_TO_TRAVEL"
    INTERNATIONAL_PRE_APPROVAL = "INTERNATIONAL_PRE_APPROVAL"
    POLICY_VIOLATIONS = "POLICY_VIOLATIONS"
    TRAVEL_AGENCIES = "TRAVEL_AGENCIES"
    PREFERRED_VENDORS = "PREFERRED_VENDORS"
    ADDITIONAL_GUIDELINES = "ADDITIONAL_GUIDELINES"
    SPOUSE_COMPANION = "SPOUSE_COMPANION"
    AIR_TRAVEL = "AIR_TRAVEL"
    CLASS_OF_SERVICE = "CLASS_OF_SERVICE"
    LOWEST_LOGICAL_AIRFARE = "LOWEST_LOGICAL_AIRFARE"
    FREQUENT_FLYER = "FREQUENT_FLYER"
    CHANGES_CANCELLATION = "CHANGES_CANCELLATION"
    KEY_PERSONNEL = "KEY_PERSONNEL"
    GROUND_TRANSPORTATION = "GROUND_TRANSPORTATION"
    PERSONAL_VEHICLE = "PERSONAL_VEHICLE"
    RAIL_CLASS = "RAIL_CLASS"
    LODGING = "LODGING"
    MEETING_COMPANION = "MEETING_COMPANION"
    MEALS = "MEALS"
    INTERNET = "INTERNET"
    LUGGAGE = "LUGGAGE"
    NON_REIMBURSABLE = "NON_REIMBURSABLE"


class Passenger(Enum):
    EMPLOYEE = "EMPLOYEE"
    SPOUSE_OR_COMPANION = "SPOUSE_OR_COMPANION"


class Purpose(Enum):
    CUSTOMER_VISIT = "CUSTOMER_VISIT"
    INTERNAL_MEETING = "INTERNAL_MEETING"
    TRAINING = "TRAINING"
    TRADE_SHOW = "TRADE_SHOW"
    BOARD_MEETING = "BOARD_MEETING"
    CUSTOMER_EVENT = "CUSTOMER_EVENT"
    ENTERTAINMENT = "ENTERTAINMENT"
    PERSONAL = "PERSONAL"


class ApprovalSubject(Enum):
    TRIP = "TRIP"
    COMPANION_TICKET = "COMPANION_TICKET"
    SHARED_FLIGHT = "SHARED_FLIGHT"
    CABIN = "CABIN"


@dataclass
class Approval(Output):
    approver_name: Annotated[str, "Who gave it"]
    approver_title: Annotated[str, "Their job title"]
    subject: Annotated[ApprovalSubject, "What it covers"]
    in_writing: Annotated[bool, "True when it is on file as an email or signed document; false when it was only said"]
    given_on: Annotated[str, "The day it was given, YYYY-MM-DD"]


@dataclass
class Colleague(Output):
    name: Annotated[str, "Their name"]
    title: Annotated[str, "Their job title"]
    elt_member: Annotated[bool, "Whether they sit on the company's ELT"]
    flights: Annotated[list[str], "The flight numbers they are already booked on for this trip"]


@dataclass
class Trip(Output):
    traveller_name: Annotated[str, "Who flies"]
    traveller_title: Annotated[str, "Their job title, or their relation to the employee they go with"]
    elt_member: Annotated[bool, "Whether the person flying sits on the company's ELT"]
    passenger: Annotated[Passenger, "What the person flying is to the company"]
    accompanies: Annotated[str, "For a spouse or companion, the employee they go with, by name and title; empty otherwise"]
    home_country: Annotated[str, "The country the employee is based in, as an ISO code"]
    elt_representative: Annotated[str, "The name of the ELT member over the employee's part of the company"]
    supervisor: Annotated[str, "The employee's own manager, by name and title"]
    origin: Annotated[Airport, "Where the flight leaves from"]
    destination: Annotated[Airport, "Where the traveller has to be"]
    travel_date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport"]
    return_date: Annotated[str, "For a round-trip ticket, the day to fly back, YYYY-MM-DD; empty for one way"]
    booking_date: Annotated[str, "Today in this world, the day the ticket is bought, YYYY-MM-DD"]
    purpose: Annotated[str, "Why the trip is made, in plain words"]
    purpose_kind: Annotated[Purpose, "The kind of trip"]
    requested_cabin: Annotated[Cabin, "The cabin the traveller asks for"]
    prefers_nonstop: Annotated[bool, "Whether the traveller asks for a nonstop flight"]
    requested_refundable: Annotated[bool, "Whether the traveller asks for a fare that can be refunded"]
    requested_airline: Annotated[str, "An airline the traveller asks for by name; empty when none"]
    requested_airline_why: Annotated[str, "The traveller's reason for asking for that airline; empty when none"]
    preferred_airlines: Annotated[list[str], "Airlines with negotiated company rates, by name; empty when none are on file"]
    companion_business_purpose: Annotated[
        str, "For a spouse or companion, the business reason on file for them to come; empty when none is on file"
    ]
    approvals: Annotated[list[Approval], "Sign-offs on file for this trip"]
    colleagues: Annotated[list[Colleague], "Other employees going to the same event, with the flights they are booked on"]
    notes: Annotated[list[str], "Other facts on file for this trip"]


# ---------------------------------------------------------------------------------------------------------
# SHARED (template), continued: the tools' and tasks' inputs and outputs.
# ---------------------------------------------------------------------------------------------------------


@dataclass
class TaskInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    request: Annotated[str, "The traveller's request, in their own words"]


@dataclass
class TripInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id, as the task input gives it"]


@dataclass
class TripOutput(Output):
    scenario: Annotated[Scenario, "The case id"]
    request: Annotated[str, "The traveller's request, in their own words"]
    trip: Annotated[Trip, "The trip record behind the request"]


@dataclass
class SearchInput(Output):
    scenario: Annotated[Scenario, "The booking request's case id"]
    origin: Annotated[str, "The airport to leave from: An IATA airport code, e.g. JFK"]
    destination: Annotated[str, "The airport to fly to: An IATA airport code, e.g. JFK"]
    date: Annotated[str, "The day to leave, YYYY-MM-DD: the local date at the origin airport, on or after the booking date"]
    return_date: Annotated[str, "For round-trip fares, the day to fly back, YYYY-MM-DD, local at the destination; empty for one way"]


@dataclass
class SearchOutput(Output):
    note: Annotated[str, "Where the offers come from, and a word when this case lists none for the search"]
    currency: Annotated[str, "The currency of every fare, as an ISO code"]
    offers: Annotated[list[Offer], "Every offer leaving on that local date, in departure order"]


@dataclass
class BookingOutput(Output):
    decision: Annotated[
        Decision,
        "BOOK: buy offer_id now. REFUSE: buy nothing, because the organisation buys no ticket at all for this request. "
        "FLAG_FOR_APPROVAL: hold offer_id and buy nothing yet, because someone must approve it first or "
        "the handbook's words leave the answer open",
    ]
    offer_id: Annotated[str, "The offer bought or held, exactly as search_flights listed it; empty when refusing"]
    cabin: Annotated[Cabin, "That offer's cabin; NONE when refusing"]
    reason_code: Annotated[ReasonCode, "Why, from the closed list"]
    approver: Annotated[
        Approver,
        "The role whose sign-off this decision relies on, whether already on file or still awaited; NONE when "
        "this decision relies on no one's sign-off, even if a sign-off for something else is on file; NOT_NAMED "
        "when a sign-off is needed but the handbook names no role",
    ]
    clause: Annotated[Clause, "The handbook section the decision rests on"]


@dataclass
class SolveOutput(Output):
    trip: Annotated[Trip, "The trip record"]
    offers: Annotated[list[Offer], "Every offer on the trip's route and date"]
    decision: Annotated[Decision, "The correct decision"]
    offer_ids: Annotated[list[str], "Every offer id that is a correct choice; empty when refusing"]
    cabins: Annotated[list[Cabin], "Every correct cabin"]
    reason_codes: Annotated[list[ReasonCode], "Every accepted reason"]
    approvers: Annotated[list[Approver], "Every accepted approver"]
    clauses: Annotated[list[Clause], "Every accepted section"]
    unclear_phrase: Annotated[str, "For a hold over unclear words, those words; empty otherwise"]
    explanation: Annotated[str, "How the answer key reached the answer"]


@dataclass
class FieldHelp(Output):
    name: Annotated[str, "The trip record field's name"]
    kind: Annotated[str, "Its type"]
    description: Annotated[str, "What it means"]


@dataclass
class RequirementsInput(Output):
    topic: Annotated[Topic, "ALL for everything, FIELDS for the trip record's fields, AIRPORTS for the airport list"]


@dataclass
class RequirementsOutput(Output):
    fields: Annotated[list[FieldHelp], "The trip record's fields; empty for AIRPORTS"]
    conventions: Annotated[list[str], "How times, dates, fares and seats work in this world; empty for AIRPORTS"]
    airports: Annotated[list[Airport], "The airports the simulated world knows; empty for FIELDS"]


TOOLS = {
    Tool.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Tool.GET_TRIP: (TripInput, TripOutput),
    Tool.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Tool.SOLVE_BOOKING: (TaskInput, SolveOutput),
}
TASKS = {
    Task.BOOKING_REQUIREMENTS: (RequirementsInput, RequirementsOutput),
    Task.SEARCH_FLIGHTS: (SearchInput, SearchOutput),
    Task.BOOK_FLIGHT: (TaskInput, BookingOutput),
}
