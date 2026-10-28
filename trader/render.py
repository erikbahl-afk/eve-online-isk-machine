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
    1: ("Fix undercut sell orders", "My Orders → Selling, sorted by Type. Right-click → Modify Order. "
        "If yours is already the lowest, skip."),
    2: ("List new stock", "Item hangar sorted by Name. Right-click → Sell This Item → Advanced. Duration 3 months."),
    3: ("Fix outbid buy orders", "My Orders → Buying, sorted by Type. Right-click → Modify Order. "
        "If yours is already the highest, skip."),
    4: ("Cancel buy orders", "My Orders → Buying. Right-click → Cancel Order."),
    5: ("New buy orders", "Market → search item → Place Buy Order. Range: Station. Duration: 3 months. "
        "Skip if the highest buy is already at or above the cap."),
    6: ("Buy for import", "Market → search item → Buy. Only take sell orders in this station, never above the max."),
    7: ("Ship to the other hub", ""),
}


def _item(names, ty):
    return names.get(ty, f"type {ty}")


def _hub_section(cfg, steps, names, hub):
    out = []
    for g, (title, how) in GROUPS.items():
        gs = [s for s in steps if s["group"] == g]
        if not gs:
            continue
        out += [f"### {title}", f"_{how}_" if how else "", ""]
        if g == 1:
            out += ["| # | Item | Yours | Type this | Rule: lowest − 1 tick, never below | Lowest when written |",
                    "|---|---|---|---|---|---|"]
            out += [f"| {s['n']} | ☐ {_item(names, s['type_id'])} | {_p(s['mine'])} | **{_p(s['target'])}** | "
                    f"{_p(s['floor'])} | {_p(s['ref'])} |" for s in gs]
        elif g == 2:
            out += ["| # | Item | Qty | Type this | Rule: lowest − 1 tick, never below | Lowest when written |",
                    "|---|---|---|---|---|---|"]
            out += [f"| {s['n']} | ☐ {_item(names, s['type_id'])} | {s['qty']:,} | **{_p(s['target'])}** | "
                    f"{_p(s['floor'])} | {_p(s['ref'])} |" for s in gs]
        elif g == 3:
            out += ["| # | Item | Yours | Type this | Rule: highest + 1 tick, never above | Highest when written |",
                    "|---|---|---|---|---|---|"]
            out += [f"| {s['n']} | ☐ {_item(names, s['type_id'])} | {_p(s['mine'])} | **{_p(s['target'])}** | "
                    f"{_p(s['cap'])} | {_p(s['ref'])} |" for s in gs]
        elif g == 4:
            out += ["| # | Item | Your price |", "|---|---|---|"]
            out += [f"| {s['n']} | ☐ {_item(names, s['type_id'])} | {_p(s['mine'])} |" for s in gs]
        elif g == 5:
            out += ["| # | Item | Qty | Type this | Rule: highest + 1 tick, never above | Highest when written |",
                    "|---|---|---|---|---|---|"]
            out += [f"| {s['n']} | ☐ {_item(names, s['type_id'])}{' (spec)' if s.get('tag') == 'spec' else ''} | "
                    f"{s['qty']:,} | **{_p(s['target'])}** | {_p(s['cap'])} | {_p(s['ref'])} |" for s in gs]
        elif g == 6:
            out += ["| # | Item | Qty | Max price per unit | Lowest when written |", "|---|---|---|---|---|"]
            out += [f"| {s['n']} | ☐ {_item(names, s['type_id'])} | {s['qty']:,} | **{_p(s['max_price'])}** | "
                    f"{_p(s['ref'])} |" for s in gs]
        else:
            for s in gs:
                dest = HUBS[s["to"]]["name"]
                items = ", ".join(_item(names, t) for t in s["type_ids"])
                n = s.get("contracts", 1)
                out += [f"{s['n']}. ☐ **{n} courier contract{'s' if n > 1 else ''} via {s.get('service', 'PushX')}"
                        f"** → {dest}. Items: everything bought above plus any import stock already in the hangar "
                        f"({items}); total about {isk(s['est_value'])}, {s['est_m3']:,.0f} m³. "
                        f"Split it so each contract's collateral is at most 1.5B. Get the reward from the "
                        f"PushX quote page (about {isk(s['est_fee'] / n)} each), then Contracts → Create "
                        "Contract → Courier, assign to PushX's corporation, expiration 7 days, 7 days to complete."]
        out.append("")
    return out


