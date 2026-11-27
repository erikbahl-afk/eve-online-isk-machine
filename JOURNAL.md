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
- Verified: a manually triggered run at 23:44 UTC succeeded (no variant failures); exports ran its session (−15M → −67M realized).
  The 5 'gap 19.7h' data alerts come from the outage and clear themselves. Main's summary still lists no Thu 12 login: Sat checks
  whether the missed login was skipped for main. Memo: reports/2026-11-13-memo.md.

## 2026-11-14 · risk and concentration (Saturday)
- Live Amarr/Jita books vs main's holdings (3.91B at cost incl. 791M courier landing Tue 17): bid value 1.40B (36%). Bottom
  exits (bid/cost): both SKINs 0.00 (no bids, no other asks), Boots 0.01, M-Set ME 0.07, Cap I-a rep 0.20, Valdimar 0.26,
  Void XL 0.32, Crystal Epsilon 0.34, Dread Guristas RL 0.44. All 10 are pre-guard legacy imports (min_exit_frac 0.6 would block
  them today); the new courier's 10 items all pass (0.60–1.10). Top 5 = 37% of NW, 8 positions over 5%, Typhoon SKIN 8.6% (cost
  basis, can't trim). ~80% of NW sits in one hub/strategy (Amarr import). Stress: top 3 −30% = −356M = 7.3% of NW.
- Guard gap 1: `valuation` counted in-transit stock at full cost. Now valued at the destination's bids → liquidation drops from
  50.4% to ~48%: below the 50% push line (pushed). Guard gap 2: a sell order on top (or the only seller) was never repriced, so
  9 legacy asks sat at ~2x cost with 0 fills for 10.7 d. New `stale_step = 0.10`: past stale_days, unfilled, not repriced for a
  day → cut 10% per session, never below the stale floor (break-even −3%). Tests added; 29 pass. Crystal Epsilon exit still
  pending (our 154M vs best 137M): main hasn't been in Amarr since Fri's override; next Amarr visit fires it.
- Main's Thu 12 login did run (caught up Fri 13 15:43 PT after the outage, 32/32 steps, amarr→jita).
- Alerts: stale sells → step-down above; liquidation / Typhoon → legacy, the step-down is the remedy; idle bids (2.3k, 2.25M) noise.
  Thresholds unchanged. No risk probe: slots 6/6.
- Next: Sun/Thu check the step-down fired at the next Amarr visit and whether any legacy item sells; Thu 19 SKIN decision stands.

## 2026-11-15 · is the fill model realistic? (Sunday)
- Own fills since the history gate went live (09 Nov 04:00 UTC, all 7 portfolios) vs official region history: ISK-weighted
  97% at a price an official trade reached that day (last week 25 of 34 fills were outside). No fill took >30% of a day's
  official volume (median 0.05%). Main's one big sale, Cap I-a rep at 199.7M, matches 1-unit official trades at 199.8–199.9M.
  ~416M of today's fills can't be checked until CCP publishes 15 Nov history; recheck the Hezorime buys (5 portfolios, 23.8M each).
- Gate hole: history 404 ("Type not found", never traded) was treated as an ESI error (reach 1.0), so Chemal Tech Turret
  Booster III sold for 3.39M in start_1b_more_time with no trade ever recorded. 404 now = empty history = blocked.
- Calibration fell to 0.47 Jita / 0.54 Amarr, but 11-08 and 11-13 (outages) only had 17% / 25% coverage and counted as full
  days. `calibrate.full_days` now drops days under 60% of the window's median ISK: 0.665 Jita / 0.745 Amarr (5 days), in
  line with last week's 0.64 / 0.65. One Jita item at 2.05 (over-count), not chased. alpha / gone_weight left unchanged.
- Bug, Saturday's stale step-down: when we're the only seller (best ask NaN), the expected-fill "stale" check caught the order
  first and planned a same-price modify, so the 10% cut never ran (only Valdimar was cut, 249.8M → 224.8M). Now a modify that
  wouldn't change the price falls through to the step-down. Typhoon SKIN (815.9M ask, cost 418.5M) and the other only-seller
  asks now drop 10% per Amarr session down to their floor. Tests added (2); 31 pass.
