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
