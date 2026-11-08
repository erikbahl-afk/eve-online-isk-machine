import numpy as np
import pandas as pd

from trader import market
from trader.common import load_config
from trader.fees import Fees, tick_down, tick_up, valid_down, valid_up
from trader.sim import Sim, new_portfolio

CFG = load_config()


def test_ticks():
    assert tick_down(12_340_000) == 12_330_000
    assert tick_down(10_000_000) == 9_999_000
    assert tick_up(9_999_000) == 10_000_000
    assert tick_up(12_340_000) == 12_350_000
    assert tick_down(5.55) == 5.54
    assert valid_down(12_345_678) == 12_340_000
    assert valid_up(12_345_678) == 12_350_000


def test_fees():
    f = Fees(CFG)
    assert abs(f.broker - 0.015) < 1e-12
    assert abs(f.tax - 0.03375) < 1e-12
    # price drop: only the relist part, 20% of broker on new value
    assert abs(f.relist_fee(100, 90, 1000) - 0.2 * 0.015 * 90_000) < 1e-6


def book(rows):
    return pd.DataFrame(rows, columns=["order_id", "type_id", "is_buy", "price", "vol", "issued", "duration"])


def test_diff_prints():
    t0, t1 = 1_000_000, 1_007_200
    prev = book([
        (1, 7, False, 100.0, 10, t0 - 999, 90),   # partially bought
        (2, 7, False, 105.0, 5, t0 - 999, 90),    # vanished at top after 1 is... deeper -> cancel
        (3, 7, True, 90.0, 20, t0 - 999, 90),     # vanished top bid -> sold into
        (4, 7, True, 80.0, 20, t0 - 999, 90),     # vanished deep bid, better bid remains -> cancel
        (5, 7, True, 85.0, 20, t0 - 999, 90),     # stays
    ])
    cur = book([
        (1, 7, False, 100.0, 4, t0 - 999, 90),
        (5, 7, True, 85.0, 20, t0 - 999, 90),
        (6, 7, False, 99.0, 3, t0 + 100, 90),     # new undercut
    ])
    pr = market.diff_prints(prev, cur, market.tops(prev), market.tops(cur), t1, 0.8)
    asks = pr[pr.side == "ask"]
    bids = pr[pr.side == "bid"]
    assert asks.qty.sum() == 6 and asks.price.tolist() == [100.0]
    assert bids.qty.sum() == 16 and bids.price.tolist() == [90.0]
    upd = market.update_counts(cur, market.tops(cur), t0)
    assert upd.loc[7, "ask_upd"] == 1


def test_day_and_stats():
    top = pd.DataFrame({"best_ask": [100.0], "best_bid": [90.0]}, index=pd.Index([7], name="type_id"))
    pr = pd.DataFrame({"type_id": [7, 7], "side": ["ask", "bid"], "price": [100.0, 90.0], "qty": [6.0, 4.0]})
    upd = pd.DataFrame({"ask_upd": [2.0], "bid_upd": [0.0]}, index=pd.Index([7], name="type_id"))
    d = market.Day("2026-01-01")
    t0 = 1_800_000_000 - 1_800_000_000 % 86400  # 00:00 UTC
    d.add("jita", market.aggregate(pr, upd, top), t0, t0 + 7200)
    d.add("jita", market.aggregate(pr, upd, top), t0 + 7200, t0 + 14400)
    f = d.frame()
    assert f.ask_units.iloc[0] == 12 and f.hours.iloc[0] == 4 and f.hours0.iloc[0] == 4
    st = market.build_stats("jita", [], f)
    assert abs(st.loc[7, "A"] - 72) < 1e-9 and abs(st.loc[7, "lam_a"] - 1.0) < 1e-9
    assert market.block_hours(t0 + 5 * 3600, t0 + 7 * 3600) == [1.0, 1.0, 0.0, 0.0]
    empty = market.aggregate(pr.iloc[:0], upd, top)
    assert empty.loc[7, "ask_units"] == 0


