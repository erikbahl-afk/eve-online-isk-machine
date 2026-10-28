"""Markdown outputs: the session checklist (INSTRUCTIONS.md) and the reviewer summary."""
import datetime as dt
from zoneinfo import ZoneInfo

import numpy as np

from .common import HUBS, isk, price_str


def _local(cfg, t, fmt="%a %d %b %H:%M %Z"):
    return dt.datetime.fromtimestamp(t, ZoneInfo(cfg["timezone"])).strftime(fmt)


def _p(x):
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else price_str(x)


GROUPS = {
    1: ("Fix undercut sell orders", "Market → My Orders → Selling. Right-click the order → Modify Order."),
    2: ("List new stock", "Inventory (item hangar) → right-click item → Sell This Item. Duration 3 months."),
    3: ("Fix outbid buy orders", "Market → My Orders → Buying. Right-click → Modify Order."),
    4: ("Cancel buy orders", "Market → My Orders → Buying. Right-click → Cancel Order."),
    5: ("New buy orders", "Market → search item → Place Buy Order. Range: Station. Duration: 3 months."),
}


def instructions(cfg, plan, names, val, warm_msg=None):
    hub = HUBS[plan["hub"]]["name"]
    n = len(plan["steps"])
    out = []
    if cfg["mode"] == "practice":
        out += ["> **PRACTICE MODE.** This is the paper trader's current plan. Nothing to do in game yet;",
                "> it shows what a real session would look like.", ""]
    out += ["# Session checklist", "",
            f"**Updated:** {_local(cfg, plan['generated'])} · **Be docked at:** {hub}  ",
            f"**Steps:** {n} · **Est. time:** {round(plan['est_secs'] / 60)} min. Work top to bottom; stop any time.  ",
            "**When you log off, tell Claude:** `done` or `stopped after step N`.", ""]
    if warm_msg:
        out += [f"_{warm_msg}_", ""]
    out += ["**Ticks:** prices keep 4 significant digits, so \"1 tick below 12,340,000\" is 12,330,000. "
            "\"Lowest/highest\" means *other people's* best order (yours is highlighted).", ""]
    for g, (title, how) in GROUPS.items():
        steps = [s for s in plan["steps"] if s["group"] == g]
        if not steps:
            continue
        out += [f"## {title}", f"_{how}_", ""]
        if g in (1, 3):
            word = "lowest sell − 1 tick, never below" if g == 1 else "highest buy + 1 tick, never above"
            out += [f"| # | Item | Your price | Set to {word} | Best when written |", "|---|---|---|---|---|"]
            for s in steps:
                lim = s["floor"] if g == 1 else s["cap"]
                out.append(f"| {s['n']} | ☐ {names.get(s['type_id'], s['type_id'])} | {_p(s['mine'])} | "
                           f"**{_p(lim)}** | {_p(s['ref'])} |")
        elif g == 2:
            out += ["| # | Item | Qty | Price: lowest sell − 1 tick, never below | Lowest when written |",
                    "|---|---|---|---|---|"]
            for s in steps:
                out.append(f"| {s['n']} | ☐ {names.get(s['type_id'], s['type_id'])} | {s['qty']:,} | "
                           f"**{_p(s['floor'])}** | {_p(s['ref'])} |")
        elif g == 4:
            out += ["| # | Item | Your price |", "|---|---|---|"]
            for s in steps:
                out.append(f"| {s['n']} | ☐ {names.get(s['type_id'], s['type_id'])} | {_p(s['mine'])} |")
        else:
            out += ["| # | Item | Qty | Price: highest buy + 1 tick, never above | Highest when written | "
                    "Skip if highest ≥ cap |", "|---|---|---|---|---|---|"]
            for s in steps:
                out.append(f"| {s['n']} | ☐ {names.get(s['type_id'], s['type_id'])} | {s['qty']:,} | "
                           f"**{_p(s['cap'])}** | {_p(s['ref'])} | ✓ |")
        out.append("")
    if not plan["steps"]:
        out += ["**Nothing to do this session.**", ""]
    out += ["---", f"Wallet {isk(val['cash'])} · escrow {isk(val['escrow'])} · stock at cost "
            f"{isk(val['stock_cost'])} · net worth {isk(val['nw_book'])} (liquidation {isk(val['nw_liquid'])})", ""]
    return "\n".join(out)


