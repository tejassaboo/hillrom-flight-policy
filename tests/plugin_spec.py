"""The handbook-specific settings the template's acceptance tests read. Every other file in tests/ is the
template's and stays identical across plugins (see TEMPLATE_GUIDE.md)."""

from pathlib import Path

import contract

ROOT = Path(__file__).resolve().parents[1]

# Ids that are published or taken: a new plugin never reuses one (MASTER_PLAN section 4, "id check").
PUBLISHED_IDS = {
    "aiib-delegation-entitlement", "ec-mission-cabin-allowance", "ftr-city-pair-fare-selection",
    "gates-vendor-flight-ranking", "njc-cabin-meal-allowance", "sfc-travel-preapproval", "uc-g28-expense-audit",
    "un-staff-air-travel-audit", "vt-airfare-policy-booking", "wa-saam-travel-versioned-audit",
    "energy-corporate-flight-booking", "pharma-distributor-flight-booking", "shipping-company-flight-booking",
    "telecommunications-flight-booking", "preference-aware-flight-booking", "llm-context-compress",
    "weather-alert", "word-check", "arxiv-source",
}

# The frozen original's SHA256SUMS, when this checkout sits beside pilot_work/ (skipped elsewhere).
FROZEN_SHA256SUMS = ROOT.parents[1] / "pilot_work" / "originals" / "hillrom" / "frozen" / "SHA256SUMS"

# Scenario mix by primary category (EDGE_CASES.md section 5.2; the 32-scenario row).
MIX = {"easy": 6, "boundary_twin": 8, "multi_rule": 5, "hidden_clause": 3, "distractor": 3, "refusal": 3, "flag": 4}

# Overlay minimums (EDGE_CASES.md section 5.3) for the rules this handbook has. It has no rule on overnight
# stops, so the overnight multi-leg case is not required.
OVERLAY_MINIMUMS = {
    "multi_leg": 3, "date_arithmetic": 2, "month_end": 1, "personal_travel": 1, "multi_traveller": 1,
    "dearer_option": 2, "upgrade_not_taken": 2, "outside_air_section": 2,
}

# Words a scenario id may not contain beyond the template's universal list: this handbook's rule and role
# terms.
ID_FORBIDDEN_TERMS = {
    "coach", "economy", "business", "premium", "plus", "segment", "spouse", "wife", "husband", "companion", "guest",
    "elt", "executive", "leadership", "vice", "president", "regional", "officer", "ceo", "cfo", "legal", "manager",
    "supervisor", "director", "domestic", "international", "continent", "intercontinental", "mexico", "europe",
    "connection", "nonstop", "routing", "preferred", "vendor", "miles", "loyalty", "status", "refundable", "savings",
    "gatwick", "heathrow", "alternate", "airport", "gambling", "casino", "vegas", "personal", "vacation", "holiday",
    "together", "group", "wifi", "internet", "advance", "approval", "authorization", "agency", "key", "personnel",
}

# The handbook-specific enums whose member words a scenario id may not contain either.
ID_CATEGORY_ENUMS = [contract.Passenger, contract.Purpose, contract.ApprovalSubject]

# How many scenarios a degenerate agent may pass: one that always holds the right offer for approval, and
# one that always books the cheapest seat (with the right section). Set to what each actually passes (README).
MAX_PASS_ALWAYS_FLAG = 2
MAX_PASS_ALWAYS_LOWEST = 12  # README: domestic and authorized bookings whose answer is the lowest fare

# Hand-built duration cases beyond the automatic both-sides tests: (rule, scheduled minutes per flight, layovers,
# expected True / False / None). Every rule is asked per segment (lines 425-426): a connection is over only when
# every segment is, within only when none is, and None when its segments fall on both sides.
DURATION_CASES = [
    ("below-six", [359], [], False),
    ("below-six", [360], [], True),
    ("below-six", [230, 195], [70], False),  # 425 flying minutes, every segment under six hours
    ("below-six", [125, 465], [110], None),  # one segment each side
    ("below-six", [400, 380], [60], True),
    ("above-six", [360], [], False),
    ("above-six", [361], [], True),
    ("above-six", [300, 300], [90], False),  # 600 flying minutes: no segment over six hours
    ("above-six", [361, 90], [60], None),
    ("below-ten", [599], [], False),
    ("below-ten", [600], [], True),
    ("below-ten", [590, 140], [80], False),
    ("above-ten", [600], [], False),
    ("above-ten", [601], [], True),
    ("above-ten", [700, 120], [90], None),
    ("above-ten", [610, 620], [75], True),
]
