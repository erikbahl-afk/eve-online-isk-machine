# Summary · Thu 05 Nov 13:49 PST

Updated every ~2 hours. **Your real character** is the first section; everything after it is the **practice trader** (pretend ISK, real market data). Each section starts with a line on how to read it.

## ⚠ Alerts
_Automatic red flags from this run. The daily analysis must deal with each one: fix it, or explain why it's fine._


- 🔴 Data problem in amarr: fetch failed: ESI GET /markets/10000043/orders/ failed after 6 tries
- 🔴 Data problem in character: SSO read failed: RuntimeError
- 🔴 Data problem in dodixie: fetch failed: ESI GET /markets/10000032/orders/ failed after 6 tries
- 🔴 Data problem in hek: fetch failed: ESI GET /markets/10000042/orders/ failed after 6 tries
- 🔴 Data problem in jita: fetch failed: ESI GET /markets/10000002/orders/ failed after 6 tries
- 🔴 Data problem in rens: fetch failed: ESI GET /markets/10000030/orders/ failed after 6 tries
- 🟠 Liquidation value is 69% of net worth (3.42B of 4.98B): much of the stock couldn't be sold quickly without a big loss.
- 🟠 Typhoon Fleet Issue Capsuleer Elite XX SKIN is 8.4% of net worth (418.51M).
- 🔵 Buy order for Glorified Unstable Magnetic Field Stabilizer Mutaplasmid in jita hasn't filled at all in 5 days (369.40M tied up).
- 🔵 Buy order for Mid-grade Centurion Delta in jita hasn't filled at all in 5 days (333.80M tied up).
- 🔵 Buy order for Corelum B-Type 10MN Afterburner in amarr hasn't filled at all in 5 days (191.00M tied up).
- 🔵 Buy order for Sentient Damage Control in amarr hasn't filled at all in 5 days (313.00M tied up).
- 🔵 Buy order for Standup Guided Bomb Launcher I in amarr hasn't filled at all in 5 days (190.06M tied up).
- 🔵 Buy order for Tetryon Exotic Plasma XL in amarr hasn't filled at all in 5 days (98.99M tied up).
- 🔵 Buy order for Unstable Large Shield Extender Mutaplasmid in amarr hasn't filled at all in 5 days (104.60M tied up).

## 2. Practice portfolio
_The paper trader started with 5.00B on 28 Oct. Net worth counts stock at what we paid; liquidation is the worst case if we dumped everything into buy orders right now._

- **Net worth:** 4.98B (-0.48% in 0.0 days) · liquidation 3.42B
- **Where the ISK is:** cash 260.10M · locked in buy orders 1.60B · stock 3.11B · on a courier 0.00
- **Profit so far (realized):** -24.20M. That's completed sales minus every fee paid. Fees: broker 24.20M, relist 0.00, sales tax 0.00, courier 138.00M
- **Location:** amarr · import hub amarr · shipments on the way 0
- **What's limiting profit** (near 100% = the bottleneck): order slots 7/113 · ISK in use 95% · your time last plan 13 of 25 min

## 3. Results by strategy
_station = buy and sell in the same hub · import = buy in Jita, ship, sell elsewhere · spec = bets ahead of patches. Realized stays at 0 until items actually sell._

| Strategy | Spent buying | Sold for | Fees | Realized profit |
|---|---|---|---|---|
| import | 2.96B | 0.00 | 138.00M | 0.00 |
| station | 12.22M | 0.00 | 24.20M | -24.20M |

## 4. Strategy experiments
_Separate pretend portfolios trading the same market with the same logins but different settings. Whichever wins for about 2 weeks gets adopted by the main one._

| Experiment | Kind | Net worth | Change | Liquidation | Realized profit | What it tests |
|---|---|---|---|---|---|---|
| main | main | 4.98B | -0.48% | 69% | -24.20M | current settings (drives INSTRUCTIONS.md) |
| no_imports | regular | 4.93B | -1.42% | 98% | -71.06M | station trading only: measures what imports add |
| loose | regular | 4.98B | -0.48% | 69% | -24.20M | lower margin bars (4% station, 7% import): more items, thinner edges |
| start_1b | regular | 1.00B | +0.00% | 100% | 0.00 | 1B starting capital, normal sessions: the likely live start |
| start_1b_more_time | regular | 986.11M | -1.39% | 91% | -13.89M | 1B start with 60-min sessions and 2-3 weekday logins: is extra early time worth it? |
| bold_dodixie_imports | bold | 5.00B | +0.00% | 100% | 0.00 | BOLD: imports only, to Dodixie (cheapest shipping), no trading inside hubs |

