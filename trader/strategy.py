"""Station-trading strategy: pick types, then write the ordered session checklist."""
import math

import numpy as np
import pandas as pd

from .fees import tick_down, tick_up
from .sim import buy_cap, floor_price, surv_avg


def candidates(cfg, fees, stats, top):
    """Expected ISK/day per type for a trader who only reprices every logon_gap_hours."""
    s = cfg["strategy"]
    if len(stats) == 0 or len(top) == 0:
        return pd.DataFrame()
    df = stats.join(top, how="inner")
    df = df[df.best_ask.notna() & df.best_bid.notna() & (df.best_bid > 0)]
    df = df[~df.index.isin(s["exclude_types"])]
    if len(df) == 0:
        return df
    T = cfg["sim"]["logon_gap_hours"]
    alpha = cfg["sim"]["alpha"]
    df = df.assign(ask_t=df.best_ask.map(tick_down), bid_t=df.best_bid.map(tick_up))
    df["sa"] = surv_avg(df.lam_a, T)
    df["sb"] = surv_avg(df.lam_b, T)
    df["q"] = alpha * np.minimum(df.A * df.sa, df.B * df.sb)  # units/day we can flip
    df["unit_margin"] = df.ask_t * (1 - fees.tax - fees.broker) - df.bid_t * (1 + fees.broker)
    df["margin"] = df.unit_margin / df.bid_t
    stock = df.q * T / 24 * 1.5
    relist_rate = (1 - fees.relist_discount) * fees.broker
    p_a, p_b = 1 - np.exp(-df.lam_a * T), 1 - np.exp(-df.lam_b * T)
    df["relist_day"] = 24 / T * relist_rate * stock * (p_a * df.ask_t + p_b * df.bid_t)
    df["profit_day"] = df.unit_margin * df.q - df.relist_day
    band = s["vwap_band"]
    ok = (
        (df.hours >= s["warmup_hours"])
        & (df.margin >= s["min_margin"])
        & (df.profit_day >= s["min_daily_profit"])
        & (df.ask_t / df.bid_t <= s["max_price_ratio"])
        & (df.vwap_a.between(df.ask_t * (1 - band), df.ask_t * (1 + band)))
        & (df.vwap_b.between(df.bid_t * (1 - band), df.bid_t * (1 + band)))
    )
    return df[ok].sort_values("profit_day", ascending=False)


def _rank_all(cfg, fees, stats, top):
    """Same scoring without the filters, for the summary's 'near misses' view."""
    return candidates({**cfg, "strategy": {**cfg["strategy"], "min_margin": -1, "min_daily_profit": -1e18,
                                          "warmup_hours": 0, "vwap_band": 1e9, "max_price_ratio": 1e9}},
                      fees, stats, top)


