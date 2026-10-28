"""Read-only "cornerability" scanner: which items could be bought out and relisted higher?

For each item at a hub we walk up the sell side: buying out the cheapest k orders leaves order
k+1 as the new lowest price. We relist just under it, but never above the ceiling where other
traders would simply bring more in (Jita price + shipping for other hubs, 1.5x recent trade price
in Jita). An item qualifies when the buyout fits one item's risk budget, the paper return is
large, the stock would sell within ~10 days at today's demand, and rivals rarely add sell orders.

Nothing here trades. Results go into the summary and data/corners/<date>.csv, so later reviews
can check whether flagged items really stayed expensive or got refilled.
"""
import numpy as np
import pandas as pd

from .common import DATA
from .fees import tick_down

MAX_ORDERS = 20  # consider buying out at most the cheapest 20 sell orders


def scan(cfg, fees, hub, book, stats, jita_top, nw):
    s = cfg["corners"]
    if len(stats) == 0 or len(book) == 0:
        return pd.DataFrame()
    asks = book[~book.is_buy & book.type_id.isin(stats.index[stats.A > 0])]
    asks = asks.sort_values(["type_id", "price"])
    asks = asks.assign(rank=asks.groupby("type_id").cumcount())
    asks = asks[asks["rank"] <= MAX_ORDERS]
    g = asks.groupby("type_id")
    asks = asks.assign(units=g.vol.cumsum(), cost=(asks.price * asks.vol).groupby(asks.type_id).cumsum(),
                       next_price=g.price.shift(-1))
    asks = asks[asks.next_price.notna()].join(stats[["A", "vwap_a", "lam_a"]], on="type_id")
    if hub == cfg["strategy"]["hub"] or hub not in cfg["routes"]:
        ceiling = asks.vwap_a * 1.5
    else:
        r = cfg["routes"][hub]
        ja = asks.type_id.map(jita_top.best_ask)
        ceiling = ja * (1 + r["contract_fee"] / r["max_collateral"] + 0.05)  # where imports kick in
    relist = np.fmin(asks.next_price, ceiling).map(lambda p: tick_down(p) if p > 0 else np.nan)
    df = asks.assign(relist=relist, ceiling=ceiling)
    df["profit"] = df.units * df.relist * (1 - fees.tax - fees.broker) - df.cost
    df["roi"] = df.profit / df.cost
    df["exit_days"] = df.units / (df.A * cfg["sim"]["alpha"]).clip(lower=1e-9)
    df["refill_day"] = df.lam_a * 24  # rival sell orders created/updated near the top per day
    ok = ((df.cost <= cfg["strategy"]["max_type_frac"] * nw) & (df.cost >= s["min_cost"])
          & (df.roi >= s["min_roi"]) & (df.exit_days <= s["max_exit_days"]) & (df.refill_day <= s["max_refill_day"]))
    best = df[ok].sort_values("profit", ascending=False).groupby("type_id").head(1)
    best = best.assign(hub=hub, best_ask=best.type_id.map(book[~book.is_buy].groupby("type_id").price.min()))
    return best[["hub", "type_id", "best_ask", "rank", "units", "cost", "relist", "profit", "roi", "exit_days",
                 "refill_day"]].rename(columns={"rank": "orders"}).assign(orders=lambda d: d.orders + 1)


def scan_all(cfg, fees, books, stats, tops, nw, date):
    parts = [scan(cfg, fees, h, books[h], stats.get(h, pd.DataFrame()), tops.get(cfg["strategy"]["hub"],
                  pd.DataFrame(columns=["best_ask"])), nw) for h in books]
    parts = [p for p in parts if len(p)]
    if not parts:
        return pd.DataFrame()
    out = pd.concat(parts, ignore_index=True).sort_values("profit", ascending=False)
    path = DATA / "corners" / f"{date}.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    out.head(50).to_csv(path, index=False, float_format="%.6g")
    return out
