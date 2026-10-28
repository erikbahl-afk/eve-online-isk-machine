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

from . import corners, logons, market, render
from .common import CACHE, DATA, HUBS, ROOT, STATE, load_config, load_json, save_json
from .esi import ESI
from .fees import Fees
from .sim import Sim, new_portfolio
from .strategy import Planner, add_density, candidates, choose_import_hub, import_candidates

LEDGER_COLS = ["t", "event", "hub", "type_id", "qty", "price", "cash_delta", "note"]


def load_day(today):
    try:
        with open(CACHE / "day.pkl", "rb") as f:
            day = pickle.load(f)
        return day if hasattr(day, "hb") else market.Day(today)  # older format
    except (FileNotFoundError, EOFError, pickle.UnpicklingError, AttributeError):
        return market.Day(today)


def collect(cfg, esi, now, day):
    """Snapshot every hub and fold the interval since the previous snapshot into `day`."""
    cc = cfg["collect"]
    meta = load_json(CACHE / "meta.json", {})
    tops, books, prints, intervals, health = {}, {}, {}, {}, {}
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
            day.add(hub, market.aggregate(pr, upd, top), t0, t1)
            intervals[hub], prints[hub] = (t0, t1), pr
        if consistent and (t0 is None or t1 > t0):
            cur.to_pickle(path)
            meta[hub] = t1
        tops[hub], books[hub] = top, cur
        health[hub] = {"orders": len(cur), "hours": day.hours.get(hub, 0.0), "prints": len(pr), "note": note}
    save_json(CACHE / "meta.json", meta)
    return tops, books, prints, intervals, health


def load_types():
    path = DATA / "types.csv"
    if not path.exists():
        return {}, {}
    df = pd.read_csv(path)
    if "volume" not in df:
        df["volume"] = np.nan
    return (dict(zip(df.type_id, df.name)),
            {int(t): float(v) for t, v in zip(df.type_id, df.volume) if not pd.isna(v)})


def save_types(names, vols):
    ids = sorted(set(names) | set(vols))
    pd.DataFrame({"type_id": ids, "name": [names.get(i, "") for i in ids],
                  "volume": [vols.get(i, np.nan) for i in ids]}).to_csv(DATA / "types.csv", index=False)


def lookup(esi, names, vols, need_names, need_vols):
    try:
        miss = set(need_names) - set(names)
        if miss:
            names.update(esi.names(miss))
        miss = set(need_vols) - set(vols)
        if miss:
            vols.update(esi.volumes(miss))
    except Exception as e:
        print("type lookup failed:", e, file=sys.stderr)


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
    tops, books, prints, intervals, health = collect(cfg, esi, now, day)
    with open(CACHE / "day.pkl", "wb") as f:
        pickle.dump(day, f)

    frames = market.load_window(today, cfg["strategy"]["window_days"])
    today_frame = day.frame()
    stats = {h: market.build_stats(h, frames, today_frame) for h in tops}
    start_w = logons.start_profile(cfg, now)

    names, vols = load_types()
    shared = {"esi": esi, "now": now, "tops": tops, "books": books, "prints": prints, "intervals": intervals,
              "stats": stats, "start_w": start_w, "names": names, "vols": vols}
    variants = {}
    for v in cfg.get("variants", []):
        vcfg = merge(cfg, {k: val for k, val in v.items() if k not in ("name", "note")})
        r = run_portfolio(vcfg, STATE / "variants" / v["name"], shared)
        variants[v["name"]] = {"nw": r["val"]["nw_book"], "realized": r["pf"]["pnl"]["realized"], "note": v["note"]}
    r = run_portfolio(cfg, STATE, shared)
    pf, val, plan = r["pf"], r["val"], r["plan"]
    corner = corners.scan_all(cfg, Fees(cfg), books, stats, tops, val["nw_book"], today)
    lookup(esi, names, vols, corner.type_id.head(15) if len(corner) else [], [])
    save_types(names, vols)

    hub = cfg["strategy"]["hub"]
    hours = float(stats[hub].hours.max()) if hub in stats and len(stats[hub]) else 0.0
    warm = None
    if hours < cfg["strategy"]["warmup_hours"]:
        warm = f"Warming up: {hours:.0f} of {cfg['strategy']['warmup_hours']} hours of market data collected."
    (ROOT / "INSTRUCTIONS.md").write_text(render.instructions(cfg, plan, names, val, warm))
    summary = render.summary(cfg, pf, val, health, r["sessions"], names,
                             {h: add_density(df, cfg, val["nw_book"]) for h, df in r["station"].items()},
                             {h: add_density(df, cfg, val["nw_book"]) for h, df in r["imports_by_hub"].items()},
                             now, stats, plan, variants, corner)
    (STATE / "summary.md").write_text(summary)
    week = dt.date.fromtimestamp(now).isocalendar()
    week = f"{week[0]}-W{week[1]:02d}"
    if pf.get("report_week") and pf["report_week"] != week:
        (ROOT / "reports" / f"{pf['report_week']}.md").write_text(summary)
    pf["report_week"] = week
    save_json(STATE / "portfolio.json", pf)
    print(summary)


