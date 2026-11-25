# Build notes: hillrom-flight-policy (wave 2, 2026-11-24)

This file lives under tests/ because stock `nanoagent plugin inspect` rejects any extra file at the plugin root
("unexpected BUILD_NOTES.md").

Built from `pilot_work/tier_plan/build/WAVE2_BUILD_BRIEF.md` with no questions asked; every choice below is the
recommended one. Frozen handbook: `pilot_work/originals/hillrom/frozen/hillrom_policy.txt` (12,518 words, 1,288
lines, sha256 `ce8a8582...c4a20b05`). Task id `book-hillrom-flight`. 32 scenarios (over 10,000 words).

## What the handbook supports, and what it does not

Checkable flight rules used (frozen lines):

| Rule | Lines | Used by |
|---|---|---|
| Class table per segment and position | 424-435 | gannet-sill, heather-knap, iris-combe, jackdaw-scar, bramble-tor, egret-shale, thistle-moraine, yew-strand, umber-carse, dunlin-esker, eider-rigg |
| Pre-travel authorization between continents (ELT representative or Regional President) | 288-291 | cinder-fell, egret-shale, iris-combe, jackdaw-scar, rowan-skerry, umber-carse, eider-rigg, finch-holt; Mexico in quince-firth |
| Lowest logical airfare within a continent (one connection, +2 h, $250 of the round-trip fare) | 438-445 | kittiwake-holm, lupin-wold, quince-firth |
| Between continents (+3 h, $1,000) | 451-455 | rowan-skerry, umber-carse |
| Refundable margin "less than $150" | 446 | mallow-crag, nettle-brae |
| Alternate airports (Gatwick/Heathrow by name) | 456-459 | umber-carse |
| Preferred vendor at an equal or lower fare | 331-332, 400-401, 447-448 | alder-bight, vetch-linn, wren-scaur |
| Frequent flyer: no non-preferred vendor "even if the costs are equal" | 461-464 | vetch-linn |
| Key personnel: at most 4 ELT members, at most 2 of CEO/CFO/CLO; CEO approves exceptions | 490-494 | osprey-dene, plover-ghyll, zephyr-mire, gorse-haven |
| Spouse/companion: bona fide purpose and ELT member's advance approval | 356-365, 865-871, 1281 | sorrel-haugh, aster-fold |
| No gambling trips | 343-345 | bittern-hythe |
| Personal travel not covered | 145-146, 1237, 1250-1251 | corrie-wynd |
| Situation not covered: manager/supervisor or Manager of Global Travel | 159-160 | the two gap flags |

Not tested, and why:

- **Advance purchase** (395-396, "should ... 14 days / 21 days"): advice, never a refusal (EDGE_CASES H-2). Used
  only as a distractor (`cinder-fell` 12 days ahead across the month end, `quince-firth` 15 days).
- **Time window** (443, "no more than two hours before or after requested time"): no trip record names a requested
  time, so the window never binds; all pinned flights of a routing case leave within two hours of each other.
- **No seats in the permitted class** (449-450) and **upgrades at no additional cost** (349-350): codes exist
  (`NO_SEATS_IN_PERMITTED_CLASS`, `UPGRADE_NO_ADDITIONAL_COST`) but no scenario: the first reads "no other seats"
  either on that flight or on any flight, and the second collides with 449-450 for premium economy; both would need
  a fifth flag and the cap is 4.
- **Mixed-class itineraries** (a short coach-entitled segment next to a long business-entitled one): the template's
  offer sells one cabin on every flight, so a through business fare on such an itinerary has no clear answer. No
  scenario has one; `rules.entitlement` raises on it.
- **The overnight multi-leg overlay:** the handbook has no rule on overnight stops.
- **Batesville alternates (Cincinnati, Indianapolis), Midway, Love Field:** not in the shared world's airports;
  only Gatwick/Heathrow is tested.
- **ELT members travelling between continents** (whose "ELT representative" would be themselves): avoided; every
  ELT case is within North America.

## Design choices

- The class table's comparisons are four duration rules, each clear on its own (below-six `>=` 360, above-six `>`
  360, below-ten `>=` 600, above-ten `>` 600), so `tests/test_duration.py`'s both-sides test holds and the gaps
  appear only in the class lookup. `over()` is per segment over out and back segments: all over, none over, or
  None when a connection's segments fall on both sides.
- **The gaps are flags, never twins** (brief, EDGE_CASES 2.3): exactly 360 minutes for a Vice President
  (`dunlin-esker`, twins 359/361), exactly 600 minutes for a Director (`eider-rigg`, twins 599/601). Unclear
  phrases "< 6 hours > 6 hours" and "< 10 hours > 10 hours" (the header as its wrapped lines read joined). A gap
  where the neighbouring columns agree (an ELT member at any length; a Director at 360; a Vice President at 600) is
  clear and is not a flag. The hold accepts the cheapest offer of either class, with approvers `NOT_NAMED`,
  `SUPERVISOR`, `GLOBAL_TRAVEL` (lines 159-160) and `CORPORATE_CONTROLLER` (lines 133-134, concerns about the
  policy).
