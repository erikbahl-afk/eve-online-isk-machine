# Summary · Thu 05 Nov 06:00 PST

Updated every ~2 hours. **Your real character** is the first section; everything after it is the **practice trader** (pretend ISK, real market data). Each section starts with a line on how to read it.

## 1. Your trading character
_Read from the game over SSO. Shows how far the skill plan is and what needs your attention._

- **Skill plan:** 1.1% done · 3,994,345 SP to go · about **79.2 days** of training left
- **Training now:** Broker Relations 2, Broker Relations 3, Broker Relations 4, Accounting 1 · next plan skill: Trade → 5
- **Unallocated SP:** 0
- **Skill books still to buy and inject:** Daytrading, Advanced Broker Relations, Wholesale, Infomorph Psychology, Infomorph Synchronizing, Contracting
- Attributes Cha 27 / Mem 21 / Wil 17 · free remaps 2 · jump clones 0 · total SP 420,335
- Broker fee in Jita 4-4 with today's skills: 2.7% (goal 1.5%)

## 2. Practice portfolio
_The paper trader started with 5.00B on 28 Oct. Net worth counts stock at what we paid; liquidation is the worst case if we dumped everything into buy orders right now._

- **Net worth:** 4.98B (-0.48% in 7.8 days) · liquidation 2.54B
- **Where the ISK is:** cash 260.10M · locked in buy orders 1.60B · stock 3.11B · on a courier 0.00
- **Profit so far (realized):** -24.20M. That's completed sales minus every fee paid. Fees: broker 24.20M, relist 0.00, sales tax 0.00, courier 138.00M
- **Location:** amarr · import hub amarr · shipments on the way 0
- **What's limiting profit** (near 100% = the bottleneck): order slots 7/113 · ISK in use 95% · your time last plan 20 of 25 min

## 3. Results by strategy
_station = buy and sell in the same hub · import = buy in Jita, ship, sell elsewhere · spec = bets ahead of patches. Realized stays at 0 until items actually sell._

| Strategy | Spent buying | Sold for | Fees | Realized profit |
|---|---|---|---|---|
| import | 2.96B | 0.00 | 138.00M | 0.00 |
| station | 12.22M | 0.00 | 24.20M | -24.20M |

## 4. Strategy experiments
_Separate pretend portfolios trading the same market with the same logins but different settings. Whichever wins for about 2 weeks gets adopted by the main one._

| Experiment | Net worth | Change | Realized profit | What it tests |
|---|---|---|---|---|
| main | 4.98B | -0.48% | -24.20M | current settings (drives INSTRUCTIONS.md) |
| no_imports | 4.93B | -1.42% | -71.06M | station trading only: measures what imports add |
| loose | 4.98B | -0.48% | -24.20M | lower margin bars (4% station, 7% import): more items, thinner edges |
| start_1b | 1.00B | +0.00% | 0.00 | 1B starting capital, normal sessions: the likely live start |
| start_1b_more_time | 1.00B | +0.00% | 0.00 | 1B start with 60-min sessions and 2-3 weekday logins: is extra early time worth it? |

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
| jita | 4.66T | 78 | 173.83M | - | - |
| amarr | 501.78B | 23 | 73.26M | 99 | 408.88M |
| dodixie | 164.77B | 9 | 29.43M | 83 | 254.51M |
| rens | 44.69B | 2 | 6.30M | 41 | 227.92M |
| hek | 63.20B | 4 | 9.65M | 53 | 193.10M |

## 8. Best items to trade inside Jita
_Buy at the highest buy price + 1 tick, sell at the lowest sell price − 1 tick. Margin is after all fees. On top = how much of the time between your logins our order would stay the best price before a rival undercuts it (sell side / buy side). Limited by = which resource it eats most: order slots, ISK, or your time._

| Item | Buy → sell price | Margin | Sold per day | On top (sell/buy) | Profit/day | Limited by |
|---|---|---|---|---|---|---|
| Standup Siren II | 20.01M → 39.40M | 85.8% | 0.8 | 24% / 73% | 13.16M | time |
| Inherent Implants 'Squire' Power Grid Management EG-604 | 75.02M → 124.10M | 55.9% | 0.3 | 24% / 54% | 11.31M | time |
| Antipharmakon Aeolis | 22.51M → 28.85M | 20.4% | 1.3 | 14% / 85% | 5.67M | time |
| Dread Guristas Multispectrum Shield Hardener | 178.40M → 221.30M | 16.5% | 0.3 | 3% / 10% | 7.30M | time |
| Angel NET Resonator | 2.25M → 2.65M | 10.4% | 46.1 | 9% / 5% | 9.82M | ISK |
| Corelum B-Type 10MN Afterburner | 169.60M → 213.90M | 18.5% | 0.2 | 13% / 28% | 6.38M | time |
| Compressed Zeolites | 1.26k → 1.54k | 14.6% | 38707.3 | 4% / 6% | 6.67M | time |
| Syndicate Gas Cloud Scoop | 94.04M → 111.10M | 10.9% | 0.7 | 4% / 5% | 6.15M | time |
| Republic Fleet Light Missile Launcher | 37.30M → 52.62M | 32.7% | 0.3 | 40% / 74% | 4.16M | time |
| Zainou 'Deadeye' Medium Hybrid Turret MH-803 | 14.05M → 19.81M | 32.6% | 1.0 | 32% / 63% | 4.32M | time |
| Platinum | 7.03k → 8.09k | 8.0% | 13504.9 | 5% / 4% | 6.71M | ISK |
| Core C-Type 100MN Afterburner | 120.40M → 159.80M | 24.8% | 0.2 | 22% / 33% | 4.65M | time |