def merge(base, over):
    out = dict(base)
    for k, v in over.items():
        out[k] = merge(base.get(k, {}), v) if isinstance(v, dict) else v
    return out


def run_portfolio(cfg, sdir, sh):
    """Advance one paper portfolio (fills, a due session, a new plan) and save it under sdir."""
    sdir.mkdir(parents=True, exist_ok=True)
    now, tops, books, stats, names, vols = sh["now"], sh["tops"], sh["books"], sh["stats"], sh["names"], sh["vols"]
    fees = Fees(cfg)
    pf = load_json(sdir / "portfolio.json", None) or new_portfolio(cfg, now)
    ledger = []
    sim = Sim(cfg, pf, fees, np.random.default_rng(int(now)), ledger)
    sim.arrivals(now)
    for h, (t0, t1) in sh["intervals"].items():
        sim.apply_fills(h, sh["prints"][h], stats[h], t0, t1)

    hub = cfg["strategy"]["hub"]
    sched = logons.ensure(cfg, load_json(sdir / "logons.json", []), now)
    sessions = load_json(sdir / "sessions.json", [])
    due = logons.due(sched, now)
    if due and pf["location"] in tops:
        e = due[-1]
        plan_prev = load_json(sdir / "plan.json", {"steps": []})
        loc0 = pf["location"]
        done, used = sim.execute(plan_prev, tops, books, vols, now, cfg["sim"]["session_seconds"] * e["frac"])
        for x in due:
            x["done"] = True
        sessions.append({"t": e["t"], "local": e["local"], "frac": e["frac"], "planned": len(plan_prev["steps"]),
                         "done": done, "secs": used, "run_t": now, "merged": len(due), "from": loc0,
                         "to": pf["location"]})

    val = sim.valuation(tops)
    spec = load_json(STATE / "spec.json", [])
    spec_types = {int(e["type_id"]) for e in spec if e.get("active", True)}
    station = {h: candidates(cfg, fees, stats[h], tops[h], sh["start_w"], spec_types) for h in tops}
    imports_by_hub = {}
    if hub in tops:
        for h in tops:
            if h == hub or h not in cfg["routes"]:
                continue
            args = (cfg, fees, tops[hub], stats[h], tops[h])
            rough = import_candidates(*args, vols, cfg["routes"][h], sh["start_w"], spec_types)
            lookup(sh["esi"], names, vols, [], rough.index[:150])
            imports_by_hub[h] = import_candidates(*args, vols, cfg["routes"][h], sh["start_w"], spec_types)
    pf["import_hub"] = choose_import_hub(cfg, imports_by_hub, pf.get("import_hub"))
    imports = imports_by_hub.get(pf["import_hub"], pd.DataFrame())

    need = {int(k.split(":")[1]) for k in pf["per_type"]} | spec_types
    need |= {int(o["type_id"]) for o in pf["orders"]}
    for h in pf["inventory"].values():
        need |= {int(k) for k in h}
    for df in list(station.values()) + list(imports_by_hub.values()):
        need |= {int(i) for i in df.index[:60]}
    lookup(sh["esi"], names, vols, need, [])

    plan = Planner({"cfg": cfg, "fees": fees, "sim": sim, "t": now, "nw": val["nw_book"], "names": names,
                    "tops": tops, "stats": stats, "books": books, "vols": vols, "start_w": sh["start_w"],
                    "station": station, "imports": imports, "import_hub": pf["import_hub"],
                    "spec": spec}).plan()
    pf["last_t"] = now
    save_json(sdir / "portfolio.json", pf)
    save_json(sdir / "plan.json", plan)
    save_json(sdir / "logons.json", sched)
    save_json(sdir / "sessions.json", sessions)
    append_csv(sdir / "ledger.csv", LEDGER_COLS, [(int(r[0]), *r[1:]) for r in ledger])
    append_csv(sdir / "metrics.csv", ["t", "cash", "escrow", "stock_cost", "transit", "nw_book", "nw_liquid",
                                      "realized", "orders", "esi_calls"],
               [(int(now), *(round(val[k]) for k in ("cash", "escrow", "stock_cost", "transit", "nw_book",
                                                     "nw_liquid")),
                 round(pf["pnl"]["realized"]), len(pf["orders"]), sh["esi"].calls)])
    return {"pf": pf, "val": val, "plan": plan, "sessions": sessions, "station": station,
            "imports_by_hub": imports_by_hub}


if __name__ == "__main__":
    main()
