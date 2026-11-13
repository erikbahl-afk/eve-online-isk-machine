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

## 2026-11-03 · review (recovered: the review's push was refused, so this entry was copied from its transcript)
- Health OK. Net worth 4.98B (−0.48% over 5.9 d), realized −24.2M (broker fees only, no sales yet); 95% of ISK
  deployed (1.6B escrow, 3.1B in transit to Amarr), 7/113 slots. Last session Sat 31 Oct.
- Calibration: median inferred/official ratio 0.42 (Jita), 0.43 (Amarr). Stable and below 1; gone_weight unchanged.
- Variants: no_imports −1.42% vs main −0.48%; loose identical to main. Too early to promote anything.
- Fixed since: calibrate crash (numpy int), and a checklist crash on a blank item name (failed runs 16–17 on Oct 31).
- Infra: GitHub starts the workflow only about every 6 h despite the 2 h cron (asked the user for the
  cron-job.org trigger). The review routine has no repo source, so it can't push (user to add the repo).
- 2026-11-04 · review push test OK

## 2026-11-04 · in-game checks
- Verified: 3% broker / 7.5% tax base, the 4-significant-figure price rule, and a relist charge of 50% × broker × new value
  at ABR 0. The fee model in config.toml needs no change. A jump clone looks installable in Jita 4-4.

## 2026-11-04 · SSO connection
- Training option A: the account's single training slot moves to the trader (no MCT).
- Added `trader/sso.py` (login link, code exchange, refresh) and `trader/character.py` (skills, queue,
  attributes, standings, jump clones → state/character.json, with no name or ID), plus `sso-connect.yml`
  for the one-time code exchange. The refresh token is stored AES-GCM encrypted in state/sso_token.enc
  with a key derived from the ESI_CLIENT_SECRET Actions secret. The summary shows plan progress and ETA.

## 2026-11-05 · bootstrap scenario
- The user says the live start may be as little as 1B ISK, and the session times are a floor: more time in the
  first weeks. Added variants `start_1b` (1B, normal sessions) and `start_1b_more_time` (1B, 60-min sessions,
  2–3 weekday logins). Imports now wait until net worth ≥4B (`import_min_nw`).
- Use these two to set expectations: weeks to grow 1B → 4B, and whether extra early time pays.

## 2026-11-05 · AIR Career Program
- An Omega character earns up to 1.5M SP (750k base + 750k Omega track, per patch 23.01 and the EVE University table);
  Alpha gets 750k. CCP says the program moves into Paragon Services around Fractured Skies (launches Nov 10) and all
  progress resets, so it can be run again; unclaimed rewards are lost at the move. Exact move date and post-reset
  SP not confirmed. Each 1M SP saves about 20 days of training (about 50k SP/day at Cha 27/Mem 21).
- Confirmed on eveonline.com: with Fractured Skies (10 Nov) the ACP moves into Achievements, "all current progress will be
  reset, meaning all capsuleers can complete it again, for rewards and achievements". CCP's advice: claim unfinished
  rewards before the move. The user will fully complete it before and after (2 × 1.5M SP), so expect the trader ready
  around late November or early December instead of late January. Pull the go-live tasks forward to mid-November.

## 2026-11-05 · liquidation gap → import guards
- Practice book value 4.98B, liquidation 2.54B. The 3.1B of Amarr imports would fetch about 0.7B if dumped: the picker had
  chosen SKINs (best bids 0–4% of cost), clothing (1%), a Standup rig (7%) and rare modules (19–46%). Their Amarr asks
  are about 2× our cost, so they're big winners only if they sell. Nothing has listed yet (next simulated login Thu evening).
- Fixes: SKIN and Apparel categories excluded; imports need destination bid × (1 − tax) ≥ 60% of all-in cost
  (`min_exit_frac`). Existing stock is left alone: next week shows whether those thin items actually sell.
- Pipeline: 31 runs since cron-job.org went live, average gap 1.2 h, max 2.0 h.

## 2026-11-05 · player-time features
- Checklist in priority blocks (must / should / if time), ranked by estimated ISK over the next gap per second of
  player time. Paste-ready Multibuy list for import purchases.
