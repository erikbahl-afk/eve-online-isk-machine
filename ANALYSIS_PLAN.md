# Analysis schedule (being designed with the user, one day at a time)

Status: design in progress. Nothing below is scheduled yet. Agreed so far:

## Principles
- All analysis sessions run on Opus 5.5, and usage is tracked weekly (the user asked for this).
- Sessions make changes on their own (logged in JOURNAL.md). The weekly memo sends a push notification.
- Day topics are not fixed: the Sunday review judges whether each day produced useful findings and can
  reassign a day to something more valuable.
- Rules are guidelines, not fixed numbers. Boundaries are tested with probe portfolios (paper, same data),
  one setting changed per probe. Adopt a new value after 2+ weeks as a baseline, adjusting that bar from data.
- Up to about 6 parallel experiments.
- Live phase: up to 10% of net worth in probe positions outside the guidelines, at most 10 positions at a time.

## Monday: risk and concentration (agreed)
Exit value per holding (bid ÷ cost), concentration (top 5, the 8% guideline, clumping by hub, type or strategy),
age (stock/sells >7 and >14 days, buys unfilled >5 days, late couriers), falling prices, stress test
(top 3 positions −30%), and how anything slipped past the guards. Keeps 1–2 probe portfolios on risk settings
(item cap 8%, import exit check 60%, stale stock 10 d / 3%, falling-price filter 10%). Alert thresholds are
tuned by usefulness (false alarms vs real catches). Push only for serious risk.

## Tuesday: is the fill model realistic? (agreed)
Calibration trend (inferred vs official volume, per hub and item kind), fill sanity on our own orders (first in
line? implausible share of the day's volume?), predicted vs observed time on top (incl. time of day), the
vanished-order guess (80%) against official volumes, the effect of snapshot spacing (1 h vs 2 h), and probes
on alpha / gone_weight judged by match to official volume, not profit. Live: the user's wallet transactions
(SSO) are the ground truth, and every real fill is compared with the model's prediction.

## Wednesday: audit the picks (agreed)
For the top ~20 station and import candidates and everything held: real repeated demand (distinct trades/day),
believable margin (not one stale or absurd order), 30–90 day official history (spike?), supply (manufacturable
or NPC-seeded price ceilings, imports), and an exit if it doesn't sell. Patterns by item kind and their actual
results, predicted vs actual margin and sell speed. Acts via the avoid list, tighter filters (with probes) and
scoring ideas. Push only if a large held position looks like a trap. The user has no favoured or avoided markets;
no per-unit price cap beyond the 8% guideline.

## Thursday: competition and timing (agreed)
Rival activity by 6-hour block and weekday, undercut style (1 tick vs jumps), bot detection → avoid list,
observed vs predicted time on top for our orders, day-of-week demand (when to refresh sells and place buys),
rising competition as an exit signal, probes (e.g. minimum time-on-top filter). The user's login times are a
black box until real sessions are observed; then weight rival activity by the logged real times. Never ask the
user to shift login times.

## Friday: open questions, then time efficiency (agreed)
Work through STRATEGY.md's open questions one at a time (investigate, write up, act or close).
When the list is exhausted, focus on the user's time efficiency.

## Saturday: experiments (agreed)
Scoreboard vs main (return %, realized, liquidation ratio, unsold stock, worst position, fees share, trade count),
fair comparison over the same dates, robustness (drop each portfolio's best and worst item), and an adopt / extend /
kill decision per experiment (2+ weeks baseline, adjusted from data). Hygiene: written hypothesis and success measure,
one change each, at most 6 running, of which **2 slots are reserved for bold experiments** (whole different approaches).
Weekly projection of the 1B start (weeks to 4B, value of extra early time).
Cost: each experiment adds about 2–5 s to a GitHub run (free while public) and a couple of steps to Saturday's session.

## Live-phase inputs (agreed)
The user will report each real session: from/to times and how far down the checklist they got. Keep a log
and use it to set expectations (session length, sessions per week, usual times of day).

## Checklist ordering (agreed)
Priority blocks (must do / should do / if time) instead of one long list grouped by window; implemented 2026-11-05.
