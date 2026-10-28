"""Pick what to trade and write the ordered session checklist.

Strategies:
  station  buy and sell orders at the same hub (home hub and import hub)
  import   buy from Jita sellers, courier to the import hub, sell there
  spec     positions the reviewer opens in state/spec.json (e.g. ahead of a patch)

A session starts wherever the character is, does that hub's work, jump-clones to the other
hub (if the cooldown allows) and does that hub's work. Time is spent by tier:
  1 fix undercut sells + list stock, 2 fix/cancel buys + imports + spec, 3 new station buys.
Within each hub the checklist is grouped like the in-game windows and sorted by item name.
"""
import datetime as dt
import math

import numpy as np
import pandas as pd

from .fees import tick_down, tick_up, valid_down
from .sim import buy_cap, floor_price, surv_avg

GROUP_ORDER = {"modify_sell": 1, "new_sell": 2, "modify_buy": 3, "cancel": 4, "new_buy": 5,
               "instant_buy": 6, "courier": 7}


def _lam4(df, side):
    return df[[f"lam_{side}{b}" for b in range(4)]].to_numpy(dtype=float)


def candidates(cfg, fees, stats, top, start_w, exclude=()):
    """Station trading: expected ISK/day per type for a trader who reprices only at sessions."""
    s = cfg["strategy"]
    if len(stats) == 0 or len(top) == 0:
        return pd.DataFrame()
    df = stats.join(top, how="inner")
    df = df[df.best_ask.notna() & df.best_bid.notna() & (df.best_bid > 0)]
    df = df[~df.index.isin(list(s["exclude_types"]) + list(exclude))]
    if len(df) == 0:
        return df
    T = cfg["sim"]["logon_gap_hours"]
    alpha = cfg["sim"]["alpha"]
    df = df.assign(ask_t=df.best_ask.map(tick_down), bid_t=df.best_bid.map(tick_up))
    df["sa"] = surv_avg(_lam4(df, "a"), T, start_w)
    df["sb"] = surv_avg(_lam4(df, "b"), T, start_w)
    df["q"] = alpha * np.minimum(df.A * df.sa, df.B * df.sb)  # units/day we can flip
    df["unit_margin"] = df.ask_t * (1 - fees.tax - fees.broker) - df.bid_t * (1 + fees.broker)
    df["margin"] = df.unit_margin / df.bid_t
    stock = df.q * T / 24 * 1.5
    relist_rate = (1 - fees.relist_discount) * fees.broker
    df["relist_day"] = 24 / T * relist_rate * stock * ((1 - df.sa) * df.ask_t + (1 - df.sb) * df.bid_t)
    df["profit_day"] = df.unit_margin * df.q - df.relist_day
    c = cfg["sim"]
    df["capital"] = df.bid_t * df.q * T / 24 * 2  # buy order + stock covering two session gaps
    df["slots"] = 2
    df["secs"] = c["secs_modify"] * ((1 - df.sa) + (1 - df.sb)) + c["secs_new_sell"]  # clicks per session
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


