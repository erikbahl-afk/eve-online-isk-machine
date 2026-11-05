# Summary · Thu 05 Nov 12:00 PST

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

- **Net worth:** 4.98B (-0.48% in 8.1 days) · liquidation 2.54B
- **Where the ISK is:** cash 260.10M · locked in buy orders 1.60B · stock 3.11B · on a courier 0.00
- **Profit so far (realized):** -24.20M. That's completed sales minus every fee paid. Fees: broker 24.20M, relist 0.00, sales tax 0.00, courier 138.00M
- **Location:** amarr · import hub amarr · shipments on the way 0
- **What's limiting profit** (near 100% = the bottleneck): order slots 7/113 · ISK in use 95% · your time last plan 21 of 25 min

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
| start_1b_more_time | 986.11M | -1.39% | -13.89M | 1B start with 60-min sessions and 2-3 weekday logins: is extra early time worth it? |

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
| jita | 4.75T | 72 | 226.79M | - | - |
| amarr | 520.38B | 22 | 150.07M | 57 | 310.18M |
| dodixie | 167.92B | 8 | 23.60M | 52 | 234.04M |
| rens | 45.30B | 1 | 2.05M | 13 | 92.67M |
| hek | 66.06B | 5 | 12.11M | 27 | 126.17M |

## 8. Best items to trade inside Jita
_Buy at the highest buy price + 1 tick, sell at the lowest sell price − 1 tick. Margin is after all fees. On top = how much of the time between your logins our order would stay the best price before a rival undercuts it (sell side / buy side). Limited by = which resource it eats most: order slots, ISK, or your time._

| Item | Buy → sell price | Margin | Sold per day | On top (sell/buy) | Profit/day | Limited by |
|---|---|---|---|---|---|---|
| Standup Siren II | 20.01M → 38.99M | 83.9% | 0.7 | 23% / 73% | 11.96M | time |
| Inherent Implants 'Squire' Power Grid Management EG-604 | 75.02M → 123.90M | 55.6% | 0.3 | 23% / 55% | 12.08M | time |
| Mid-grade Amulet Epsilon | 202.10M → 299.80M | 39.6% | 0.2 | 5% / 3% | 14.67M | time |
| Zainou 'Deadeye' Medium Hybrid Turret MH-803 | 11.53M → 19.97M | 63.3% | 1.2 | 31% / 65% | 9.00M | time |
| Compressed Dark Glitter | 316.10k → 390.10k | 15.9% | 225.5 | 18% / 22% | 10.76M | ISK |
| Babaroga | 4.69B → 5.63B | 12.7% | 0.1 | 5% / 23% | 50.12M | ISK |
| Blood Raider NET Resonator | 3.60M → 4.40M | 14.7% | 16.2 | 8% / 2% | 8.02M | time |
| 50MN Microwarpdrive II | 3.52M → 4.22M | 12.4% | 16.7 | 12% / 41% | 6.86M | time |
| Antipharmakon Aeolis | 22.52M → 28.81M | 20.2% | 1.2 | 13% / 73% | 5.11M | time |
| Syndicate Gas Cloud Scoop | 94.25M → 112.80M | 12.3% | 0.6 | 4% / 5% | 6.41M | time |
| Compressed Zeolites | 1.27k → 1.54k | 13.8% | 37013.4 | 4% / 5% | 6.05M | time |
| Noctis | 73.53M → 85.91M | 9.6% | 0.8 | 11% / 37% | 5.18M | time |

## 9. Best items to import Jita → Amarr
_Buy from Jita sellers, ship by courier, sell just under the cheapest seller there. Margin is after shipping and fees. m³ = cargo volume per unit._