def test_fill_and_session():
    pf = new_portfolio(CFG, 0)
    ledger = []
    sim = Sim(CFG, pf, Fees(CFG), np.random.default_rng(1), ledger)
    o = sim.place_buy("jita", 7, 10, 90_000.0, 0)
    assert o and pf["cash"] < 5e9 - 900_000
    stats = pd.DataFrame({f"lam_{s}{b}": [0.0] for s in "ab" for b in range(4)}, index=[7])
    pr = pd.DataFrame({"type_id": [7], "side": ["bid"], "price": [89_000.0], "qty": [100.0]})
    sim.apply_fills("jita", pr, stats, 0, 7200)
    assert pf["inventory"]["jita"]["7"]["qty"] == 10 and not pf["orders"]
    top = pd.DataFrame({"best_ask": [100_000.0], "best_bid": [91_000.0]}, index=[7])
    plan = {"steps": [{"kind": "new_sell", "hub": "jita", "type_id": 7, "qty": 10, "floor": 95_000.0,
                       "fallback": 120_000.0, "secs": 45, "group": 2}]}
    done, _ = sim.execute(plan, {"jita": top}, {}, {}, 8000, 1800)
    assert done == 1 and pf["orders"][0]["price"] == 99_990
    pr = pd.DataFrame({"type_id": [7], "side": ["ask"], "price": [100_000.0], "qty": [50.0]})
    sim.apply_fills("jita", pr, stats, 8000, 15200)
    assert not pf["orders"] and pf["pnl"]["realized"] > 0


def test_history_gate_blocks_fills_nobody_traded_at():
    from trader.market import PriceLevels
    hist = pd.DataFrame({"date": ["1970-01-05", "1970-01-06", "1970-01-07", "1970-01-08"],
                         "lowest": [100.0, 100.0, 80.0, 100.0], "highest": [120.0] * 4, "volume": [5, 5, 5, 5]})
    lv = PriceLevels(None, {}, days=14, fetch=lambda hub, ty: hist)
    t = 8 * 86400
    assert lv.reach("jita", 7, "buy", 60.0, t) == 0.0     # bid below every official trade
    assert lv.reach("jita", 7, "buy", 90.0, t) == 0.25    # one day in four traded down to 90
    assert lv.reach("jita", 7, "sell", 130.0, t) == 0.0   # ask above every official trade
    assert lv.reach("jita", 7, "sell", 110.0, t) == 1.0
    assert PriceLevels(None, {}, fetch=lambda h, ty: None).reach("jita", 7, "buy", 1.0, t) == 1.0  # unknown: no change
    pf = new_portfolio(CFG, 0)
    sim = Sim(CFG, pf, Fees(CFG), np.random.default_rng(1), [])
    sim.place_buy("jita", 7, 10, 60.0, 0)
    stats = pd.DataFrame({f"lam_{s}{b}": [0.0] for s in "ab" for b in range(4)}, index=[7])
    pr = pd.DataFrame({"type_id": [7], "side": ["bid"], "price": [59.0], "qty": [100.0]})
    sim.apply_fills("jita", pr, stats, t - 7200, t, lv)
    assert pf["orders"][0]["remain"] == 10                 # phantom fill blocked
    sim.apply_fills("jita", pr, stats, t - 7200, t)
    assert not pf["orders"] or pf["orders"][0]["remain"] < 10  # without the gate it would have filled


def test_survival_by_time_of_day():
    from trader.sim import hazard, surv_avg
    w = np.zeros(24)
    w[3] = 1.0  # sessions at 03:00 UTC
    eu_rivals = np.array([[0.0, 0.0, 0.0, 2.0]])  # rivals only active 18-24 UTC
    all_day = np.array([[0.5, 0.5, 0.5, 0.5]])  # same daily total, spread out
    assert surv_avg(eu_rivals, 48, w)[0] > surv_avg(all_day, 48, w)[0]
    assert hazard([0, 0, 0, 2.0], 0, 86400) == 12.0


def test_import_courier_flow():
    pf = new_portfolio(CFG, 0)
    sim = Sim(CFG, pf, Fees(CFG), np.random.default_rng(1), [])
    book = pd.DataFrame({"type_id": [7, 7], "is_buy": [False, False], "price": [1e6, 1.1e6], "vol": [5, 5]})
    assert sim.instant_buy("jita", 7, 8, 1.05e6, book, 0) == 5  # second order above max price
    c = sim.courier("jita", "amarr", [7], {7: 10.0}, 0)
    assert c and c["fee"] == CFG["routes"]["amarr"]["contract_fee"] and not pf["inventory"]["jita"]
    sim.arrivals(c["arrive"] + 1)
    it = pf["inventory"]["amarr"]["7"]
    assert it["qty"] == 5 and it["cost"] > 1e6 and it["tag"] == "import"
    assert sim.jump("amarr", 0) and not sim.jump("jita", 3600) and pf["location"] == "amarr"