## 9. Best items to import Jita → Amarr
_Buy from Jita sellers, ship by courier, sell just under the cheapest seller there. Margin is after shipping and fees. m³ = cargo volume per unit._

| Item | Jita price → sell price | m³ | Margin | Sold per day | On top | Profit/day | Limited by |
|---|---|---|---|---|---|---|---|
| Dark Blood Mega Pulse Laser | 64.20M → 129.70M | 20.0 | 87.6% | 1.4 | 74% | 77.75M | ISK |
| Starsi Blast! Classic | 40.82M → 73.89M | 1.0 | 67.6% | 0.6 | 51% | 15.95M | time |
| Dread Guristas Torpedo Launcher | 98.16M → 136.20M | 20.0 | 27.4% | 0.8 | 85% | 20.80M | ISK |
| Large Projectile Collision Accelerator II | 20.32M → 48.23M | 20.0 | 121.2% | 0.5 | 100% | 12.61M | time |
| Corelum C-Type Medium Remote Armor Repairer | 29.50M → 46.79M | 10.0 | 46.3% | 1.1 | 44% | 14.41M | time |
| Golem State Police SKIN | 54.86M → 99.57M | 0.0 | 68.1% | 0.4 | 63% | 13.41M | time |
| Ogdin's Eye Coordination Enhancer | 295.00M → 402.90M | 1.0 | 25.3% | 0.3 | 49% | 21.52M | ISK |
| State Hardpoint Booster II | 9.78M → 20.89M | 1.0 | 98.5% | 1.1 | 86% | 10.90M | time |
| Large Energy Burst Aerator II | 6.93M → 12.11M | 20.0 | 61.7% | 2.4 | 86% | 10.42M | time |
| Large Mercoxit Compressor I | 46.97M → 115.80M | 1,000.0 | 129.9% | 0.2 | 54% | 10.81M | time |
| ElectroPunch Ultra L | 11.00k → 16.37k | 0.0 | 37.0% | 2628.3 | 44% | 10.61M | time |
| Blood Raider NET Resonator | 4.00M → 5.19M | 1.0 | 18.8% | 21.8 | 7% | 16.02M | ISK |

## 10. Cornering watchlist (read-only, nothing is traded)
_Items where buying out the cheapest few sell orders and relisting higher would pay on paper. We only watch them, to learn whether such prices hold or get undercut._

| Hub | Item | Cheapest now | Buy out | Cost | Relist at | Paper profit | Return | Days to sell | Rival updates/day |
|---|---|---|---|---|---|---|---|---|---|
| jita | Inherent Implants 'Squire' Capacitor Systems Operation EO-602 | 7.00M | 1 orders / 47 units | 329.00M | 11.88M | 202.14M | 61% | 4.8 | 0.9 |
| jita | Mid-grade Centurion Alpha | 78.00M | 2 orders / 5 units | 392.00M | 118.00M | 169.24M | 43% | 6.1 | 1.4 |
| jita | Oxidative Stress - Unlimited | 40.00M | 5 orders / 5 units | 261.67M | 88.56M | 159.54M | 61% | 9.0 | 1.2 |
| jita | Rattlesnake King's Ransom Luecin SKIN | 40.00M | 2 orders / 7 units | 299.90M | 64.16M | 127.33M | 42% | 6.3 | 0.3 |
| jita | Capital Projectile Turret | 32.35M | 3 orders / 9 units | 291.30M | 48.63M | 125.03M | 43% | 7.7 | 1.5 |
| jita | Dark Blood Small Capacitor Booster | 46.88M | 5 orders / 5 units | 238.67M | 76.34M | 124.42M | 52% | 5.3 | 1.9 |
| jita | Advanced Armor Layering | 17.00M | 2 orders / 17 units | 289.50M | 24.86M | 112.52M | 39% | 4.4 | 0.3 |
| amarr | Small Auxiliary Nano Pump I | 588.00k | 3 orders / 356 units | 209.96M | 931.10k | 105.35M | 50% | 7.2 | 2.7 |
| jita | Capital Energy Turret | 17.90M | 3 orders / 14 units | 264.90M | 27.67M | 103.60M | 39% | 3.8 | 1.0 |
| jita | Rupture Blueprint | 87.88M | 2 orders / 4 units | 351.76M | 119.40M | 102.56M | 29% | 5.4 | 1.7 |

## 11. Data health
_Is the market data flowing? Orders = orders seen in the station · Hours today = hours of data collected since 00:00 UTC · Trades seen = trades inferred since the last snapshot. Any note means something went wrong._

| Hub | Orders | Hours today | Trades seen | Note |
|---|---|---|---|---|
| jita | 328,163 | 15.7 | 6,821 |  |
| amarr | 128,624 | 15.7 | 1,998 |  |
| dodixie | 68,363 | 15.7 | 985 |  |
| rens | 31,796 | 15.7 | 375 |  |
| hek | 41,411 | 15.7 | 560 |  |
