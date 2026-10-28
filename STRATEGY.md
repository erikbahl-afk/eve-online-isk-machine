# Strategy

## Constraints we optimise for
- Character: Trade, Retail, Accounting, Broker Relations, Advanced Broker Relations, Marketing
  and Daytrading at V; Wholesale III–IV (113–129 order slots). 5–10B ISK.
- Sessions: 1–2 on weekdays (06:15–07:30 or 18:00–22:00 PT, usually evening) plus 1–2 at
  random weekend times. 30 minutes maximum each, sometimes cut short. Short moves are allowed
  within a session; long relocations at most once every two weeks.
- **Your time is the scarcest resource.** Each repricing click costs about 25 s, so an item has
  to earn enough per session to justify the clicks it costs.

## Current approach: slow station trading (v1)
Trade items whose rivals rarely reprice, holding a buy order and a sell order at the same
time and repricing only when you log in.

Score per item = (net margin after tax, broker and relist fees) × (units/day we'd capture).
- Units/day = observed volume × `alpha` × the average chance we're still top of the book over
  a ~48 h gap. That chance falls with the rate at which rivals update near-top orders, so items
  hot with bots score close to 0 automatically.
- Filters: at least 6% net margin, at least 2M ISK/day expected, sane spread, and recent trade
  prices close to our targets (guards against manipulated or dead markets).
- Sizing: at most 8% of net worth per item, a 2% cash reserve, order slots capped at 113.
- Sell floors start at break-even + 0.5%. After 10 days, accept up to a 3% loss to free capital.
- Checklist order: fix undercut sells → list new stock → fix outbid buys → cancels → new buys.
  If a session gets cut short, the most valuable steps are already done.

## Fee model (verify in game when live)
- Sales tax 7.5% × (1 − 0.11 × Accounting) = 3.375%.
- Broker fee at an NPC station: 3% − 0.3% × Broker Relations − 0.03% × faction standing −
  0.02% × corp standing = 1.5% with no standings.
- Relist fee: (1 − (0.5 + 0.06 × ABR)) × broker × new value + broker × any increase in value.
- Prices are limited to 4 significant figures (tick).

## Open questions and experiments (update as results come in)
1. **Which hub?** `state/summary.md` compares each hub's station-trading opportunity using the
   same scoring. Relocate if another hub is clearly better for two weeks running.
2. **Hub imports** (buy in Jita, courier the goods, sell in another hub): needs a jump clone in
   each hub so one session covers both regions. *Waiting on the user.* Not simulated yet.
3. **Standings grind**: worth it only if the broker-fee savings beat the time. Compute this
   from realized order volume once there's a week of data.
4. **Wholesale IV/V**: only if slots become the binding constraint (`orders` near 113 in the
   summary while good candidates go unused).
5. **Player structures** (e.g. the Perimeter Keepstar): lower fees, but their market data
   needs an authenticated token. Revisit once the SSO app exists.
6. **Calibration**: when live, compare real fills against what the simulation predicted and
   adjust `alpha` and `gone_weight`.
