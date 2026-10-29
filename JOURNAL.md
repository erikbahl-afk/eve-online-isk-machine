# Journal

## 2026-10-28 · setup
- Built v1: 3-hourly snapshots of five hubs, trade inference, a paper portfolio of 5B at Jita
  4-4, simulated sessions (1–2 weekday + 1–2 weekend, PT), slow station-trading strategy.
- Assumptions to validate against live data: `alpha=0.6`, `gone_weight=0.8`, 48 h session gap.
- Data warmup: no trading until 20 h of data has been collected; stats get better over 7 days.
- Next review: check that the runs are healthy, that the trade counts look plausible (compare
  Jita's daily units with known volumes for common items), and which hubs score best.

## 2026-10-28 · cadence
- The repo is public during practice (unlimited free Actions minutes), so collection runs every 2 hours.
  Before going live: make it private and switch back to 3-hourly (see README).
- First live runs: about 600k orders across the five hubs, about 90 s per run, about 916 ESI calls.

## 2026-10-28 · v2: imports, time of day, faster checklist, speculation
- The first live diff worked: about 6.4k inferred trades in Jita over 1.2 h; the other hubs scale down as expected.
- Added the import strategy (Jita → auto-chosen hub, jump clone each session, courier estimates),
  rival activity per 6-hour UTC block weighted by your session times, checklists grouped and
  sorted to match the in-game windows with exact prices, spec positions via `state/spec.json`,
  and results split by strategy.
- Reset `state/metrics.csv` to the new columns (it held only no-trade warmup rows).
- Next: once warmed up, check that the import candidates are real items with sane m³ and margins,
  and verify the courier prices (CHECKS.md section 6).

## 2026-10-28 · real courier prices
- PushX (pushx.net/rates.php): 1.5M/warp up to 1.5B collateral → per contract from Jita: Amarr 69M,
  Dodixie 24M, Rens 39M, Hek 30M. Red Frog API: 73M / 35M / 53M / 43M (≤1.5B, ≤845k m³, up to 7 days).
- The model now charges per contract (≤1.5B, ≤62.5k m³ each), up to 2 contracts per session, and ships
  only when the contracts are ≥60% full. The old guesses badly underpriced Amarr (about 4.6% of
  cargo value per full contract versus 1.6% for Dodixie), so expect Dodixie or Hek to win the import-hub choice.

## 2026-10-28 · hub market sizes (user asked to weigh volume, not just shipping cost)
- ESI region history, last 30 days, 160 typical import items (1M–1B ISK/unit): daily ISK traded as a share
  of Jita: Amarr 8.2%, Dodixie 3.5%, Hek 1.7%, Rens 1.3%. Median item per day: Amarr 465M, Dodixie 146M,
  Hek 88M, Rens 79M.
- Full PushX contract cost as a share of cargo value: Amarr 4.6%, Dodixie 1.6%, Hek 2.0%, Rens 2.6%.
- Import scoring already scales by destination sales × time on top of the book; the summary now also
  shows each hub's market size. Added `python -m trader.calibrate` to check our inferred volumes
  against the official history (weekly, in REVIEW.md).
- Hypothesis: Dodixie (cheap shipping, mid volume) or Amarr (big but pricey to ship) will win;
  Rens and Hek only if their margins are much wider. Check the hub comparison after 2–3 days of data.

## 2026-10-28 · shelf-space ranking (user's store analogy)
- New items are now ranked by profit/day ÷ the item's largest share of a scarce resource: order slots
  (station 2, import 1), ISK tied up (stock covering the gaps between sessions), or player seconds per
  session. Fast, low-margin sellers win when slots or time bind; high-margin ones win when ISK binds.
- The summary shows shelf use (slots, ISK deployed, plan minutes) and which resource each top candidate
  leans on. Watch which one sits near 100%; that's where more capacity (Wholesale skills, more capital,
  a smaller checklist) would pay.

## 2026-10-28 · deep dive changes
- Added guards: plan sell prices capped at recent trade VWAP + 5% (anti-pump), no new buys when trade
  prices fell >10% (falling knives), and selling into buy orders when that nets ≥97% of listing.
- Added parallel experiments: `no_imports` and `loose` portfolios trade the same data and sessions.
  Promote whatever beats main for about 2 weeks.
- Queued in STRATEGY.md: exports (reverse trip), seeding empty markets, Perimeter structure buy orders,
  and the sales-tax question (7.5% vs 8% base).

## 2026-10-28 · cornerability scanner (read-only)
- The user asked when market manipulation becomes viable. Answer: not now. Supply refills, we can't
  defend a corner with 2–4 logins a week, and paper trading can't simulate the market's reaction.
  Revisit at about 20B with a small live test (about 5%).
- Added `trader/corners.py`: per hub, the cheapest buy-out of up to 20 sell orders, relisted just under
  the next order (capped at import parity, or 1.5× VWAP in Jita). Flags ROI ≥15%, sells within 10 days
  of demand, ≤3 rival updates/day. Top 10 in the summary; daily top 50 in data/corners/.
- Later: compare flagged items' prices 1–2 weeks on. Did they hold (cornerable) or refill?

## 2026-10-29 · schedule and skills
- GitHub's schedule only started firing after the user edited market.yml (00:00 and 05:49 UTC runs), and it
  still drops slots. Asked the user to add an odd-hour backup cron line themselves.
- Skill plan from ESI data: about 4.04M SP (Trade/Retail/Marketing/Daytrading/Accounting/BR/ABR V,
  Wholesale IV, IP I, IS III, Social I, Contracting II). About 80 days on Omega with a Cha/Mem remap.
  AIR gives 0.75–1.5M SP. Alpha can't train Retail or Accounting, so the trader must be Omega.
