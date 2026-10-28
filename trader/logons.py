"""Simulated player sessions: 1-2 weekday + 1-2 weekend logons per week, Pacific time."""
import datetime as dt
import random
from zoneinfo import ZoneInfo


def _week(cfg, monday, tz):
    c = cfg["sim"]
    rng = random.Random(monday.isoformat())  # deterministic per week
    out = []

    def at(day, h0, h1):
        minute = rng.randint(int(h0 * 60), int(h1 * 60))
        local = dt.datetime.combine(day, dt.time(minute // 60, minute % 60), tz)
        partial = rng.random() < c["partial_prob"]
        out.append({"t": local.timestamp(), "local": local.strftime("%a %d %b %H:%M"),
                    "frac": round(rng.uniform(c["partial_min"], c["partial_max"]), 2) if partial else 1.0,
                    "done": False})

    for d in rng.sample(range(5), rng.choice(c["weekday_logons"])):
        day = monday + dt.timedelta(days=d)
        if rng.random() < c["before_work_prob"]:
            at(day, 6.25, 7.5)
        else:
            at(day, 18, 22)
    for _ in range(rng.choice(c["weekend_logons"])):
        at(monday + dt.timedelta(days=rng.choice([5, 6])), 8, 23)
    return out


def ensure(cfg, sched, now):
    """Extend the schedule through next week; never rewrites existing entries."""
    tz = ZoneInfo(cfg["timezone"])
    today = dt.datetime.fromtimestamp(now, tz).date()
    have = {e.get("week") for e in sched}
    for k in (0, 1):
        monday = today - dt.timedelta(days=today.weekday()) + dt.timedelta(weeks=k)
        if monday.isoformat() in have:
            continue
        for e in _week(cfg, monday, tz):
            if e["t"] > now - 3600 or k == 1:  # don't backfill sessions before the sim started
                sched.append({**e, "week": monday.isoformat()})
    sched.sort(key=lambda e: e["t"])
    return sched


def due(sched, now):
    return [e for e in sched if not e["done"] and e["t"] <= now]
