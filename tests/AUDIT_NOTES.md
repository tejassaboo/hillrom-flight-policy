# Audit notes: hillrom-flight-policy (2026-11-24)

This file is under tests/ because stock `nanoagent plugin inspect` rejects extra files at the plugin root.

This is an independent audit of the build at d7e42f2. I re-derived every answer from the frozen handbook
(`pilot_work/originals/hillrom/frozen/hillrom_policy.txt`, sha256 `ce8a8582...c4a20b05`, byte-identical to
`src/plugin/data/policy.txt`) and from the tool outputs the agent sees (`get_trip` and every pinned
`search_flights`). I did not read `rules.py` before deriving the answers. The standard was MASTER_PLAN section 4,
EDGE_CASES sections 1-3 and 5 (section 4.7 for the planned design), `_template/SYNC_NOTES.md` including 4', and the
defect classes found by the paid validations (Thornton/NJC VALIDATION.md; LSU, NJC and Anixter
REVALIDATION_NOTES).

**Verdict: pass after fixes.** The key was right on all 28 non-flag scenarios and the 4 flags are genuine. The
defects were in request wording, one trip record, and some accept sets. No answer changed, and no offer or flight
changed: every offer id, fare and time is identical before and after the fix.

## Class table (frozen lines 424-435)

The PDF extraction wraps the header ("< 6 hours > 6 hours and < 10" / "hours" / "> 10 hours") and the last row
("Premium Coach /" / "Economy Plus"). Read with its lines joined, the table is unambiguous:

- ELT: Standard Business in all three columns.
- Vice Presidents and above: Coach / Economy, then Standard Business, then Standard Business.
- All other employees: Coach / Economy, then Coach / Economy, then Premium Coach / Economy Plus.

`rules.TABLE` matches this. Segments of exactly 360 or 600 minutes fall in no column. They are a real gap only
where the neighbouring columns differ for the traveller's row: a VP at 360 minutes and all other employees at 600.
The two flags (`dunlin-esker`, `eider-rigg`) sit there, and their twins at 359/361 and 599/601 change only the
minutes. "length of individual flight segment" (line 426) makes the measure per segment, and `thistle-moraine`
tests that correctly.

## Defects found and fixed

| # | Scenario(s) | Class | Defect | Fix |
|---|---|---|---|---|
| 1 | umber-carse | unfair hidden fact | The key books Gatwick, but nothing the agent can see names LGW. The record's destination is LHR, and the booking task cannot call `booking_requirements` (the only tool that lists airports). So the agent had to guess the code. | The trip record gets a note: "Central London is served by London Gatwick (LGW) as well as London Heathrow (LHR)." The clause test (456-459, alternates are considered) is unchanged. |
| 2 | cinder-fell, finch-holt, egret-shale, umber-carse | ambiguous arrival (LSU tupelo-wren), here worse | "I have to be at the training on December 10" / "meeting on December 15" / "need to be in London on January 19". Every listed flight leaves that evening and lands the next day, so on the request's words no offer arrives in time, and REFUSE or another date reads as correct. | Each request now names the departure day and puts the event later ("I fly out to Frankfurt on December 10 for the distributor training there on December 12"; London December 15 for a meeting December 17; London January 19 for a negotiation January 21). finch-holt changed the same way as its twin. |
| 3 | alder-bight, bramble-tor, drumlin-sedge, fernwick-cove, sorrel-haugh (+ twin aster-fold), thistle-moraine, vetch-linn and wren-scaur | ambiguous arrival with no deadline (preventive) | The event looked same-day, and the key's flight lands later than a listed alternative: alder-bight UA 12:35 against DL 10:05; bramble-tor AA 13:05 against UA 10:30; drumlin-sedge 11:50 against an 08:45 background flight; fernwick-cove LH 12:45 against BA 09:55; sorrel-haugh WN 14:10 against UA 11:30; thistle-moraine AS 14:50 against DL 12:45; vetch-linn UA 12:25 against AA 11:05. | Each event is now "the next day" (or "starts" / "opens the next day"). Twins keep identical wording. |
| 4 | osprey-dene, plover-ghyll | ambiguous arrival (preventive) | Board meeting with no time on file (gorse-haven had 13:00). | Both records get the note "The board meets at 13:00.", the same as gorse-haven. |
| 5 | vetch-linn (+ twin wren-scaur) | request names only a fare the policy forbids, with no fallback (Anixter zinnia-loch, vesper-dale) | "Put me on American" when only the preferred United may be bought at an equal fare. A model may REFUSE because the requested ticket cannot be bought. | Both requests add "If American isn't possible, book what the policy allows." |
| 6 | gorse-haven | same-date assumption | The note said only that no other flight that morning is listed, so "fly the night before" was left open. Any other date or airport search lists nothing, so the answer already held, but the record did not say why. | The note now says: "The board meets at 13:00. The CFO cannot leave Chicago before the morning of December 9, and no other flight that morning is listed." |
| 7 | dunlin-esker, eider-rigg | hold that also awaits a sign-off (NJC iron-plover) | The gap flags send the case to the manager/supervisor or the Manager of Global Travel (159-160) for direction, so APPROVAL_REQUIRED is a fair reason, and the template allows it beside UNCLEAR_POLICY_TEXT. | `rules.gap_hold` accepts both codes. |
| 8 | sorrel-haugh | same class (Anixter aspen-knoll) | The key accepted LOWEST_FARE as the reason but not the lowest-fare section. | The `companion` booking adds LOWEST_LOGICAL_AIRFARE. |

## Lead's uniform rule (applied during this audit)

- The task instructions now end with: "When you book something other than what the traveller asked for, the
  reason code gives why their request is declined."