| Item | Jita price → sell price | m³ | Margin | Sold per day | On top | Profit/day | Limited by |
|---|---|---|---|---|---|---|---|
| Dread Guristas Torpedo Launcher | 95.97M → 136.20M | 20.0 | 30.4% | 0.8 | 85% | 22.57M | ISK |
| Starsi Blast! Classic | 40.73M → 73.89M | 1.0 | 68.0% | 0.6 | 52% | 16.27M | time |
| Corelum C-Type Medium Remote Armor Repairer | 29.51M → 46.79M | 10.0 | 46.2% | 1.1 | 45% | 14.62M | time |
| Mid-grade Amulet Epsilon | 299.90M → 406.70M | 1.0 | 24.4% | 0.4 | 13% | 29.33M | ISK |
| Gallente Control Tower Small | 122.30M → 161.30M | 2,000.0 | 20.9% | 0.5 | 56% | 13.05M | ISK |
| Mid-grade Virtue Gamma | 137.90M → 178.70M | 1.0 | 18.7% | 0.8 | 86% | 19.47M | ISK |
| Mid-grade Virtue Epsilon | 402.50M → 518.50M | 1.0 | 17.9% | 0.3 | 39% | 19.42M | ISK |
| Federation Navy 50MN Microwarpdrive | 83.74M → 120.30M | 10.0 | 32.1% | 0.3 | 73% | 8.78M | time |
| Mid-grade Virtue Alpha | 74.58M → 127.80M | 1.0 | 58.4% | 0.2 | 20% | 8.82M | time |
| Zainou 'Beancounter' Metallurgy MY-705 | 150.40M → 187.90M | 1.0 | 14.2% | 0.3 | 87% | 7.30M | ISK |
| Mid-grade Virtue Delta | 239.30M → 296.60M | 1.0 | 13.3% | 0.5 | 50% | 14.80M | ISK |
| Nighthawk | 291.00M → 373.90M | 15,000.0 | 16.5% | 0.2 | 6% | 7.47M | time |

## 10. Cornering watchlist (read-only, nothing is traded)
_Items where buying out the cheapest few sell orders and relisting higher would pay on paper. We only watch them, to learn whether such prices hold or get undercut._

| Hub | Item | Cheapest now | Buy out | Cost | Relist at | Paper profit | Return | Days to sell | Rival updates/day |
|---|---|---|---|---|---|---|---|---|---|
| jita | Inherent Implants 'Squire' Capacitor Systems Operation EO-602 | 7.00M | 1 orders / 45 units | 315.00M | 11.85M | 192.25M | 61% | 4.7 | 0.8 |
| jita | Mid-grade Centurion Alpha | 78.00M | 2 orders / 5 units | 392.00M | 118.00M | 169.24M | 43% | 6.4 | 1.3 |
| dodixie | Tetrimon Resistance Booster IV | 15.00M | 6 orders / 6 units | 137.00M | 47.99M | 136.90M | 100% | 6.3 | 2.1 |
| jita | Rattlesnake King's Ransom Luecin SKIN | 40.00M | 2 orders / 7 units | 299.90M | 64.16M | 127.33M | 42% | 6.6 | 0.3 |
| jita | Capital Projectile Turret | 32.28M | 3 orders / 9 units | 290.75M | 48.63M | 125.58M | 43% | 8.0 | 2.1 |
| jita | Dark Blood Small Capacitor Booster | 46.86M | 5 orders / 5 units | 238.63M | 76.34M | 124.46M | 52% | 5.3 | 2.1 |
| jita | Savant’s Ruin - Unlimited | 34.99M | 2 orders / 10 units | 349.99M | 49.10M | 117.07M | 33% | 7.5 | 1.1 |
| jita | Advanced Armor Layering | 17.00M | 2 orders / 16 units | 272.50M | 24.88M | 106.17M | 39% | 4.2 | 0.3 |
| jita | Capital Energy Turret | 17.90M | 3 orders / 14 units | 264.90M | 27.67M | 103.60M | 39% | 3.9 | 1.0 |
| jita | Rupture Blueprint | 87.88M | 2 orders / 4 units | 351.76M | 119.40M | 102.56M | 29% | 5.7 | 1.6 |

## 11. Data health
_Is the market data flowing? Orders = orders seen in the station · Hours today = hours of data collected since 00:00 UTC · Trades seen = trades inferred since the last snapshot. Any note means something went wrong._

| Hub | Orders | Hours today | Trades seen | Note |
|---|---|---|---|---|
| jita | 329,353 | 21.7 | 4,868 |  |
| amarr | 127,901 | 21.7 | 1,637 |  |
| dodixie | 68,343 | 21.7 | 890 |  |
| rens | 31,856 | 21.7 | 203 |  |
| hek | 41,362 | 21.7 | 430 |  |