- Alerts: liquidation 50% / Typhoon 8.4%: legacy imports, the step-down (now working) is the remedy, Thu 19 SKIN decision
  stands. Stale Amarr sells: same fix. Antikythera (Jita, 7 d) under stale_days. Idle bids 2.3k / 2.25M: noise. Thresholds kept.
- Not done (budget): time on top vs snapshots, 1 h vs 2 h spacing, gone_weight probe (slots 6/6 anyway).
- Next: Mon check the next Amarr session cut the SKIN/M-Set/Boots asks; Sun 22 recheck 15 Nov fills vs official history.

## 2026-11-16 · audit the picks (Monday)
- Checked 46 lines against live books and 30 d official history: the 10 items on the courier landing Tue 17 (722M), main's
  14 sell orders, today's 12 Jita station and 12 Jita→Amarr import picks.
- Courier is clean: every item traded 30 of 30 days, Amarr bid ÷ cost 0.66–0.95, reach 0.43–1.0. No spikes, no SKINs.
- Import picks look sound (reach 0.27–0.90, 30/30 trading days). #1 Republic Fleet Mining Survey Chipset is drifting down
  (90 d avg 281M → 30 d 247M → 7 d 216M; our ask 204M), but the margin is 77% and the Amarr bid is 0.7 of cost. Not a trap.
- **Gap found:** `apply_reach` only checked the top 40 picks. In Jita only 2 of those 40 passed, so rows 3–12 of the station
  table were never checked: Tachyon Beam Laser II (reach 0.00 over 14 d), Zealot (bid side 0.14) and others were being
  planned. Fix: check in chunks of 40 until 40 picks pass, up to 120 rows per list (`max_check`). Worst case is about
  +700 history calls per run, cached. Test added; 32 pass.
- Legacy holdings: Dread Guristas RL asks 99.2M vs a 7 d avg of 66.1M (reach 0.07). Antikythera (Jita) asks 996k vs 559k
  best, price down 37% in 90 d (6.8M total). The stale step-down covers both. Golem SKIN at 175M (2 trades ~295M) should sell.
- Alerts: liquidation 50% and Typhoon SKIN 8.4% are still the legacy imports; the SKIN decision stays Thu 19. The stale Amarr
  sells have had no Amarr session since Sat, so the step-down hasn't fired yet. Idle bids (2.3k, 2.25M) are noise.
  Thresholds kept.
- Next: Tue, check the Jita station count and profit/day after the fix, plus run time and ESI calls. Thu, the SKIN decision.

## 2026-11-17 · competition and timing (Tuesday)
- Time on top, 1 week of `state/time_on_top.csv` (22,463 rows, 13,942 unique by time/hub/item/side): model predicts 15% of
  our orders still first in line, observed 40%. Up to ~12 h the model is calibrated (age 6–12 h: pred 0.39/0.34, obs 0.40/0.38
  buy/sell). Past 24 h it predicts ~0.03–0.10 while observed stays 0.25–0.36: a floor, not a rate error.
- Fit P(top) = f + (1−f)·exp(−k·H): f 0.33, k 1.4 (log-loss 10.5k vs 53.7k as-is, 13.4k for a scale alone). By book: Jita buy
  f 0.30 k 0.9, Jita sell 0.25/0.5, Amarr sell 0.52/3.0, Amarr buy 0.08/0.5. Per item it's bimodal: of 146 items seen 10+
  times past 24 h, 66 never on top, 30 always. Rival rate barely separates them (median 0.18 vs 0.09 updates/h); the "busy"
  boosters from last week (Tetrimon, Chemal, Harvest, Antikythera) are always-on-top bids, so near-top updates overcount rivals.
