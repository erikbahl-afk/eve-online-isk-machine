# EVE ISK machine

A market trader built for **a few 30-minute sessions a week**. A scheduled job watches the
markets; you follow a checklist when you log in.

- **[INSTRUCTIONS.md](INSTRUCTIONS.md)**: the checklist for your next session. Open it on your
  phone or a second screen, work top to bottom, then tell Claude `done` or `stopped after step N`.
- **[state/summary.md](state/summary.md)**: how the trader is doing (net worth, fees, best and
  worst items, data health).
- **[STRATEGY.md](STRATEGY.md)**: what we're doing and why. **[JOURNAL.md](JOURNAL.md)**: what
  was tried, what worked, what didn't.

## Current phase: practice (paper trading)

Until the character is ready, the system trades 5B of pretend ISK against the live market:

1. Every 2 hours, GitHub Actions (`.github/workflows/market.yml`) downloads the public order
   books of Jita, Amarr, Dodixie, Rens and Hek from ESI.
2. Comparing consecutive snapshots shows which orders got filled. That lets us estimate
   whether *our* orders would have filled, and how quickly rivals would have undercut us.
3. Simulated logins follow your pattern (1–2 weekday logins before or after work, 1–2 on the
   weekend, sometimes cut short). Each one executes the checklist that was current at that time.
4. A fresh checklist is written after every run.
5. Twice a week a short Claude session reviews the results, tunes `config.toml` or the code,
   and logs the reasons in `JOURNAL.md` (see `REVIEW.md`).

Fills are estimated conservatively: we capture only part of the observed volume, and our
chance of staying top of the book decays at each item's measured rival-update rate.
Real results should be at least as good as practice ones.

## Layout

| Path | What |
|---|---|
| `trader/esi.py` | public ESI client |
| `trader/market.py` | snapshots → inferred trades, competition rates, daily stats |
| `trader/sim.py` | paper portfolio, fill model, session execution, fees |
| `trader/strategy.py` | item scoring and checklist generation |
| `trader/logons.py` | simulated session schedule |
| `trader/run.py` | one scheduled run |
| `state/` | portfolio, plan, sessions, ledger, metrics (committed by the bot) |
| `data/daily/` | per-type daily trade stats for each hub |
| `reports/` | weekly snapshots of the summary |

Run the tests with `pip install -r requirements.txt && python -m pytest -q`.

## Before going live
- Make the repo **private** (the checklist reveals items and price limits), then set the
  cron in `.github/workflows/market.yml` back to every 3 hours to stay within the free
  2,000 Actions minutes a month.
- Set `mode = "live"` in `config.toml`, and enter the verified fees, slots and standings from `CHECKS.md`.
- Write `PLAYBOOK.md` for the user: which tools to install to speed up sessions (EULA-safe only:
  no input automation) and exact click-by-click steps for every checklist action (modify,
  list, buy order, market buy, courier contract, jump clone), plus the window layout to use.
