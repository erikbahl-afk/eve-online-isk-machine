# Summary · Thu 05 Nov 01:30 PST

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

- **Net worth:** 4.98B (-0.48% in 7.7 days) · liquidation 2.54B
- **Where the ISK is:** cash 260.10M · locked in buy orders 1.60B · stock 3.11B · on a courier 0.00
- **Profit so far (realized):** -24.20M. That's completed sales minus every fee paid. Fees: broker 24.20M, relist 0.00, sales tax 0.00, courier 138.00M
- **Location:** amarr · import hub amarr · shipments on the way 0
- **What's limiting profit** (near 100% = the bottleneck): order slots 7/113 · ISK in use 95% · your time last plan 19 of 25 min

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
| jita | 4.67T | 80 | 210.39M | - | - |
| amarr | 503.03B | 25 | 82.00M | 101 | 432.98M |
| dodixie | 165.44B | 8 | 26.27M | 79 | 288.25M |
| rens | 44.22B | 2 | 6.26M | 43 | 235.84M |
| hek | 62.75B | 5 | 12.86M | 48 | 192.75M |

## 8. Best items to trade inside Jita
_Buy at the highest buy price + 1 tick, sell at the lowest sell price − 1 tick. Margin is after all fees. On top = how much of the time between your logins our order would stay the best price before a rival undercuts it (sell side / buy side). Limited by = which resource it eats most: order slots, ISK, or your time._

| Item | Buy → sell price | Margin | Sold per day | On top (sell/buy) | Profit/day | Limited by |
|---|---|---|---|---|---|---|
| Standup Siren II | 20.01M → 39.40M | 85.8% | 0.8 | 23% / 72% | 13.12M | time |
| Inherent Implants 'Squire' Power Grid Management EG-604 | 75.02M → 124.10M | 55.9% | 0.3 | 23% / 54% | 11.26M | time |
| Dread Guristas Multispectrum Shield Hardener | 177.30M → 221.70M | 17.4% | 0.3 | 3% / 10% | 8.36M | time |
| Compressed Zeolites | 1.24k → 1.54k | 17.0% | 41043.9 | 5% / 6% | 8.14M | time |
| Antipharmakon Aeolis | 22.51M → 28.84M | 20.4% | 1.2 | 13% / 85% | 5.50M | time |
| Noctis | 73.31M → 85.89M | 9.9% | 0.8 | 11% / 61% | 5.36M | time |
| Republic Fleet Light Missile Launcher | 37.30M → 52.62M | 32.7% | 0.4 | 43% / 73% | 4.26M | time |
| Platinum | 7.01k → 8.10k | 8.3% | 13559.2 | 5% / 4% | 7.03M | ISK |
| Compressed Glistening Zeolites | 2.84k → 3.26k | 7.9% | 67685.0 | 10% / 12% | 13.54M | ISK |
| Zainou 'Deadeye' Medium Hybrid Turret MH-803 | 14.06M → 19.81M | 32.5% | 0.9 | 32% / 63% | 4.17M | time |
| Corpus C-Type Heavy Energy Nosferatu | 25.02M → 40.92M | 54.1% | 0.3 | 19% / 62% | 4.34M | time |
| Dark Blood Small Focused Beam Laser | 17.00M → 32.89M | 82.5% | 0.3 | 33% / 43% | 4.40M | time |

## 9. Best items to import Jita → Amarr
_Buy from Jita sellers, ship by courier, sell just under the cheapest seller there. Margin is after shipping and fees. m³ = cargo volume per unit._