- Timing: share on top past 24 h is flat by UTC block (0.40–0.41) and weekday (0.35 Mon to 0.51 Fri, n=354). No timing signal.
- Changed: `[sim] top_floor` / `hazard_scale` (defaults 0 / 1, so nothing changes) used by sim fills and planning survival, to
  allow a probe. Not adopted in main: it raises paper fills, and only 1 week of rows so far (11-10's snapshot agreed).
- Alert fix: the stale step-down skipped partly-filled orders forever (Cap I-a rep, 1 of 3 sold, untouched since 11-08). Now
  a partial fill blocks it only if the order was touched within stale_days. The Tue 06:56 Amarr session did step the others
  (Typhoon SKIN 815.9M → 734.3M, M-Set, Boots, Golem, Valdimar...). 34 tests pass.
- Alerts: liquidation 50% / Typhoon 8.5%: legacy, being stepped down, SKIN decision Thu 19. Antikythera (Jita, 9 d) under
  stale_days. Idle bids 2.3k / 2.25M: noise. Thresholds kept. Mon follow-up: run 43 s, 1,255 ESI calls: fine after the fix.
- Next, Thu: consider swapping a slot for a fill probe (top_floor 0.3, hazard_scale 1.0), judged by match to official volume.

## 2026-11-18 · open questions: Perimeter Keepstar (Q3), structure bids (Q9), Wholesale (Q4) (Wednesday)
- Perimeter reader ran 16 times since Mon 16 06:00 UTC (the scope got granted then). Stable: ~6,500 orders, only ~373 sells,
  median ask 1.05–1.07x Jita 4-4, 25–28% of shared types cheaper. Not a better place to buy or sell: Q3 closed.
- Buy side is the story: ~6,100 bids on ~3,850 types, 99% with range 1+ jumps, ~780 types bid above Jita 4-4's best. The
  public region feed (`/markets/10000002/orders/`) already carries these structure orders, but `station_book` kept only 4-4.
  Live check on main's 15 Jita bids: 11 (541M) have Perimeter bids (range 1-5, all system 30000144) above our price that the
  model didn't see, and on 2 (34595, 83471) a Perimeter bid is the real top. So the paper bids were being put "first in line"
  when they weren't: one more reason for optimistic paper fills.
- Changed: ESI order frames keep `system_id` / `range`; new `[reach] jita = {30000142 = 0, 30000144 = 1}` adds bids whose range
  covers 4-4 to the Jita book (queue, best bid, inferred volume). Test added; 36 pass. structure.py's top list now skips junk
  0.01 ISK Jita bids (the gap was 1e9x). Q9 answered (rivals do it); placing our own Perimeter bids waits for go-live (fee).
- Q4 Wholesale: 41/113 slots, ISK 97% in use: capital is the limit. Parked.
- Expect: Jita inferred volume up a little (Perimeter fills now count), so Sunday's calibration (0.665 Jita) should rise; paper
  Jita bid fills a little lower. Check Sun that calibration didn't overshoot 1.0 and the run time is unchanged.
- Alerts: same as Tue. Liquidation 50% / Typhoon SKIN 8.5%: legacy imports being stepped down, SKIN decision Thu 19. Stale
  Amarr sells: step-down fired Tue 06:56, next Amarr session continues it. Antikythera (Jita, 10 d): now at stale_days, step-down
  applies from here. Idle bids 2.3k / 2.25M: noise. Thresholds kept.

## 2026-11-19 · experiments (Thursday)
- Scoreboard since 11-05 23:02 UTC: main −0.25% (liq 50%, legacy), no_imports −0.79% (realized −110M, fees 23% of turnover),
  start_1b +0.60%, start_1b_more_time +4.70% (realized +32M, +23M w/o best+worst), exports −1.78%, seeding −1.89%, rotation
  −1.78% (liq 84–89%). Since 11-12 the 1B pair flipped: start_1b +2.03% vs more_time +0.21%, so the extra-time lead is noisy.
- The three "open question" variants are near-identical (realized −89 to −94M): each did 1 import courier of 12 items (11-05)
  and none since. Seeding placed **0** seeds in 14 days (it rides on imports). Rotation went to Dodixie once (1 bid), never
  shipped there. Exports bought 4 items in Amarr (1.01B, incl. 399M and 248M singles), sold 1 of 11 units (40M): 1B tied up.
- Verdicts: seeding **kill** (no signal possible until imports cycle). exports **extend** 1 week, kill Thu 26 unless the
  export stock sells (it lowers liq vs peers). rotation (bold) **extend**, kill Thu 26 if still no Dodixie courier. start_1b
  pair, no_imports **extend**. Open question for Sun/Mon: why no second import courier in 14 days with 0.25–0.6B cash.
- New slot: `fill_floor` (regular), `[sim] top_floor = 0.3` only (Tue fit f 0.33). Success = its paper fills per item closer
  to official volume × alpha than main's, without overshooting; profit not the measure. Slots 6/6 (bold rotation, flex more_time).
- Projection 1B start: more_time ~+2.3%/wk → 4B in ~60 weeks; start_1b ~+0.3%/wk → no forecast. Fill-gated, 2 weeks: weak.
- **SKIN decision** (Typhoon FI SKIN, cost 418.5M, ask 734.3M Amarr): live Amarr history = 1 trade in a year (778M, 10-29),
  no Amarr bids; Jita ~1–2 trades/month at 400–449M, asks 398–448M, best bid 142M. Dumping = −66%. Decision: no dump; the
  stale step-down keeps cutting 10% per Amarr session to the break-even floor (~5 sessions). Accept the 8.4% alert until then.
- Alerts: liquidation 50% / Typhoon 8.4%: legacy imports, above. Stale Amarr sells: step-down firing each Amarr visit (Tue).
  Antikythera (Jita, 11 d): step-down now applies. Idle bids 2.3k / 2.25M: noise. Thresholds kept. 35 tests pass.

## 2026-11-20 · weekly review (Friday)
- Week: main NW 4.877 → 4.953B (+1.55%), realized −122.6 → −47.1M (Cap I-a rep 199.7M legacy sale 11-14; Archiver 49.7M vs
  22.8M cost). Relists 45 / 41M this week (38M on Amarr legacy step-downs): realized slid −35.5 → −47.1M since Sun on fees.
- Scoreboard since 11-13: start_1b +2.45%, more_time −0.13%, no_imports −0.75%, rotation −1.35%, exports −1.73%, fill_floor −0.37%.
- Idle-bid alerts (8 Jita bids, 6 d): live Jita book (with Perimeter reach) has rivals ahead of 15 of main's 17 bids (2–23
  orders, ~0.84B of 1.08B escrow). Cause: maintenance keeps a bid that is still "selected" and re-bids at min(cap, tick_up(bb)),
  so a bid capped below the top sits forever (Entosis, Jaguar, Quad Pulse untouched 6 d). Fix: `[strategy] buy_stale_days = 5`
  cancels bids with remain == qty, older than 5 d, best bid ≥ ours and tick_up(best) > cap. Test added; 36 pass. ~0.56B frees at the next Jita login.