def test_instant_sell():
    pf = new_portfolio(CFG, 0)
    sim = Sim(CFG, pf, Fees(CFG), np.random.default_rng(1), [])
    sim._inv_add("jita", 7, 10, 1e6, 0, "station")
    book = pd.DataFrame({"type_id": [7, 7], "is_buy": [True, True], "price": [1.2e6, 0.9e6], "vol": [6, 50]})
    assert sim.instant_sell("jita", 7, 10, 1.0e6, book, 0) == 6  # the 0.9M bid is below the minimum
    assert pf["inventory"]["jita"]["7"]["qty"] == 4 and pf["pnl"]["realized"] > 0


def test_corner_scan():
    from trader import corners
    book = pd.DataFrame({"order_id": range(4), "type_id": [7] * 4, "is_buy": [False] * 4,
                         "price": [100e6, 101e6, 102e6, 150e6], "vol": [1, 1, 1, 5],
                         "issued": [0] * 4, "duration": [90] * 4})
    stats = pd.DataFrame({"A": [1.0], "vwap_a": [110e6], "lam_a": [0.01]}, index=[7])
    out = corners.scan(CFG, Fees(CFG), "jita", book, stats, pd.DataFrame(columns=["best_ask"]), 5e9)
    r = out.iloc[0]
    assert r.orders == 3 and r.cost == 303e6 and r.relist == tick_down(150e6) and r.roi > 0.3


def test_import_exit_check():
    from trader.strategy import import_candidates
    stats = pd.DataFrame({"A": [5.0], "vwap_a": [2e6], "hours": [100.0], "trend_a": [1.0],
                          **{f"lam_a{b}": [0.0] for b in range(4)}}, index=[7])
    src = pd.DataFrame({"best_ask": [1e6], "best_bid": [0.9e6]}, index=[7])
    w = np.ones(24) / 24
    route = CFG["routes"]["dodixie"]

    def run(dst_bid):
        dst = pd.DataFrame({"best_ask": [2e6], "best_bid": [dst_bid]}, index=[7])
        return import_candidates(CFG, Fees(CFG), src, stats, dst, {7: 1.0}, route, w)

    assert len(run(0.9e6)) == 1      # a fair buy order at the destination: OK to import
    assert len(run(0.05e6)) == 0     # no real buyers if it doesn't sell (the SKIN case): skip



def test_alerts():
    from trader import alerts
    pf = new_portfolio(CFG, 0)
    pf["inventory"] = {"amarr": {"7": {"qty": 3, "cost": 200e6, "since": 0, "tag": "import"}}}
    val = {"nw_book": 5e9, "nw_liquid": 2e9, "cash": 4.4e9}
    out = alerts.compute(CFG, pf, val, {"est_secs": 2000}, {"jita": {"note": "fetch failed: x"}},
                         {"queue_empty": True, "unallocated_sp": 0}, 10 * 86400, {7: "Thing"})
    keys = {a["key"] for a in out}
    assert {"liquidation", "position:7", "stale_stock:amarr:7", "plan_time", "data:jita", "char_queue"} <= keys
    assert out[0]["severity"] == "high"



def test_skip_run_keeps_summary(tmp_path, monkeypatch):
    import trader.run as run
    monkeypatch.setattr(run, "STATE", tmp_path)
    (tmp_path / "summary.md").write_text("# Summary\nold content\n")
    run.skip_run(1_800_000_000, "ESI down")
    run.skip_run(1_800_007_200, "ESI down")
    text = (tmp_path / "summary.md").read_text()
    assert "old content" in text and text.count("Skipped run") == 1
    al = __import__("json").loads((tmp_path / "alerts.json").read_text())
    assert al[0]["key"] == "esi_down" and al[0]["since"] == 1_800_000_000