- Position: `elt_member` in the record decides the ELT row; a title starting "Vice President", "Senior Vice
  President" or "Executive Vice President" is "Vice Presidents and above"; anything else is "All other employees".
  Titles with "President" or "Chief" outside the ELT raise (not modelled).
- "Between continents": by the countries of the two airports (US, CA, MX North America; western Europe; East and
  South Asia). South America, Hawaii, the Caribbean and Istanbul are never used.
- Requests are honoured when the policy permits them (a nonstop when the saving is under $250, a refundable fare
  under $150 more, economy for a Vice President who asks for it), as in the template's worked example.
- The within-continent saving is "of the round-trip coach/economy fare", so those routing cases are round trips
  with pinned round-trip searches (the ticket convention allows a case that is itself a round trip).
- Approvers follow template amendment 4' (coordinator message, 2026-11-24): a BOOK with the needed sign-off on
  file accepts that role and `NONE`; holds accept only the awaited roles; the supervisor's sign-off in
  `finch-holt` is the invalid one the case tests and is not accepted.
- Background offers: `background_offers: 0`; 2 per search on `drumlin-sedge`, `fernwick-cove`, `bittern-hythe` and
  `corrie-wynd`, where no background routing can change the answer. Every duration-sensitive search has none
  (the Thornton validation's `linden-spire` read a background flight's minutes).
- Degenerate baselines: always-flag passes 2 (the gap flags); always-cheapest with `LOWEST_FARE` and `NONE` passes
  12 of 32 (37.5%, under the lead's ~40% target). `alder-bight` was made a preferred-airline tie (the first-listed
  cheapest is the non-preferred Delta) to bring it from 13 to 12.

## Template change requests (not applied; worked around)

