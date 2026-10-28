# Strategy

## Constraints we optimise for
- Character: Trade, Retail, Accounting, Broker Relations, Advanced Broker Relations, Marketing
  and Daytrading at V; Wholesale III–IV (113–129 order slots). 5–10B ISK.
- Sessions: 1–2 on weekdays (06:15–07:30 or 18:00–22:00 PT, usually evening) plus 1–2 at
  random weekend times. 30 minutes maximum each, sometimes cut short. Short moves are allowed
  within a session; long relocations at most once every two weeks.
- **Your time is the scarcest resource.** Each repricing click costs about 25 s, so an item has
  to earn enough per session to justify the clicks it costs.

## Strategies (v2)
Every order and every unit of stock carries a tag, so `state/summary.md` can show results per strategy.

**station**: buy and sell orders on the same item at one hub, repriced only at sessions.
- Score per item = net margin after tax, broker and relist fees × the units/day we'd capture.
- Units/day = observed volume × `alpha` × the average chance we're still top of the book until
  the next session.
- That chance comes from how often rivals update their orders in each 6-hour UTC block,
  weighted by when your sessions start (mostly 18–22 PT). Items whose rivals are European and
  asleep during your evening get credit for that. Items crowded by bots score close to zero.
- Filters: at least 6% net margin, at least 2M ISK/day, a sane spread, recent trade prices close to ours.

**import**: buy from Jita sellers, courier the goods to the import hub, sell there.
- The import hub is chosen automatically, once (the best expected profit of the four); reviews can change it.
- Requires at least 10% margin after shipping. A shipment goes out only when the courier's minimum
  fee is at most 3% of the cargo value. At most 12 items per session.
- Courier prices are **estimates** (see `config.toml` `[routes.*]`) until checked against real quotes.

**spec**: positions the reviewer opens in `state/spec.json` ahead of patches or events (capped at 10% of net worth).
```json
[{"hub": "jita", "type_id": 12345, "qty": 100, "max_buy": 1500000, "sell_after": "2026-12-01",
  "min_sell": 1800000, "note": "why", "active": true}]
```
The planner keeps a buy order up to `max_buy` until `qty` is held, holds the stock until
`sell_after`, then sells it no lower than `min_sell`.

## Choosing what to stock (shelf-space logic)
Think of it as a shop that can only restock when you log in. New items compete for three shelves:
order slots, ISK, and your seconds per session. Each candidate's score is profit/day divided by the
largest share of any of those it would use, so the scarcest resource drives the choice: a $1 × 10/day
item beats a $5 × 1/day item when slots or time are tight, but not when ISK is. Stock is sized to
last two session gaps, since shelves only get restocked at logins.

## How a session is laid out
- Start at whichever hub the character is in, do that hub's work, then jump-clone to the other hub
  (19 h cooldown assumed) and do its work there. Imports are bought and shipped at Jita.
- Time goes by tier: (1) fix undercut sells and list stock, (2) fix or cancel buys, imports and spec,
  (3) new station buys by expected profit. The plan uses 25 of the 30 minutes.
- Within each hub the steps follow the in-game windows, sorted by item name, with an exact
  "type this" price plus the rule to use if the market has moved.

## Sizing and risk
- At most 8% of net worth in one item, 10% in speculation, and a 2% cash reserve. Slots are capped at 113.
- Sell floors start at break-even + 0.5%, and break-even includes the shipping cost. After 10 days
  we accept up to a 3% loss to free capital.
- Stock in transit is the courier's risk: reputable services repay the collateral.

## Fee model (verify in game when live)
- Sales tax 7.5% × (1 − 0.11 × Accounting) = 3.375%.
- Broker fee at an NPC station: 3% − 0.3% × Broker Relations − 0.03% × faction standing −
  0.02% × corp standing = 1.5% with no standings.
- Relist fee: (1 − (0.5 + 0.06 × ABR)) × broker × new value + broker × any increase in value.
- Prices are limited to 4 significant figures (tick).

## Open questions and experiments (update as results come in)
1. **Which import hub?** The summary's hub comparison shows it. Move the second clone only if
   another hub beats the current one for two weeks running.
2. **Standings** (investigate): yearly savings = broker-fee volume × the fee reduction. Compare
   with the hours of missions needed. Use realized order volume from `state/ledger.csv` after a week.
3. **Player structures** (investigate): the Perimeter Keepstar's fees and competition. Its market
   needs an authenticated ESI token (the SSO app); then compare its scoring with Jita 4-4.
4. **Wholesale IV/V**: only if slots become the limit (orders near 113 while good candidates go unused).
5. **Later, when capital allows**: manufacturing (long jobs suit infrequent logins) and a
   second trading character (a third hub, more slots). Revisit at about 15B net worth.
6. **Calibration**: when live, compare real fills against what the simulation predicted and
   adjust `alpha` and `gone_weight`.