def instructions(cfg, plan, names, val, warm_msg=None):
    L, O = plan["location"], plan.get("other")
    steps = plan["steps"]
    out = []
    if cfg["mode"] == "practice":
        out += ["> **PRACTICE MODE.** This is the paper trader's current plan. Nothing to do in game yet;",
                "> it shows what a real session would look like.", ""]
    out += ["# Session checklist", "",
            f"**Updated:** {_local(cfg, plan['generated'])} · **Start docked at:** {HUBS[L]['name']}  ",
            f"**Steps:** {len(steps)} · **Est. time:** {round(plan['est_secs'] / 60)} min. Work top to bottom; "
            "stop any time.  ",
            "**When you log off, tell Claude:** `done` or `stopped after step N`.", ""]
    if warm_msg:
        out += [f"_{warm_msg}_", ""]
    out += ["**Prices:** \"Type this\" was correct when written. If the market moved since then, apply the rule "
            "instead (4 significant digits: 1 tick below 12,340,000 is 12,330,000). "
            "\"Lowest/highest\" means other people's orders; yours are highlighted.", ""]
    jump = next((s for s in steps if s["kind"] == "jump"), None)
    first = [s for s in steps if s["hub"] == L and s["kind"] != "jump"]
    second = [s for s in steps if jump and s["hub"] == O]
    out += [f"## At {HUBS[L]['name']}", ""] + (_hub_section(cfg, first, names, L) if first else ["Nothing here.", ""])
    if jump:
        out += [f"## {jump['n']}. ☐ Jump clone to {HUBS[O]['name']}",
                f"_Clone Bay → Jump Clone → {HUBS[O]['name']}. Needs {cfg['strategy']['jump_cooldown_hours']} h "
                "since your last jump; if it isn't allowed yet, you're done for this session._", ""]
        out += [f"## At {HUBS[O]['name']}", ""] + _hub_section(cfg, second, names, O)
    if not steps:
        out += ["**Nothing to do this session.**", ""]
    out += ["---", f"Wallet {isk(val['cash'])} · escrow {isk(val['escrow'])} · stock {isk(val['stock_cost'])} · "
            f"in transit {isk(val['transit'])} · net worth {isk(val['nw_book'])} "
            f"(liquidation {isk(val['nw_liquid'])})", ""]
    return "\n".join(out)