1. `world.py`: add IND and CVG (Hill-Rom's own Batesville alternates, line 457), MDW and DAL (line 458), so the
   alternate-airport clause can be tested beyond Gatwick/Heathrow.
2. `world.py` `flight_number`: a background itinerary that leaves at the same minute as a pinned flight of the same
   airline and route gets the same flight number with different minutes and fare (seen in an early `alder-bight`:
   two "AA 341" at 12:15, 115 and 100 minutes). Worked around by turning background off there. Suggest salting the
   hash with the path or the slot.
3. The `Offer` contract sells one cabin on every flight. Per-segment cabins (Hill-Rom, NJC) cannot be tested on
   connections whose segments earn different classes; a per-segment cabin list would allow it.

## Things I was unsure about

- `umber-carse` needs a second search (Gatwick) the record does not name; it is the hidden-clause case by design,
  and both readings of 451-459 book Gatwick because the saving clears $1,000. It also makes 4 calls and crosses the
  hosted cap under `full`.
- `vetch-linn`/`wren-scaur` accept `LOYALTY_PROGRAM_PREFERENCE` beside the main code, as Anixter's `zinnia-loch`
  does.
- Clause accept sets add `INTERNATIONAL_PRE_APPROVAL` to every booking whose airports are in two countries
  (including London-Frankfurt and Chicago-Mexico City), since a reader may cite 2.5 for "no authorization needed".
- `gorse-haven` assumes the CFO cannot simply fly another day: the record says no other flight that morning is
  listed, and a search on another day lists nothing.

## Independent blind read (no agents; handbook text and tool outputs only)

For every non-flag scenario I re-read `get_trip` and every pinned `search_flights` output as the agent sees them
(offer ids, carriers, cabins, fares, seats, refundable, segment minutes, elapsed minutes) and derived the answer
from the frozen text without looking at `rules.py`:

| Scenario | My answer from the handbook | Agrees with key |
|---|---|---|
| alder-bight | DL and UA tie at 21400; preferred UA (400-401) | yes |
| bramble-tor | ELT: business any length (432); AA business 88500 | yes |
| cinder-fell | Director 530-535 min: coach; Diane = ELT rep, authorized; LH 81900; 12 days ahead is "should" | yes |
| drumlin-sedge | AA 17900 sold out; UA 19400 | yes |
| egret-shale | VP may fly business but asks economy; RP authorized; AA economy 64500 | yes |
| fernwick-cove | Within Europe, no authorization; LH 17600 | yes |
| gannet-sill | VP, 359 min "< 6 hours": coach; DL economy 42000 | yes |
| heather-knap | VP, 361 min "> 6 hours": business; DL business 128000 | yes |
| iris-combe | Director, 599 "< 10 hours": coach; UA economy 89000 | yes |
| jackdaw-scar | Director, 601 "> 10 hours": premium; UA premium 165000 | yes |
| kittiwake-holm | +90 min each way, saving exactly 25000 "at least $250": connection | yes |
| lupin-wold | saving 24900 < $250: requested nonstop | yes |
| mallow-crag | refundable +14900 "less than $150": refundable, as asked | yes |
| nettle-brae | +15000 not less than $150: non-refundable UA 27400 | yes |
| osprey-dene | CEO and CLO on UA 375; CFO would be third of the named: AA economy 24600 | yes |
| plover-ghyll | only CEO on UA 375: two named, allowed; UA economy 21800 | yes |
| quince-firth | Mexico is the same continent: no authorization, within tests; +110 min, saving 26000: connection | yes |
| rowan-skerry | between continents: +170 min <= 3 h, saving 104000 >= $1,000: connection; all segments coach | yes |
| sorrel-haugh | spouse with business purpose, Diane (ELT member) approved in advance: WN 21900 | yes |
| thistle-moraine | VP, segments 195-235 min, each "< 6 hours": coach; AS economy 44900 | yes |
| umber-carse | VP 470-475 min: business; Gatwick saves 132000, +5 min: LGW business | yes |
| vetch-linn | equal fares: preferred UA; miles cannot pick the non-preferred (463-464) | yes |
| wren-scaur | UA 100 cents dearer: AA is the lowest, allowed | yes |
| yew-strand | Director 415 min: coach; wifi clause is about internet | yes |
| zephyr-mire | 4 ELT on UA 375, traveller not ELT nor officer: no limit hit; UA 22600 | yes |
| aster-fold | spouse sightseeing, no business purpose: refuse | yes |
| bittern-hythe | casino weekend with a customer: refuse (343-345) | yes |
| corrie-wynd | family vacation: refuse | yes |

28 of 28 non-flag scenarios agree. Flags (`dunlin-esker`, `eider-rigg`, `finch-holt`, `gorse-haven`) were checked
for clear twins on both sides instead.

## Acceptance outputs
```
$ uv run pytest -q
268 passed in 2.73s
$ uv run ruff check .
All checks passed!
$ uv lock --check
Resolved 42 packages in 11ms
$ python3 ../_template/check_shared.py .
: ok
$ nanoagent plugin inspect .   (stock checkout)
ok (exit 0; JSON manifest printed, id hillrom-flight-policy, task book-hillrom-flight)
$ nanoagent plugin pack . <scratch>/hillrom-flight-policy.tar.gz
packed . into <scratch>/hillrom-flight-policy.tar.gz (189047 bytes)
$ <stock venv>/bin/python ../_template/tools/stock_verify.py .
alder-bight          right=True score=1.00 identical=True wrong-decision-rejected=True
aster-fold           right=True score=1.00 identical=True wrong-decision-rejected=True
bittern-hythe        right=True score=1.00 identical=True wrong-decision-rejected=True
bramble-tor          right=True score=1.00 identical=True wrong-decision-rejected=True
cinder-fell          right=True score=1.00 identical=True wrong-decision-rejected=True
corrie-wynd          right=True score=1.00 identical=True wrong-decision-rejected=True
drumlin-sedge        right=True score=1.00 identical=True wrong-decision-rejected=True
dunlin-esker         right=True score=1.00 identical=True wrong-decision-rejected=True
egret-shale          right=True score=1.00 identical=True wrong-decision-rejected=True
eider-rigg           right=True score=1.00 identical=True wrong-decision-rejected=True
fernwick-cove        right=True score=1.00 identical=True wrong-decision-rejected=True
finch-holt           right=True score=1.00 identical=True wrong-decision-rejected=True
gannet-sill          right=True score=1.00 identical=True wrong-decision-rejected=True
gorse-haven          right=True score=1.00 identical=True wrong-decision-rejected=True
heather-knap         right=True score=1.00 identical=True wrong-decision-rejected=True
iris-combe           right=True score=1.00 identical=True wrong-decision-rejected=True
jackdaw-scar         right=True score=1.00 identical=True wrong-decision-rejected=True
kittiwake-holm       right=True score=1.00 identical=True wrong-decision-rejected=True
lupin-wold           right=True score=1.00 identical=True wrong-decision-rejected=True
mallow-crag          right=True score=1.00 identical=True wrong-decision-rejected=True
nettle-brae          right=True score=1.00 identical=True wrong-decision-rejected=True
osprey-dene          right=True score=1.00 identical=True wrong-decision-rejected=True
plover-ghyll         right=True score=1.00 identical=True wrong-decision-rejected=True
quince-firth         right=True score=1.00 identical=True wrong-decision-rejected=True
rowan-skerry         right=True score=1.00 identical=True wrong-decision-rejected=True
sorrel-haugh         right=True score=1.00 identical=True wrong-decision-rejected=True
thistle-moraine      right=True score=1.00 identical=True wrong-decision-rejected=True
umber-carse          right=True score=1.00 identical=True wrong-decision-rejected=True
vetch-linn           right=True score=1.00 identical=True wrong-decision-rejected=True
wren-scaur           right=True score=1.00 identical=True wrong-decision-rejected=True
yew-strand           right=True score=1.00 identical=True wrong-decision-rejected=True
zephyr-mire          right=True score=1.00 identical=True wrong-decision-rejected=True
32 scenarios, 0 failures
```