## 5. Recent simulated logins
_When the practice 'you' logged in, which hubs it visited, and how much of the checklist it got through. Partial = the session was cut short on purpose, to test that._

| When (PT) | Hubs | Steps done / planned | Minutes | Cut short |
|---|---|---|---|---|
| Thu 29 Oct 06:23 | jita | 0 / 0 | 2 |  |
| Sat 31 Oct 10:43 | jita → amarr | 21 / 21 | 25 |  |
| Sat 31 Oct 15:50 | amarr | 6 / 6 | 9 |  |

## 6. Best and worst items
_Per item: units bought and sold, fees paid, and realized profit. Items bought but not sold yet show 0 profit and only their fees._

| Item (hub) | Bought | Sold | Fees | Realized profit |
|---|---|---|---|---|
| Gravid Vorton Tuning System Mutaplasmid (jita) | 5 | 0 | 0.00 | 0.00 |
| Typhoon Fleet Issue Capsuleer Elite XX SKIN (jita) | 1 | 0 | 0.00 | 0.00 |
| Black Market 'Valdimar' Drone Navigation DN-701 (jita) | 3 | 0 | 0.00 | 0.00 |
| Golem Exoplanets Hunter SKIN (jita) | 3 | 0 | 0.00 | 0.00 |
| Capital I-a Enduring Armor Repairer (jita) | 3 | 0 | 0.00 | 0.00 |
| Void XL (jita) | 2,434 | 0 | 0.00 | 0.00 |
| Men's 'Precision' Boots (jita) | 5 | 0 | 0.00 | 0.00 |
| Standup M-Set Basic Small Ship Manufacturing Material Efficiency I (jita) | 1 | 0 | 0.00 | 0.00 |
| Glorified Unstable Magnetic Field Stabilizer Mutaplasmid (jita) | 0 | 0 | 5.54M | -5.54M |
| Mid-grade Centurion Delta (jita) | 0 | 0 | 5.01M | -5.01M |
| Sentient Damage Control (amarr) | 0 | 0 | 4.70M | -4.70M |
| Corelum B-Type 10MN Afterburner (amarr) | 0 | 0 | 2.87M | -2.87M |
| Standup Guided Bomb Launcher I (amarr) | 0 | 0 | 2.85M | -2.85M |

## 7. Which hub is best
_Market size = ISK spent per day buying from sell orders in that station. Items = how many pass our filters. Profit/day = expected daily profit from the best 30. Station = trading inside that hub; Import = buying in Jita and selling there._

| Hub | Market size/day | Station items | Station profit/day | Import items | Import profit/day |
|---|---|---|---|---|---|

## 11. Data health
_Is the market data flowing? Orders = orders seen in the station · Hours today = hours of data collected since 00:00 UTC · Trades seen = trades inferred since the last snapshot. Any note means something went wrong._

| Hub | Orders | Hours today | Trades seen | Note |
|---|---|---|---|---|
| jita | 0 | 0.0 | 0 | fetch failed: ESI GET /markets/10000002/orders/ failed after 6 tries |
| amarr | 0 | 0.0 | 0 | fetch failed: ESI GET /markets/10000043/orders/ failed after 6 tries |
| dodixie | 0 | 0.0 | 0 | fetch failed: ESI GET /markets/10000032/orders/ failed after 6 tries |
| rens | 0 | 0.0 | 0 | fetch failed: ESI GET /markets/10000030/orders/ failed after 6 tries |
| hek | 0 | 0.0 | 0 | fetch failed: ESI GET /markets/10000042/orders/ failed after 6 tries |
| character | 0 | 0.0 | 0 | SSO read failed: RuntimeError |
