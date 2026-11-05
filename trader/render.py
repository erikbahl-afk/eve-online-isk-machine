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
    3: ("Sell straight to buy orders", "The buy price here is close to what listing would net, so take it now: "
        "hangar → right-click → Sell This Item (Immediate). Only fill buy orders at or above the minimum."),
    4: ("Fix outbid buy orders", "My Orders → Buying, sorted by Type. Right-click → Modify Order. "
        "If yours is already the highest, skip."),
    5: ("Cancel buy orders", "My Orders → Buying. Right-click → Cancel Order."),
    6: ("New buy orders", "Market → search item → Place Buy Order. Range: Station. Duration: 3 months. "
        "Skip if the highest buy is already at or above the cap."),
    7: ("Buy for import", "Market → search item → Buy. Only take sell orders in this station, never above the max."),
    8: ("Ship to the other hub", ""),
}


BLOCKS = {1: "must do", 2: "should do", 3: "if there's time"}


def _item(names, ty):
    n = names.get(ty)
    return n if isinstance(n, str) and n else f"type {ty}"


def _hub_section(cfg, steps, names, hub, level="###"):
    out = []
    for g, (title, how) in GROUPS.items():
        gs = [s for s in steps if s["group"] == g]
        if not gs:
            continue
        out += [f"{level} {title}", f"_{how}_" if how else "", ""]
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
            out += ["| # | Item | Qty | Accept no less than | Highest buy when written |", "|---|---|---|---|---|"]
            out += [f"| {s['n']} | ☐ {_item(names, s['type_id'])} | {s['qty']:,} | **{_p(s['min_price'])}** | "
                    f"{_p(s['ref'])} |" for s in gs]
        elif g == 4:
            out += ["| # | Item | Yours | Type this | Rule: highest + 1 tick, never above | Highest when written |",
                    "|---|---|---|---|---|---|"]
            out += [f"| {s['n']} | ☐ {_item(names, s['type_id'])} | {_p(s['mine'])} | **{_p(s['target'])}** | "
                    f"{_p(s['cap'])} | {_p(s['ref'])} |" for s in gs]
        elif g == 5:
            out += ["| # | Item | Your price |", "|---|---|---|"]
            out += [f"| {s['n']} | ☐ {_item(names, s['type_id'])} | {_p(s['mine'])} |" for s in gs]
        elif g == 6:
            out += ["| # | Item | Qty | Type this | Rule: highest + 1 tick, never above | Highest when written |",
                    "|---|---|---|---|---|---|"]
            out += [f"| {s['n']} | ☐ {_item(names, s['type_id'])}{' (spec)' if s.get('tag') == 'spec' else ''} | "
                    f"{s['qty']:,} | **{_p(s['target'])}** | {_p(s['cap'])} | {_p(s['ref'])} |" for s in gs]
        elif g == 7:
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

    def density(ss):
        return sum(x.get("benefit", 0) for x in ss) / max(sum(x["secs"] for x in ss), 1)

    def blocks(ss, hub, skip_note=None):
        res = []
        for b, label in BLOCKS.items():
            bs = [x for x in ss if x.get("block", 1) == b]
            if not bs:
                continue
            res += [f"### Block {b} · {label} · about {max(1, round(sum(x['secs'] for x in bs) / 60))} min"]
            if b > 1 and skip_note and density(bs) < skip_note[1]:
                res += [f"_Short on time? Skip to the jump (step {skip_note[0]}): the next hub's Block 1 is worth "
                        "more per minute than the rest of this hub._"]
            res += [""] + _hub_section(cfg, bs, names, hub, "####")
        return res

    o_first = [x for x in second if x.get("block") == 1]
    note = (jump["n"], density(o_first)) if jump and o_first else None
    out += ["Each hub's steps come in **priority blocks**: finish Block 1 before anything else, and stop "
            "wherever your time runs out. Within a block, steps follow the in-game windows for speed.", ""]
    out += [f"## At {HUBS[L]['name']}", ""] + (blocks(first, L, note) if first else ["Nothing here.", ""])
    if jump:
        out += [f"## {jump['n']}. ☐ Jump clone to {HUBS[O]['name']}",
                f"_Clone Bay → Jump Clone → {HUBS[O]['name']}. Needs {cfg['strategy']['jump_cooldown_hours']} h "
                "since your last jump; if it isn't allowed yet, you're done for this session._", ""]
        out += [f"## At {HUBS[O]['name']}", ""] + blocks(second, O)
    if not steps:
        out += ["**Nothing to do this session.**", ""]
    out += ["---", f"Wallet {isk(val['cash'])} · escrow {isk(val['escrow'])} · stock {isk(val['stock_cost'])} · "
            f"in transit {isk(val['transit'])} · net worth {isk(val['nw_book'])} "
            f"(liquidation {isk(val['nw_liquid'])})", ""]
    return "\n".join(out)