def summary(cfg, pf, val, health, sessions, names, cands_by_hub, top_types, t):
    s0 = pf["start_isk"]
    pnl = pf["pnl"]
    days = max((t - pf["created"]) / 86400, 1e-9)
    out = [f"# Summary · {_local(cfg, t)}", "",
           "Auto-generated every run. Reviewers: start here.", "",
           "## Portfolio",
           f"- Net worth (book): **{isk(val['nw_book'])}** ({(val['nw_book'] / s0 - 1) * 100:+.2f}% "
           f"over {days:.1f} days) · liquidation value {isk(val['nw_liquid'])}",
           f"- Cash {isk(val['cash'])} · escrow {isk(val['escrow'])} · stock {isk(val['stock_cost'])} · "
           f"orders {len(pf['orders'])}/{cfg['skills']['order_slots']}",
           f"- Realized P&L {isk(pnl['realized'])} · sales {isk(pnl['sales'])} · buys {isk(pnl['buys'])} · "
           f"fees: broker {isk(pnl['broker'])}, relist {isk(pnl['relist'])}, tax {isk(pnl['tax'])}", ""]
    out += ["## Recent sessions", "| When (PT) | Steps done/planned | Minutes | Partial |", "|---|---|---|---|"]
    for e in sessions[-8:]:
        out.append(f"| {e['local']} | {e['done']}/{e['planned']} | {e['secs'] / 60:.0f} | "
                   f"{'yes' if e['frac'] < 1 else ''} |")
    out += ["", "## Per-type results (best and worst realized)", "| Type | Bought | Sold | Fees | Realized |",
            "|---|---|---|---|---|"]
    rows = sorted(pf["per_type"].items(), key=lambda kv: kv[1]["realized"])
    for k, v in (rows[-8:][::-1] + rows[:5]) if len(rows) > 13 else rows[::-1]:
        ty = int(k.split(":")[1])
        out.append(f"| {names.get(ty, ty)} ({k.split(':')[0]}) | {v['bought_units']:,} | {v['sold_units']:,} | "
                   f"{isk(v['fees'])} | {isk(v['realized'])} |")
    out += ["", "## Hub comparison (station trading, top 40 types)",
            "| Hub | Qualifying types | Sum exp. profit/day (top 40) | Median margin |", "|---|---|---|---|"]
    for hub, c in cands_by_hub.items():
        top40 = c.head(40)
        out.append(f"| {hub} | {len(c)} | {isk(top40.profit_day.sum()) if len(c) else '-'} | "
                   f"{f'{top40.margin.median() * 100:.1f}%' if len(c) else '-'} |")
    out += ["", f"## Top candidates at {cfg['strategy']['hub']}",
            "| Type | Bid→Ask | Margin | Units/day | Rival updates/h (ask/bid) | Exp. profit/day |",
            "|---|---|---|---|---|---|"]
    for ty, r in top_types.head(15).iterrows():
        out.append(f"| {names.get(ty, ty)} | {isk(r.bid_t)}→{isk(r.ask_t)} | {r.margin * 100:.1f}% | {r.q:.1f} | "
                   f"{r.lam_a:.2f}/{r.lam_b:.2f} | {isk(r.profit_day)} |")
    out += ["", "## Data health", "| Hub | Orders | Hours today | Prints this run | Note |", "|---|---|---|---|---|"]
    for hub, h in health.items():
        out.append(f"| {hub} | {h.get('orders', 0):,} | {h.get('hours', 0):.1f} | {h.get('prints', 0):,} | "
                   f"{h.get('note', '')} |")
    out.append("")
    return "\n".join(out)