def import_candidates(cfg, fees, src_top, dst_stats, dst_top, vols, route, start_w, exclude=()):
    """Buy at the source hub's best ask, ship, sell 1 tick under the destination's best ask."""
    s = cfg["strategy"]
    if len(dst_stats) == 0 or len(dst_top) == 0 or len(src_top) == 0:
        return pd.DataFrame()
    df = dst_stats.join(dst_top, how="inner").join(src_top.best_ask.rename("src_ask"), how="inner")
    df = df[df.best_ask.notna() & df.src_ask.notna() & df.vwap_a.notna()]
    df = df[~df.index.isin(list(s["exclude_types"]) + list(exclude))]
    if len(df) == 0:
        return df
    T = cfg["sim"]["logon_gap_hours"]
    df = df.assign(sell=df.best_ask.map(tick_down))
    df["vol_m3"] = [vols.get(int(t), np.nan) for t in df.index]
    v = df.vol_m3.fillna(0.0)
    # each unit pays its share of a full contract, by collateral or by volume, whichever binds
    fee, C, M = route["contract_fee"], route["max_collateral"], route["max_m3"]
    df["ship_unit"] = fee * np.maximum(df.src_ask / C, v / M)
    net = df.sell * (1 - fees.tax - fees.broker)
    df["unit_margin"] = net - df.src_ask - df.ship_unit
    df["margin"] = df.unit_margin / df.src_ask
    m = s["min_import_margin"]
    cap = np.minimum(net / (1 + m + fee / C), (net - fee * v / M) / (1 + m))
    df["max_price"] = cap.map(lambda p: valid_down(p) if p > 0 else 0.0)
    df["sa"] = surv_avg(_lam4(df, "a"), T, start_w)
    df["q"] = cfg["sim"]["alpha"] * df.A * df.sa
    relist = 24 / T * (1 - fees.relist_discount) * fees.broker * df.sell * df.q * T / 24 * (1 - df.sa)
    df["profit_day"] = df.unit_margin * df.q - relist
    c = cfg["sim"]
    df["capital"] = df.src_ask * df.q * (T + 24 * route["days"]) / 24 * 1.2  # stock in transit and on sale
    df["slots"] = 1
    df["secs"] = c["secs_instant_buy"] + c["secs_modify"] * (1 - df.sa) + c["secs_new_sell"]
    band = s["vwap_band"]
    ok = (
        (df.hours >= s["warmup_hours"])
        & (df.margin >= s["min_import_margin"])
        & (df.profit_day >= s["min_daily_profit"])
        & (df.sell / df.src_ask <= s["max_price_ratio"])
        & df.vwap_a.between(df.sell * (1 - band), df.sell * (1 + band))
    )
    return df[ok].sort_values("profit_day", ascending=False)


def add_density(df, cfg, nw):
    """Profit/day per share of the scarcest resource the item uses (shelf-space logic).

    Resources: order slots, ISK, and the player's seconds per session. An item that sells many
    cheap units can beat a high-margin slow seller when slots or time are the limit, and lose
    when capital is. Dividing by the largest share ranks by whatever binds for that item.
    """
    if len(df) == 0:
        return df
    shares = pd.DataFrame({"slots": df.slots / cfg["skills"]["order_slots"],
                           "ISK": df.capital / max(nw, 1.0),
                           "time": df.secs / cfg["strategy"]["plan_seconds"]})
    df = df.assign(limited_by=shares.idxmax(axis=1), density=df.profit_day / shares.max(axis=1).clip(lower=1e-9))
    return df.sort_values("density", ascending=False)


def walk_asks(book, ty, qty, max_price):
    """(units available, average price) buying up to qty from sell orders priced <= max_price."""
    a = book[(book.type_id == ty) & ~book.is_buy & (book.price <= max_price)].sort_values("price")
    take, cost = 0, 0.0
    for p, v in zip(a.price, a.vol):
        k = min(int(v), qty - take)
        take += k
        cost += k * p
        if take >= qty:
            break
    return take, (cost / take if take else 0.0)


def active_spec(spec, t):
    today = dt.datetime.fromtimestamp(t, dt.timezone.utc).date().isoformat()
    out = {}
    for e in spec:
        if e.get("active", True):
            out[(e["hub"], int(e["type_id"]))] = {**e, "selling": today >= e["sell_after"]}
    return out


