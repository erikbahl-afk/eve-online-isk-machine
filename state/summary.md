# Summary · Wed 04 Nov 22:00 PST

Updated every ~2 hours. **Your real character** is the first section; everything after it is the **practice trader** (pretend ISK, real market data). Each section starts with a line on how to read it.

## 1. Your trading character
_Read from the game over SSO. Shows how far the skill plan is and what needs your attention._

- **Skill plan:** 0.2% done · 4,032,100 SP to go · about **80.1 days** of training left
- **Training now:** Trade 4, Broker Relations 1, Broker Relations 2, Broker Relations 3 · next plan skill: Trade → 5
- **Unallocated SP:** 0
- **Skill books still to buy and inject:** Daytrading, Advanced Broker Relations, Wholesale, Infomorph Psychology, Infomorph Synchronizing, Contracting
- Attributes Cha 27 / Mem 21 / Wil 17 · free remaps 2 · jump clones 0 · total SP 382,580
- Broker fee in Jita 4-4 with today's skills: 3.0% (goal 1.5%)

## 2. Practice portfolio
_The paper trader started with 5.00B on 28 Oct. Net worth counts stock at what we paid; liquidation is the worst case if we dumped everything into buy orders right now._

- **Net worth:** 4.98B (-0.48% in 7.5 days) · liquidation 2.54B
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
| jita | 4.67T | 91 | 225.76M | - | - |
| amarr | 504.11B | 21 | 70.22M | 101 | 433.09M |
| dodixie | 166.25B | 7 | 23.01M | 85 | 283.79M |
| rens | 45.05B | 2 | 6.28M | 43 | 244.83M |
| hek | 62.83B | 6 | 14.48M | 48 | 180.96M |

## 8. Best items to trade inside Jita
_Buy at the highest buy price + 1 tick, sell at the lowest sell price − 1 tick. Margin is after all fees. On top = how much of the time between your logins our order would stay the best price before a rival undercuts it (sell side / buy side). Limited by = which resource it eats most: order slots, ISK, or your time._

| Item | Buy → sell price | Margin | Sold per day | On top (sell/buy) | Profit/day | Limited by |
|---|---|---|---|---|---|---|
| Inherent Implants 'Squire' Power Grid Management EG-604 | 75.02M → 124.20M | 56.0% | 0.3 | 25% / 54% | 12.41M | time |
| Dread Guristas Multispectrum Shield Hardener | 175.70M → 222.20M | 18.8% | 0.3 | 3% / 12% | 10.61M | time |
| Angel NET Resonator | 2.25M → 2.72M | 13.8% | 46.2 | 10% / 5% | 13.34M | ISK |
| Compressed Zeolites | 1.23k → 1.54k | 17.7% | 40967.9 | 5% / 6% | 8.46M | time |
| Compressed Fullerite-C32 | 20.11k → 23.81k | 11.1% | 4298.7 | 4% / 8% | 8.82M | ISK |
| Antipharmakon Aeolis | 22.51M → 28.84M | 20.4% | 1.2 | 13% / 85% | 5.49M | time |
| Platinum | 6.95k → 8.10k | 9.3% | 14193.6 | 6% / 4% | 8.26M | ISK |
| Republic Fleet Light Missile Launcher | 37.30M → 52.62M | 32.7% | 0.4 | 43% / 73% | 4.37M | time |
| Curse | 131.10M → 162.10M | 16.1% | 0.3 | 11% / 36% | 5.44M | time |
| Corpus X-Type EM Armor Hardener | 158.30M → 188.90M | 12.0% | 0.3 | 6% / 9% | 5.90M | time |
| Compressed Fullerite-C28 | 12.53k → 14.49k | 8.5% | 7669.5 | 5% / 10% | 7.31M | ISK |
| Corpus C-Type Heavy Energy Nosferatu | 25.02M → 40.93M | 54.1% | 0.3 | 20% / 62% | 4.63M | time |

## 9. Best items to import Jita → Amarr
_Buy from Jita sellers, ship by courier, sell just under the cheapest seller there. Margin is after shipping and fees. m³ = cargo volume per unit._

