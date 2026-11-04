"""Read the trading character over SSO: skills, training queue, attributes, standings, jump clones.

Writes state/character.json without the character's name or ID (the repo is public during practice).
"""
import datetime as dt

from .common import DATA, load_json, save_json

CUM_SP = [0, 250, 1415, 8000, 45255, 256000]  # skill points to reach each level, per point of rank
ATTR = {164: "charisma", 165: "intelligence", 166: "memory", 167: "perception", 168: "willpower"}
CALDARI_STATE, CALDARI_NAVY = 500001, 1000035


def skill_info(esi, names):
    """Rank and attributes per plan skill (cached in data/skills.json)."""
    path = DATA / "skills.json"
    cache = load_json(path, {})
    missing = [n for n in names if n not in cache]
    if missing:
        ids = {d["name"]: d["id"] for d in esi.request("POST", "/universe/ids/", json=missing).json()
               .get("inventory_types", [])}
        for n, i in ids.items():
            a = {d["attribute_id"]: d["value"] for d in
                 esi.request("GET", f"/universe/types/{i}/").json().get("dogma_attributes", [])}
            cache[n] = {"id": i, "rank": int(a[275]), "pri": ATTR[int(a[180])], "sec": ATTR[int(a[181])]}
        save_json(path, cache)
    return cache


def report(cfg, esi, token, cid, path):
    h = {"Authorization": f"Bearer {token}"}

    def get(p):
        r = esi.request("GET", p, headers=h)
        r.raise_for_status()
        return r.json()

    skills = get(f"/characters/{cid}/skills/")
    queue = get(f"/characters/{cid}/skillqueue/")
    attrs = get(f"/characters/{cid}/attributes/")
    standings = get(f"/characters/{cid}/standings/")
    clones = get(f"/characters/{cid}/clones/")

    plan = cfg["training"]["plan"]
    target = {}
    for name, lvl in plan:
        target[name] = max(target.get(name, 0), lvl)
    info = skill_info(esi, list(target))
    have = {s["skill_id"]: s for s in skills.get("skills", [])}
    rows, left_total, total, minutes = [], 0, 0, 0.0
    for name, lvl in target.items():
        si = info[name]
        need = CUM_SP[lvl] * si["rank"]
        cur = have.get(si["id"], {})
        sp = cur.get("skillpoints_in_skill", 0)
        left = max(0, need - sp)
        rate = attrs[si["pri"]] + attrs[si["sec"]] / 2  # SP per minute (Omega)
        rows.append({"skill": name, "level": cur.get("trained_skill_level", 0), "target": lvl, "sp_left": left})
        left_total += left
        total += need
        minutes += left / rate
    by_id = {v["id"]: k for k, v in info.items()}
    q = [{"skill": by_id.get(e["skill_id"], str(e["skill_id"])), "level": e["finished_level"],
          "finish": e.get("finish_date")} for e in sorted(queue, key=lambda e: e.get("queue_position", 0))]
    st = {(s["from_type"], s["from_id"]): s["standing"] for s in standings}
    br = next((r["level"] for r in rows if r["skill"] == "Broker Relations"), 0)
    fac, corp = st.get(("faction", CALDARI_STATE), 0.0), st.get(("npc_corp", CALDARI_NAVY), 0.0)
    out = {
        "updated": dt.datetime.now(dt.timezone.utc).isoformat(timespec="minutes"),
        "total_sp": skills.get("total_sp", 0), "unallocated_sp": skills.get("unallocated_sp", 0),
        "plan": rows, "plan_sp_total": total, "plan_sp_left": left_total,
        "plan_done_pct": round(100 * (1 - left_total / total), 1) if total else 100.0,
        "eta_days": round(minutes / 1440, 1),
        "attributes": {k: attrs[k] for k in ATTR.values()}, "bonus_remaps": attrs.get("bonus_remaps", 0),
        "queue": q, "queue_empty": not q,
        "standing_caldari_state": fac, "standing_caldari_navy": corp,
        "broker_fee_jita_now": round(max(1.0, 3 - 0.3 * br - 0.03 * fac - 0.02 * corp), 3),
        "jump_clones": len(clones.get("jump_clones", [])),
    }
    save_json(path, out)
    return out