def _why(text):
    """One-line explanation under a heading."""
    return [f"_{text}_", ""]


def summary(cfg, pf, val, health, sessions, names, station, imports_by_hub, t, stats=None, plan=None,
            variants=None, corner=None, char=None):
    s0 = pf["start_isk"]
    pnl = pf["pnl"]
    days = max((t - pf["created"]) / 86400, 1e-9)
    out = [f"# Summary · {_local(cfg, t)}", "",
           "Updated every ~2 hours. **Your real character** is the first section; everything after it is the "
           "**practice trader** (pretend ISK, real market data). Each section starts with a line on how to read it.", ""]

    if char:
        nxt = next((r for r in char["plan"] if r["sp_left"] > 0), None)
        a = char["attributes"]
        qtxt = ("**EMPTY: nothing is training!**" if char["queue_empty"]
                else ", ".join(f"{e['skill']} {e['level']}" for e in char["queue"][:4]))
        books = ", ".join(char.get("books_needed", [])) or "none, all injected"
        out += ["## 1. Your trading character",
                *_why("Read from the game over SSO. Shows how far the skill plan is and what needs your attention."),
                f"- **Skill plan:** {char['plan_done_pct']}% done · {char['plan_sp_left']:,} SP to go · "
                f"about **{char['eta_days']} days** of training left",
                f"- **Training now:** {qtxt}" + (f" · next plan skill: {nxt['skill']} → {nxt['target']}" if nxt else ""),
                f"- **Unallocated SP:** {char['unallocated_sp']:,}"
                + (" ← apply these (Retail, Broker Relations or Trade first)" if char["unallocated_sp"] else ""),
                f"- **Skill books still to buy and inject:** {books}",
                f"- Attributes Cha {a['charisma']} / Mem {a['memory']} / Wil {a['willpower']} · free remaps "
                f"{char['bonus_remaps']} · jump clones {char['jump_clones']} · total SP {char['total_sp']:,}",
                f"- Broker fee in Jita 4-4 with today's skills: {char['broker_fee_jita_now']}% (goal 1.5%)", ""]

    out += ["## 2. Practice portfolio",
            *_why(f"The paper trader started with {isk(s0)} on {_local(cfg, pf['created'], '%d %b')}. "
                  "Net worth counts stock at what we paid; liquidation is the worst case if we dumped "
                  "everything into buy orders right now."),
            f"- **Net worth:** {isk(val['nw_book'])} ({(val['nw_book'] / s0 - 1) * 100:+.2f}% in {days:.1f} days) · "
            f"liquidation {isk(val['nw_liquid'])}",
            f"- **Where the ISK is:** cash {isk(val['cash'])} · locked in buy orders {isk(val['escrow'])} · "
            f"stock {isk(val['stock_cost'])} · on a courier {isk(val['transit'])}",
            f"- **Profit so far (realized):** {isk(pnl['realized'])}. That's completed sales minus every fee paid. "
            f"Fees: broker {isk(pnl['broker'])}, relist {isk(pnl['relist'])}, sales tax {isk(pnl['tax'])}, "
            f"courier {isk(pnl['courier'])}",
            f"- **Location:** {pf['location']} · import hub {pf.get('import_hub') or 'not chosen yet'} · "
            f"shipments on the way {len(pf['in_transit'])}",
            f"- **What's limiting profit** (near 100% = the bottleneck): order slots "
            f"{len(pf['orders'])}/{cfg['skills']['order_slots']} · ISK in use "
            f"{(1 - val['cash'] / max(val['nw_book'], 1)) * 100:.0f}% · your time last plan "
            f"{(plan or {}).get('est_secs', 0) / 60:.0f} of {cfg['strategy']['plan_seconds'] / 60:.0f} min", ""]

    out += ["## 3. Results by strategy",
            *_why("station = buy and sell in the same hub · import = buy in Jita, ship, sell elsewhere · "
                  "spec = bets ahead of patches. Realized stays at 0 until items actually sell."),
            "| Strategy | Spent buying | Sold for | Fees | Realized profit |", "|---|---|---|---|---|"]
    for tag, v in sorted(pf["per_strategy"].items()):
        out.append(f"| {tag} | {isk(v['buys'])} | {isk(v['sales'])} | {isk(v['fees'])} | {isk(v['realized'])} |")
    out.append("")

    if variants:
        out += ["## 4. Strategy experiments",
                *_why("Separate pretend portfolios trading the same market with the same logins but different "
                      "settings. Whichever wins for about 2 weeks gets adopted by the main one."),
                "| Experiment | Net worth | Change | Realized profit | What it tests |", "|---|---|---|---|---|"]
        for name, v in [("main", {"nw": val["nw_book"], "realized": pnl["realized"],
                                  "note": "current settings (drives INSTRUCTIONS.md)"})] + list(variants.items()):
            out.append(f"| {name} | {isk(v['nw'])} | {(v['nw'] / v.get('start', s0) - 1) * 100:+.2f}% | "
                       f"{isk(v['realized'])} | {v['note']} |")
        out.append("")

    out += ["## 5. Recent simulated logins",
            *_why("When the practice 'you' logged in, which hubs it visited, and how much of the checklist "
                  "it got through. Partial = the session was cut short on purpose, to test that."),
            "| When (PT) | Hubs | Steps done / planned | Minutes | Cut short |", "|---|---|---|---|---|"]
    for e in sessions[-8:]:
        route = e.get("from", "?") + (f" → {e['to']}" if e.get("to") and e.get("to") != e.get("from") else "")
        out.append(f"| {e['local']} | {route} | {e['done']} / {e['planned']} | {e['secs'] / 60:.0f} | "
                   f"{'yes' if e['frac'] < 1 else ''} |")
    out.append("")

    out += ["## 6. Best and worst items",
            *_why("Per item: units bought and sold, fees paid, and realized profit. Items bought but not sold yet "
                  "show 0 profit and only their fees."),
            "| Item (hub) | Bought | Sold | Fees | Realized profit |", "|---|---|---|---|---|"]
    rows = sorted(pf["per_type"].items(), key=lambda kv: kv[1]["realized"])
    for k, v in (rows[-8:][::-1] + rows[:5]) if len(rows) > 13 else rows[::-1]:
        ty = int(k.split(":")[1])
        out.append(f"| {names.get(ty, ty)} ({k.split(':')[0]}) | {v['bought_units']:,} | {v['sold_units']:,} | "
                   f"{isk(v['fees'])} | {isk(v['realized'])} |")
    out.append("")

    out += ["## 7. Which hub is best",
            *_why("Market size = ISK spent per day buying from sell orders in that station. Items = how many pass "
                  "our filters. Profit/day = expected daily profit from the best 30. Station = trading inside that "
                  "hub; Import = buying in Jita and selling there."),
            "| Hub | Market size/day | Station items | Station profit/day | Import items | Import profit/day |",
            "|---|---|---|---|---|---|"]
    for hub in station:
        st, im = station[hub], imports_by_hub.get(hub)
        hs = (stats or {}).get(hub)
        size = isk(float((hs.A * hs.vwap_a).sum())) if hs is not None and len(hs) else "-"
        out.append(f"| {hub} | {size} | {len(st)} | {isk(st.head(30).profit_day.sum()) if len(st) else '-'} | "
                   f"{len(im) if im is not None else '-'} | "
                   f"{isk(im.head(30).profit_day.sum()) if im is not None and len(im) else '-'} |")
    out.append("")

    home = cfg["strategy"]["hub"]
    st = station.get(home)
    if st is not None and len(st):
        out += [f"## 8. Best items to trade inside {home.title()}",
                *_why("Buy at the highest buy price + 1 tick, sell at the lowest sell price − 1 tick. Margin is after "
                      "all fees. On top = how much of the time between your logins our order would stay the best "
                      "price before a rival undercuts it (sell side / buy side). Limited by = which resource it eats "
                      "most: order slots, ISK, or your time."),
                "| Item | Buy → sell price | Margin | Sold per day | On top (sell/buy) | Profit/day | Limited by |",
                "|---|---|---|---|---|---|---|"]
        for ty, r in st.head(12).iterrows():
            out.append(f"| {names.get(ty, ty)} | {isk(r.bid_t)} → {isk(r.ask_t)} | {r.margin * 100:.1f}% | {r.q:.1f} | "
                       f"{r.sa:.0%} / {r.sb:.0%} | {isk(r.profit_day)} | {r.get('limited_by', '-')} |")
        out.append("")
    im = imports_by_hub.get(pf.get("import_hub"))
    if im is not None and len(im):
        out += [f"## 9. Best items to import Jita → {pf['import_hub'].title()}",
                *_why("Buy from Jita sellers, ship by courier, sell just under the cheapest seller there. Margin is "
                      "after shipping and fees. m³ = cargo volume per unit."),
                "| Item | Jita price → sell price | m³ | Margin | Sold per day | On top | Profit/day | Limited by |",
                "|---|---|---|---|---|---|---|---|"]
        for ty, r in im.head(12).iterrows():
            out.append(f"| {names.get(ty, ty)} | {isk(r.src_ask)} → {isk(r.sell)} | {r.vol_m3:,.1f} | "
                       f"{r.margin * 100:.1f}% | {r.q:.1f} | {r.sa:.0%} | {isk(r.profit_day)} | "
                       f"{r.get('limited_by', '-')} |")
        out.append("")
    if corner is not None and len(corner):
        out += ["## 10. Cornering watchlist (read-only, nothing is traded)",
                *_why("Items where buying out the cheapest few sell orders and relisting higher would pay on paper. "
                      "We only watch them, to learn whether such prices hold or get undercut."),
                "| Hub | Item | Cheapest now | Buy out | Cost | Relist at | Paper profit | Return | Days to sell | "
                "Rival updates/day |", "|---|---|---|---|---|---|---|---|---|---|"]
        for _, r in corner.head(10).iterrows():
            out.append(f"| {r.hub} | {names.get(int(r.type_id), int(r.type_id))} | {isk(r.best_ask)} | "
                       f"{int(r.orders)} orders / {int(r.units):,} units | {isk(r.cost)} | {isk(r.relist)} | "
                       f"{isk(r.profit)} | {r.roi * 100:.0f}% | {r.exit_days:.1f} | {r.refill_day:.1f} |")
        out.append("")
    out += ["## 11. Data health",
            *_why("Is the market data flowing? Orders = orders seen in the station · Hours today = hours of data "
                  "collected since 00:00 UTC · Trades seen = trades inferred since the last snapshot. "
                  "Any note means something went wrong."),
            "| Hub | Orders | Hours today | Trades seen | Note |", "|---|---|---|---|---|"]
    for hub, h in health.items():
        out.append(f"| {hub} | {h.get('orders', 0):,} | {h.get('hours', 0):.1f} | {h.get('prints', 0):,} | "
                   f"{h.get('note', '')} |")
    out.append("")
    return "\n".join(out)
