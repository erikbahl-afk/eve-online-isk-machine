"""Read a player structure's market (the Perimeter trade Keepstar) over SSO and compare it with Jita 4-4.

Open questions 3 and 9 in STRATEGY.md: is the structure's book better than Jita's (prices, spread, competition),
and do its buy orders with a range reach Jita sellers? Writes state/structure.json (no character data).
"""
import time

import pandas as pd

from .common import save_json

RANGE_JUMPS = {"station": 0, "solarsystem": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "10": 10, "20": 20,
               "30": 30, "40": 40, "region": 99}
COLS = ["order_id", "type_id", "is_buy_order", "price", "volume_remain", "range", "issued"]


def find_structure(esi, h, cid, name, fallback):
    """Structure ID by name via the character's search (needs esi-search.search_structures.v1)."""
    try:
        r = esi.request("GET", f"/characters/{cid}/search/", headers=h,
                        params={"categories": "structure", "search": name})
        ids = r.json().get("structure", []) if r.status_code == 200 else []
        for sid in ids:
            info = esi.request("GET", f"/universe/structures/{sid}/", headers=h)
            if info.status_code == 200 and name.lower() in info.json().get("name", "").lower():
                return sid, info.json().get("name", "")
    except Exception:
        pass
    return fallback, ""


def orders(esi, h, sid):
    first = esi.request("GET", f"/markets/structures/{sid}/", headers=h, params={"page": 1})
    first.raise_for_status()
    rows = list(first.json())
    for p in range(2, int(first.headers.get("X-Pages", 1)) + 1):
        r = esi.request("GET", f"/markets/structures/{sid}/", headers=h, params={"page": p})
        r.raise_for_status()
        rows += r.json()
    df = pd.DataFrame(rows, columns=COLS)
    df["is_buy_order"] = df["is_buy_order"].astype(bool)
    return df


def compare(df, jita_top, names=None, n=15):
    """Summary of the structure book against Jita's best bid/ask (jita_top: index type_id, best_ask, best_bid)."""
    asks = df[~df.is_buy_order].groupby("type_id").price.min().rename("s_ask")
    bids = df[df.is_buy_order].groupby("type_id").price.max().rename("s_bid")
    t = pd.concat([asks, bids], axis=1).join(jita_top[["best_ask", "best_bid"]], how="inner")
    both = t.dropna(subset=["s_ask", "best_ask"])
    buys = df[df.is_buy_order]
    reach = buys["range"].astype(str).map(RANGE_JUMPS).fillna(0)
    # Perimeter is 1 jump from Jita: a bid with range >= 1 jump can be filled by sellers in Jita 4-4.
    reaching = buys[reach >= 1].groupby("type_id").price.max().rename("s_bid_reach")
    t = t.join(reaching, how="left")
    over = t[t.s_bid_reach > t.best_bid].copy()  # structure bids that outbid Jita's best and reach Jita sellers
    over["gap"] = over.s_bid_reach / over.best_bid - 1
    nm = names or {}

    def rows(d, cols):
        return [{"type_id": int(i), "name": nm.get(int(i), ""), **{c: round(float(d.at[i, c]), 4) for c in cols}}
                for i in d.index[:n]]

    cheaper = both[both.s_ask < both.best_ask].copy()
    cheaper["gap"] = 1 - cheaper.s_ask / cheaper.best_ask
    return {
        "orders": int(len(df)), "sell_orders": int((~df.is_buy_order).sum()), "buy_orders": int(len(buys)),
        "types": int(df.type_id.nunique()), "types_also_in_jita": int(len(t)),
        "buy_orders_reaching_jita": int((reach >= 1).sum()),
        "ask_ratio_median": round(float((both.s_ask / both.best_ask).median()), 4) if len(both) else None,
        "share_ask_below_jita": round(float((both.s_ask < both.best_ask).mean()), 4) if len(both) else None,
        "types_bid_over_jita_reaching": int(len(over)),
        "top_bid_over_jita": rows(over.sort_values("gap", ascending=False), ["s_bid_reach", "best_bid", "gap"]),
        "top_ask_below_jita": rows(cheaper.sort_values("gap", ascending=False), ["s_ask", "best_ask", "gap"]),
    }


def report(cfg, esi, token, cid, jita_top, path, names=None):
    s = cfg.get("structure", {})
    h = {"Authorization": f"Bearer {token}"}
    sid, sname = find_structure(esi, h, cid, s.get("name", "Tranquility Trading Tower"), s.get("id"))
    if not sid:
        return None
    out = {"t": time.time(), "structure_id": int(sid), "name": sname,
           **compare(orders(esi, h, sid), jita_top, names)}
    save_json(path, out)
    return out
