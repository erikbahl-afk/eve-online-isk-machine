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
    d.add("jita", market.aggregate(pr, upd, top), 2.0)
    d.add("jita", market.aggregate(pr, upd, top), 2.0)
    f = d.frame()
    assert f.ask_units.iloc[0] == 12 and f.hours.iloc[0] == 4
    st = market.build_stats("jita", [], f)
    assert abs(st.loc[7, "A"] - 72) < 1e-9 and abs(st.loc[7, "lam_a"] - 1.0) < 1e-9
    empty = market.aggregate(pr.iloc[:0], upd, top)
    assert empty.loc[7, "ask_units"] == 0


def test_fill_and_session():
    pf = new_portfolio(CFG, 0)
    ledger = []
    sim = Sim(CFG, pf, Fees(CFG), np.random.default_rng(1), ledger)
    o = sim.place_buy("jita", 7, 10, 90_000.0, 0)
    assert o and pf["cash"] < 5e9 - 900_000
    stats = pd.DataFrame({"lam_a": [0.0], "lam_b": [0.0]}, index=[7])
    pr = pd.DataFrame({"type_id": [7], "side": ["bid"], "price": [89_000.0], "qty": [100.0]})
    sim.apply_fills("jita", pr, stats, 0, 7200)
    assert pf["inventory"]["jita"]["7"]["qty"] == 10 and not pf["orders"]
    top = pd.DataFrame({"best_ask": [100_000.0], "best_bid": [91_000.0]}, index=[7])
    plan = {"hub": "jita", "steps": [{"kind": "new_sell", "type_id": 7, "qty": 10, "floor": 95_000.0,
                                      "fallback": 120_000.0, "secs": 45, "group": 2}]}
    done, _ = sim.execute(plan, top, 8000, 1800)
    assert done == 1 and pf["orders"][0]["price"] == 99_990
    pr = pd.DataFrame({"type_id": [7], "side": ["ask"], "price": [100_000.0], "qty": [50.0]})
    sim.apply_fills("jita", pr, stats, 8000, 15200)
    assert not pf["orders"] and pf["pnl"]["realized"] > 0