| Item | Jita price → sell price | m³ | Margin | Sold per day | On top | Profit/day | Limited by |
|---|---|---|---|---|---|---|---|
| Dark Blood Mega Pulse Laser | 64.41M → 129.70M | 20.0 | 86.9% | 1.5 | 73% | 81.30M | ISK |
| Golem State Police SKIN | 54.94M → 99.58M | 0.0 | 67.8% | 0.4 | 74% | 16.68M | time |
| Starsi Blast! Classic | 40.96M → 73.89M | 1.0 | 67.0% | 0.6 | 51% | 15.86M | time |
| Large Projectile Collision Accelerator II | 20.38M → 48.23M | 20.0 | 120.5% | 0.5 | 100% | 13.33M | time |
| Ferrogel | 27.57k → 42.14k | 1.0 | 40.8% | 1453.2 | 21% | 16.20M | time |
| Dread Guristas Torpedo Launcher | 98.29M → 136.20M | 20.0 | 27.2% | 0.8 | 85% | 20.69M | ISK |
| Blood Raider NET Resonator | 3.80M → 5.19M | 1.0 | 25.4% | 25.0 | 8% | 23.76M | ISK |
| State Hardpoint Booster II | 9.79M → 20.89M | 1.0 | 98.5% | 1.2 | 86% | 11.56M | time |
| Corelum C-Type Medium Remote Armor Repairer | 29.51M → 45.60M | 10.0 | 42.4% | 1.0 | 43% | 12.84M | time |
| Ogdin's Eye Coordination Enhancer | 299.30M → 402.90M | 1.0 | 23.5% | 0.3 | 49% | 17.72M | ISK |
| ElectroPunch Ultra L | 11.00k → 16.37k | 0.0 | 37.0% | 2945.6 | 49% | 11.90M | time |
| Large Energy Burst Aerator II | 6.93M → 12.07M | 20.0 | 61.1% | 2.5 | 86% | 10.55M | time |

## 10. Cornering watchlist (read-only, nothing is traded)
_Items where buying out the cheapest few sell orders and relisting higher would pay on paper. We only watch them, to learn whether such prices hold or get undercut._

| Hub | Item | Cheapest now | Buy out | Cost | Relist at | Paper profit | Return | Days to sell | Rival updates/day |
|---|---|---|---|---|---|---|---|---|---|
| jita | Mid-grade Centurion Alpha | 78.00M | 2 orders / 5 units | 392.00M | 118.00M | 169.24M | 43% | 5.8 | 1.4 |
| jita | Oxidative Stress - Unlimited | 40.00M | 5 orders / 5 units | 261.67M | 88.56M | 159.54M | 61% | 8.5 | 1.3 |
| jita | Rattlesnake King's Ransom Luecin SKIN | 40.00M | 2 orders / 7 units | 299.90M | 64.16M | 127.33M | 42% | 6.0 | 0.4 |
| jita | Capital Projectile Turret | 32.36M | 3 orders / 9 units | 291.44M | 48.63M | 124.89M | 43% | 7.3 | 1.4 |
| jita | Dark Blood Small Capacitor Booster | 46.88M | 5 orders / 5 units | 238.67M | 76.34M | 124.42M | 52% | 5.3 | 2.0 |
| jita | Heavy Interdiction Cruisers | 38.00M | 2 orders / 8 units | 304.99M | 54.99M | 113.48M | 37% | 3.5 | 2.5 |
| jita | Advanced Armor Layering | 17.00M | 2 orders / 17 units | 289.50M | 24.86M | 112.52M | 39% | 4.1 | 0.4 |
| jita | Capital Energy Turret | 17.90M | 3 orders / 15 units | 282.80M | 27.70M | 112.44M | 40% | 3.9 | 1.1 |
| jita | Zainou 'Deadeye' Large Hybrid Turret LH-1003 | 18.00M | 3 orders / 14 units | 267.88M | 28.44M | 110.87M | 41% | 2.7 | 1.4 |
| jita | Vorton Projector Operation | 25.30M | 2 orders / 11 units | 279.00M | 37.14M | 109.62M | 39% | 4.1 | 0.4 |

## 11. Data health
_Is the market data flowing? Orders = orders seen in the station · Hours today = hours of data collected since 00:00 UTC · Trades seen = trades inferred since the last snapshot. Any note means something went wrong._

| Hub | Orders | Hours today | Trades seen | Note |
|---|---|---|---|---|
| jita | 327,335 | 7.7 | 2,742 |  |
| amarr | 128,601 | 7.7 | 1,032 |  |
| dodixie | 68,568 | 7.7 | 523 |  |
| rens | 31,801 | 7.7 | 103 |  |
| hek | 41,299 | 7.7 | 191 |  |
