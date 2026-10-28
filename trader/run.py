"""One scheduled run: snapshot hubs -> infer trades -> fill paper orders -> simulated session -> new plan.

python -m trader.run
"""
import csv
import datetime as dt
import pickle
import sys
import time

import numpy as np
import pandas as pd

from . import logons, market, render
from .common import CACHE, DATA, HUBS, ROOT, STATE, load_config, load_json, save_json
from .esi import ESI
from .fees import Fees
from .sim import Sim, new_portfolio
from .strategy import candidates, make_plan

LEDGER_COLS = ["t", "event", "hub", "type_id", "qty", "price", "cash_delta", "note"]


def load_day(today):
    try:
        with open(CACHE / "day.pkl", "rb") as f:
            return pickle.load(f)
    except (FileNotFoundError, EOFError, pickle.UnpicklingError):
        return market.Day(today)


def collect(cfg, esi, now, day):
    """Snapshot every hub and fold the interval since the previous snapshot into `day`."""
    cc = cfg["collect"]
    meta = load_json(CACHE / "meta.json", {})
    tops, prints, intervals, health = {}, {}, {}, {}
    for hub in cc["hubs"]:
        info = HUBS[hub]
        try:
            df, consistent, lm = esi.region_orders(info["region"])
        except Exception as e:  # one bad hub shouldn't kill the run
            health[hub] = {"note": f"fetch failed: {e}"[:120]}
            continue
        cur = market.station_book(df, info["station"])
        del df
        t1 = lm or now
        top = market.tops(cur)
        path = CACHE / f"snap_{hub}.pkl"
        prev = pd.read_pickle(path) if path.exists() else None
        t0 = meta.get(hub)
        pr, note = pd.DataFrame(columns=market.PRINT_COLS), ""
        if not consistent:
            note = "pages from mixed cache generations; skipped"
        elif prev is None or t0 is None:
            note = "first snapshot"
        elif t1 <= t0:
            note = "no new data since last run"
        elif (t1 - t0) / 3600 > cc["max_gap_hours"]:
            note = f"gap {(t1 - t0) / 3600:.1f}h too long; restarted"
        elif market.gone_fraction(prev, cur) > cc["max_gone_frac"]:
            note = f"{market.gone_fraction(prev, cur):.0%} of orders vanished; skipped"
        else:
            pr = market.diff_prints(prev, cur, market.tops(prev), top, t1, cc["gone_weight"])
            upd = market.update_counts(cur, top, t0)
            day.add(hub, market.aggregate(pr, upd, top), (t1 - t0) / 3600)
            intervals[hub], prints[hub] = (t0, t1), pr
        if consistent and (t0 is None or t1 > t0):
            cur.to_pickle(path)
            meta[hub] = t1
        tops[hub] = top
        health[hub] = {"orders": len(cur), "hours": day.hours.get(hub, 0.0), "prints": len(pr), "note": note}
    save_json(CACHE / "meta.json", meta)
    return tops, prints, intervals, health


def load_names():
    path = DATA / "types.csv"
    if not path.exists():
        return {}
    df = pd.read_csv(path)
    return dict(zip(df.type_id, df.name))


def save_names(names):
    pd.DataFrame(sorted(names.items()), columns=["type_id", "name"]).to_csv(DATA / "types.csv", index=False)


def append_csv(path, cols, rows):
    new = not path.exists()
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(cols)
        w.writerows(rows)


def main():
    cfg = load_config()
    fees = Fees(cfg)
    now = time.time()
    today = market.utc_date(now)
    CACHE.mkdir(exist_ok=True)
    STATE.mkdir(exist_ok=True)
    esi = ESI()

    day = load_day(today)
    if day.date != today:
        day.flush(cfg["collect"]["daily_min_isk"])
        day = market.Day(today)
    tops, prints, intervals, health = collect(cfg, esi, now, day)
    with open(CACHE / "day.pkl", "wb") as f:
        pickle.dump(day, f)

    frames = market.load_window(today, cfg["strategy"]["window_days"])
    today_frame = day.frame()
    stats = {h: market.build_stats(h, frames, today_frame) for h in tops}

    pf = load_json(STATE / "portfolio.json", None) or new_portfolio(cfg, now)
    ledger = []
    sim = Sim(cfg, pf, fees, np.random.default_rng(int(now)), ledger)
    for h, (t0, t1) in intervals.items():
        sim.apply_fills(h, prints[h], stats[h], t0, t1)

    hub = cfg["strategy"]["hub"]
    sched = logons.ensure(cfg, load_json(STATE / "logons.json", []), now)
    sessions = load_json(STATE / "sessions.json", [])
    due = logons.due(sched, now)
    if due and hub in tops:
        e = due[-1]
        plan_prev = load_json(STATE / "plan.json", {"steps": [], "hub": hub})
        done, used = sim.execute(plan_prev, tops[hub], now, cfg["sim"]["session_seconds"] * e["frac"])
        for x in due:
            x["done"] = True
        sessions.append({"t": e["t"], "local": e["local"], "frac": e["frac"], "planned": len(plan_prev["steps"]),
                         "done": done, "secs": used, "run_t": now, "merged": len(due)})

    val = sim.valuation(tops)
    empty = pd.DataFrame()
    cands_by_hub = {h: candidates(cfg, fees, stats[h], tops[h]) for h in tops}
    cands = cands_by_hub.get(hub, empty)
    plan = make_plan(cfg, fees, sim, hub, stats.get(hub, empty), tops.get(hub, empty), cands, now, val["nw_book"])

    hours = float(stats[hub].hours.max()) if hub in stats and len(stats[hub]) else 0.0
    warm = None
    if hours < cfg["strategy"]["warmup_hours"]:
        warm = f"Warming up: {hours:.0f} of {cfg['strategy']['warmup_hours']} hours of market data collected."

    names = load_names()
    need = {s["type_id"] for s in plan["steps"]} | {int(k.split(":")[1]) for k in pf["per_type"]}
    for c in cands_by_hub.values():
        need |= set(int(i) for i in c.index[:15])
    missing = need - set(names)
    if missing:
        try:
            names.update(esi.names(missing))
            save_names(names)
        except Exception as e:
            print("name lookup failed:", e, file=sys.stderr)

    (ROOT / "INSTRUCTIONS.md").write_text(render.instructions(cfg, plan, names, val, warm))
    summary = render.summary(cfg, pf, val, health, sessions, names, cands_by_hub, cands, now)
    (STATE / "summary.md").write_text(summary)
    week = dt.date.fromtimestamp(now).isocalendar()
    week = f"{week[0]}-W{week[1]:02d}"
    if pf.get("report_week") and pf["report_week"] != week:
        (ROOT / "reports" / f"{pf['report_week']}.md").write_text(summary)
    pf["report_week"] = week
    pf["last_t"] = now

    save_json(STATE / "portfolio.json", pf)
    save_json(STATE / "plan.json", plan)
    save_json(STATE / "logons.json", sched)
    save_json(STATE / "sessions.json", sessions)
    append_csv(STATE / "ledger.csv", LEDGER_COLS, [(int(r[0]), *r[1:]) for r in ledger])
    append_csv(STATE / "metrics.csv", ["t", "cash", "escrow", "stock_cost", "nw_book", "nw_liquid", "realized",
                                       "orders", "esi_calls"],
               [(int(now), *(round(val[k]) for k in ("cash", "escrow", "stock_cost", "nw_book", "nw_liquid")),
                 round(pf["pnl"]["realized"]), len(pf["orders"]), esi.calls)])
    print(summary)


if __name__ == "__main__":
    main()
