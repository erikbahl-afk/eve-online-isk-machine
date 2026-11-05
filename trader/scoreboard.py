"""Experiment scoreboard: main vs every variant over the same dates (Thursday analysis).

    python3 -m trader.scoreboard            # common window = since the youngest portfolio started
    python3 -m trader.scoreboard --since 2026-11-01

Columns: return % over the window, realized (all time), liquidation / net worth, unsold stock share,
worst item, fees as a share of turnover, trades, and realized without each portfolio's best and worst item.
"""
import argparse
import csv
import datetime as dt

from .common import STATE, load_config, load_json

TRADES = {"buy_fill", "sell_fill", "market_buy", "market_sell"}


def _rows(path):
    try:
        with open(path) as f:
            return [{k: float(v) for k, v in r.items()} for r in csv.DictReader(f)]
    except FileNotFoundError:
        return []


def _trades(path):
    try:
        with open(path) as f:
            return sum(1 for r in csv.DictReader(f) if r["event"] in TRADES)
    except FileNotFoundError:
        return 0


def score(name, sdir, since):
    pf = load_json(sdir / "portfolio.json", None)
    rows = _rows(sdir / "metrics.csv")
    if not pf or not rows:
        return None
    last = rows[-1]
    base = next((r for r in rows if r["t"] >= since), last)
    ret = (last["nw_book"] / base["nw_book"] - 1) * 100 if base["nw_book"] else 0.0
    pnl = pf["pnl"]
    items = sorted((v["realized"], k) for k, v in pf.get("per_type", {}).items())
    trimmed = sum(r for r, _ in items[1:-1]) if len(items) > 2 else 0.0
    fees = sum(pnl.get(k, 0.0) for k in ("broker", "relist", "tax", "courier"))
    turnover = pnl.get("buys", 0.0) + pnl.get("sales", 0.0)
    nw = last["nw_book"] or 1.0
    return {
        "name": name, "start": dt.datetime.fromtimestamp(pf["created"], dt.timezone.utc).strftime("%m-%d"),
        "ret": ret, "realized": pnl["realized"], "liq": last["nw_liquid"] / nw,
        "unsold": (last["stock_cost"] + last["transit"]) / nw,
        "worst": items[0] if items else (0.0, "-"), "fees": fees / turnover if turnover else 0.0,
        "trades": _trades(sdir / "ledger.csv"), "trimmed": trimmed,
    }


def scoreboard(since=None):
    cfg = load_config()
    dirs = [("main", STATE)] + [(v["name"], STATE / "variants" / v["name"]) for v in cfg.get("variants", [])]
    if since is None:
        starts = [load_json(d / "portfolio.json", {}).get("created", 0) for _, d in dirs]
        since = max(starts or [0])
    return since, [s for s in (score(n, d, since) for n, d in dirs) if s]


def render(since, rows):
    m = 1e6
    out = [f"Window from {dt.datetime.fromtimestamp(since, dt.timezone.utc):%Y-%m-%d %H:%M} UTC",
           "| Portfolio | Start | Return % | Realized M | Liq/NW | Unsold | Worst item (M) | Fees/turnover | Trades | Realized w/o best+worst M |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append(f"| {r['name']} | {r['start']} | {r['ret']:+.2f} | {r['realized'] / m:.1f} | {r['liq']:.0%} | "
                   f"{r['unsold']:.0%} | {r['worst'][1]} ({r['worst'][0] / m:.1f}) | {r['fees']:.1%} | "
                   f"{r['trades']} | {r['trimmed'] / m:.1f} |")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="YYYY-MM-DD (UTC); default: youngest portfolio's start")
    a = ap.parse_args()
    since = dt.datetime.strptime(a.since, "%Y-%m-%d").replace(tzinfo=dt.timezone.utc).timestamp() if a.since else None
    print(render(*scoreboard(since)))


if __name__ == "__main__":
    main()
