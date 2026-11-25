# Hill-Rom Global Travel Flight Policy

**No affiliation with Hill-Rom (Hillrom).** The handbook is Hill-Rom Holdings' public *Global Travel, Meeting &
Expense Policy* (Corporate Policy 1016, effective June 1, 2021), bundled verbatim for research. It is a corporate
handbook: do not publish this plugin before the course staff confirm that a verbatim corporate handbook may be
redistributed (MASTER_PLAN section 4).

A `nanoagent.plugin/v0001` plugin. An agent handles one traveller's flight request under the company's real
travel policy: it reads the trip record, searches a simulated flight world and submits **BOOK**, **REFUSE** or
**FLAG_FOR_APPROVAL** with the offer, cabin, reason, approver and handbook section. A deterministic Python
verifier, with no LLM, rebuilds the offers and the handbook's answer itself and checks every field. Built from
the original-handbook template (`handbook_plugins/_template`); `tests/build_scenarios.py` writes the scenario
files (the JSON files are the truth).

## The handbook and the harness flag

The frozen text (`src/plugin/data/policy.txt`, 12,518 words, 1,288 lines, sha256 `ce8a8582...c4a20b05`, equal to
`pilot_work/originals/hillrom/frozen/SHA256SUMS`) is never paraphrased, and the task text restates no rule. Under
stock NanoAgent the agent does not see it: the plugin then runs as the `off` baseline. The `harness.policy`
switch of the NanoAgent fork (github.com/tejassaboo/nanoagent, branch `policy-switch`) adds it to the system
prompt: `harness.policy: full` adds all of it, and the selection methods add parts of it. These plugins are meant
to run with `query: instructions+input`, so a selector sees the traveller's request.

**Flight duration, as this handbook defines it.** The only duration clause is the class table of section 3.1
(lines 424-435): "Class of service is predicated upon the length of individual flight segment and position in the
Company", with columns "< 6 hours", "> 6 hours and < 10 hours" and "> 10 hours". It is measured per segment
(legs never added, layovers never counted), and coded as four comparisons (`rules.DURATION_RULES`, `rules.over`):
not under six hours from 360 minutes, over six hours from 361, not under ten hours from 600, over ten hours from
601. A segment of exactly 360 or 600 minutes is in no column. That gap matters only where the two columns beside it
differ for the traveller's row: a Vice President at 360 minutes (coach or business: `dunlin-esker`) and an
"all other employees" traveller at 600 minutes (coach or premium coach: `eider-rigg`). Each is a flag with clear
twins at 359/361 and 599/601 minutes, never a boundary twin. An ELT member flies business in every column.

**Size.** At 1.33 tokens a word the handbook is about 16,650 tokens (about 20,500 at 4 characters a token). Under
`full` the first call carries about 18,400 input tokens (handbook, task instructions, tool and submit schemas
about 1,700, the request); the trip record adds about 300 tokens and a search about 650 (up to 1,060 for the two
London searches of `umber-carse`). A run makes 3 calls (`get_trip`, `search_flights`, `submit`): about 56,600
input tokens, under the hosted cap of 65,536 with about 9,000 tokens of margin for output. `umber-carse`, whose
answer needs a second search (Gatwick), makes 4 calls, about 77,000 input tokens, and crosses the cap, as does any
run that adds an extra search. At 4 characters a token for the handbook too, 3-call runs are about 68,000 and cross
the cap: run `full` locally with a raised cap.

## Task

- **Input:** `TaskInput`: `scenario` (one of 32 case ids) and `request`, the traveller's own words.
- **Steps:** `get_trip`, then `search_flights` on each route and date the decision needs (one search for every case
  but `umber-carse`, which needs the alternate London airport its trip record names too; the round-trip cases search with the record's
  return date), then `submit`.
