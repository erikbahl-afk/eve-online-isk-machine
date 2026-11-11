import pandas as pd

from trader import structure
from trader.common import load_config


class R:
    def __init__(self, data, status=200, pages=1):
        self.data, self.status_code, self.headers = data, status, {"X-Pages": pages}

    def json(self):
        return self.data

    def raise_for_status(self):
        pass


BOOK = [
    {"order_id": 1, "type_id": 10, "is_buy_order": False, "price": 95.0, "volume_remain": 5, "range": "region"},
    {"order_id": 2, "type_id": 10, "is_buy_order": True, "price": 92.0, "volume_remain": 5, "range": "1"},
    {"order_id": 3, "type_id": 20, "is_buy_order": True, "price": 60.0, "volume_remain": 5, "range": "station"},
    {"order_id": 4, "type_id": 20, "is_buy_order": False, "price": 120.0, "volume_remain": 5, "range": "region"},
]


class FakeESI:
    def request(self, method, path, **kw):
        if "/search/" in path:
            return R({"structure": [555]})
        if path.startswith("/universe/structures/"):
            return R({"name": "Perimeter - Tranquility Trading Tower"})
        return R(BOOK)


def test_structure_report(tmp_path):
    jita = pd.DataFrame({"best_ask": [100.0, 110.0], "best_bid": [90.0, 70.0]}, index=pd.Index([10, 20], name="type_id"))
    out = structure.report(load_config(), FakeESI(), "tok", 1, jita, tmp_path / "s.json", {10: "A"})
    assert out["structure_id"] == 555 and out["types_also_in_jita"] == 2
    assert out["buy_orders_reaching_jita"] == 1          # the station-range bid can't reach Jita sellers
    assert out["types_bid_over_jita_reaching"] == 1      # 92 > Jita's 90 and range 1 jump
    assert out["top_ask_below_jita"][0]["type_id"] == 10 and out["share_ask_below_jita"] == 0.5
    assert (tmp_path / "s.json").exists()