def summary(cfg, pf, val, health, sessions, names, station, imports_by_hub, t, stats=None):
    s0 = pf["start_isk"]
    pnl = pf["pnl"]
    days = max((t - pf["created"]) / 86400, 1e-9)
    out = [f"# Summary · {_local(cfg, t)}", "", "Auto-generated every run. Reviewers: start here.", "",
           "## Portfolio",
           f"- Net worth (book): **{isk(val['nw_book'])}** ({(val['nw_book'] / s0 - 1) * 100:+.2f}% "
           f"over {days:.1f} days) · liquidation value {isk(val['nw_liquid'])}",
           f"- Cash {isk(val['cash'])} · escrow {isk(val['escrow'])} · stock {isk(val['stock_cost'])} · "
           f"in transit {isk(val['transit'])} · orders {len(pf['orders'])}/{cfg['skills']['order_slots']}",
           f"- Realized P&L {isk(pnl['realized'])} · sales {isk(pnl['sales'])} · buys {isk(pnl['buys'])} · "
           f"fees: broker {isk(pnl['broker'])}, relist {isk(pnl['relist'])}, tax {isk(pnl['tax'])}, "
           f"courier {isk(pnl['courier'])}",
           f"- Character at **{pf['location']}** · import hub: **{pf.get('import_hub') or 'none yet'}** · "
           f"shipments in transit: {len(pf['in_transit'])}", ""]
    out += ["## By strategy", "| Strategy | Buys | Sales | Fees | Realized |", "|---|---|---|---|---|"]
    for tag, v in sorted(pf["per_strategy"].items()):
        out.append(f"| {tag} | {isk(v['buys'])} | {isk(v['sales'])} | {isk(v['fees'])} | {isk(v['realized'])} |")
    out += ["", "## Recent sessions", "| When (PT) | Route | Steps done/planned | Minutes | Partial |",
            "|---|---|---|---|---|"]
    for e in sessions[-8:]:
        route = e.get("from", "?") + (f"→{e['to']}" if e.get("to") and e.get("to") != e.get("from") else "")
        out.append(f"| {e['local']} | {route} | {e['done']}/{e['planned']} | {e['secs'] / 60:.0f} | "
                   f"{'yes' if e['frac'] < 1 else ''} |")
    out += ["", "## Per-type results (best and worst realized)", "| Type | Bought | Sold | Fees | Realized |",
            "|---|---|---|---|---|"]
    rows = sorted(pf["per_type"].items(), key=lambda kv: kv[1]["realized"])
    for k, v in (rows[-8:][::-1] + rows[:5]) if len(rows) > 13 else rows[::-1]:
        ty = int(k.split(":")[1])
        out.append(f"| {names.get(ty, ty)} ({k.split(':')[0]}) | {v['bought_units']:,} | {v['sold_units']:,} | "
                   f"{isk(v['fees'])} | {isk(v['realized'])} |")
    out += ["", "## Hub comparison (expected profit/day of the top 30 types)",
            "Market size = ISK/day bought from sell orders at the station (what we'd be selling into).", "",
            "| Hub | Market size | Station types | Station top-30 | Import types (from Jita) | Import top-30 |",
            "|---|---|---|---|---|---|"]
    for hub in station:
        st, im = station[hub], imports_by_hub.get(hub)
        hs = (stats or {}).get(hub)
        size = isk(float((hs.A * hs.vwap_a).sum())) if hs is not None and len(hs) else "-"
        out.append(f"| {hub} | {size} | {len(st)} | {isk(st.head(30).profit_day.sum()) if len(st) else '-'} | "
                   f"{len(im) if im is not None else '-'} | "
                   f"{isk(im.head(30).profit_day.sum()) if im is not None and len(im) else '-'} |")
    home = cfg["strategy"]["hub"]
    st = station.get(home)
    if st is not None and len(st):
        out += ["", f"## Top station candidates at {home}",
                "| Type | Bid→Ask | Margin | Units/day | Still on top (ask/bid) | Exp. profit/day |",
                "|---|---|---|---|---|---|"]
        for ty, r in st.head(12).iterrows():
            out.append(f"| {names.get(ty, ty)} | {isk(r.bid_t)}→{isk(r.ask_t)} | {r.margin * 100:.1f}% | {r.q:.1f} | "
                       f"{r.sa:.0%}/{r.sb:.0%} | {isk(r.profit_day)} |")
    im = imports_by_hub.get(pf.get("import_hub"))
    if im is not None and len(im):
        out += ["", f"## Top import candidates Jita → {pf['import_hub']}",
                "| Type | Jita → sell | m³ | Margin | Units/day | Still on top | Exp. profit/day |",
                "|---|---|---|---|---|---|---|"]
        for ty, r in im.head(12).iterrows():
            out.append(f"| {names.get(ty, ty)} | {isk(r.src_ask)}→{isk(r.sell)} | {r.vol_m3:,.1f} | "
                       f"{r.margin * 100:.1f}% | {r.q:.1f} | {r.sa:.0%} | {isk(r.profit_day)} |")
    out += ["", "## Data health", "| Hub | Orders | Hours today | Prints this run | Note |", "|---|---|---|---|---|"]
    for hub, h in health.items():
        out.append(f"| {hub} | {h.get('orders', 0):,} | {h.get('hours', 0):.1f} | {h.get('prints', 0):,} | "
                   f"{h.get('note', '')} |")
    out.append("")
    return "\n".join(out)