def test_seed_candidates_and_fills():
    from trader.strategy import seed_candidates
    stats = pd.DataFrame({"A": [10.0], "vwap_a": [3e6], "hours": [100.0]}, index=[7])
    src = pd.DataFrame({"best_ask": [1.5e6], "best_bid": [1.4e6]}, index=[7])
    dst = pd.DataFrame({"best_ask": [np.nan], "best_bid": [np.nan]}, index=[7])  # sold out at the destination
    w = np.ones(24) / 24
    cand = seed_candidates(CFG, Fees(CFG), src, stats, dst, {7: 1.0}, CFG["routes"]["dodixie"], w)
    assert len(cand) == 1 and cand.iloc[0].tag == "seed" and cand.iloc[0].sell <= 3e6
    pf = new_portfolio(CFG, 0)
    sim = Sim(CFG, pf, Fees(CFG), np.random.default_rng(1), [])
    sim._inv_add("dodixie", 7, 10, 1.6e6, 0, "seed")
    o = sim.place_sell("dodixie", 7, 10, 2.9e6, 0)
    pf["seed_rates"] = {"dodixie:7": [2.0, 3e6]}
    sim.seed_fills("dodixie", dst, 0, 2 * 86400)  # no rival seller: fills at the assumed rate (2/day)
    assert o["remain"] == 6
    rival = pd.DataFrame({"best_ask": [2.5e6], "best_bid": [np.nan]}, index=[7])
    sim.seed_fills("dodixie", rival, 0, 2 * 86400)  # someone else now sells it: no assumed fills
    assert o["remain"] == 6


def test_courier_respects_destination():
    pf = new_portfolio(CFG, 0)
    sim = Sim(CFG, pf, Fees(CFG), np.random.default_rng(1), [])
    book = pd.DataFrame({"type_id": [7, 8], "is_buy": [False, False], "price": [1e6, 2e6], "vol": [5, 5]})
    sim.instant_buy("jita", 7, 5, 1e6, book, 0, "import", dest="amarr")
    sim.instant_buy("jita", 8, 5, 2e6, book, 0, "seed", dest="dodixie")
    c = sim.courier("jita", "amarr", [7, 8], {7: 1.0, 8: 1.0}, 0)
    assert [i["type_id"] for i in c["items"]] == [7] and pf["inventory"]["jita"]["8"]["qty"] == 5
    c2 = sim.courier("jita", "dodixie", [8], {8: 1.0}, 0)
    sim.arrivals(c2["arrive"] + 1)
    assert pf["inventory"]["dodixie"]["8"]["tag"] == "seed"


def test_scoreboard(tmp_path):
    import json

    from trader import scoreboard
    pf = new_portfolio(CFG, 1000.0)
    pf["pnl"].update(broker=10.0, buys=100.0, realized=-10.0)
    pf["per_type"] = {f"jita:{i}": {"realized": float(r)} for i, r in enumerate([-5, 1, 2, 9])}
    (tmp_path / "portfolio.json").write_text(json.dumps(pf))
    (tmp_path / "metrics.csv").write_text("t,cash,escrow,stock_cost,transit,nw_book,nw_liquid,realized,orders,esi_calls\n"
                                          "1000,100,0,0,0,100,100,0,0,0\n2000,50,0,60,0,110,55,-10,1,0\n")
    (tmp_path / "ledger.csv").write_text("t,event,hub,type_id,qty,price,cash_delta,note\n"
                                         "1500,buy_fill,jita,1,1,1,-1,o1\n1500,broker,jita,1,0,0,-1,bid\n")
    s = scoreboard.score("x", tmp_path, 1000.0)
    assert abs(s["ret"] - 10.0) < 1e-9 and abs(s["liq"] - 0.5) < 1e-9 and s["trades"] == 1
    assert s["worst"] == (-5.0, "jita:0") and s["trimmed"] == 3.0 and abs(s["fees"] - 0.1) < 1e-9


def test_liquidation_no_bid_is_zero():
    pf = new_portfolio(CFG, 0.0)
    sim = Sim(CFG, pf, Fees(CFG), np.random.default_rng(1), [])
    top = pd.DataFrame({"best_bid": [50.0, np.nan], "best_ask": [120.0, 130.0]}, index=[1, 2])
    assert sim._liq({"jita": top}, "jita", 1, 100.0) == 50.0 * (1 - sim.fees.tax)
    assert sim._liq({"jita": top}, "jita", 2, 100.0) == 0.0   # no bid at all
    assert sim._liq({"jita": top}, "jita", 3, 100.0) == 0.0   # no orders at all
    assert sim._liq({}, "jita", 1, 100.0) == 50.0              # hub missing this run: fallback guess
