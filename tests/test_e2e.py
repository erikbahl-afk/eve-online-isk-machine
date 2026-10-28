"""Run the full pipeline for a few simulated days against a synthetic market."""
import shutil

import numpy as np
import pandas as pd

import trader.common as common
import trader.market as market
import trader.run as run
from trader.common import HUBS, ROOT


class FakeMarket:
    """Jita-only book: 30 types, random buyers/sellers, a few active rival traders."""

    def __init__(self, seed=0, hub="jita", markup=1.0):
        self.rng = np.random.default_rng(seed)
        self.hub = hub
        self.next_id = 1 + 10_000_000 * seed
        self.orders = {}
        base = np.random.default_rng(0)  # same items and base prices in every hub
        self.base = {ty: 10 ** base.uniform(4, 8) * markup for ty in range(1000, 1030)}
        for ty, p in self.base.items():
            for k in range(4):
                self._new(ty, False, p * (1.15 + 0.03 * k), 0)
                self._new(ty, True, p * (0.95 - 0.03 * k), 0)

    def _new(self, ty, buy, price, t):
        self.orders[self.next_id] = dict(order_id=self.next_id, type_id=ty, is_buy_order=buy, price=round(price, 2),
                                         volume_remain=int(self.rng.integers(5, 50)), issued=t, duration=90,
                                         location_id=HUBS[self.hub]["station"])
        self.next_id += 1

    def step(self, t):
        for ty in self.base:
            for buy in (False, True):
                side = [o for o in self.orders.values() if o["type_id"] == ty and o["is_buy_order"] == buy]
                side.sort(key=lambda o: -o["price"] if buy else o["price"])
                if side and self.rng.random() < 0.7:  # someone trades against the best order
                    o = side[0]
                    o["volume_remain"] -= int(self.rng.integers(1, o["volume_remain"] + 1))
                    if o["volume_remain"] <= 0:
                        del self.orders[o["order_id"]]
                if side and ty % 3 == 0 and self.rng.random() < 0.8:  # active rival reprices
                    o = side[-1]
                    best = side[0]["price"]
                    o["price"] = round(best * (1.001 if buy else 0.999), 2)
                    o["issued"] = t
                if len(side) < 3:
                    p = self.base[ty] * (0.9 if buy else 1.2)
                    self._new(ty, buy, p, t)

    def frame(self):
        df = pd.DataFrame(list(self.orders.values()))
        df["issued"] = pd.to_datetime(df.issued, unit="s", utc=True).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        return df


def test_pipeline(tmp_path, monkeypatch):
    for d in ("state", "data/daily", "cache", "reports"):
        (tmp_path / d).mkdir(parents=True)
    shutil.copy(ROOT / "config.toml", tmp_path / "config.toml")
    for mod in (common, run, market):
        for name, sub in (("ROOT", ""), ("STATE", "state"), ("DATA", "data"), ("CACHE", "cache")):
            if hasattr(mod, name):
                monkeypatch.setattr(mod, name, tmp_path / sub if sub else tmp_path)
    monkeypatch.setattr(run, "load_config", lambda: common.load_config(tmp_path / "config.toml"))

    markets = {HUBS["jita"]["region"]: FakeMarket(0), HUBS["amarr"]["region"]: FakeMarket(1, "amarr", 1.35)}
    clock = {"t": 1_790_000_000.0}

    class FakeESI:
        calls = 0

        def region_orders(self, region_id):
            if region_id not in markets:
                raise RuntimeError("not simulated")
            return markets[region_id].frame(), True, clock["t"]

        def names(self, ids):
            return {i: f"Item {i}" for i in ids}

        def volumes(self, ids):
            return {i: 5.0 for i in ids}

    monkeypatch.setattr(run, "ESI", FakeESI)
    monkeypatch.setattr(run.time, "time", lambda: clock["t"])
    for _ in range(12 * 9):  # nine days of 2-hourly runs
        clock["t"] += 7200
        for m in markets.values():
            m.step(clock["t"])
        run.main()

    pf = common.load_json(tmp_path / "state" / "portfolio.json", None)
    sessions = common.load_json(tmp_path / "state" / "sessions.json", [])
    assert sessions, "no simulated sessions ran"
    assert pf["pnl"]["broker"] > 0, "never placed an order"
    assert pf["import_hub"] == "amarr" and pf["pnl"]["courier"] > 0, "never shipped an import"
    assert any(s.get("to") != s.get("from") for s in sessions), "never jumped"
    assert (tmp_path / "INSTRUCTIONS.md").read_text().startswith("> **PRACTICE MODE")
    assert list((tmp_path / "data" / "daily").glob("*.csv.gz"))
    print(open(tmp_path / "state" / "summary.md").read())
    print(open(tmp_path / "INSTRUCTIONS.md").read())