- On every BOOK that declines what was asked, LOWEST_FARE is no longer accepted unless the handbook's ground for
  declining is the lowest-fare rule itself:
  - `nettle-brae` (refundable fare declined under line 446): only REFUNDABLE_FARE_NOT_ALLOWED (was also
    LOWEST_FARE).
  - `vetch-linn` (American declined under 400-401 and 461-464): only LOYALTY_PROGRAM_PREFERENCE or
    PREFERRED_CARRIER_REQUIRED. I had added LOWEST_FARE earlier in this audit and dropped it again.
  - `osprey-dene` (the team's flight declined under 490-494): only KEY_OFFICERS_TOGETHER or
    TRAVELLER_LIMIT_PER_FLIGHT, clause KEY_PERSONNEL. I had added LOWEST_FARE and LOWEST_LOGICAL_AIRFARE earlier
    and dropped them again.
  - Already specific: the denied cabins (`gannet-sill`, `iris-combe`, `thistle-moraine`, `yew-strand`) accept
    only UPGRADE_NOT_ELIGIBLE or LONG_FLIGHT_CONDITION_NOT_MET.
  - Kept: `kittiwake-holm`, `quince-firth` and `rowan-skerry` decline the requested nonstop under section 3.2
    "Lowest Logical Airfare" (the $250 / $1,000 savings tests). That is the lowest-fare rule itself, so they
    accept COST_SAVINGS or LOWEST_FARE. If the lead reads these as generic too, dropping LOWEST_FARE there would
    take the baseline to 8.
- Not declines: `wren-scaur` (American is booked as asked), `umber-carse` ("London" in business, as asked),
  `egret-shale`, `mallow-crag`, `lupin-wold`, `zephyr-mire`, `bramble-tor`, `sorrel-haugh`.

Baselines: always-cheapest (`LOWEST_FARE`, `NONE`, first accepted section) went from 12 to **11** of 32 (34%;
`nettle-brae` no longer passes), and `MAX_PASS_ALWAYS_LOWEST` is 11. Always-flag still passes 2.

## Builder's unsure list, resolved

- **umber-carse Gatwick:** unfair as built. Fixed by defect 1. The 4-call run (get_trip, two searches, submit)
  still crosses the hosted 65,536-token cap under `full` (README, about 77,000 tokens). It needs a raised cap or a
  local run. This is budget, not a scenario defect.
- **vetch-linn / wren-scaur reason codes:** LOYALTY_PROGRAM_PREFERENCE is fair in both. In vetch-linn it names why
  the requested airline was declined, the same pattern as NJC maple-osprey. In wren-scaur the requested airline is
  the cheapest and allowed. vetch-linn does not accept LOWEST_FARE (lead's rule, below).
- **INTERNATIONAL_PRE_APPROVAL on intra-Europe (fernwick-cove) and Chicago-Mexico City (quince-firth):** kept.
  Section 2.5 is where "international" is defined as between continents and where "not required for travel within
  the same continent" sits (290-291), so citing it for "no authorization needed" is a correct reading. The offer
  still shows whether the within-continent routing test (438-445) was applied.
- **gorse-haven same date:** fair as built, because every other date or airport search lists nothing. The record
  now states it (defect 6).

## Re-derivation, scenario by scenario (all agree with the key after the fixes)

- Easy (6): alder-bight UA (preferred at a tie, 400-401); bramble-tor AA business (ELT any length);
  cinder-fell LH economy (Director 530-535 min coach; ELT representative authorized; 12 days ahead is "should");
  drumlin-sedge UA 19400 (cheapest is sold out); egret-shale AA economy (VP may fly business, asks economy);
  fernwick-cove LH (within Europe).
- Boundary twins (8): gannet-sill / heather-knap (359 coach / 361 business); iris-combe / jackdaw-scar (599 coach /
  601 premium); kittiwake-holm / lupin-wold (+90 min each way, saving 25000 is "at least $250" / 24900 is not);
  mallow-crag / nettle-brae (14900 is "less than $150" / 15000 is not).
- Multi-rule (5): osprey-dene AA (third named officer on UA 375); plover-ghyll UA (two named);
  quince-firth connection (Mexico is North America: +110 min, saving 26000); rowan-skerry connection (between
  continents: +170 min, saving 104000; every segment coach); sorrel-haugh WN (business purpose and the ELT member's
  advance written approval).
- Hidden clause (3): thistle-moraine AS economy (every segment under 6 h); umber-carse LGW business; vetch-linn UA.
- Distractors (3): wren-scaur AA (United 100 cents dearer); yew-strand DL economy (the wifi clause is about
  internet); zephyr-mire UA (traveller not ELT nor officer; "recommended" is soft).
- Refusals (3): aster-fold (no business purpose); bittern-hythe (gambling, 343-345); corrie-wynd (vacation).
- Flags (4): dunlin-esker and eider-rigg (gap words, genuinely open, readings give different cabins);
  finch-holt (only the supervisor signed; 288 needs the ELT representative or a Regional President);
  gorse-haven (only flight; CEO's advance approval, 490-491). Each has clear twins on both sides.

Not changed, but checked: denied-upgrade economy bookings (gannet-sill, iris-combe, thistle-moraine, yew-strand)
do not accept LOWEST_FARE. That matches Thornton yarrow-mosaic (classed as a model slip). Accepting it would raise
the always-cheapest baseline to 15 of 32.

## Acceptance (after the fixes)

```
uv run pytest -q                               268 passed
uv run ruff check .                            All checks passed!
uv lock --check                                Resolved 42 packages
python3 ../_template/check_shared.py .         : ok
<stock venv>/bin/python ../_template/tools/stock_verify.py .   32 scenarios, 0 failures
<stock venv>/bin/nanoagent plugin inspect .    exit 0
```
