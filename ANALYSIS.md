# Analysis runbook (daily Claude session, designed with the user)

One scheduled session runs every day at about 15:40 Pacific time, on Opus 5.5. It does the **day's topic**
from the schedule below, deals with every open alert, makes the changes it judges right (autonomy agreed with
the user), and writes a journal entry. The Friday session is the big-picture review: it lands its memo by
**5 PM PT** with a push notification.

## Schedule (Friday's review may reassign a topic that keeps producing nothing; record why in JOURNAL.md)

| Day (PT) | Topic | Section |
|---|---|---|
| Saturday | Risk and concentration | [Risk](#risk-and-concentration) |
| Sunday | Is the fill model realistic? | [Fills](#is-the-fill-model-realistic) |
| Monday | Audit the picks | [Picks](#audit-the-picks) |
| Tuesday | Competition and timing | [Competition](#competition-and-timing) |
| Wednesday | Open questions, then time efficiency | [Open questions](#open-questions-then-time-efficiency) |
| Thursday | Experiments | [Experiments](#experiments) |
| Friday | Weekly review and memo (monthly step-back on the first Friday) | [Review](#weekly-review-friday) |

## Every session
0. Setup: `cd /home/user/eve-online-isk-machine` (clone the repo there if it's missing), `git pull --rebase`,
   `python3 -m pip install -q -r requirements.txt`. Always run Python as `python3 -m ...`.
1. Read `state/summary.md` (alerts first), `state/alerts.json`, the last ~60 lines of `JOURNAL.md`, and this
   file's section for today.
2. **Alerts.** For every open alert: fix the cause, or write in the journal why it's acceptable. An alert that
   is consistently a false alarm means its threshold (config `[alerts]`) needs adjusting.
3. **Today's topic**, as described below. Dig into the data (`state/`, `data/daily/`, `data/corners/`,
   `state/variants/`, live ESI via `trader.esi.ESI`). Prefer evidence over opinion; quote numbers.
4. **Act.** Allowed without asking: config changes, code changes (with tests), `state/overrides.json`
   (avoid / exit lists, below), `state/spec.json`, starting, stopping or changing experiments (`[[variants]]`).
   Run `python3 -m pytest -q` before committing. Commit with a clear message and push to `claude/busy-carson-bj9fgk`
   (`git pull --rebase` first; a bot commits every hour or two).
5. **Journal entry**, at most 15 lines: `## <date> · <topic>`, what you looked at, numbers, what you changed and
   why, what to check next. Add one line to `reports/usage.csv`: `date,topic,tool_calls,notes`.
6. Push notifications: only where the topic says so, and Friday's memo. No other messages.

### Guidelines, not fixed numbers
Thresholds (8% per item, 60% exit check, 10 days stale, alert levels…) are starting points. Test the boundaries
with **probe experiments**: paper portfolios on the same data with **one** setting moved slightly outside the
guideline. Adopt a new value after about 2+ weeks of consistent evidence. That 2-week bar is itself adjusted by
how quickly results become clear. Judge probes on profit **and** risk (liquidation ratio, unsold stock, worst position).

### Experiments
At most 6 at once: **1 slot reserved for a bold experiment** (a whole different approach), **1 flex slot** (bold or
regular, whichever has better ideas waiting), the rest regular. Each one gets `kind`, a one-line `note`
(the hypothesis) and a success measure in the journal when it starts. Live phase: probe positions with real
ISK are capped at 10% of net worth and 10 positions.

### Overrides (`state/overrides.json`)
```json
{"avoid": [{"type_id": 123, "reason": "bots reprice every few minutes", "until": "2026-12-31"}],
 "exit":  [{"type_id": 456, "reason": "thin market, no exit", "mode": "fast"}]}
```
`avoid`: no new trades, and open buy orders are cancelled. `exit`: no new trades, buy orders cancelled, and stock is
sold at the market's lowest price − 1 tick, ignoring break-even (`mode: "fast"`), or straight into buy orders
(`mode: "dump"`). Remove entries when they stop applying.

### Usage budget (the user's rule: ask first if usage gets high)
Aim for about 30 tool calls on weekdays and 60 on Friday. If a topic needs a deeper dive than that, don't do it:
send a push notification asking the user, and note it in the journal. Friday tracks the week's usage. If the
claude-code-remote tools are available, read each analysis session's `result` events (cost and tokens) with
`list_sessions` / `list_events`; otherwise use `reports/usage.csv`. If usage trends above the first weeks' baseline
by more than 50%, ask the user before continuing at that pace. Baseline from the first session (Thu 2026-11-05,
experiments): 22 tool calls, about 1.6M cached input tokens and 12k output tokens, about $0.99 at list price.

---

## Risk and concentration
Purpose: catch what could cost ISK before it does.
1. **Exit value** per holding: best buy order at its hub ÷ what we paid. Flag the bottom 10 and anything under 50%.
   Track liquidation ÷ net worth week to week.
2. **Concentration:** the top 5 positions as a share of net worth; anything over the 8% guideline (why?); clumping
   in one hub, item kind or strategy.
3. **Age:** stock or sell orders older than 7 and 14 days; buy orders unfilled for more than 5 days; late couriers.
4. **Falling prices:** holdings whose trade price fell more than 10% in recent days.
5. **Stress test:** cost of the 3 largest positions falling 30%, as a share of net worth.
6. **Guard review:** how did anything get past the guards (exit check, falling-price filter, item cap)?
Act: exit/avoid lists, tighter risk settings, and 1–2 probe experiments on risk settings (item cap, exit check,
stale days/loss, falling-price filter). Tune alert thresholds by usefulness. **Push only** if liquidation < 50% of
net worth or one position > 15%.

## Is the fill model realistic?
Purpose: practice results only mean something if paper fills resemble real ones.
1. Calibration trend: `python3 -m trader.calibrate <hub>` (inferred vs official volume, per hub and item kind).
2. Fill sanity on our orders: were we really first in line? Fills that took an implausible share of a day's volume?
3. Time on top: predicted vs observed (snapshots), including the time-of-day pattern.
4. The vanished-order guess (`gone_weight` 0.8) vs official volumes.
5. Snapshot spacing (1 h vs 2 h) and its effect on inferred volume.
6. Probes on `alpha` / `gone_weight`, judged by match to official volume, not by profit.
Live: the user's wallet transactions (SSO) are the ground truth; compare every real fill with the prediction.

## Audit the picks
Purpose: judgment on what the maths picked. Catch traps like the SKINs of early November.
For the top ~20 station and ~20 import candidates and everything held: real repeated demand (distinct trades/day,
not one-off sales), a believable margin (not one stale or absurd order), 30–90 day official history (is it a spike?),
supply (can it be manufactured or imported cheaply, or is it NPC-seeded? Either caps the price), and an exit if it
doesn't sell. Then patterns by item kind vs actual results, and predicted vs actual margin and sell speed.
Act: avoid list, tighter filters (with probes), new scoring ideas. **Push only** if a large position looks like a
trap. (The user has no favoured or avoided markets; there's no per-unit price cap beyond the 8% guideline.)

## Competition and timing
Purpose: the strategy relies on repricing only a few times a week; study when and how rivals act.
Rival activity by 6-hour block and weekday; undercut style (1 tick vs jumps, price wars); **bots** (repricing every
few minutes around the clock) → avoid list; observed vs predicted time on top for our orders; day-of-week demand
(when to refresh sells, when to place buys); rising competition as an early exit signal; probes (e.g. a minimum
time-on-top filter). The user's login times are a black box: never suggest changing them. Once live, weight rival
activity by the logged real session times.

## Open questions, then time efficiency
Until go-live, work through **two open questions per week** (front-loaded at the user's request), starting with
standings and the Perimeter player station (its market can be read with the SSO token: `/markets/structures/{id}/`,
structure found via the character's search). Exports, seeding and two-hub rotation are already running as
experiments, so judge them from Thursday's data. Manufacturing research waits until after go-live. After go-live:
one per week. For each question: investigate properly, write up the result, then act
or close it. Add new questions as they come up. When the list is exhausted, this day turns to the user's
time efficiency: steps per minute from session reports, which steps earn the most per second, whether the
click-time estimates (`secs_*`) are right, and the minimum step value (`min_step_value_frac`).

## Experiments
Scoreboard vs main: return %, realized, liquidation ratio, unsold stock, worst position, fees share, trade count.
Compare over the same dates; check robustness by removing each portfolio's best and worst item. Decide **adopt /
extend / kill** for each, with the evidence in the journal. Keep the slots full: 1 bold, 1 flex, the rest regular,
refilled from ideas the other days produced. Weekly projection of the 1B start (weeks to 4B, value of extra time).

## Weekly review (Friday)
1. The week in numbers: net worth and realized profit (main and experiments) vs earlier weeks; by strategy; best and
   worst items; session time (simulated now, the user's real logs once live).
2. Lessons: turn the week's journal entries into 3–5 lessons: what changed, and whether it worked.
3. Direction: right hubs and strategies? Shift capital? Next week's focus and experiments.
4. Grade each day's topic: "changed something / prevented a loss", "marginal" or "nothing". Reassign a topic that
   produces nothing for 2+ weeks (edit the schedule table above, and explain it in the memo).
5. Usage: the week's analysis usage and its trend (see Usage budget). Ask the user before continuing if it runs hot.
6. **Memo** in `reports/<date>-memo.md` (one page: headline numbers, lessons, decisions, next week, questions for the
   user). It must be committed by 5 PM PT. Then a **push notification** with a 2-line summary and the memo's path.
7. **First Friday of the month: the bigger step-back.** Challenge the core assumptions (fill share, fees, competition),
   a "what would make this fail?" exercise, compare with other ways to make ISK (manufacturing, a second character),
   and go-live readiness.