def make_plan(cfg, fees, sim, hub, stats, top, cands, t, nw):
    s, c = cfg["strategy"], cfg["sim"]
    pf = sim.pf
    T = c["logon_gap_hours"]
    steps, secs = [], c["secs_overhead"]
    budget = s["plan_seconds"]
    slots = cfg["skills"]["order_slots"]
    n_orders = len(pf["orders"])

    def lam(ty, col):
        return float(stats[col].get(ty, 0.1)) if len(stats) else 0.1

    def best(ty, col):
        return float(top[col].get(ty, np.nan)) if len(top) else np.nan

    def add(step, value):
        steps.append({**step, "value": float(value)})

    selected = set(cands.index[:200]) if len(cands) else set()

    # 1. undercut (or likely-undercut-by-then) sell orders
    for o in [o for o in pf["orders"] if o["hub"] == hub and o["side"] == "sell"]:
        ba = best(o["type_id"], "best_ask")
        stale = lam(o["type_id"], "lam_a") * (t - o["updated"]) / 3600 > 0.7
        if (not np.isnan(ba) and ba <= o["price"]) or stale:
            fl = floor_price(fees, cfg, o["unit_cost"], o.get("since"), t)
            add({"kind": "modify_sell", "oid": o["oid"], "type_id": o["type_id"], "floor": fl,
                 "ref": ba, "mine": o["price"], "secs": c["secs_modify"], "group": 1}, o["remain"] * o["price"])

    # 2. list stock sitting in the hangar
    for ty, it in sorted(pf["inventory"].get(hub, {}).items(), key=lambda kv: -kv[1]["qty"] * kv[1]["cost"]):
        ty = int(ty)
        fl = floor_price(fees, cfg, it["cost"], it.get("since"), t)
        add({"kind": "new_sell", "type_id": ty, "qty": it["qty"], "floor": fl, "ref": best(ty, "best_ask"),
             "fallback": round(fl * 1.3, 2), "secs": c["secs_new_sell"], "group": 2}, it["qty"] * it["cost"])
        n_orders += 1

    # 3. buy orders: drop the ones no longer worth it, reprice the outbid ones
    for o in [o for o in pf["orders"] if o["hub"] == hub and o["side"] == "buy"]:
        ty = o["type_id"]
        ba, bb = best(ty, "best_ask"), best(ty, "best_bid")
        cap = buy_cap(fees, cfg, ba) if not np.isnan(ba) else 0.0
        if ty not in selected and (np.isnan(ba) or cap < o["price"] * 0.97):
            add({"kind": "cancel", "oid": o["oid"], "type_id": ty, "ref": bb, "mine": o["price"],
                 "secs": c["secs_cancel"], "group": 4}, o["remain"] * o["price"])
            n_orders -= 1
            continue
        stale = lam(ty, "lam_b") * (t - o["updated"]) / 3600 > 0.7
        if (not np.isnan(bb) and bb >= o["price"]) or stale or o["price"] > cap:
            add({"kind": "modify_buy", "oid": o["oid"], "type_id": ty, "cap": cap, "ref": bb,
                 "mine": o["price"], "secs": c["secs_modify"], "group": 3}, o["remain"] * o["price"])

    steps.sort(key=lambda st: (st["group"], -st["value"]))
    keep = []
    for st in steps:
        if secs + st["secs"] <= budget:
            keep.append(st)
            secs += st["secs"]
    steps = keep

    # 4. new buy orders, best expected profit first
    reserve = s["cash_reserve_frac"] * nw
    cash = pf["cash"] - reserve
    have_buy = {o["type_id"] for o in pf["orders"] if o["hub"] == hub and o["side"] == "buy"}
    limit = s["max_type_frac"] * nw
    for ty, r in cands.iterrows() if len(cands) else []:
        if secs + c["secs_new_buy"] > budget or n_orders + 2 > slots - 4 or cash <= 0:
            break
        if ty in have_buy:
            continue
        exposure = sum(o["remain"] * (o.get("unit_cost") or o["price"])
                       for o in pf["orders"] if o["hub"] == hub and o["type_id"] == ty)
        it = pf["inventory"].get(hub, {}).get(str(ty))
        exposure += it["qty"] * it["cost"] if it else 0.0
        qty = math.ceil(r.q * T / 24 * 2)
        qty = int(min(qty, (limit - exposure) / r.bid_t, cash / (r.bid_t * (1 + fees.broker))))
        if qty < 1:
            continue
        cap = buy_cap(fees, cfg, r.best_ask)
        if cap < r.bid_t:
            continue
        steps.append({"kind": "new_buy", "type_id": int(ty), "qty": qty, "cap": cap, "ref": float(r.best_bid),
                      "secs": c["secs_new_buy"], "group": 5, "value": float(r.profit_day),
                      "exp_profit_day": float(r.profit_day), "margin": float(r.margin)})
        secs += c["secs_new_buy"]
        cash -= qty * r.bid_t * (1 + fees.broker)
        n_orders += 2  # its sell order comes later
    for i, st in enumerate(steps, 1):
        st["n"] = i
    return {"generated": t, "hub": hub, "steps": steps, "est_secs": secs}
