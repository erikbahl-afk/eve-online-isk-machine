"""Turn order-book snapshots into inferred trades ("prints") and per-type daily stats.

Between two snapshots of a station's book:
  * an order whose volume_remain dropped was filled by that amount (certain);
  * an order that vanished while at/below the current best price was most likely
    bought out (weighted by gone_weight); deeper vanished orders are treated as cancels.
side "ask" = someone bought from a sell order; side "bid" = someone sold into a buy order.

Competition is measured as how many near-top orders were created/repriced per hour
("updates"): each one is a moment a rival trader would have undercut us.
"""
import datetime as dt

import numpy as np
import pandas as pd

from .common import DATA

EPOCH = pd.Timestamp("1970-01-01", tz="UTC")
PRINT_COLS = ["type_id", "side", "price", "qty"]
NB = 4  # rival activity is tracked per 6-hour UTC block (00-06, 06-12, 12-18, 18-24)
UPD_COLS = ["ask_upd", "bid_upd"] + [f"{s}_upd{b}" for s in ("ask", "bid") for b in range(NB)]
SUM_COLS = ["ask_units", "ask_isk", "bid_units", "bid_isk"] + UPD_COLS
DAILY_COLS = ["hub", "type_id"] + SUM_COLS + ["best_ask", "best_bid", "hours"] + [f"hours{b}" for b in range(NB)]
NEAR_TOP = 0.05


