"""Check inferred trade volumes against CCP's official daily history.

python -m trader.calibrate [hub] [n_items]

Our volumes come from diffing order-book snapshots at the hub station; the history endpoint
counts the whole region. Station volume should be a large, stable share of the region's (well
under 100%). A ratio far above 1 means we're over-counting fills; a very low one means under-counting.
"""
import concurrent.futures as cf
import datetime as dt
import sys

import numpy as np
import pandas as pd

from . import market
from .common import HUBS, load_config
from .esi import ESI


def main():
    hub = sys.argv[1] if len(sys.argv) > 1 else "jita"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    cfg = load_config()
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    frames = market.load_window(today, cfg["strategy"]["window_days"])
    days = sorted({f.day.iloc[0] for f in frames})
    if not frames:
        print("no daily files yet")
        return
    allf = pd.concat(frames)
    allf = allf[allf.hub == hub]
    ours = allf.groupby("type_id")[["ask_units", "bid_units"]].sum() / len(days)
    ours["units"] = ours.ask_units + ours.bid_units
    sample = ours.sort_values("units", ascending=False).head(n).index
    dates = {(dt.date.fromisoformat(today) - dt.timedelta(days=k)).isoformat() for k in days}
    esi = ESI(workers=6)

    def hist(ty):
        r = esi.request("GET", f"/markets/{HUBS[hub]['region']}/history/", params={"type_id": int(ty)})
        if r.status_code != 200:
            return ty, np.nan
        h = pd.DataFrame(r.json())
        h = h[h.date.isin(dates)] if len(h) else h
        return ty, float(h.volume.sum() / len(days)) if len(h) else np.nan

    with cf.ThreadPoolExecutor(6) as ex:
        off = dict(ex.map(hist, sample))
    df = ours.loc[sample].assign(official=pd.Series(off))
    df["ratio"] = df.units / df.official
    print(f"{hub}: {len(days)} day(s), {len(df)} items. inferred/official units per day")
    print(df.ratio.describe(percentiles=[0.1, 0.25, 0.5, 0.75, 0.9]).round(3).to_string())


if __name__ == "__main__":
    main()