- Overrides: 7 avoid entries expired today, removed (reach filter + history gate cover them). Crystal Epsilon exit kept (2 left).
- Other alerts: liquidation 50% / Typhoon 8.4%: legacy, step-down continues (Thu decision). Stale Amarr sells: step-down each
  Amarr visit. Antikythera (Jita, 12 d): step-down applies. Thresholds kept.
- Grades: all 7 topics "changed something"; no reassignment. Usage ~22 calls/day, flat vs baseline.
- Memo: reports/2026-11-20-memo.md. Next: Sat check cancels freed escrow and new bids sit on top; Thu 26 exports/rotation kill.

## 2026-11-21 · risk and concentration (Saturday)
- Liquidation ratio by week: 0.503 (11-06) → 0.504 → 0.497 (11-15) → 0.499 → **0.515** today. Flat; stock 3.67B, of which the
  11 legacy Amarr sells (3.13B, 16 d) have no bid at all, so they count 0. New imports (4 d) exit at 0.82–0.99x cost: healthy.
- Concentration: top 5 = 36.5% of NW (Typhoon SKIN 8.4%, Golem SKIN 7.8%, Valdimar 7.6%, M-Set 6.7%, Crystal Eps 6.0%), all
  legacy; 99.8% of stock in Amarr, all import. Stress: top 3 −30% = 356M = 7.2% of NW. No push (liq > 50%, max 8.4% < 15%).