def block_hours(t0, t1):
    """Hours of (t0, t1] falling in each UTC block."""
    out = [0.0] * NB
    t = t0
    while t < t1:
        nxt = min(t1, (t // 3600 + 1) * 3600)
        out[int(t // 3600 % 24 // 6)] += (nxt - t) / 3600
        t = nxt
    return out


def station_book(region_df, station_id):
    b = region_df.loc[region_df.location_id == station_id,
                      ["order_id", "type_id", "is_buy_order", "price", "volume_remain", "issued", "duration"]].copy()
    b["issued"] = (pd.to_datetime(b["issued"], utc=True) - EPOCH) // pd.Timedelta("1s")
    b = b.rename(columns={"is_buy_order": "is_buy", "volume_remain": "vol"})
    b["is_buy"] = b["is_buy"].astype(bool)
    return b.drop_duplicates("order_id").reset_index(drop=True)


def tops(book):
    asks = book[~book.is_buy].groupby("type_id").price.min().rename("best_ask")
    bids = book[book.is_buy].groupby("type_id").price.max().rename("best_bid")
    return pd.concat([asks, bids], axis=1)


def diff_prints(prev, cur, prev_top, cur_top, t1, gone_weight):
    m = prev.merge(cur[["order_id", "price", "vol"]], on="order_id", how="left", suffixes=("", "_c"))

    part = m[m.vol_c.notna() & (m.vol_c < m.vol)]
    # if the order was repriced in between we don't know the fill price: take the
    # one least favourable to us (lower for asks, higher for bids)
    p_part = np.where(part.is_buy, np.maximum(part.price, part.price_c), np.minimum(part.price, part.price_c))
    a = pd.DataFrame({"type_id": part.type_id.values, "is_buy": part.is_buy.values,
                      "price": p_part, "qty": (part.vol - part.vol_c).values.astype(float)})

    g = m[m.vol_c.isna()]
    g = g[g.issued + g.duration * 86400 > t1]  # expired orders aren't trades
    g = g.join(prev_top.add_prefix("p_"), on="type_id").join(cur_top.add_prefix("c_"), on="type_id")
    ask_hit = ~g.is_buy & ((g.price <= g.p_best_ask) | (g.price <= g.c_best_ask) | g.c_best_ask.isna())
    bid_hit = g.is_buy & ((g.price >= g.p_best_bid) | (g.price >= g.c_best_bid) | g.c_best_bid.isna())
    g = g[ask_hit | bid_hit]
    b = pd.DataFrame({"type_id": g.type_id.values, "is_buy": g.is_buy.values,
                      "price": g.price.values, "qty": g.vol.values.astype(float) * gone_weight})

    out = pd.concat([a, b], ignore_index=True)
    out["side"] = np.where(out.is_buy, "bid", "ask")
    return out[PRINT_COLS]


def gone_fraction(prev, cur):
    if len(prev) == 0:
        return 0.0
    return 1 - prev.order_id.isin(cur.order_id).mean()


def update_counts(cur, top, t0):
    """Near-top orders created or repriced after t0, per type, side and UTC block of the update."""
    r = cur[cur.issued > t0].join(top, on="type_id")
    r = r.assign(blk=r.issued // 3600 % 24 // 6)
    parts = []
    for side, mask in (("ask", ~r.is_buy & (r.price <= r.best_ask * (1 + NEAR_TOP))),
                       ("bid", r.is_buy & (r.price >= r.best_bid * (1 - NEAR_TOP)))):
        g = r[mask].groupby(["type_id", "blk"]).size().unstack("blk", fill_value=0)
        g = g.reindex(columns=range(NB), fill_value=0)
        g.columns = [f"{side}_upd{b}" for b in range(NB)]
        g[f"{side}_upd"] = g.sum(axis=1)
        parts.append(g)
    return pd.concat(parts, axis=1).fillna(0)


def aggregate(prints, upd, top):
    """One interval's per-type totals (same columns as the running day)."""
    p = prints.assign(isk=prints.price * prints.qty)
    parts = [upd]
    for side in ("ask", "bid"):
        ps = p[p.side == side].groupby("type_id")[["qty", "isk"]].sum()
        parts.append(ps.rename(columns={"qty": f"{side}_units", "isk": f"{side}_isk"}))
    df = pd.concat(parts, axis=1)
    for c in SUM_COLS:
        if c not in df:
            df[c] = 0.0
    df = df.fillna(0.0)
    return df.join(top, how="left")


class Day:
    """Running per-hub, per-type totals for the current UTC day (kept in the Actions cache)."""

    def __init__(self, date):
        self.date = date
        self.rows = {}
        self.hours = {}
        self.hb = {}  # hub -> hours observed per UTC block

    def add(self, hub, agg, t0, t1):
        old = self.rows.get(hub)
        if old is None:
            new = agg
        else:
            new = old[SUM_COLS].add(agg[SUM_COLS], fill_value=0.0)
            last = agg[["best_ask", "best_bid"]].combine_first(old[["best_ask", "best_bid"]])
            new = new.join(last)
        self.rows[hub] = new
        self.hours[hub] = self.hours.get(hub, 0.0) + (t1 - t0) / 3600
        self.hb[hub] = [a + b for a, b in zip(self.hb.get(hub, [0.0] * NB), block_hours(t0, t1))]

    def frame(self, min_isk=0.0):
        parts = []
        for hub, df in self.rows.items():
            d = df.rename_axis("type_id").reset_index()
            d.insert(0, "hub", hub)
            d["hours"] = self.hours.get(hub, 0.0)
            for b, h in enumerate(self.hb.get(hub, [0.0] * NB)):
                d[f"hours{b}"] = h
            parts.append(d[(d.ask_isk + d.bid_isk) >= min_isk])
        if not parts:
            return pd.DataFrame(columns=DAILY_COLS)
        return pd.concat(parts, ignore_index=True)[DAILY_COLS]

    def flush(self, min_isk):
        f = self.frame(min_isk)
        if len(f):
            path = DATA / "daily" / f"{self.date}.csv.gz"
            path.parent.mkdir(parents=True, exist_ok=True)
            f.to_csv(path, index=False, float_format="%.6g")
        return f


def utc_date(t):
    return dt.datetime.fromtimestamp(t, dt.timezone.utc).date().isoformat()


def load_window(today, days):
    """Daily files for the `days` UTC dates before today (missing files skipped)."""
    d0 = dt.date.fromisoformat(today)
    frames = []
    for k in range(1, days + 1):
        path = DATA / "daily" / f"{(d0 - dt.timedelta(days=k)).isoformat()}.csv.gz"
        if path.exists():
            frames.append(pd.read_csv(path).assign(day=k))
    return frames


def build_stats(hub, frames, today_frame):
    """Per-type rates over the window for one hub.

    A/B = units/day bought from asks / sold into bids, lam_a/lam_b = near-top updates per hour.
    Days where a type had no row count as zero activity.
    """
    fr = [f[f.hub == hub] for f in frames] + [today_frame[today_frame.hub == hub].assign(day=0)]
    fr = [f for f in fr if len(f)]
    if not fr:
        return pd.DataFrame()
    allf = pd.concat(fr, ignore_index=True)
    for c in DAILY_COLS:  # files written before a column existed
        if c not in allf:
            allf[c] = 0.0
    hours = allf.groupby("day").hours.max()
    total_h = hours.sum()
    if total_h <= 0:
        return pd.DataFrame()
    s = allf.groupby("type_id")[SUM_COLS].sum()
    block_h = allf.groupby("day")[[f"hours{b}" for b in range(NB)]].max().sum()
    out = pd.DataFrame(index=s.index)
    out["A"] = s.ask_units / total_h * 24
    out["B"] = s.bid_units / total_h * 24
    # damp one-off spikes: with 3+ days, cap the mean at 2x the median day
    if len(hours) >= 3:
        per_day = allf.pivot_table(index="type_id", columns="day", values=["ask_units", "bid_units"],
                                   aggfunc="sum", fill_value=0.0)
        for col, key in (("A", "ask_units"), ("B", "bid_units")):
            daily = per_day[key].reindex(columns=hours.index, fill_value=0.0) / hours * 24
            out[col] = np.minimum(out[col], 2 * daily.median(axis=1).reindex(out.index).fillna(0) + 1e-9)
    out["lam_a"] = s.ask_upd / total_h
    out["lam_b"] = s.bid_upd / total_h
    for side in ("a", "b"):
        for b in range(NB):
            h = block_h[f"hours{b}"]
            out[f"lam_{side}{b}"] = (s[f"{'ask' if side == 'a' else 'bid'}_upd{b}"] / h) if h >= 2 else out[f"lam_{side}"]
    out["vwap_a"] = (s.ask_isk / s.ask_units).where(s.ask_units > 0)
    out["vwap_b"] = (s.bid_isk / s.bid_units).where(s.bid_units > 0)
    out["isk_day"] = (s.ask_isk + s.bid_isk) / total_h * 24
    # trend: trade price over the last ~2 days vs the days before (NaN until there's history)
    rec = allf[allf.day <= 1].groupby("type_id")[["ask_isk", "ask_units"]].sum()
    pri = allf[allf.day >= 2].groupby("type_id")[["ask_isk", "ask_units"]].sum()
    out["trend_a"] = ((rec.ask_isk / rec.ask_units) / (pri.ask_isk / pri.ask_units)).reindex(out.index)
    out["hours"] = total_h
    return out