- **Output:** `BookingOutput`: `decision`, `offer_id` (empty when refusing), `cabin` (`NONE` when refusing;
  otherwise the chosen offer's own cabin), `reason_code`, `approver` and `clause`, each from a closed list. The
  reason list is the template's shared list plus 11 Hill-Rom codes (`SEGMENT_CLASS_ENTITLEMENT`,
  `SAVINGS_BELOW_THRESHOLD`, `REFUNDABLE_WITHIN_MARGIN`, `ALTERNATE_AIRPORT_LOWER_FARE`,
  `INTERCONTINENTAL_PRE_APPROVAL`, `KEY_OFFICERS_TOGETHER`, `ELT_MEMBERS_TOGETHER`,
  `COMPANION_BUSINESS_PURPOSE_APPROVED`, `GAMBLING_TRIP_NOT_PERMITTED`, `NO_SEATS_IN_PERMITTED_CLASS`,
  `UPGRADE_NO_ADDITIONAL_COST`; no scenario expects the last three, which stand for rules the cases do not test,
  and `ELT_MEMBERS_TOGETHER` is the distractor `zephyr-mire`'s untriggered limit), plus decoy codes from other
  handbooks' rules (weekend trips home, Fly America, creative ticketing and others). Fares are in cents of US
  dollars (`currency: USD`).
- **Success:** every field is one the answer key accepts. Score = fields right / 6.
- **Hidden facts:** none (`answer_key_inputs` is unused). Who is on the ELT, the traveller's ELT representative and
  the colleagues already booked (with flight numbers) are in the trip record.

| Scenario | Category | Expected decision (offer; cabin) | Reason | Approver | Clause (frozen lines) |
|---|---|---|---|---|---|
| `alder-bight` | easy | BOOK (ua-economy; ECONOMY) | LOWEST_FARE or PREFERRED_CARRIER_REQUIRED | NONE | AIR_TRAVEL or LOWEST_LOGICAL_AIRFARE or PREFERRED_VENDORS (290-291, 400-401, 424-435, 425-426) |
| `bramble-tor` | easy | BOOK (aa-business; BUSINESS) | SEGMENT_CLASS_ENTITLEMENT or SENIOR_ROLE_ENTITLEMENT | NONE | CLASS_OF_SERVICE (424-435) |
| `cinder-fell` | easy | BOOK (lh-economy; ECONOMY) | LOWEST_FARE | ELT_REPRESENTATIVE or NONE | AIR_TRAVEL or CLASS_OF_SERVICE or INTERNATIONAL_PRE_APPROVAL or LOWEST_LOGICAL_AIRFARE (288-290, 424-435, 425-426) |
| `drumlin-sedge` | easy | BOOK (ua-economy; ECONOMY) | LOWEST_FARE | NONE | AIR_TRAVEL or CLASS_OF_SERVICE or LOWEST_LOGICAL_AIRFARE (424-435, 425-426) |
| `egret-shale` | easy | BOOK (aa-economy; ECONOMY) | LOWEST_FARE | NONE or REGIONAL_PRESIDENT | AIR_TRAVEL or CLASS_OF_SERVICE or INTERNATIONAL_PRE_APPROVAL or LOWEST_LOGICAL_AIRFARE (288-290, 424-435, 425-426) |
| `fernwick-cove` | easy | BOOK (lh-economy; ECONOMY) | LOWEST_FARE | NONE | AIR_TRAVEL or CLASS_OF_SERVICE or INTERNATIONAL_PRE_APPROVAL or LOWEST_LOGICAL_AIRFARE (290-291, 424-435, 425-426) |
| `gannet-sill` | boundary_twin | BOOK (dl-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or SEGMENT_CLASS_ENTITLEMENT or UPGRADE_NOT_ELIGIBLE | NONE | CLASS_OF_SERVICE (424-435) |
| `heather-knap` | boundary_twin | BOOK (dl-business; BUSINESS) | SEGMENT_CLASS_ENTITLEMENT or SENIOR_ROLE_ENTITLEMENT | NONE | CLASS_OF_SERVICE (424-435) |
| `iris-combe` | boundary_twin | BOOK (ua-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or SEGMENT_CLASS_ENTITLEMENT or UPGRADE_NOT_ELIGIBLE | ELT_REPRESENTATIVE or NONE | CLASS_OF_SERVICE or INTERNATIONAL_PRE_APPROVAL (288-290, 424-435) |
| `jackdaw-scar` | boundary_twin | BOOK (ua-premium; PREMIUM_ECONOMY) | PREMIUM_ECONOMY_ALLOWED or SEGMENT_CLASS_ENTITLEMENT | ELT_REPRESENTATIVE or NONE | CLASS_OF_SERVICE or INTERNATIONAL_PRE_APPROVAL (288-290, 424-435) |
| `kittiwake-holm` | boundary_twin | BOOK (connection-economy; ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or ALTERNATE_ROUTE_WITHIN_MARGIN or COST_SAVINGS or LOWEST_FARE | NONE | LOWEST_LOGICAL_AIRFARE (425-426, 438-445) |
| `lupin-wold` | boundary_twin | BOOK (nonstop-economy; ECONOMY) | ALTERNATE_ROUTE_WITHIN_MARGIN or SAVINGS_BELOW_THRESHOLD | NONE | LOWEST_LOGICAL_AIRFARE (425-426, 438-445) |
| `mallow-crag` | boundary_twin | BOOK (ua-flex; ECONOMY) | REFUNDABLE_WITHIN_MARGIN | NONE | LOWEST_LOGICAL_AIRFARE (425-426, 446) |
| `nettle-brae` | boundary_twin | BOOK (ua-saver; ECONOMY) | REFUNDABLE_FARE_NOT_ALLOWED | NONE | LOWEST_LOGICAL_AIRFARE (425-426, 446) |
| `osprey-dene` | multi_rule | BOOK (aa-economy; ECONOMY) | KEY_OFFICERS_TOGETHER or TRAVELLER_LIMIT_PER_FLIGHT | NONE | KEY_PERSONNEL (424-435, 490-494) |
| `plover-ghyll` | multi_rule | BOOK (ua-economy; ECONOMY) | LOWEST_FARE | NONE | AIR_TRAVEL or CLASS_OF_SERVICE or KEY_PERSONNEL or LOWEST_LOGICAL_AIRFARE (424-435, 425-426, 490-494) |
| `quince-firth` | multi_rule | BOOK (connection-economy; ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or ALTERNATE_ROUTE_WITHIN_MARGIN or COST_SAVINGS or LOWEST_FARE | NONE | INTERNATIONAL_PRE_APPROVAL or LOWEST_LOGICAL_AIRFARE (288-290, 290-291, 438-445) |
| `rowan-skerry` | multi_rule | BOOK (connection-economy; ECONOMY) | ALTERNATE_ROUTE_TOO_EXPENSIVE or ALTERNATE_ROUTE_WITHIN_MARGIN or COST_SAVINGS or LOWEST_FARE | ELT_REPRESENTATIVE or NONE | INTERNATIONAL_PRE_APPROVAL or LOWEST_LOGICAL_AIRFARE (288-290, 424-435, 451-455) |
| `sorrel-haugh` | multi_rule | BOOK (wn-economy; ECONOMY) | COMPANION_BUSINESS_PURPOSE_APPROVED or LOWEST_FARE | ELT_MEMBER or ELT_REPRESENTATIVE or NONE | LOWEST_LOGICAL_AIRFARE or MEETING_COMPANION or SPOUSE_COMPANION (356-361, 865-867) |
| `thistle-moraine` | hidden_clause | BOOK (as-economy; ECONOMY) | LONG_FLIGHT_CONDITION_NOT_MET or SEGMENT_CLASS_ENTITLEMENT or UPGRADE_NOT_ELIGIBLE | NONE | CLASS_OF_SERVICE (424-435) |
| `umber-carse` | hidden_clause | BOOK (lgw-ba-business; BUSINESS) | ALTERNATE_AIRPORT_LOWER_FARE or COST_SAVINGS or SEGMENT_CLASS_ENTITLEMENT or SENIOR_ROLE_ENTITLEMENT | NONE or REGIONAL_PRESIDENT | CLASS_OF_SERVICE or INTERNATIONAL_PRE_APPROVAL or LOWEST_LOGICAL_AIRFARE (288-290, 424-435, 451-455, 456-459) |
| `vetch-linn` | hidden_clause | BOOK (ua-economy; ECONOMY) | LOYALTY_PROGRAM_PREFERENCE or PREFERRED_CARRIER_REQUIRED | NONE | AIR_TRAVEL or FREQUENT_FLYER or LOWEST_LOGICAL_AIRFARE or PREFERRED_VENDORS (331-332, 400-401, 461-464) |
| `wren-scaur` | distractor | BOOK (aa-economy; ECONOMY) | LOWEST_FARE or LOYALTY_PROGRAM_PREFERENCE | NONE | AIR_TRAVEL or FREQUENT_FLYER or LOWEST_LOGICAL_AIRFARE or PREFERRED_VENDORS (331-332, 400-401, 425-426) |
| `yew-strand` | distractor | BOOK (dl-economy; ECONOMY) | SEGMENT_CLASS_ENTITLEMENT or UPGRADE_NOT_ELIGIBLE | NONE | CLASS_OF_SERVICE (424-435, 449-450) |
| `zephyr-mire` | distractor | BOOK (ua-economy; ECONOMY) | LOWEST_FARE | NONE | AIR_TRAVEL or CLASS_OF_SERVICE or KEY_PERSONNEL or LOWEST_LOGICAL_AIRFARE (424-435, 425-426, 490-494) |
| `aster-fold` | refusal | REFUSE (none; NONE) | COMPANION_NOT_COVERED or PERSONAL_TRAVEL_NOT_COVERED | NONE | MEETING_COMPANION or NON_REIMBURSABLE or SPOUSE_COMPANION (356-361, 363-365, 1281) |
| `bittern-hythe` | refusal | REFUSE (none; NONE) | GAMBLING_TRIP_NOT_PERMITTED or OUTSIDE_POLICY_SCOPE | NONE | ADDITIONAL_GUIDELINES (343-345) |
| `corrie-wynd` | refusal | REFUSE (none; NONE) | OUTSIDE_POLICY_SCOPE or PERSONAL_TRAVEL_NOT_COVERED | NONE | NON_REIMBURSABLE or PURPOSE or SCOPE (145-146, 1237, 1250-1251) |
| `dunlin-esker` | flag | FLAG_FOR_APPROVAL (dl-business, dl-economy; BUSINESS or ECONOMY) | APPROVAL_REQUIRED or UNCLEAR_POLICY_TEXT | CORPORATE_CONTROLLER or GLOBAL_TRAVEL or NOT_NAMED or SUPERVISOR | CLASS_OF_SERVICE or RESPONSIBILITY (159-160, 424-435) |
| `eider-rigg` | flag | FLAG_FOR_APPROVAL (ua-economy, ua-premium; ECONOMY or PREMIUM_ECONOMY) | APPROVAL_REQUIRED or UNCLEAR_POLICY_TEXT | CORPORATE_CONTROLLER or GLOBAL_TRAVEL or NOT_NAMED or SUPERVISOR | CLASS_OF_SERVICE or RESPONSIBILITY (159-160, 288-290, 424-435) |
| `finch-holt` | flag | FLAG_FOR_APPROVAL (lh-economy; ECONOMY) | APPROVAL_REQUIRED or INTERCONTINENTAL_PRE_APPROVAL | ELT_REPRESENTATIVE or REGIONAL_PRESIDENT | INTERNATIONAL_PRE_APPROVAL (288-290, 424-435, 425-426) |
| `gorse-haven` | flag | FLAG_FOR_APPROVAL (ua-economy; ECONOMY) | APPROVAL_REQUIRED or KEY_OFFICERS_TOGETHER or TRAVELLER_LIMIT_PER_FLIGHT | CEO | KEY_PERSONNEL (424-435, 490-494) |

Mix (EDGE_CASES.md 5.2, 32-scenario row): 6 easy, 8 boundary twins, 5 multi-rule, 3 hidden clause or synonym, 3
distractor, 3 refusal, 4 flags (12.5%; the 15% cap is 4). Boundary twins: a Vice President's nonstop at 359 or 361
minutes (`gannet-sill`, `heather-knap`); a Director's at 599 or 601 (`iris-combe`, `jackdaw-scar`); a one-stop
round trip saving 25000 or 24900 cents ("at least $250", `kittiwake-holm`, `lupin-wold`); a refundable fare 14900
or 15000 cents dearer ("less than $150", `mallow-crag`, `nettle-brae`). The other numeric rules have twins in other
categories: the preferred airline at an equal fare or 100 cents dearer (`vetch-linn`, `wren-scaur`) and two or
three named officers on one flight (`plover-ghyll`, `osprey-dene`); the between-continents tests (three hours,
$1,000) are met in `rowan-skerry` and `umber-carse`, and the within-continent ones applied to Mexico in
`quince-firth`. Flags: the two table gaps (`dunlin-esker`, `eider-rigg`, unclear words, held for the
manager/supervisor or the Manager of Global Travel, lines 159-160), a trip between continents with only the
supervisor's sign-off (`finch-holt`: approval required from the ELT representative or a Regional President; twins
`cinder-fell` and `quince-firth`) and a third named officer on the only flight (`gorse-haven`: the CEO's advance
approval, lines 490-491; twins `plover-ghyll` and `osprey-dene`).

Accepted approvers (template amendment 4'): a BOOK whose needed sign-off is on file (the ELT representative's or a
Regional President's authorization of a trip between continents; the ELT member's approval of a companion) accepts
that role and `NONE`; a hold awaiting a sign-off accepts only the awaited roles; bookings within a continent rely on
no sign-off (line 290-291) and accept `NONE`. The supervisor's sign-off in `finch-holt` is what that case tests,
so `SUPERVISOR` is not accepted there. Degenerate agents: one that always holds the right offer as unclear passes
the 2 gap flags; one that always books the cheapest seat with `LOWEST_FARE` and approver `NONE` passes 11 (the
domestic and authorized bookings whose answer is the lowest fare: `cinder-fell`, `drumlin-sedge`, `egret-shale`,
`fernwick-cove`, `kittiwake-holm`, `plover-ghyll`, `quince-firth`, `rowan-skerry`, `sorrel-haugh`,
`wren-scaur`, `zephyr-mire`).

## Tools

| Tool | Does | Code |
|---|---|---|
| `booking_requirements` | The trip record's fields, the world's conventions (local times, dates, fares, sold-out seats) and its airports | `src/plugin/guide.py` |
| `get_trip` | A case's request and trip record: traveller, job title and ELT membership, route, dates, purpose, requested cabin, nonstop, refundable fare or airline, a companion's business purpose, colleagues already booked with their flight numbers, sign-offs, notes | `src/plugin/tools.py` |
| `search_flights` | Every offer on a route and local date (one way, or round trip with `return_date`): the pinned scenario offers plus seeded background offers on those searches only; a search the case does not pin lists nothing and says so | `src/plugin/world.py` |
| `solve_booking` | The answer key (`rules.solve`), the agent task's `reference`, never shown to the agent | `src/plugin/rules.py` |

| Task | Does | Runner |
|---|---|---|
| `book-hillrom-flight` | Handles one booking request | `agent`, with `get_trip` and `search_flights`; reference `solve_booking` |
| `booking-requirements` | Shows `booking_requirements` | `tool` |
| `search-flights` | Shows `search_flights` | `tool` |

## Layout

- `contract.py`: the template's shared contract plus this handbook's scenario ids, approvers, sections and trip record.
- `src/plugin/`: `world.py` (the simulated world: real airports and airline hubs, distance-based times
  and fares, hash-seeded background offers and opaque offer ids), `scenarios.py`, `guide.py`,
  `answer.py`, `tools.py`, `rules.py` (this handbook's rules, citing frozen lines), `__main__.py`.
- `src/plugin/data/`: `policy.txt` (frozen), `handbook.json`, `scenarios/*.json`.
- `verifier/`: byte-identical copies of `world.py`, `scenarios.py`, `guide.py`, `answer.py` and
  `rules.py`, plus `booking.py` (`verify_task`) and `tools.py` (`verify_input`, `verify_output`).
- `tests/`: the template's acceptance suite; `tests/plugin_spec.py` holds this handbook's settings;
  `tests/build_scenarios.py` writes the scenario files. `tests/BUILD_NOTES.md` records the build choices, the blind read and
  the acceptance outputs.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
uv run ruff check .
uv lock --check
python3 tests/build_scenarios.py   # rewrites src/plugin/data/scenarios/*.json
# from a NanoAgent checkout (stock NanoAgent runs this plugin as the `off` baseline;
# the fork's `harness.policy: full` flag adds the handbook):
nanoagent plugin inspect <this folder>
nanoagent plugin pack <this folder> /tmp/hillrom-flight-policy.tar.gz
<nanoagent>/.venv/bin/python ../_template/tools/stock_verify.py
```

Offline: `hosts: []`, an empty `.env`, `write: []`, no clock (each case fixes its `booking_date`).