- Step-down check: legacy sells repriced 1.7 d ago (Thu 21:08 Amarr session) but still 1.1–2.3x cost (Cartel 2.26x, Dread
  2.10x, Typhoon 1.58x); at 10%/session and ~2 Amarr visits/week that's 2–4 more weeks to the floor. Idea for Thu 26 slot
  refill: probe `stale_step = 0.2`, judged on liq ratio and realized vs main.
- Falling: Zero-Point Mass Entangler (16, 137M) Amarr ask −10.3% in a week, exit still 0.90x. Watch Mon.
- Guards: nothing new got through; everything flagged predates the history gate / reach filter (11-05 import).
- Changed: Antikythera Element (Jita, 13 d untouched, ask 0.54x cost, below the stale floor so step-down can't act) → exit
  list, fast (~3M loss). Alert tuning: stale-sell alerts on orders repriced < `stale_handled_days = 3` days ago are now
  "info" with "step-down working", so untouched ones stand out. Test added; 37 pass.
- Alerts: liquidation 51% / Typhoon 8.4%: legacy, as above. Idle Jita bids (8, 0.84B): the buy_stale_days fix landed after
  the last Jita login (Thu 21:08), so they clear next Jita session — check Sun. Infomorph Key / Void XL / Mordunium (8 d) under
  strategy stale_days 10. Crystal Epsilon exit still working (2 left, 0.92x).

## 2026-11-22 · is the fill model realistic? (Sunday)
- Calibration (7 days, `full_days` filter): Jita median 0.662 (0.665 last Sun), Amarr 0.757 (0.745). The Perimeter reach
  (Wed) didn't move Jita and nothing overshoots 1.0 in Jita (max 0.985); one Amarr item at 1.67. alpha / gone_weight kept.
- Own fills since 11-15, all 7 portfolios (202 fills, 138 checkable, ±1 day vs region history): ISK-weighted 88% inside the
  official range, 11% conservative (sold lower / bought higher than any trade), 1% optimistic. Cap I-a rep 199.7M matches.
  Median fill = 1.4% of the day's volume, but Hezorime (82314) bids filled 30.6k units = **57%** of the 11-15 day, in 5
  portfolios at once (vanished big bids counted as trades). New `[sim] max_day_share = 0.3`: one paper fill takes at most 30%
  of the 14-day median official day volume (min 1 unit). Test added.
- Idle Jita bids still there after today's 09:08 Jita session (Fri's buy_stale fix): time_on_top shows Entosis Link II and
  Jaguar at 0% on top (288 / 432 checks), but their cap could still re-top them, so they got a modify step worth ~0 (bid-side
  rate ~0) that the planner dropped as low-value: untouched 8 days. `buy_stale_days` now cancels any never-filled bid behind a
  rival after 5 d, capped or not (test extended). Frees ~0.3B more at the next Jita login. Quad Pulse (90% on top, 0 fills in
  8 d) is a real no-sellers case and stays.
- Alerts: liquidation 51% / Typhoon 8.4%: legacy, step-down continues (Thu 19 decision). Idle Jita bids: fixed above. Stale
  Amarr sells: info, step-down working. Antikythera: on the exit list since Sat, next Jita session. Infomorph Key / Void XL /
  Mordunium (9 d) under stale_days 10. Thresholds kept. 38 tests pass.
- Not done (budget): time-on-top by time of day, 1 h vs 2 h spacing, gone_weight probe (slots 6/6).
- Next: Mon/Tue check Entosis/Jaguar/Siren/Bomb Launcher bids cancelled at the next Jita session and fill counts after the cap.

