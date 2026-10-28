"""Minimal public ESI client (no auth needed for market data)."""
import concurrent.futures as cf
import email.utils
import time

import pandas as pd
import requests

BASE = "https://esi.evetech.net/latest"
UA = "eve-online-isk-machine/0.1 (private market research; github actions)"
ORDER_COLS = ["order_id", "type_id", "is_buy_order", "price", "volume_remain",
              "issued", "duration", "location_id"]


def _lm(r):
    v = r.headers.get("Last-Modified")
    return email.utils.parsedate_to_datetime(v).timestamp() if v else 0.0


class ESI:
    def __init__(self, workers=8):
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA, "Accept": "application/json"})
        ad = requests.adapters.HTTPAdapter(pool_connections=workers, pool_maxsize=workers)
        self.s.mount("https://", ad)
        self.workers = workers
        self.calls = 0

    def request(self, method, path, tries=6, **kw):
        for i in range(tries):
            try:
                r = self.s.request(method, BASE + path, timeout=40, **kw)
            except requests.RequestException:
                time.sleep(2 ** i)
                continue
            self.calls += 1
            remain = r.headers.get("X-ESI-Error-Limit-Remain")
            if remain is not None and int(remain) < 15:
                time.sleep(int(r.headers.get("X-ESI-Error-Limit-Reset", 30)) + 1)
            if r.status_code in (200, 404):
                return r
            if r.status_code in (420, 429):
                time.sleep(float(r.headers.get("Retry-After", 30)))
                continue
            if r.status_code >= 500:
                time.sleep(2 ** i)
                continue
            r.raise_for_status()
        raise RuntimeError(f"ESI {method} {path} failed after {tries} tries")

    def region_orders(self, region_id):
        """All orders in a region from one consistent cache generation.

        Returns (DataFrame, consistent, last_modified_epoch). Pages are refetched until
        they all share the newest Last-Modified, so a cache flip mid-fetch can't make
        orders look like they vanished.
        """
        path = f"/markets/{region_id}/orders/"

        def fetch(p):
            r = self.request("GET", path, params={"order_type": "all", "page": p})
            if r.status_code != 200:
                return p, None, 0.0, 0
            return (p, pd.DataFrame(r.json(), columns=ORDER_COLS), _lm(r),
                    int(r.headers.get("X-Pages", 1)))

        pages = {}
        _, df1, lm1, npages = fetch(1)
        pages[1] = (df1, lm1)
        todo = list(range(2, npages + 1))
        consistent = False
        for _ in range(5):
            if todo:
                with cf.ThreadPoolExecutor(self.workers) as ex:
                    for p, df, lm, n in ex.map(fetch, todo):
                        if df is not None:
                            pages[p] = (df, lm)
                            if lm >= max(v[1] for v in pages.values()):
                                npages = n
            latest = max(v[1] for v in pages.values())
            for p in [p for p in pages if p > npages]:
                del pages[p]
            todo = [p for p in range(1, npages + 1) if p not in pages or pages[p][1] != latest]
            if not todo:
                consistent = True
                break
        df = pd.concat([v[0] for v in pages.values()], ignore_index=True)
        return df, consistent, max(v[1] for v in pages.values())

    def names(self, ids):
        out = {}
        ids = sorted(set(int(i) for i in ids))
        for i in range(0, len(ids), 1000):
            r = self.request("POST", "/universe/names/", json=ids[i:i + 1000])
            if r.status_code == 200:
                out.update({d["id"]: d["name"] for d in r.json()})
        return out

    def volumes(self, ids):
        """Packaged volume (m3) per type."""
        def one(ty):
            r = self.request("GET", f"/universe/types/{ty}/")
            if r.status_code != 200:
                return ty, None
            d = r.json()
            return ty, float(d.get("packaged_volume") or d.get("volume") or 0.0)
        with cf.ThreadPoolExecutor(self.workers) as ex:
            return {ty: v for ty, v in ex.map(one, sorted(set(int(i) for i in ids))) if v is not None}
