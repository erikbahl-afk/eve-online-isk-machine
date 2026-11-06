"""Automatic red flags, computed every run (no AI). Every analysis session must address the open ones.

Thresholds live in config.toml [alerts]. Like every other number here they are guidelines: the analysis
sessions tune them by whether past alerts turned out useful or were false alarms.
"""
import datetime as dt
import re

from .common import ROOT, STATE, isk, load_json


def compute(cfg, pf, val, plan, health, char, now, names=None):
    a = cfg["alerts"]
    nm = lambda ty: (names or {}).get(int(ty), f"item {ty}")  # noqa: E731
    nw = max(val["nw_book"], 1.0)
    found = []

    def add(key, severity, text):
        found.append({"key": key, "severity": severity, "text": text})

    ratio = val["nw_liquid"] / nw
    if ratio < a["liquidation_ratio"]:
        add("liquidation", "high" if ratio < a["liquidation_ratio"] - 0.2 else "medium",
            f"Liquidation value is {ratio:.0%} of net worth ({isk(val['nw_liquid'])} of {isk(nw)}): "
            "much of the stock couldn't be sold quickly without a big loss.")

    pos = {}
    for o in pf["orders"]:
        pos[o["type_id"]] = pos.get(o["type_id"], 0.0) + o["remain"] * (o.get("unit_cost") or o["price"])
    for h in pf["inventory"].values():
        for ty, it in h.items():
            pos[int(ty)] = pos.get(int(ty), 0.0) + it["qty"] * it["cost"]
    for c in pf["in_transit"]:
        for it in c["items"]:
            pos[it["type_id"]] = pos.get(it["type_id"], 0.0) + it["qty"] * it["cost"]
    for ty, v in sorted(pos.items(), key=lambda kv: -kv[1]):
        if v / nw > a["position_frac"]:
            add(f"position:{ty}", "medium", f"{nm(ty)} is {v / nw:.1%} of net worth ({isk(v)}).")

    day = 86400
    for hub, h in pf["inventory"].items():
        for ty, it in h.items():
            age = (now - it.get("since", now)) / day
            if age > a["stale_days"]:
                add(f"stale_stock:{hub}:{ty}", "medium",
                    f"{it['qty']:,} × {nm(ty)} unsold in the {hub} hangar for {age:.0f} days.")
    for o in pf["orders"]:
        age = (now - o["created"]) / day
        if o["side"] == "sell" and age > a["stale_days"]:
            add(f"stale_sell:{o['oid']}", "medium",
                f"Sell order for {nm(o['type_id'])} in {o['hub']} still has {o['remain']:,} left after {age:.0f} days.")
        if o["side"] == "buy" and o["remain"] == o["qty"] and age > a["buy_stale_days"]:
            add(f"idle_buy:{o['oid']}", "info",
                f"Buy order for {nm(o['type_id'])} in {o['hub']} hasn't filled at all in {age:.0f} days "
                f"({isk(o['price'] * o['remain'])} tied up).")

    if plan.get("est_secs", 0) > cfg["sim"]["session_seconds"]:
        add("plan_time", "medium", f"Checklist needs {plan['est_secs'] / 60:.0f} min, longer than a session.")

    for hub, h in health.items():
        note = h.get("note", "")
        if any(w in note for w in ("failed", "too long", "skipped", "mixed")):
            add(f"data:{hub}", "high" if "failed" in note else "medium", f"Data problem in {hub}: {note}")

    if char:
        if char.get("queue_empty"):
            add("char_queue", "high", "Trading character's skill queue is EMPTY: nothing is training.")
        if char.get("unallocated_sp", 0) > 0:
            add("char_unallocated", "info", f"{char['unallocated_sp']:,} unallocated SP on the trading character.")

    # watch the watchers: the daily analysis should leave a journal entry every day
    journal = ROOT / "JOURNAL.md"
    dates = re.findall(r"^## (\d{4}-\d{2}-\d{2})", journal.read_text(), re.M) if journal.exists() else []
    if dates:
        last = dt.date.fromisoformat(max(dates))
        gap = (dt.datetime.fromtimestamp(now, dt.timezone.utc).date() - last).days
        if gap >= a.get("analysis_stale_days", 2):
            add("analysis_stale", "high", f"No analysis journal entry since {last} ({gap} days): "
                                          "the daily analysis session may have stopped.")

    # keep the first-seen time so the summary can show how long an alert has been open
    prev = {x["key"]: x.get("since", now) for x in load_json(STATE / "alerts.json", [])}
    for x in found:
        x["since"] = prev.get(x["key"], now)
    order = {"high": 0, "medium": 1, "info": 2}
    return sorted(found, key=lambda x: (order[x["severity"]], x["key"]))