- Steps worth less than 0.02% of net worth per minute of player time are left out (`min_step_value_frac`), as
  the user asked (tied to net worth, not PvE income). The number is a guideline for Monday probes.
- `helper/ingame.py`: a local helper with the checklist, "Open in game" buttons (ESI ui/openwindow/marketdetails,
  PKCE login, token stays on the user's PC), tick logging, and a copyable session report. Tested here except
  the EVE login and the real window opening; the user tests it in-game in a few days.

## 2026-11-05 · analysis system (designed with the user)
- Daily Opus 5.5 session (about 15:40 PT) with a weekday topic: Sat risk, Sun fills, Mon picks, Tue competition,
  Wed open questions (then time efficiency), Thu experiments, Fri weekly review + memo by 5 PM PT with a push
  (monthly step-back on the first Friday). Runbook: ANALYSIS.md. Topics are graded weekly and can be reassigned.
- Built: automatic alerts (config [alerts], shown at the top of the summary; every session must address them),
  state/overrides.json avoid/exit lists, experiment kinds (1 bold slot reserved, 1 flex), and the first bold
  experiment `bold_dodixie_imports` (imports only, to Dodixie, no trading inside hubs).
- Usage: ~30 tool calls on weekdays, ~60 on Fridays. Ask the user before going deeper or if usage trends high.

## 2026-11-05 · ESI outage handling
- From about 21:50 UTC ESI returned 504s; runs spent 10–20 min in retries and committed empty data (all hubs "fetch failed").
  A profile confirmed ~100% of the run time was ESI back-off, not our code.
- Now: a quick ESI status check first. If ESI is down, or nothing could be downloaded, the run is skipped in seconds,
  the previous checklist and summary are kept, and an "esi_down" alert with a banner at the top of the summary is raised.
- Fixed: the alerts box reused the `days` variable, so the summary showed "in 0.0 days".

## 2026-11-05 · open questions front-loaded
- The user asked to front-load the open questions before go-live (about late Nov / early Dec). Wednesday now takes two a
  week until go-live, starting with standings and the Perimeter station. Live-only: fill accuracy, Wholesale, Perimeter fee.
- New experiments (one change each): `exports` (reverse trip, hub → Jita), `seeding` (sold-out items at the import hub;
  assumed 50% of the recent sales rate; fills only while no rival sells), and bold `rotation` (Dodixie + Amarr, least
  recently visited next). Retired `loose` (identical to main) and `bold_dodixie_imports`. Still at most 6.
- Code: generic shipping bundles (any src → dst, several per session), items remember their destination, couriers
  carry each item's tag, and portfolios track hub visits.

## 2026-11-05 · experiments (Thursday)
- New `python3 -m trader.scoreboard [--since YYYY-MM-DD]`: main vs variants over the same window (return, realized,
  liquidation, unsold, worst item, fees/turnover, trades, realized without best+worst item). Tested.
- Since 28 Oct: main -0.48% (realized -24M, all fees; liq 51%), no_imports -1.42% (-71M; fees 47% of turnover).
  start_1b_more_time -1.4% (11 buy fills, nothing sold yet). start_1b, exports, seeding, rotation started today and have no
  login yet (first sim login Thu 19:39 PT). Verdict for all six: **extend** (no sale anywhere yet; nothing to judge).
  Slots 6/6 (bold = rotation, flex = start_1b_more_time). Success measures: exports/seeding = realized ahead of main
  with liq ≥ main's; rotation = return ahead of main over 2 weeks at equal liq; start_1b pair = weeks to 4B, and whether the
  extra-time arm leads by more than its extra minutes are worth.
- Finding: broker fee is charged on the full bid at placement, and big thin-item bids barely fill: no_imports paid 71M
  broker on 4.7B of bids that filled 150M (3%) in 7 days. Idea for the next free slot (or Monday/Sunday): probe a
  minimum expected fill rate per bid, or smaller bid quantities on rare items.
- Alerts. Liquidation 51%: known (yesterday's import guards); acceptable until those imports list tonight and get a week.
  Typhoon FI SKIN 8.4%: over 8% only because courier cost entered its basis; Amarr best bid 16M vs 418M cost, the only
  Amarr ask is 816M. Dumping would lose 400M, so hold and list; no new SKINs (excluded). Recheck Saturday (risk day).
  7 idle buys (5 days): no sim login since 31 Oct; live books show 3 outbid (85668 Jita, 18688 and 41202 Amarr) and 4 still
  top in thin markets. Tonight's login reprices. Alerts fine as is.

## 2026-11-06 · weekly review (Friday, first-Friday step-back)
- Memo: reports/2026-11-06-memo.md. Main 4.89B (−2.3%), liq 50%, realized −113.9M (fees only), no sale in any portfolio.
- Alerts. Liquidation 50% and Typhoon FI SKIN 8.6%: the import stock was finally listed Thu (0.8 d ago); hold and give it a week,
  recheck Sat. 7 idle buys (6 d, 1.64B): Thu's login was cut at 56% and didn't reprice them. Live books show 4 outbid
  (85668, 18688, 41202, 47806). Official 30 d regional volume is 1–4/day, at prices near the ask. Our snapshots' bid
  "trades" on them were 0.8-unit events, so one vanished buy order (gone_weight 0.8) was read as a fill. Cause found.
- Changed: overrides avoid (until 2026-11-20) for 85668, 28792, 18688, 41202, 35923, 47806 → bids cancelled, ~1.54B freed.
  Kept 53301 Tetryon XL (7k units/day). Alert thresholds unchanged: every alert was useful.
- Next: Sun fills: count distinct bid events / use official volume before a thin station bid is fillable (with a probe).
  Mon picks: liquidity floor for station items. exports/seeding/rotation identical so far (no import-hub step yet).


## 2026-11-07 · risk and concentration (Saturday)
- Live books (ESI, 23:40 UTC) on every holding: stock costs 3.14B but dumps for only 0.45B (14%). With cash + escrow,
  liquidation is ~45% of 4.89B, not the summary's 50%. Bottom of the list (best bid ÷ cost): Golem Exoplanets SKIN 0%,
  Men's 'Precision' Boots 1%, Typhoon FI XX SKIN 4%, Standup M-Set ME I 7%, Gravid Vorton Mutaplasmid 9%, Capital I-a
  Enduring Armor Rep 18%, 'Cartel' PDS 20%, Low-grade Crystal Epsilon 22%, Valdimar DN-701 25%, Dread Guristas RL 31%.
  All are 31 Oct Amarr imports, bought before the 60% exit check existed; today's guards would block every one of them.
- Bug fixed (trader/sim.py `_liq`): an item with no buy order at all was valued at 50% of cost, which hid ~0.27B of
  stuck stock. Now 0 (the 50% guess stays only when a whole hub's data is missing). Test added. Liquidation will read lower.
- Concentration: top 5 = 37% of net worth, all Amarr imports (one hub, one strategy, one buying day). Only Typhoon SKIN is
  over 8% (8.6%, courier cost in basis). Stress: 3 largest −30% = 7.3% of net worth. No price fell >10% in the daily files.
- Domain 30 d history: real demand exists for Crystal Epsilon (34, avg 293M vs our 248M ask), Cartel PDS (48), Capital
  rep (45), Dread RL (90, but avg 49M vs our 99M ask), M-Set (14, avg 780M vs 700M), Gravid (33). Lottery tickets:
  Golem SKIN (2/30 d), Boots (3), Typhoon SKIN (1); their Jita asks are 95%, 88%, 95% of our cost. Dumping loses ~99%, so
  hold all: no exit entries. Alerts: liquidation and Typhoon 8.6% are true and known; thresholds unchanged.
  7 idle buys: 6 are on the avoid list and get cancelled at the next sim login; Tetryon XL kept (still top bid).
- Unlisted: 3,642 Infomorph Decryption Keys (6 d) and 2,434 Void XL in Amarr. Thursday's cut login missed them; the next
  login lists them. No probe started: 6/6 slots full (Thursday decides). Idea for a slot: a "ship stuck imports back to Jita"
  exit mode, and a min-regional-history (≥1 sale/day) import filter (Monday).

## 2026-11-08 · is the fill model realistic? (Sunday)
- Calibration (7 d, inferred station ÷ official region units): top-60 Jita median 0.64, Amarr 0.65; a random 80 thin items
  (<5 units/day, >5M) per hub: median 0.80 both. Implied bid share (official avg vs our best bid/ask) 22–27% vs inferred 18%
  on thin items, 35–50% vs 26–46% on liquid ones. In aggregate the market inference does not over-count.
- Our own fills do: of 34 paper fills (all portfolios) with official data for that day, 25 were at a price no official trade
  reached (buys below the day's lowest, sells above its highest). Examples: 2993 bought at 382k for 3 days while every
  trade was 646k; 13982 bid 26.6M vs low 38.5M; 1969 sold at 3.48M vs high 2.2M. Cause: in wide-spread markets most
  vanished top bids are cancels, and gone_weight 0.8 credits them as fills at a price nobody traded at.
- Changed: new `[sim] history_gate` (on) / `history_days = 14` and `market.PriceLevels`: every fill is scaled by the share of
  recent trading days whose official low (our buys) or high (our sells) reached our price; 0 blocks the fill; ESI error = no
  change. Test added; 22 pass. Back-test: 10 of 51 buy fills blocked, ISK-weighted reach 0.49 buys / 0.55 sells. Main's
  fills 69M → 22M, start_1b_more_time 436M → 244M. Paper results so far are roughly 2x optimistic on fills; the gate applies
  to every portfolio from tonight, so experiment comparisons stay fair from here (older fills are not rewritten).
- Alerts. Liquidation 51% and Typhoon SKIN 8.6%: unchanged, known (Sat entry), hold. Tetryon XL bid (6,602, 15k units, 99M,
  9 d): sellers hit the 6,601 bid on 2 of ~20 days (33k units on 29 Oct), asks trade at 11.3k: slow but real; keep.
- Not done (budget): time-on-top vs observed, 1 h vs 2 h spacing, gone_weight probe. With the gate in place, the bid-side
  gone_weight matters less; next Sunday measure fills/official volume per portfolio after a week of gated fills.
- Next: Mon picks: the gate's reach (share of days at our price) is a natural pick filter for station bids; consider it.

## 2026-11-09 · audit the picks (Monday)
- Rebuilt today's top 20 Jita station, 20 Amarr station and 20 Jita→Amarr import picks plus holdings, against 30 d official
  region history. Demand is real for most (19–29 trading days of 30) and no pick looks like a spike (7 d ÷ 90 d volume 0.4–2.7).
- The trap is price, not demand: on 33 of 60 picks the official daily high reached our ask (or the low reached our station
  bid) on under 25% of days. #1 import Mid-grade Virtue Omega (26M/day predicted): 0 of 19 days at our 1.04B ask. Gneiss IV
  ask 2,847 vs 30 d avg 2,423 (3%). Rattlesnake, Corpus B hardener, Triplot bids: no trade that low in 30 d. Only ~3 of 20 Jita
  station picks survive. The planner ranked by profits Sunday's fill gate will never pay.
- Changed: `strategy.apply_reach` + `[strategy] pick_min_reach = 0.25`, `pick_reach_top = 40`: the top 40 picks per hub (station,
  import, export) are scaled by that reach and dropped under 25% (one cached history call each, prefetched in parallel).
  Applies to every portfolio, as the fill gate does, so comparisons stay fair. 25% sits between the bad cluster (0–0.12) and the
  good one (0.3–1.0); probe it when a slot frees.
- Alert, stale Infomorph Decryption Keys (3,642, 8.6 d) and Void XL: never listed because a 45 s listing of a 12M stack is under
  min_step_value at 4.9B. New `list_after_days = 3`: stock older than that is always listed. Keys cost 3,356 vs avg 3,526.
- Alert, Tetryon XL idle bid (99M, 11 d): reach about 10%, under the new bar → avoid until 11-20 (bid cancelled). Liquidation 50% and
  Typhoon SKIN 8.6%: unchanged legacy imports (Sat entry), hold. Tests: 24 pass (2 new).
- Next: Tue: does reach shrink station profit/day in the summary, and by how much? Thu: a probe of pick_min_reach 0.15 vs 0.4.

## 2026-11-10 · competition and timing (Tuesday)
- Rival activity (near-top order updates per observed hour, 9 full days): busiest 12–18 UTC (04–10 PT) and 18–24 UTC
  (10–16 PT); quietest 00–06 UTC (16–22 PT). Jita 2,358 → 3,819/h, Amarr 578 → 859/h (~1.5x). Evening logins (18–22 PT)
  reprice into the quiet block, then face the busy stretch; morning logins (06–07 PT) land at its start. Weekdays: Wed/Sat
  busiest (Jita 8.5B/day inferred), Tue lowest (6.0B); one or two samples per weekday, so not yet a signal to act on.
- Our 102 order lines: 7 see 19–40 near-top updates/day in all four blocks (Remote Sensor Dampener II, Antikythera Element,
  Armor Plates, Chemal/Harvest/Tetrimon boosters, ElectroPunch); sells there were undercut 5 of 6 times. The model already gives
  them ~0 survival, so no avoid entries. 1–2 h snapshots can't separate a minute-level bot from busy humans.
- Time on top, live check (143 paper orders, ESI now vs `sim.hazard`): model predicts 12% still first in line, observed 41%.
  Survival is flat ~30% across hazard 3–44, not exponential; best single scale ≈ 0.1x the hazard. Undercut gap median 1.3%.
  One snapshot of correlated orders (most last repriced Sunday, ~50 h), so not adopted.
- Changed: `sim.top_check` + every run appends (portfolio, hub, type, side, age, pred, top) to `state/time_on_top.csv`
  (seeded with today's 143 rows). Test added; 25 pass. Thu/Sun: with ~1 week of rows, fit a hazard scale or a "floor" and
  run a probe (judged on official volume match). Slots are 6/6, so no probe started today.
- Alerts: liquidation 50%, Typhoon SKIN 8.6% (legacy imports, hold); Infomorph keys (listed at next login via list_after_days);
  Tetryon XL bid (avoid since Mon, cancelled at the next sim login; none since Sun). All acceptable; thresholds unchanged.
- Data gap: no collector runs 08 Nov 00:55–21:23 UTC (20 h > max_gap 12 h), so Sunday has 3.7 h of data. Watch for repeats.

## 2026-11-11 · open questions: standings, Perimeter Keepstar (Wednesday)
- Standings (Q2), closed. Character has 0.0 Caldari State / 0.0 Caldari Navy. Each faction point saves 0.03 pp of broker
  (2% of the 1.5% fee), each corp point 0.02 pp (1.3%). Paper broker fees per year: main 3.9B (89% Amarr import listings,
  which Caldari standings don't touch), no_imports 2.6B Jita, start_1b 1.0B Jita; roughly half after Sunday's fill gate.
  Corp 5 / faction 2 (-0.16 pp, 11%) is worth ~55–140M/yr; max 10/10 (-0.5 pp to the 1% floor) ~150–430M/yr. Cost: tens of
  hours of Navy missions on a 420k-SP trade-only character, delaying the 79-day skill plan. Not worth it; revisit when real
  Jita broker fees pass ~1B/yr (around 15B net worth). STRATEGY.md updated.
- Perimeter (Q3 + Q9), started. No ESI secret in this session, so the bot must read it: new `trader/structure.py` +
  `[structure]` config. Each run with SSO finds the Tranquility Trading Tower via the character's structure search
  (fallback id 1028858195912), pulls `/markets/structures/{id}/` and writes `state/structure.json`: median ask vs Jita,
  share of items cheaper than Jita, bids with range >= 1 jump that outbid Jita's best (Q9). Errors go to health, never
  break the run. Test added; 26 pass. Next Wednesday: judge from ~1 week of files (and check the scope was granted).
- Alerts: liquidation 50% and Typhoon SKIN 8.6% are the known legacy imports (Sat entry), hold. Stale Amarr stock (Keys, Void
  XL, 1 Legion missile) and the Tetryon XL bid (avoid since Mon): no sim login since Sun 08 Nov (next Thu 12 Nov 21:10 PT),
  so list_after_days and the avoid cancel haven't had a chance to act; expected to clear Thursday. Gneiss III idle bid is
  2.33k ISK: noise. Thresholds unchanged.
- Next: Thu experiments (slots 6/6; reach probe 0.15 vs 0.4 is waiting); Thu night confirm the stale stock got listed.

## 2026-11-12 · experiments (Thursday)
- Scoreboard since 11-05 23:02 UTC (only 2 sim logins in the window: Thu 05, Sun 08): main -1.88% (legacy imports, liq 50%),
  no_imports -0.15% (liq 100%), start_1b -1.40% (realized -14M), start_1b_more_time +4.48% (realized +30M, +20M without its best
  and worst item, 48 trades vs 19), exports -0.30% (liq 77%), seeding -0.64%, rotation -0.61% (both liq 88%). No import sold
  anywhere: the 11-05 variants' 12 Amarr imports (arrived 11-06) were never listed on Sunday (no Amarr sell broker fee).
- Exports and seeding: their plans now list that stock first (list_after_days, added Mon), so tonight's login (21:10 PT) fixes it.
- Bug, rotation: it ships to Amarr but the next login picked the least-visited hub, Dodixie, so ~2.9B of stock sits unlisted
  in Amarr while the sim is in Dodixie. New `Planner.next_import_hub`: go where unlisted stock is waiting or arriving, else the
  least-visited hub. Test added; 27 pass. Rotation still returns via Jita first, so its stock lists one session late.
- Verdicts: all six **extend** (two logins, nothing imported has sold; no basis to adopt or kill). Rotation's clock restarts
  today (fix); exports/seeding judged from tonight. start_1b pair: extra time leads by ~44M/week on 1B. Projection: at +3%/wk
  (more_time) 1B → 4B takes ~45 weeks, start_1b is flat to negative; one week, fill-gated only since Sun, so not yet a forecast.
- Caveat: main carries pre-11-05 legacy imports, so seeding/rotation (~-0.6%) are the best proxy for "fresh main".
- Slots 6/6 (bold rotation, flex start_1b_more_time); reach probe (pick_min_reach 0.15 vs 0.4) still waiting for a slot.
- Alerts: liquidation 50% and Typhoon SKIN 8.6% (legacy imports, hold, as Sat). Stale Amarr stock (Keys, Void XL, Legion missile)
  and the Tetryon XL bid (avoid): no sim login since Sun; tonight's login lists/cancels them. Gneiss III bid (2.33k): noise.
- Next: Fri review: confirm tonight listed main's and exports/seeding's Amarr stock; first import sales.

## 2026-11-13 · weekly review (Friday)
- **Outage:** every bot run since 13 Nov 04:00 UTC failed (≈10 runs, ~20 h): exports' first return courier Amarr → Jita hit
  `cfg["routes"]["jita"]` → KeyError, aborting main too; Thursday's 21:10 PT sim login never ran. Fixed: `Sim.courier` uses the
  source hub's route for return trips; `run.py` catches a variant failure, logs it to health (→ alert) and carries on. 28 pass (1 new).
- Week: main 4.88B (flat vs 4.89B on 11-06), realized −117.5M, liq 50%; scoreboard since 11-06 in the memo (more_time +4.48%,
  the rest −1.4% to −0.15%). 2 sim logins only (Thu 05, Sun 08). No import sold anywhere in 16 days.
- Live check of main's 10 Amarr sells (3.09B at cost): asks ~2x cost, mostly at or near the 30 d high; 30 d region trades 1–49.
  Low-grade Crystal Epsilon: best ask 137M vs ours 247.7M, cost 148.4M, 30 d high 394.7M → exit (fast). SKINs (Typhoon 419M,
  Golem 389M): 1 and 2 trades in 30 d, no bids: hold to Thu 19 Nov, then write off or reprice.
- Alerts: liquidation 50% / Typhoon SKIN 8.6%: see above (decision Thu). Stale Amarr stock, Tetryon XL avoid and the Gneiss bid
  were all waiting on Thursday's login, which the outage blocked; they should clear on the next run. Thresholds unchanged.
- Perimeter structure.json looks off (6,168 of 6,241 buys "reach Jita"; 370 sells; asks 99% under Jita): check the parser Wed.
- Memo: reports/2026-11-13-memo.md. Next: confirm the 00:00 UTC run succeeds and the missed login executes.