## 2026-11-23 · audit the picks (Monday)
- Checked 71 lines (main's 40 orders + 3 stock lots, 12 Jita station + 12 Jita→Amarr import picks) vs live books and 90 d history.
- **Bug:** exit-list sells at a loss have benefit ~0 (no profit over cost), so the planner's low-value filter dropped them:
  Antikythera (on the exit list since Sat) still asks 1.00M vs best 0.26M after two Jita sessions, untouched 15 d. New
  `Planner.forced()`: exit-list sell/cancel steps and avoid-list cancels always pass the filter. Test added; 39 pass.
- Import picks: 11/12 trade 15–30 of 30 days with Amarr bid ≥ 0.69x Jita cost. Watch two rising Amarr prices: Imperial Navy
  Small Armor Repairer (90 d avg 26M → 7 d 41.8M, 26 units/30 d; downside small, Amarr bid 16M ≈ Jita cost) and Corpus X-Type
  Thermal Hardener (356M → 482M, bid 0.69x cost). Neither is a trap yet; profit/day 3.4M / 5.5M.
- Station picks: Mid-grade Rapture Gamma's 84% margin rests on a 239.9M ask vs 7 d avg 200.6M / 30 d 168M (margin overstated,
  1.7M/day). Federation Mobility / State Defense Booster III and SARO booster have only 11–13 days of history (new event
  items); prices flat so far (Fed Mobility 7 d 39.7M vs 30 d 40.7M, but our sell target 52M). Idea: an age/history-days gate.
- Holdings: no new trap. 'Cartel' PDS last-7-day trades at 24.5M (the bid) vs our 68M ask; step-down continues. Gravid Vorton
  has no live Amarr seller (7 d avg 81M, ours 67.7M). Void XL / Infomorph Key asks sit above the best ask (small, ~20M total,
  low-value drops by design). No push: no large position looks like a new trap.
- Alerts: liquidation 53% / Typhoon 8.3%: legacy, step-down continues (Thu 19 decision). Stale Amarr sells: info, step-down
  working. Antikythera: fixed above. Idle Jita bids: buy_stale_days applies at the next Jita session. Thresholds kept.
- Next: Tue confirm Antikythera relisted at ~0.26M and Entosis/Jaguar bids cancelled; Thu slot refill candidates: stale_step 0.2, history-days gate.

## 2026-11-24 · competition and timing (Tuesday)
- Rival activity, 14 daily files (11-10..23): near-top updates/h per traded item by UTC block, Jita ask 0.22 / 0.26 / 0.38 /
  0.33 (00-06 / 06-12 / 12-18 / 18-24), bid 0.13 / 0.16 / 0.23 / 0.21; Amarr ask 0.11 → 0.19. Quietest block is 00-06 UTC,
  ~1.7x less than 12-18; the sim's per-block rates already carry this. By weekday rivals are flat (Jita 0.44 Tue – 0.51 Mon).
- Demand by weekday (traded ISK/day): Jita Tue 7.0T vs Sun 9.4T (+34%), Amarr 0.84T vs 0.98T, Sat/Sun top everywhere. Paper
  fills come from real snapshots, so the sim sees it; planning uses 14-day averages (fine at our ~4 sessions/week).
- Bots (≥1 near-top update/h in all 4 blocks on ≥5 of 7 days): 20 Jita books, none Amarr; none of main's 45 orders are on one.
  No avoid entries needed. Rising competition (last 3 d ≥2x prior 7): Zorya's Entropic Disintegrator bid (0.21 → 0.53/h,
  outbid 11 h after Mon's placement) and State Security Token bid (0.36 → 0.98/h, yet on top in every check): watch only.
- Time on top, out-of-sample since 11-23 00Z (1,335 main rows): the floor holds: age > 24 h obs 0.33–0.79 vs pred 0.08–0.35;
  refit f 0.28 k 0.5 (11-17: 0.33 / 1.4). Flat by UTC block (0.47–0.50). Jita buy 0.35 obs vs 0.04 pred; Amarr sell 0.65 vs 0.30.