class Planner:
    def __init__(self, ctx):
        self.__dict__.update(ctx)  # cfg, fees, sim, t, nw, names, tops, stats, books, vols, start_w,
        self.s, self.c = self.cfg["strategy"], self.cfg["sim"]  # station, imports, import_hub, spec
        self.pf = self.sim.pf
        self.home = self.s["hub"]
        self.specs = active_spec(self.spec, self.t)
        self.station = {h: add_density(df, self.cfg, self.nw) for h, df in self.station.items()}
        self.imports = add_density(self.imports, self.cfg, self.nw)

    def best(self, hub, ty, col):
        top = self.tops.get(hub)
        return float(top[col].get(ty, np.nan)) if top is not None and len(top) else np.nan

    def lam(self, hub, ty, side):
        st = self.stats.get(hub)
        return float(st[f"lam_{side}"].get(ty, 0.1)) if st is not None and len(st) else 0.1

    def step(self, kind, hub, value, **kw):
        return {"kind": kind, "hub": hub, "secs": self.c[{"modify_sell": "secs_modify", "modify_buy": "secs_modify",
                                                       "new_sell": "secs_new_sell", "new_buy": "secs_new_buy",
                                                       "cancel": "secs_cancel", "instant_buy": "secs_instant_buy",
                                                       "courier": "secs_courier"}[kind]],
                "value": float(value), "group": GROUP_ORDER[kind], **kw}

    # ---- per-hub maintenance -------------------------------------------------
    def maintenance(self, hub):
        t, tier1, tier2 = self.t, [], []
        for o in [o for o in self.pf["orders"] if o["hub"] == hub and o["side"] == "sell"]:
            ba = self.best(hub, o["type_id"], "best_ask")
            stale = self.lam(hub, o["type_id"], "a") * (t - o["updated"]) / 3600 > 0.7
            if (not np.isnan(ba) and ba <= o["price"]) or stale:
                sp = self.specs.get((hub, o["type_id"]), {})
                fl = floor_price(self.fees, self.cfg, o["unit_cost"], o.get("since"), t, sp.get("min_sell", 0.0))
                tier1.append(self.step("modify_sell", hub, o["remain"] * o["price"], oid=o["oid"],
                                       type_id=o["type_id"], floor=fl, ref=ba, mine=o["price"],
                                       target=max(fl, tick_down(ba)) if not np.isnan(ba) else o["price"]))
        for key, it in self.pf["inventory"].get(hub, {}).items():
            ty = int(key)
            sp = self.specs.get((hub, ty))
            if sp and not sp["selling"]:
                continue  # speculation: hold until sell_after
            if it.get("tag") == "import" and hub != self.import_hub and hub == self.home:
                continue  # bought for import, waiting for the courier step
            fl = floor_price(self.fees, self.cfg, it["cost"], it.get("since"), t, (sp or {}).get("min_sell", 0.0))
            ba = self.best(hub, ty, "best_ask")
            tier1.append(self.step("new_sell", hub, it["qty"] * it["cost"], type_id=ty, qty=it["qty"], floor=fl,
                                   ref=ba, target=max(fl, tick_down(ba)) if not np.isnan(ba) else round(fl * 1.3, 2),
                                   fallback=round(fl * 1.3, 2)))
        selected = set(self.station.get(hub, pd.DataFrame()).index[:200])
        for o in [o for o in self.pf["orders"] if o["hub"] == hub and o["side"] == "buy"]:
            ty = o["type_id"]
            ba, bb = self.best(hub, ty, "best_ask"), self.best(hub, ty, "best_bid")
            sp = self.specs.get((hub, ty))
            if sp:
                cap, keep = sp["max_buy"], not sp["selling"]
            else:
                cap = buy_cap(self.fees, self.cfg, ba) if not np.isnan(ba) else 0.0
                keep = ty in selected or (not np.isnan(ba) and cap >= o["price"] * 0.97)
            if not keep:
                tier2.append(self.step("cancel", hub, o["remain"] * o["price"], oid=o["oid"], type_id=ty, ref=bb,
                                       mine=o["price"]))
                continue
            stale = self.lam(hub, ty, "b") * (t - o["updated"]) / 3600 > 0.7
            if (not np.isnan(bb) and bb >= o["price"]) or stale or o["price"] > cap:
                tier2.append(self.step("modify_buy", hub, o["remain"] * o["price"], oid=o["oid"], type_id=ty,
                                       cap=cap, ref=bb, mine=o["price"],
                                       target=min(cap, tick_up(bb)) if not np.isnan(bb) else min(cap, o["price"])))
        return tier1, tier2

    # ---- exposure helpers ----------------------------------------------------
    def exposure(self, ty):
        e = sum(o["remain"] * (o.get("unit_cost") or o["price"]) for o in self.pf["orders"] if o["type_id"] == ty)
        e += sum(h[str(ty)]["qty"] * h[str(ty)]["cost"] for h in self.pf["inventory"].values() if str(ty) in h)
        e += sum(i["qty"] * i["cost"] for c in self.pf["in_transit"] for i in c["items"] if i["type_id"] == ty)
        return e

    def held_at(self, hub, ty):
        n = sum(o["remain"] for o in self.pf["orders"] if o["hub"] == hub and o["type_id"] == ty)
        it = self.pf["inventory"].get(hub, {}).get(str(ty))
        n += it["qty"] if it else 0
        n += sum(i["qty"] for c in self.pf["in_transit"] if c["to"] == hub for i in c["items"] if i["type_id"] == ty)
        return n

    # ---- imports (at the home hub) ---------------------------------------------
    def import_bundle(self):
        hub, dst = self.home, self.import_hub
        if not dst or dst not in self.tops or hub not in self.books:
            return None
        route, book = self.cfg["routes"][dst], self.books[hub]
        T = self.c["logon_gap_hours"] + route["days"] * 24
        steps, value, m3, profit = [], 0.0, 0.0, 0.0
        limit = self.s["max_type_frac"] * self.nw
        max_val, max_m3 = route["max_collateral"] * self.s["max_contracts"], route["max_m3"] * self.s["max_contracts"]
        waiting = [int(k) for k, it in self.pf["inventory"].get(hub, {}).items() if it.get("tag") == "import"]
        for ty, r in self.imports.iterrows():
            if len(steps) >= self.s["max_import_types"]:
                break
            ty = int(ty)
            want = math.ceil(r.q * T / 24 * 1.2) - self.held_at(dst, ty) - self.held_at(hub, ty)
            want = min(want, int((limit - self.exposure(ty)) / r.src_ask))
            vol = r.vol_m3 if not np.isnan(r.vol_m3) else 0.0
            if vol > 0:
                want = min(want, int((max_m3 - m3) / vol))
            want = min(want, int((max_val - value) / r.src_ask))
            if want < 1:
                continue
            got, avg = walk_asks(book, ty, want, r.max_price)
            if got < 1:
                continue
            steps.append(self.step("instant_buy", hub, r.profit_day, type_id=ty, qty=got, max_price=r.max_price,
                                   ref=float(r.src_ask), est_cost=avg * got))
            value += avg * got
            m3 += vol * got
            profit += r.profit_day
        waiting_val = sum(self.pf["inventory"][hub][str(t)]["qty"] * self.pf["inventory"][hub][str(t)]["cost"]
                          for t in waiting)
        n = contracts(route, value + waiting_val, m3)
        fill = max((value + waiting_val) / (n * route["max_collateral"]), m3 / (n * route["max_m3"]))
        if fill < self.s["min_contract_fill"] and not waiting:
            return None  # too little to fill a contract; the fee would eat the margin
        tys = [s["type_id"] for s in steps] + [t for t in waiting if t not in {s["type_id"] for s in steps}]
        steps.append(self.step("courier", hub, 0.0, to=dst, type_ids=tys, est_value=value + waiting_val,
                               est_m3=m3, contracts=n, est_fee=n * route["contract_fee"],
                               service=route.get("service", "the courier service")))
        steps[-1]["secs"] *= n
        return {"steps": steps, "value": profit, "cash": value + n * route["contract_fee"]}

    # ---- new buy orders --------------------------------------------------------
    def new_buys(self, hub, avoid):
        out = []
        for (h, ty), sp in self.specs.items():
            if h != hub or sp["selling"]:
                continue
            need = int(sp["qty"]) - self.held_at(hub, ty)
            if need > 0 and not any(o["hub"] == hub and o["type_id"] == ty and o["side"] == "buy"
                                    for o in self.pf["orders"]):
                out.append(("spec", ty, need, sp["max_buy"], 0.0, float("inf")))
        have = {o["type_id"] for o in self.pf["orders"] if o["hub"] == hub and o["side"] == "buy"}
        T = self.c["logon_gap_hours"]
        for ty, r in self.station.get(hub, pd.DataFrame()).iterrows():
            if ty in have or ty in avoid:
                continue
            out.append(("station", int(ty), math.ceil(r.q * T / 24 * 2), buy_cap(self.fees, self.cfg, r.best_ask),
                        float(r.profit_day), float(r.density)))
        return out

    # ---- assemble ---------------------------------------------------------------
    def plan(self):
        L = self.pf["location"]
        hubs = [self.home] + ([self.import_hub] if self.import_hub else [])
        O = next((h for h in hubs if h != L), None) if L in hubs else self.home
        budget = self.s["plan_seconds"] - self.c["secs_overhead"]
        used, jumped = 0, False
        chosen = []

        def fits(steps):
            nonlocal used, jumped
            secs = sum(s["secs"] for s in steps)
            extra = self.c["secs_jump"] if (O and not jumped and any(s["hub"] == O for s in steps)) else 0
            if used + secs + extra > budget:
                return False
            used += secs + extra
            jumped = jumped or extra > 0
            chosen.extend(steps)
            return True

        t1, t2 = [], []
        for h in [L] + ([O] if O else []):
            a, b = self.maintenance(h)
            t1 += a
            t2 += b
        for st in sorted(t1, key=lambda s: -s["value"]):
            fits([st])
        for st in sorted(t2, key=lambda s: -s["value"]):
            fits([st])

        cash = self.pf["cash"] - self.s["cash_reserve_frac"] * self.nw
        slots = self.cfg["skills"]["order_slots"] - 4
        n_orders = len(self.pf["orders"]) + sum(s["kind"] == "new_sell" for s in chosen) \
            - sum(s["kind"] == "cancel" for s in chosen)
        bundle = self.import_bundle()
        if bundle and bundle["cash"] <= cash and fits(bundle["steps"]):
            cash -= bundle["cash"]
            n_orders += sum(s["kind"] == "instant_buy" for s in bundle["steps"])  # their sell orders later

        # keep strategies on separate items so stock and results don't mix
        avoid = {ty for (_, ty) in self.specs}
        avoid |= {s["type_id"] for s in (bundle or {}).get("steps", []) if s["kind"] == "instant_buy"}
        avoid |= {o["type_id"] for o in self.pf["orders"] if o.get("tag") == "import"}
        avoid |= {i["type_id"] for c in self.pf["in_transit"] for i in c["items"]}
        avoid |= {int(k) for h in self.pf["inventory"].values() for k, it in h.items() if it.get("tag") == "import"}
        buys = []
        for h in [L] + ([O] if O else []):
            buys += [(h, *b) for b in self.new_buys(h, avoid)]
        limit = self.s["max_type_frac"] * self.nw
        spec_room = self.s["spec_max_frac"] * self.nw - sum(
            self.exposure(ty) for (_, ty) in self.specs)
        for hub, tag, ty, qty, cap, prof, _ in sorted(buys, key=lambda b: -b[6]):
            if n_orders + 2 > slots or cash <= 0:
                break
            bb = self.best(hub, ty, "best_bid")
            if np.isnan(bb) or bb >= cap:
                continue
            price = min(cap, tick_up(bb))
            room = (spec_room if tag == "spec" else limit - self.exposure(ty)) / price
            qty = int(min(qty, room, cash / (price * (1 + self.fees.broker))))
            if qty < 1:
                continue
            st = self.step("new_buy", hub, prof, type_id=ty, qty=qty, cap=cap, ref=bb,
                           target=price, tag=tag)
            if fits([st]):
                cash -= qty * price * (1 + self.fees.broker)
                n_orders += 2
                if tag == "spec":
                    spec_room -= qty * price

        def name(st):
            return str(self.names.get(st.get("type_id"), st.get("type_id", "")))

        steps = []
        for h in [L] + ([O] if O else []):
            part = sorted([s for s in chosen if s["hub"] == h], key=lambda s: (s["group"], name(s)))
            if h == O and part:
                steps.append({"kind": "jump", "hub": L, "to": O, "secs": self.c["secs_jump"], "group": 0,
                              "value": 0.0})
            steps += part
        for i, st in enumerate(steps, 1):
            st["n"] = i
        return {"generated": self.t, "hub": L, "location": L, "other": O, "steps": steps,
                "est_secs": used + self.c["secs_overhead"]}


def contracts(route, value, m3):
    """Courier contracts needed: each holds at most max_collateral of value and max_m3."""
    return max(1, math.ceil(value / route["max_collateral"] - 1e-9), math.ceil(m3 / route["max_m3"] - 1e-9))


def choose_import_hub(cfg, imports_by_hub, current):
    want = cfg["strategy"]["import_hub"]
    if want == "none":
        return None
    if want != "auto":
        return want
    if current:
        return current  # moving the second clone is a deliberate decision for a review
    scores = {h: float(df.head(30).profit_day.sum()) for h, df in imports_by_hub.items() if len(df)}
    return max(scores, key=scores.get) if scores else None
