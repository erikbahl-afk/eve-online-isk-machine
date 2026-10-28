"""Paper portfolio: simulated orders, fills from observed trades, and session execution.

Strategy tags on orders and stock ("station", "import", "spec") let results be split by strategy.
"""
import math

import numpy as np

from .fees import tick_down, tick_up, valid_down, valid_up

NB = 4


def new_portfolio(cfg, t):
    return {
        "version": 2, "created": t, "start_isk": cfg["capital"]["start_isk"],
        "cash": float(cfg["capital"]["start_isk"]), "location": cfg["strategy"]["hub"],
        "next_oid": 1, "orders": [], "inventory": {}, "in_transit": [],
        "pnl": {}, "per_type": {}, "per_strategy": {}, "last_t": None,
    }


def upgrade(pf):
    for k, v in (("in_transit", []), ("per_strategy", {}), ("last_jump", None), ("import_hub", None)):
        pf.setdefault(k, v)
    for k in ("realized", "broker", "relist", "tax", "sales", "buys", "courier"):
        pf["pnl"].setdefault(k, 0.0)
    return pf


def hazard(lam4, t_from, t_to):
    """Expected rival updates between two times, rates given per 6-hour UTC block."""
    total, t = 0.0, t_from
    while t < t_to:
        nxt = min(t_to, (t // 3600 + 1) * 3600)
        total += lam4[int(t // 3600 % 24 // 6)] * (nxt - t) / 3600
        t = nxt
    return total


def surv_avg(lam4, hours, start_w):
    """Mean chance we're still top of book over `hours` after repricing at a session.

    lam4: (n, 4) rival update rates per UTC block; start_w: weights over the 24 UTC hours
    at which sessions start.
    """
    H = np.repeat(np.atleast_2d(np.asarray(lam4, dtype=float)), 6, axis=1)  # n x 24
    T = int(round(hours))
    res = np.zeros(H.shape[0])
    for s in np.nonzero(start_w)[0]:
        seq = H[:, (s + np.arange(T)) % 24]
        cum = np.cumsum(seq, axis=1) - seq / 2
        res += start_w[s] * np.exp(-cum).mean(axis=1)
    return res / max(start_w.sum(), 1e-12)


def lam4_of(stats, ty, side):
    cols = [f"lam_{side}{b}" for b in range(NB)]
    if len(stats) and ty in stats.index and cols[0] in stats:
        return stats.loc[ty, cols].to_numpy(dtype=float)
    return np.full(NB, 0.1)


class Sim:
    def __init__(self, cfg, pf, fees, rng, ledger):
        self.cfg, self.pf, self.fees, self.rng, self.ledger = cfg, upgrade(pf), fees, rng, ledger

    # ---- bookkeeping -------------------------------------------------------
    def _pt(self, hub, type_id):
        return self.pf["per_type"].setdefault(f"{hub}:{type_id}", {
            "bought_units": 0, "bought_isk": 0.0, "sold_units": 0, "sold_net": 0.0, "fees": 0.0, "realized": 0.0})

    def _ps(self, tag):
        return self.pf["per_strategy"].setdefault(tag, {"realized": 0.0, "fees": 0.0, "sales": 0.0, "buys": 0.0})

    def _fee(self, kind, amount, hub, type_id, t, tag, note=""):
        self.pf["cash"] -= amount
        self.pf["pnl"][kind] += amount
        self.pf["pnl"]["realized"] -= amount
        for d in (self._pt(hub, type_id), self._ps(tag)):
            d["fees"] += amount
            d["realized"] -= amount
        self.ledger.append((t, kind, hub, type_id, 0, 0.0, -amount, note))

    def inv(self, hub, type_id):
        return self.pf["inventory"].setdefault(hub, {}).get(str(type_id))

    def _inv_add(self, hub, type_id, qty, cost, t, tag, since=None):
        h = self.pf["inventory"].setdefault(hub, {})
        it = h.get(str(type_id))
        if it is None or it["qty"] <= 0:
            h[str(type_id)] = {"qty": qty, "cost": cost, "since": since or t, "tag": tag}
        else:
            it["cost"] = (it["qty"] * it["cost"] + qty * cost) / (it["qty"] + qty)
            it["qty"] += qty
            it["since"] = min(it["since"], since or t)

    def _inv_take(self, hub, type_id, qty):
        it = self.inv(hub, type_id)
        qty = min(qty, it["qty"] if it else 0)
        if qty <= 0:
            return 0, 0.0, None, None
        it["qty"] -= qty
        out = (qty, it["cost"], it["since"], it.get("tag", "station"))
        if it["qty"] <= 0:
            del self.pf["inventory"][hub][str(type_id)]
        return out

    def order(self, oid):
        return next((o for o in self.pf["orders"] if o["oid"] == oid), None)

    # ---- fills -------------------------------------------------------------
    def _round(self, x):
        f = math.floor(x)
        return int(f + (self.rng.random() < x - f))

    def apply_fills(self, hub, prints, stats, t0, t1):
        """Fill our open orders at `hub` from trades observed in (t0, t1].

        A buyer who paid >= our ask (or a seller who took <= our bid) would have hit us
        first, as long as no rival had undercut us yet; that survival decays with the
        type's rival update rate (by time of day) since our last reprice.
        """
        if prints is None or len(prints) == 0:
            return
        alpha = self.cfg["sim"]["alpha"]
        tmid = (t0 + t1) / 2
        by = {k: g for k, g in prints.groupby(["type_id", "side"])}
        for side, pside, lside in (("sell", "ask", "a"), ("buy", "bid", "b")):
            mine = [o for o in self.pf["orders"] if o["hub"] == hub and o["side"] == side and o["remain"] > 0]
            mine.sort(key=lambda o: o["price"] if side == "sell" else -o["price"])
            used = {}
            for o in mine:
                g = by.get((o["type_id"], pside))
                if g is None:
                    continue
                elig = g.qty[g.price >= o["price"]].sum() if side == "sell" else g.qty[g.price <= o["price"]].sum()
                elig -= used.get(o["type_id"], 0.0)
                if elig <= 0:
                    continue
                surv = math.exp(-hazard(lam4_of(stats, o["type_id"], lside), o["updated"], tmid))
                q = min(o["remain"], self._round(alpha * elig * surv))
                if q <= 0:
                    continue
                used[o["type_id"]] = used.get(o["type_id"], 0.0) + q / alpha
                self._fill(o, q, t1)

    def _fill(self, o, q, t):
        o["remain"] -= q
        hub, ty, p, tag = o["hub"], o["type_id"], o["price"], o.get("tag", "station")
        pt, ps = self._pt(hub, ty), self._ps(tag)
        if o["side"] == "buy":
            self.pf["pnl"]["buys"] += p * q
            pt["bought_units"] += q
            pt["bought_isk"] += p * q
            ps["buys"] += p * q
            self._inv_add(hub, ty, q, p, t, tag)
            self.ledger.append((t, "buy_fill", hub, ty, q, p, -p * q, f"o{o['oid']}"))
        else:
            tax = self.fees.tax * p * q
            net = p * q - tax
            self.pf["cash"] += net
            gain = net - o["unit_cost"] * q
            self.pf["pnl"]["tax"] += tax
            self.pf["pnl"]["sales"] += p * q
            self.pf["pnl"]["realized"] += gain
            pt["sold_units"] += q
            pt["sold_net"] += net
            pt["realized"] += gain
            ps["sales"] += p * q
            ps["realized"] += gain
            self.ledger.append((t, "sell_fill", hub, ty, q, p, net, f"o{o['oid']}"))
        if o["remain"] <= 0:
            self.pf["orders"].remove(o)

    def arrivals(self, t):
        for c in [c for c in self.pf["in_transit"] if c["arrive"] <= t]:
            for it in c["items"]:
                self._inv_add(c["to"], it["type_id"], it["qty"], it["cost"], c["arrive"], "import")
                self.ledger.append((t, "arrived", c["to"], it["type_id"], it["qty"], it["cost"], 0.0, ""))
            self.pf["in_transit"].remove(c)

    # ---- player actions (a session executes plan steps) ----------------------
    def _new_order(self, **kw):
        o = {"oid": self.pf["next_oid"], **kw, "remain": kw["qty"], "created": kw["t"], "updated": kw["t"]}
        del o["t"]
        self.pf["next_oid"] += 1
        self.pf["orders"].append(o)
        return o

    def place_sell(self, hub, type_id, qty, price, t):
        qty, cost, since, tag = self._inv_take(hub, type_id, qty)
        if qty <= 0:
            return None
        o = self._new_order(hub=hub, type_id=type_id, side="sell", price=price, qty=qty, t=t,
                            unit_cost=cost, since=since, tag=tag)
        self._fee("broker", self.fees.broker_fee(price, qty), hub, type_id, t, tag, f"list o{o['oid']}")
        return o

    def _afford(self, unit):
        reserve = self.cfg["strategy"]["cash_reserve_frac"] * self.pf["start_isk"]
        return int(max(0.0, self.pf["cash"] - reserve) / unit)

    def place_buy(self, hub, type_id, qty, price, t, tag="station"):
        qty = min(qty, self._afford(price * (1 + self.fees.broker)))
        if qty <= 0:
            return None
        o = self._new_order(hub=hub, type_id=type_id, side="buy", price=price, qty=qty, t=t, tag=tag)
        self.pf["cash"] -= price * qty  # escrow
        self._fee("broker", self.fees.broker_fee(price, qty), hub, type_id, t, tag, f"bid o{o['oid']}")
        return o

    def instant_buy(self, hub, type_id, qty, max_price, book, t, tag="import"):
        """Buy from the cheapest sell orders up to max_price (no fees for the buyer)."""
        asks = book[(book.type_id == type_id) & ~book.is_buy & (book.price <= max_price)].sort_values("price")
        take, cost = 0, 0.0
        for p, v in zip(asks.price, asks.vol):
            k = min(int(v), qty - take, self._afford(p))
            if k <= 0:
                break
            take += k
            cost += k * p
            self.pf["cash"] -= k * p
        if take:
            self._inv_add(hub, type_id, take, cost / take, t, tag)
            self.pf["pnl"]["buys"] += cost
            self._pt(hub, type_id)["bought_units"] += take
            self._pt(hub, type_id)["bought_isk"] += cost
            self._ps(tag)["buys"] += cost
            self.ledger.append((t, "market_buy", hub, type_id, take, cost / take, -cost, ""))
        return take

    def courier(self, src, dst, type_ids, vols, t):
        """Ship hangar stock of type_ids from src to dst; shipping is added to unit cost."""
        r = self.cfg["routes"][dst]
        items, value, m3 = [], 0.0, 0.0
        for ty in type_ids:
            it = self.inv(src, ty)
            if not it:
                continue
            v = vols.get(ty, 0.0)
            room = int(min((r["max_m3"] - m3) / v if v > 0 else it["qty"],
                           (r["max_collateral"] - value) / it["cost"]))
            q, cost, _, _ = self._inv_take(src, ty, min(it["qty"], room))
            if q <= 0:
                continue
            items.append({"type_id": ty, "qty": q, "cost": cost})
            value += q * cost
            m3 += q * v
        if not items:
            return None
        fee = max(r["min_fee"], r["per_m3"] * m3) + r["collateral_pct"] * value
        for it in items:
            it["cost"] += fee * (it["cost"] / value)  # spread by value
        self.pf["cash"] -= fee
        self.pf["pnl"]["courier"] += fee
        self._ps("import")["fees"] += fee
        arrive = t + r["days"] * 86400 * (1 + 0.5 * self.rng.random())
        c = {"from": src, "to": dst, "sent": t, "arrive": arrive, "fee": fee, "value": value, "m3": m3, "items": items}
        self.pf["in_transit"].append(c)
        self.ledger.append((t, "courier", dst, 0, len(items), 0.0, -fee, f"{src}->{dst} {m3:.0f}m3"))
        return c

    def jump(self, to, t):
        last = self.pf.get("last_jump")
        if last is not None and t - last < self.cfg["strategy"]["jump_cooldown_hours"] * 3600:
            return False
        self.pf["location"], self.pf["last_jump"] = to, t
        self.ledger.append((t, "jump", to, 0, 0, 0.0, 0.0, ""))
        return True

    def reprice(self, o, new, t):
        fee = self.fees.relist_fee(o["price"], new, o["remain"])
        if o["side"] == "buy":
            extra = (new - o["price"]) * o["remain"]
            if extra + fee > self.pf["cash"]:
                return False
            self.pf["cash"] -= extra
        self._fee("relist", fee, o["hub"], o["type_id"], t, o.get("tag", "station"),
                  f"o{o['oid']} {o['price']:.2f}->{new:.2f}")
        o["price"], o["updated"] = new, t
        return True

    def cancel(self, o, t):
        if o["side"] == "buy":
            self.pf["cash"] += o["price"] * o["remain"]
        else:
            self._inv_add(o["hub"], o["type_id"], o["remain"], o["unit_cost"], t, o.get("tag", "station"),
                          o.get("since"))
        self.pf["orders"].remove(o)
        self.ledger.append((t, "cancel", o["hub"], o["type_id"], o["remain"], o["price"], 0.0, f"o{o['oid']}"))

    def execute(self, plan, tops, books, vols, t, budget):
        """Run plan steps in order until the time budget runs out. Returns (done, secs).

        Steps for a hub other than where the character is are skipped (orders can only be
        changed within the current region), e.g. when a jump clone was still on cooldown.
        """
        c = self.cfg["sim"]
        used, done = c["secs_overhead"], 0
        slots = self.cfg["skills"]["order_slots"]
        for st in plan.get("steps", []):
            if used + st["secs"] > budget:
                break
            used += st["secs"]
            done += 1
            k, hub = st["kind"], st["hub"]
            if k == "jump":
                self.jump(st["to"], t)
                continue
            if hub != self.pf["location"] or hub not in tops:
                continue
            top = tops[hub]
            ty = st.get("type_id")
            ba = top.best_ask.get(ty, np.nan) if ty is not None else np.nan
            bb = top.best_bid.get(ty, np.nan) if ty is not None else np.nan
            if k == "modify_sell":
                o = self.order(st["oid"])
                if o and not np.isnan(ba) and ba <= o["price"]:
                    new = max(st["floor"], tick_down(ba))
                    if new < o["price"]:
                        self.reprice(o, new, t)
            elif k == "modify_buy":
                o = self.order(st["oid"])
                if o:
                    want = min(st["cap"], tick_up(bb)) if not np.isnan(bb) else min(st["cap"], o["price"])
                    if (not np.isnan(bb) and bb >= o["price"] and want > o["price"]) or o["price"] > st["cap"]:
                        self.reprice(o, want, t)
            elif k == "cancel":
                o = self.order(st["oid"])
                if o:
                    self.cancel(o, t)
            elif k == "new_sell":
                if len(self.pf["orders"]) >= slots:
                    continue
                price = max(st["floor"], tick_down(ba)) if not np.isnan(ba) else st["fallback"]
                self.place_sell(hub, ty, st["qty"], price, t)
            elif k == "new_buy":
                if len(self.pf["orders"]) >= slots or np.isnan(bb) or bb >= st["cap"]:
                    continue  # rivals already at or above our cap
                self.place_buy(hub, ty, st["qty"], min(st["cap"], tick_up(bb)), t, st.get("tag", "station"))
            elif k == "instant_buy" and hub in books:
                self.instant_buy(hub, ty, st["qty"], st["max_price"], books[hub], t)
            elif k == "courier":
                self.courier(hub, st["to"], st["type_ids"], vols, t)
        return done, used

    # ---- valuation ---------------------------------------------------------
    def valuation(self, tops):
        pf = self.pf
        escrow = sum(o["price"] * o["remain"] for o in pf["orders"] if o["side"] == "buy")
        on_sale = sum(o["unit_cost"] * o["remain"] for o in pf["orders"] if o["side"] == "sell")
        inv = sum(it["qty"] * it["cost"] for h in pf["inventory"].values() for it in h.values())
        transit = sum(i["qty"] * i["cost"] for c in pf["in_transit"] for i in c["items"])
        liq = transit
        for o in pf["orders"]:
            if o["side"] == "sell":
                liq += self._liq(tops, o["hub"], o["type_id"], o["unit_cost"]) * o["remain"]
        for hub, h in pf["inventory"].items():
            for ty, it in h.items():
                liq += self._liq(tops, hub, int(ty), it["cost"]) * it["qty"]
        book = pf["cash"] + escrow + on_sale + inv + transit
        return {"cash": pf["cash"], "escrow": escrow, "stock_cost": on_sale + inv, "transit": transit,
                "nw_book": book, "nw_liquid": pf["cash"] + escrow + liq}

    def _liq(self, tops, hub, ty, cost):
        top = tops.get(hub)
        if top is None or ty not in top.index or np.isnan(top.best_bid.get(ty, np.nan)):
            return 0.5 * cost
        return min(cost, top.best_bid[ty]) * (1 - self.fees.tax)


def floor_price(fees, cfg, unit_cost, since, t, min_sell=0.0):
    s = cfg["strategy"]
    be = fees.sell_breakeven(unit_cost)
    if since is not None and t - since > s["stale_days"] * 86400:
        return valid_up(max(min_sell, be * (1 - s["stale_loss"])))
    return valid_up(max(min_sell, be * (1 + s["floor_margin"])))


def buy_cap(fees, cfg, best_ask):
    target_net = tick_down(best_ask) * (1 - fees.tax - fees.broker)
    return valid_down(target_net / (1 + fees.broker) / (1 + cfg["strategy"]["min_margin"]))