- Why the near-top count misleads: State Security Token ~1 update/h yet always on top: most "updates" sit within 5% behind us.
  Changed: daily files now also log `ask_beat` / `bid_beat` (updates priced strictly better than the previous snapshot's best,
  i.e. real undercuts). Logged only, no model change; Day cache rows from before are reindexed. Test added; 39 pass.
- Follow-ups: Antikythera relisted 996k → 197.9k at Mon 20:15 (forced() fix works). Entosis/Jaguar bids cancelled (not in orders).
- Alerts: liquidation 55% / Typhoon 8.2%: legacy, step-down continues (Thu 19 decision). Stale Amarr sells (10 medium, 7–19 d):
  step-down each Amarr visit; Golem SKIN / Gravid Vorton untouched-flagged but at or under best ask (Mon audit). Idle Jita bids
  (Bomb Launcher 40.5M on top in 59% of 175 checks and now: no sellers, like Quad Pulse, kept; Fullerite 11.2M 7 d, dust).
  Thresholds kept.
- Next: Thu judge fill_floor (2 weeks of floor evidence now), refill slots (stale_step 0.2, history-days gate). Tue 12-01: fit
  P(top) on beat-rate vs near-top rate with a week of `*_beat` data; switch lam to beats if it fits better.

## 2026-11-25 · open questions: import hub (Q1) + outage (Wednesday)
- **Outage, my regression:** all 12 bot runs from Tue 24 22:01Z to Wed 22:00Z failed with KeyError ['ask_beat','bid_beat']
  at the day-rollover flush. The cached 11-24 Day held rows built before Tuesday's change, and `Day.frame` didn't fill
  missing columns (only `add` reindexed). Fixed in e7ed9e9 (frame fills missing SUM_COLS with 0), with a regression test that
  fails on the old code. Pushed ~23:50Z. Push sent. Lost ~1 day of snapshots; no sim login missed (next Sat 28 19:48 PT).
  Lesson: a schema change to cached state needs a test that loads the old shape.
- Q1 (which import hub?): import profit/day from the best 30: Dodixie 104.5M vs Amarr 79.5M in the last summary. Amarr led on
  11-22 (131M vs 109M), Dodixie on 11-23/24. Can't check "2 weeks running": summary history before 11-22 got squashed, and
  nothing else logs per-hub numbers. Changed: main now appends `state/hubs.csv` each run (per hub: station/import items and
  top-30 profit/day). Test added; 40 pass. Also the rotation experiment (Dodixie+Amarr) is −2.49% vs main +2.41%, but it has
  barely run a Dodixie courier (Thu 26 kill date). Q1 stays open: judge from 2 weeks of hubs.csv (~Wed 12-09).
- Second question skipped (budget spent on the outage). Next Wed: Q4 Wholesale recheck, or a new question from the
  history-days gate idea (Mon).
- Alerts: same 29 as Tue, no new data since then (outage). Liquidation 55% / Typhoon 8.2%: legacy, step-down continues (Thu 19
  decision). Stale Amarr sells: step-down each Amarr visit. Idle Jita bids: Bomb Launcher on top with no sellers (Tue), others
  are dust. Thresholds kept.
- Next: Thu check the first runs after the fix committed data (daily 11-25 file, ask_beat present); judge fill_floor and the
  rotation kill date.

