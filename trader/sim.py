"""Paper portfolio: simulated orders, fills from observed trades, and session execution."""
import math

import numpy as np

from .fees import tick_down, tick_up, valid_down, valid_up


def new_portfolio(cfg, t):
    return {
        "version": 1, "created": t, "start_isk": cfg["capital"]["start_isk"],
        "cash": float(cfg["capital"]["start_isk"]), "location": cfg["strategy"]["hub"],
        "next_oid": 1, "orders": [], "inventory": {},
        "pnl": {"realized": 0.0, "broker": 0.0, "relist": 0.0, "tax": 0.0, "sales": 0.0, "buys": 0.0},
        "per_type": {}, "last_t": None,
    }


def surv_avg(lam, hours):
    """Mean probability we're still top of book over a gap, rivals arriving at rate lam/h."""
    x = np.asarray(lam, dtype=float) * hours
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(x < 1e-9, 1.0, (1 - np.exp(-x)) / np.where(x < 1e-9, 1.0, x))


class Sim:
    def __init__(self, cfg, pf, fees, rng, ledger):
        self.cfg, self.pf, self.fees, self.rng, self.ledger = cfg, pf, fees, rng, ledger

    # ---- bookkeeping -------------------------------------------------------
    def _pt(self, hub, type_id):
        return self.pf["per_type"].setdefault(f"{hub}:{type_id}", {
            "bought_units": 0, "bought_isk": 0.0, "sold_units": 0, "sold_net": 0.0, "fees": 0.0, "realized": 0.0})

    def _fee(self, kind, amount, hub, type_id, t, note=""):
        self.pf["cash"] -= amount
        self.pf["pnl"][kind] += amount
        self.pf["pnl"]["realized"] -= amount
        pt = self._pt(hub, type_id)
        pt["fees"] += amount
        pt["realized"] -= amount
        self.ledger.append((t, kind, hub, type_id, 0, 0.0, -amount, note))

    def inv(self, hub, type_id):
        return self.pf["inventory"].setdefault(hub, {}).get(str(type_id))

    def _inv_add(self, hub, type_id, qty, cost, t, since=None):
        h = self.pf["inventory"].setdefault(hub, {})
        it = h.get(str(type_id))
        if it is None or it["qty"] <= 0:
            h[str(type_id)] = {"qty": qty, "cost": cost, "since": since or t}
        else:
            it["cost"] = (it["qty"] * it["cost"] + qty * cost) / (it["qty"] + qty)
            it["qty"] += qty
            it["since"] = min(it["since"], since or t)

    def _inv_take(self, hub, type_id, qty):
        it = self.inv(hub, type_id)
        qty = min(qty, it["qty"] if it else 0)
        if qty <= 0:
            return 0, 0.0, None
        it["qty"] -= qty
        cost, since = it["cost"], it["since"]
        if it["qty"] <= 0:
            del self.pf["inventory"][hub][str(type_id)]
        return qty, cost, since

    def order(self, oid):
        return next((o for o in self.pf["orders"] if o["oid"] == oid), None)

    def orders_for(self, hub, type_id, side):
        return [o for o in self.pf["orders"] if o["hub"] == hub and o["type_id"] == type_id and o["side"] == side]

    # ---- fills -------------------------------------------------------------
    def _round(self, x):
        f = math.floor(x)
        return int(f + (self.rng.random() < x - f))

    def apply_fills(self, hub, prints, stats, t0, t1):
        """Fill our open orders at `hub` from trades observed in (t0, t1].

        A buyer who paid >= our ask (or a seller who took <= our bid) would have hit us
        first, as long as no rival had undercut us yet; that survival decays with the
        type's update rate since our last reprice.
        """
        if prints is None or len(prints) == 0:
            return
        alpha = self.cfg["sim"]["alpha"]
        tmid = (t0 + t1) / 2
        by = {k: g for k, g in prints.groupby(["type_id", "side"])}
        for side, pside, lamcol in (("sell", "ask", "lam_a"), ("buy", "bid", "lam_b")):
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
                lam = float(stats[lamcol].get(o["type_id"], 0.1)) if len(stats) else 0.1
                surv = math.exp(-lam * max(0.0, tmid - o["updated"]) / 3600)
                q = min(o["remain"], self._round(alpha * elig * surv))
                if q <= 0:
                    continue
                used[o["type_id"]] = used.get(o["type_id"], 0.0) + q / alpha
                self._fill(o, q, t1)

    def _fill(self, o, q, t):
        o["remain"] -= q
        hub, ty, p = o["hub"], o["type_id"], o["price"]
        pt = self._pt(hub, ty)
        if o["side"] == "buy":
            self.pf["pnl"]["buys"] += p * q
            pt["bought_units"] += q
            pt["bought_isk"] += p * q
            self._inv_add(hub, ty, q, p, t)
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
            self.ledger.append((t, "sell_fill", hub, ty, q, p, net, f"o{o['oid']}"))
        if o["remain"] <= 0:
            self.pf["orders"].remove(o)

    # ---- player actions (a session executes plan steps) ----------------------
    def slots_used(self):
        return len(self.pf["orders"])

    def place_sell(self, hub, type_id, qty, price, t):
        qty, cost, since = self._inv_take(hub, type_id, qty)
        if qty <= 0:
            return None
        o = {"oid": self.pf["next_oid"], "hub": hub, "type_id": type_id, "side": "sell", "price": price,
             "qty": qty, "remain": qty, "created": t, "updated": t, "unit_cost": cost, "since": since}
        self.pf["next_oid"] += 1
        self.pf["orders"].append(o)
        self._fee("broker", self.fees.broker_fee(price, qty), hub, type_id, t, f"list o{o['oid']}")
        return o

    def place_buy(self, hub, type_id, qty, price, t):
        reserve = self.cfg["strategy"]["cash_reserve_frac"] * self.pf["start_isk"]
        afford = int((self.pf["cash"] - reserve) / (price * (1 + self.fees.broker)))
        qty = min(qty, afford)
        if qty <= 0:
            return None
        o = {"oid": self.pf["next_oid"], "hub": hub, "type_id": type_id, "side": "buy", "price": price,
             "qty": qty, "remain": qty, "created": t, "updated": t}
        self.pf["next_oid"] += 1
        self.pf["orders"].append(o)
        self.pf["cash"] -= price * qty  # escrow
        self._fee("broker", self.fees.broker_fee(price, qty), hub, type_id, t, f"bid o{o['oid']}")
        return o

    def reprice(self, o, new, t):
        fee = self.fees.relist_fee(o["price"], new, o["remain"])
        if o["side"] == "buy":
            extra = (new - o["price"]) * o["remain"]
            if extra + fee > self.pf["cash"]:
                return False
            self.pf["cash"] -= extra
        self._fee("relist", fee, o["hub"], o["type_id"], t, f"o{o['oid']} {o['price']:.2f}->{new:.2f}")
        o["price"], o["updated"] = new, t
        return True

    def cancel(self, o, t):
        if o["side"] == "buy":
            self.pf["cash"] += o["price"] * o["remain"]
        else:
            self._inv_add(o["hub"], o["type_id"], o["remain"], o["unit_cost"], t, o.get("since"))
        self.pf["orders"].remove(o)
        self.ledger.append((t, "cancel", o["hub"], o["type_id"], o["remain"], o["price"], 0.0, f"o{o['oid']}"))

    def execute(self, plan, top, t, budget):
        """Run plan steps in order until the time budget runs out. Returns (done, secs)."""
        c = self.cfg["sim"]
        used, done = c["secs_overhead"], 0
        slots = self.cfg["skills"]["order_slots"]
        for st in plan.get("steps", []):
            if used + st["secs"] > budget:
                break
            used += st["secs"]
            done += 1
            ty, hub = st["type_id"], plan["hub"]
            ba = top.best_ask.get(ty, np.nan) if len(top) else np.nan
            bb = top.best_bid.get(ty, np.nan) if len(top) else np.nan
            k = st["kind"]
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
                if self.slots_used() >= slots:
                    continue
                price = max(st["floor"], tick_down(ba)) if not np.isnan(ba) else st["fallback"]
                self.place_sell(hub, ty, st["qty"], price, t)
            elif k == "new_buy":
                if self.slots_used() >= slots or np.isnan(bb):
                    continue
                price = min(st["cap"], tick_up(bb))
                if price >= st["cap"] and bb >= st["cap"]:
                    continue  # rivals already above our cap
                self.place_buy(hub, ty, st["qty"], price, t)
        return done, used

    # ---- valuation ---------------------------------------------------------
    def valuation(self, tops):
        pf = self.pf
        escrow = sum(o["price"] * o["remain"] for o in pf["orders"] if o["side"] == "buy")
        on_sale = sum(o["unit_cost"] * o["remain"] for o in pf["orders"] if o["side"] == "sell")
        inv = sum(it["qty"] * it["cost"] for h in pf["inventory"].values() for it in h.values())
        liq = 0.0
        for o in pf["orders"]:
            if o["side"] == "sell":
                liq += self._liq(tops, o["hub"], o["type_id"], o["unit_cost"]) * o["remain"]
        for hub, h in pf["inventory"].items():
            for ty, it in h.items():
                liq += self._liq(tops, hub, int(ty), it["cost"]) * it["qty"]
        book = pf["cash"] + escrow + on_sale + inv
        return {"cash": pf["cash"], "escrow": escrow, "stock_cost": on_sale + inv,
                "nw_book": book, "nw_liquid": pf["cash"] + escrow + liq}

    def _liq(self, tops, hub, ty, cost):
        top = tops.get(hub)
        if top is None or ty not in top.index or np.isnan(top.best_bid.get(ty, np.nan)):
            return 0.5 * cost
        return min(cost, top.best_bid[ty]) * (1 - self.fees.tax)


def floor_price(fees, cfg, unit_cost, since, t):
    s = cfg["strategy"]
    be = fees.sell_breakeven(unit_cost)
    if since is not None and t - since > s["stale_days"] * 86400:
        return valid_up(be * (1 - s["stale_loss"]))
    return valid_up(be * (1 + s["floor_margin"]))


def buy_cap(fees, cfg, best_ask):
    target_net = tick_down(best_ask) * (1 - fees.tax - fees.broker)
    return valid_down(target_net / (1 + fees.broker) / (1 + cfg["strategy"]["min_margin"]))
