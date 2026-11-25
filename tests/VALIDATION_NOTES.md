# Validation notes: hillrom-flight-policy (wave 2 paid validation, 2026-11-25)

Run: `efficient_corporate_travel_agent/pilot/ladder/runs/validation_w2_2026-11-25/hillrom-flight-policy@w2/`,
arm `full`, DeepSeek V4 Flash, temperature 0, max_steps 6, one run per scenario, plugin head e98b1c1. Line numbers
are lines of `src/plugin/data/policy.txt`.

## Result

26/32 valid (81.3%), easy 6/6. By category: boundary 7/8, distractor 3/3, easy 6/6, flag 2/4, hidden 2/3,
multi 3/5, refusal 3/3. No run hit max_steps; every run submitted.

## Every failure, classified

| scenario | category | submitted vs key | class | evidence |
|---|---|---|---|---|
| dunlin-esker | flag | BOOK dl-economy, UPGRADE_NOT_ELIGIBLE, NONE; key FLAG (either DL offer), APPROVAL_REQUIRED or UNCLEAR_POLICY_TEXT, gap roles | model slip | VP on an exactly 360-minute segment. The table has "< 6 hours" and "> 6 hours and < 10 hours" columns (lines 428-433), so 6 hours is in neither column, and lines 159-160 send "a particular situation ... not covered by policy" to the manager or the Manager of Global Travel. The model saw the gap: "Six hours exactly falls between ... this is ambiguous ... maybe FLAG_FOR_APPROVAL". It then settled it one way ("not > 6 hours ... so coach") and never cited lines 159-160. |
| eider-rigg | flag | BOOK ua-economy, UPGRADE_NOT_ELIGIBLE, NONE; key FLAG, the same accept sets | model slip | This is the same gap at 600 minutes for a Director ("> 6 hours and < 10 hours" coach, "> 10 hours" premium coach, lines 429-435). The model wrote "it falls in neither >10 nor <10 ... It's ambiguous" and "Given ambiguity at exactly 10 hours ... I lean that premium economy is not allowed". The trip authorization is on file (line 288), so the only open question is the table. |
| gannet-sill | boundary_twin | reason SEGMENT_CLASS_ENTITLEMENT; key LONG_FLIGHT_CONDITION_NOT_MET or UPGRADE_NOT_ELIGIBLE (the offer, cabin, approver and clause were right) | **grader defect** | It declined business for a VP on a 359-minute segment and weighed both codes: "SEGMENT_CLASS_ENTITLEMENT specifically addresses the class entitlement based on segment duration". The table's segment entitlement (lines 425-433) is exactly why the upgrade is declined, and the codes have no descriptions. The always-cheapest agent answers LOWEST_FARE, so its count is unchanged. Without the handbook a model does not know the table, so the offer still separates the twins. |
| osprey-dene | multi_rule | FLAG ua-economy (UA 07:00), KEY_OFFICERS_TOGETHER, CEO; key BOOK aa-economy (AA 08:30) | model slip | The CFO would be the third named officer on UA 07:00, and "Any exceptions ... require the advanced approval of the ... CEO" (lines 490-494). The request only says the earlier flight "would be ideal". The AA 08:30 is compliant and lands well before the 13:00 board meeting. The model saw this ("Alternatively, we could book a different flight (AA 2343) to avoid the violation") but held for an exception nobody asked for. Its twin gorse-haven (the only flight, so a hold) passed. Q3: the keyed AA economy is the cheapest offer that keeps the limit. |
| rowan-skerry | multi_rule | reason ALTERNATE_ROUTE_WITHIN_MARGIN; key COST_SAVINGS or LOWEST_FARE (the offer, cabin, approver and clause were right) | **grader defect** | It booked the connection via Newark: it saves $1,040 and adds 170 minutes, and between continents the tests are $1,000 and 3 hours (lines 451-455). It read the code as naming that: "we're selecting an alternate (connecting) route instead of the requested nonstop, because it's within the schedule margin and cheaper". The codes have no descriptions, and the plain reading of the label fits. The twin lupin-wold also accepts the code, but there the nonstop is kept, so the offer still separates the twins. The always-cheapest count is unchanged. |
| umber-carse | hidden_clause | BOOK lhr-ba-business; key lgw-ba-business | model slip | Lines 456-459 say alternate airports "will also be considered", with "London Gatwick and London Heathrow" as the example. The trip record's note says central London is served by Gatwick too, and the request says "London". The model dismissed this ("But traveler chose LHR (destination given). That's fine.") and never searched LGW. Q3: Gatwick business ($4,280) saves $1,320 against Heathrow's cheapest business and adds 5 minutes, so it is within lines 451-455. The Heathrow seat is $1,320 dearer, which is not defensible. |

On the two flags (asked to check whether the gap is real): booking economy is the conservative answer, but the gap
is real. The table is written as a partition and has no column for exactly 6 or exactly 10 hours. The handbook has
its own rule for a situation it does not cover (lines 159-160). Both runs named the gap as ambiguous before
resolving it one way. That makes both slips, by the standard used for Thornton velvet-prairie and NJC lichen-arch.
Watch item: if re-runs keep booking economy here, the lead may decide that "not > X" settles it, and then these two
would stop being flags.

## Fixes (rules.py in src/plugin/ and verifier/ stay byte-identical; tests/build_scenarios.py regenerated)

1. **Declined upgrade** (`employee`): SEGMENT_CLASS_ENTITLEMENT is now accepted beside UPGRADE_NOT_ELIGIBLE (and
   LONG_FLIGHT_CONDITION_NOT_MET). This applies to every booking where the table declines the class asked for:
   gannet-sill, iris-combe, thistle-moraine, yew-strand, and `DENIED` in the builder. One shape gets one treatment.
2. **Connection that passes the routing tests** (`routing`): ALTERNATE_ROUTE_WITHIN_MARGIN is now accepted beside
   COST_SAVINGS and LOWEST_FARE in kittiwake-holm, quince-firth and rowan-skerry.

No id, offer, decision or category changed, and no world changed. The README accept rows are updated.

**Always-cheapest agent:** 11/32 (34%) before and after. **Always-flag agent:** 2/32 before and after.

Checks at the fix commit: `uv run pytest -q` (268 passed), `ruff check`, `uv lock --check`, `check_shared.py`,
`stock_verify.py` (32 scenarios, 0 failures) and stock `nanoagent plugin inspect` (exit 0).

## Re-run

gannet-sill and rowan-skerry, to confirm they are now valid. The fixes are grader-only, so a re-score of the stored
submissions would also do. Optionally re-run dunlin-esker and eider-rigg, to see whether the economy reading of the
table gaps is stable.

Verdict: **pass after fix.** At 81% with the two grader fixes it is 28/32 = 87.5%, all easy cases are valid, and the
4 slips are on flags, a multi-rule case and the hidden clause.

## Follow-up from the cross-plugin review (second commit)

**Connection that passes the routing tests, the other code (kittiwake-holm, quince-firth, rowan-skerry):** all
three requests ask for the nonstop "if policy allows", so the booking declines it. In the same wave Carter's
jade-pennant booked the right connection with `ALTERNATE_ROUTE_TOO_EXPENSIVE` ("the alternate route (nonstop) is too
expensive"), the code FedEx, Dollar General and Standex key on this branch. It is now accepted here too (both
`rules.py` copies, `CONNECTION` in `tests/build_scenarios.py`, README, regenerated JSON). The always-cheapest agent
answers `LOWEST_FARE`, already accepted: still 11/32. No re-run needed for this change. All six checks pass
(pytest 268 passed).