| Item | Jita price → sell price | m³ | Margin | Sold per day | On top | Profit/day | Limited by |
|---|---|---|---|---|---|---|---|
| Dark Blood Mega Pulse Laser | 64.39M → 129.70M | 20.0 | 87.0% | 1.4 | 73% | 79.24M | ISK |
| Starsi Blast! Classic | 40.88M → 73.89M | 1.0 | 67.3% | 0.6 | 51% | 15.91M | time |
| Large Projectile Collision Accelerator II | 20.36M → 48.23M | 20.0 | 120.7% | 0.5 | 100% | 13.00M | time |
| Dread Guristas Torpedo Launcher | 98.23M → 136.20M | 20.0 | 27.3% | 0.8 | 85% | 20.74M | ISK |
| Golem State Police SKIN | 54.90M → 99.57M | 0.0 | 67.9% | 0.4 | 62% | 13.68M | time |
| Corelum C-Type Medium Remote Armor Repairer | 29.49M → 46.61M | 10.0 | 45.7% | 1.1 | 44% | 14.09M | time |
| Blood Raider NET Resonator | 3.80M → 5.19M | 1.0 | 25.3% | 23.2 | 7% | 21.95M | ISK |
| Ferrogel | 27.53k → 42.14k | 1.0 | 41.0% | 1214.6 | 18% | 13.59M | time |
| Ogdin's Eye Coordination Enhancer | 299.60M → 402.90M | 1.0 | 23.3% | 0.3 | 49% | 20.79M | ISK |
| State Hardpoint Booster II | 9.78M → 20.89M | 1.0 | 98.5% | 1.2 | 86% | 11.26M | time |
| ElectroPunch Ultra L | 11.00k → 16.37k | 0.0 | 37.0% | 2946.6 | 49% | 11.91M | time |
| Large Energy Burst Aerator II | 6.93M → 12.07M | 20.0 | 61.2% | 2.4 | 86% | 10.28M | time |

## 10. Cornering watchlist (read-only, nothing is traded)
_Items where buying out the cheapest few sell orders and relisting higher would pay on paper. We only watch them, to learn whether such prices hold or get undercut._

| Hub | Item | Cheapest now | Buy out | Cost | Relist at | Paper profit | Return | Days to sell | Rival updates/day |
|---|---|---|---|---|---|---|---|---|---|
| jita | Inherent Implants 'Squire' Capacitor Systems Operation EO-602 | 7.00M | 1 orders / 49 units | 343.00M | 11.91M | 212.14M | 62% | 5.0 | 0.9 |
| jita | Mid-grade Centurion Alpha | 78.00M | 2 orders / 5 units | 392.00M | 118.00M | 169.24M | 43% | 5.9 | 1.4 |
| jita | Oxidative Stress - Unlimited | 40.00M | 5 orders / 5 units | 261.67M | 88.56M | 159.54M | 61% | 8.8 | 1.2 |
| jita | Capital Nanobot Accelerator I | 45.60M | 2 orders / 8 units | 365.79M | 68.19M | 153.14M | 42% | 4.7 | 1.9 |
| amarr | Small Auxiliary Nano Pump I | 587.90k | 4 orders / 368 units | 217.01M | 985.50k | 127.97M | 59% | 7.4 | 2.8 |
| jita | Rattlesnake King's Ransom Luecin SKIN | 40.00M | 2 orders / 7 units | 299.90M | 64.16M | 127.33M | 42% | 6.1 | 0.4 |
| jita | Capital Projectile Turret | 32.35M | 3 orders / 9 units | 291.30M | 48.63M | 125.03M | 43% | 7.5 | 1.6 |
| jita | Dark Blood Small Capacitor Booster | 46.88M | 5 orders / 5 units | 238.67M | 76.34M | 124.42M | 52% | 5.3 | 1.9 |
| jita | Heavy Interdiction Cruisers | 37.00M | 2 orders / 8 units | 296.99M | 54.99M | 121.48M | 41% | 3.6 | 2.8 |
| jita | Advanced Armor Layering | 17.00M | 2 orders / 17 units | 289.50M | 24.86M | 112.52M | 39% | 4.2 | 0.4 |

## 11. Data health
_Is the market data flowing? Orders = orders seen in the station · Hours today = hours of data collected since 00:00 UTC · Trades seen = trades inferred since the last snapshot. Any note means something went wrong._

| Hub | Orders | Hours today | Trades seen | Note |
|---|---|---|---|---|
| jita | 328,111 | 11.2 | 5,081 |  |
| amarr | 128,482 | 11.2 | 1,260 |  |
| dodixie | 68,390 | 11.2 | 1,106 |  |
| rens | 31,866 | 11.2 | 202 |  |
| hek | 41,389 | 11.2 | 412 |  |