## 2026-11-26 · experiments (Thursday)
- Scoreboard from 11-20 (fill_floor's start): main +3.16% (liq 54%, legacy), start_1b +1.84%, start_1b_more_time +0.02%,
  no_imports −0.81% (fees 16.5% of turnover), exports −0.38%, rotation −0.72%, fill_floor −1.09% (realized −54M, mostly fees on new stock).
- **Why imports stall (Q from 11-19):** main has shipped 2 couriers in 29 d (10-31, 11-13), fill_floor 1, exports/rotation 1 each.
  A contract needs min_contract_fill 0.6 × 1.5B = 0.9B of cargo, but main has 450M cash with 1.01B in Jita station bids
  (station realized −52M vs import +173M). The 0.6 gate is right on cost (Amarr fee 69M ≈ 7.7% of 0.9B), so cash is the issue.
- Verdicts: exports **kill** (1.04B Amarr export stock, 126M sold in 20 d, 248M + 399M singles untouched). rotation (bold)
  **kill** (1 Dodixie bid, 0 Dodixie couriers in 21 d). fill_floor **extend** to Tue 12-01: the floor holds out of sample
  (Tue refit f 0.28 vs 0.33), but paper fills come from prints, so it only changes picks; adopt top_floor 0.3 in main then if
  the beat-rate fit agrees. start_1b pair, no_imports **extend**.
- New: `station_enabled` knob (new_buys skips station bids; test added). Bold `imports_only` (station_enabled false). Success
  by Thu 12-10: ≥1 courier/week, return and realized above main over the same dates, liq ≥ main. Flex `stale_step_20` (Mon's
  idea): success = lower unsold share and higher liq than main without realized falling below main's (shows from ~12-06).
  e2e test now adds its own rotation variant so that code stays covered. Slots 6/6 (bold imports_only, flex stale_step_20).
- Projection 1B start: start_1b ~+0.8%/wk, more_time ~+1.1%/wk → 4B in 2.5–3.5 years. Both are station-only by design
  (import_min_nw 4B), and station trading is the weak leg. Idea for next Thu: a 1B variant with import_min_nw 1B, 1 contract.
- Alerts (29): liquidation 54% / Typhoon 8.2%: legacy, step-down continues (Thu 19 decision). Stale Amarr sells: step-down each
  Amarr visit. Idle Jita bids: Bomb Launcher kept (on top, no sellers), the others are dust. 11-25 daily file missing = the outage
  day (confirmed). Thresholds kept.
- Next: Fri memo: raise the station-vs-import capital split with the user; Sat check imports_only/stale_step_20 started cleanly.

## 2026-11-27 · weekly review and memo (Friday)
- Week: main NW 4.95B → 5.12B (+3.4%; +2.41% since 10-28), realized −47.1M → +120.6M, liq 50% → 54%. Capital I-a Enduring
  Armor Repairer sold its last 2 units at 179.7M (11-23/24) after one 10% step: +263M on the item; w/o best+worst −121.5M.
  Relists 55 (38.6M), broker 18.1M. All time import +173M vs station −52M. 3 sim logins (58 min). Memo: reports/2026-11-27-memo.md.
- Found: 1.01B in Jita bids while imports are cash-gated (0.45B free vs 0.9B contract). Six 1-unit bids placed Mon 11-24 04Z
  (52236 232M, 85656 173M, 57119 123M, 41525 65M, 98440 23M, + 12076) were on top in 0 of the last 24 checks. At 5 days they
  turn stale 11-29 04Z, minutes after Sat's 03:48Z login, so they'd sit to the next session (~7 d). Changed: strategy
  `buy_stale_days` 5 → 4 (main + all variants; logic-gap fix like 11-20, no probe). 41 tests pass.
- Alerts (30): liquidation 54% / Typhoon 8.2%: legacy, step-down continues (Thu 19 decision), under push lines. Stale Amarr
  sells: step-down each Amarr visit. Idle Jita bids: Bomb Launcher and Nomad Gamma (new, 92.5M) are on top (24/24, 17/24) with
  no sellers yet, so they're kept; behind-rival ones go at 4 d now; Gneiss/Dark Glitter/Fullerite are dust. Thresholds kept.
- Grades: all topics changed something except Tue (marginal). No reassignment. Usage flat (avg 22/day vs 22 baseline).
- Asked the user: shift main's capital from station to imports before imports_only reports (~12-10)?
- Next: Sat check the Mon bids got cancelled and whether a courier ships with the freed cash.
