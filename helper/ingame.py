#!/usr/bin/env python3
"""ISK machine helper: your session checklist with "Open in game" buttons.

Run it on your own PC while the trading character is logged into EVE:

    python ingame.py

A browser tab opens with the current checklist. Each item has an "Open in game" button that opens that
item's market window in your EVE client (through CCP's official ESI interface), and a checkbox you tick
as you go. "Copy session report" puts your online times and how far you got on the clipboard, ready to
paste to Claude.

Only the Python standard library is used. Your login token stays on this PC (in ~/.isk-machine/).
"""
import base64
import csv
import datetime as dt
import hashlib
import html
import http.server
import io
import json
import os
import pathlib
import secrets
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import webbrowser

CLIENT_ID = "b4da82d1191045c695079ffef019383a"
PORT = 8765
CALLBACK = f"http://localhost:{PORT}/callback"
SCOPES = "esi-ui.open_window.v1"
REPO_RAW = "https://raw.githubusercontent.com/erikbahl-afk/eve-online-isk-machine/claude/busy-carson-bj9fgk"
HOME = pathlib.Path.home() / ".isk-machine"
TOKEN_FILE = HOME / "ingame_token.json"
LOG_FILE = HOME / "session_log.jsonl"
UA = "isk-machine-ingame-helper/1.0"
HUB_NAMES = {"jita": "Jita 4-4", "amarr": "Amarr VIII (Oris)", "dodixie": "Dodixie IX - Moon 20",
             "rens": "Rens VI - Moon 8", "hek": "Hek VIII - Moon 12"}
BLOCKS = {1: "Block 1 · must do", 2: "Block 2 · should do", 3: "Block 3 · if there's time"}

_pkce = {}  # state -> code verifier for logins in progress
_cache = {}


# ---- EVE login (PKCE: no secret needed on your PC) --------------------------------------------
def _optional_secret():
    f = HOME / "client_secret.txt"
    return os.environ.get("ESI_CLIENT_SECRET") or (f.read_text().strip() if f.exists() else None)


def _token_request(data):
    headers = {"Content-Type": "application/x-www-form-urlencoded", "Host": "login.eveonline.com", "User-Agent": UA}
    secret = _optional_secret()
    if secret:  # only if the app turns out to require it; see README
        headers["Authorization"] = "Basic " + base64.b64encode(f"{CLIENT_ID}:{secret}".encode()).decode()
    else:
        data = {**data, "client_id": CLIENT_ID}
    req = urllib.request.Request("https://login.eveonline.com/v2/oauth/token",
                                 data=urllib.parse.urlencode(data).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def login_url():
    state = secrets.token_urlsafe(12)
    verifier = secrets.token_urlsafe(64)
    _pkce[state] = verifier
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    q = {"response_type": "code", "redirect_uri": CALLBACK, "client_id": CLIENT_ID, "scope": SCOPES,
         "state": state, "code_challenge": challenge, "code_challenge_method": "S256"}
    return "https://login.eveonline.com/v2/oauth/authorize/?" + urllib.parse.urlencode(q, quote_via=urllib.parse.quote)


def finish_login(code, state):
    verifier = _pkce.pop(state, None)
    if not verifier:
        raise ValueError("this login link expired; start again")
    try:
        t = _token_request({"grant_type": "authorization_code", "code": code, "code_verifier": verifier})
    except urllib.error.HTTPError as e:
        raise ValueError(f"EVE refused the login ({e.code}). If this keeps happening, save the app's client_secret "
                         f"in {HOME / 'client_secret.txt'} and try again.") from e
    _save_token(t)


def _save_token(t):
    HOME.mkdir(parents=True, exist_ok=True)
    payload = t["access_token"].split(".")[1]
    claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    TOKEN_FILE.write_text(json.dumps({"refresh_token": t["refresh_token"], "access_token": t["access_token"],
                                      "expires": time.time() + int(t.get("expires_in", 1199)) - 60,
                                      "character": claims.get("name", "")}))


def access_token():
    if not TOKEN_FILE.exists():
        return None
    tok = json.loads(TOKEN_FILE.read_text())
    if time.time() < tok.get("expires", 0):
        return tok["access_token"]
    t = _token_request({"grant_type": "refresh_token", "refresh_token": tok["refresh_token"]})
    t.setdefault("refresh_token", tok["refresh_token"])
    _save_token(t)
    return t["access_token"]


def character():
    return json.loads(TOKEN_FILE.read_text()).get("character", "") if TOKEN_FILE.exists() else ""


def open_market(type_id):
    tok = access_token()
    if not tok:
        return False, "not logged in"
    req = urllib.request.Request(
        f"https://esi.evetech.net/latest/ui/openwindow/marketdetails/?type_id={int(type_id)}",
        data=b"", method="POST", headers={"Authorization": f"Bearer {tok}", "User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 204, ""
    except urllib.error.HTTPError as e:
        return False, f"ESI said {e.code} (is the trading character logged into EVE?)"


# ---- checklist data -------------------------------------------------------------------------------
def _fetch(path, max_age):
    hit = _cache.get(path)
    if hit and time.time() - hit[0] < max_age:
        return hit[1]
    local = os.environ.get("ISK_REPO_DIR")
    if local:  # for testing against a local checkout
        text = (pathlib.Path(local) / path).read_text()
    else:
        headers = {"User-Agent": UA}
        gh = HOME / "github_token.txt"  # needed once the repo is private
        if gh.exists():
            headers["Authorization"] = f"Bearer {gh.read_text().strip()}"
        req = urllib.request.Request(f"{REPO_RAW}/{path}?t={int(time.time() // 60)}", headers=headers)
        with urllib.request.urlopen(req, timeout=20) as r:
            text = r.read().decode()
    _cache[path] = (time.time(), text)
    return text


def plan_and_names():
    plan = json.loads(_fetch("state/plan.json", 60))
    names = {}
    for row in csv.DictReader(io.StringIO(_fetch("data/types.csv", 3600))):
        if row.get("name"):
            names[int(row["type_id"])] = row["name"]
    return plan, names


def _p(x):
    if x is None:
        return "-"
    return f"{x:,.2f}" if x < 1000 else f"{x:,.0f}"


def describe(st, names):
    item = names.get(st.get("type_id"), f"type {st.get('type_id')}")
    k = st["kind"]
    if k == "modify_sell":
        return item, f"Lower sell to <b>{_p(st['target'])}</b> (lowest − 1 tick, never below {_p(st['floor'])})"
    if k == "new_sell":
        return item, f"List {st['qty']:,} at <b>{_p(st['target'])}</b> (lowest − 1 tick, never below {_p(st['floor'])})"
    if k == "instant_sell":
        return item, f"Sell {st['qty']:,} into buy orders, no lower than <b>{_p(st['min_price'])}</b>"
    if k == "modify_buy":
        return item, f"Raise buy to <b>{_p(st['target'])}</b> (highest + 1 tick, never above {_p(st['cap'])})"
    if k == "cancel":
        return item, "Cancel this buy order"
    if k == "new_buy":
        return item, f"Buy order {st['qty']:,} at <b>{_p(st['target'])}</b> (highest + 1 tick, never above {_p(st['cap'])})"
    if k == "instant_buy":
        return item, f"Buy {st['qty']:,} from sellers, never above <b>{_p(st['max_price'])}</b>"
    if k == "courier":
        return (f"Courier → {HUB_NAMES.get(st['to'], st['to'])}",
                f"{st.get('contracts', 1)} contract(s) via {st.get('service', 'PushX')}, collateral about "
                f"{_p(st.get('est_value'))}")
    if k == "jump":
        return f"Jump clone → {HUB_NAMES.get(st['to'], st['to'])}", "Clone Bay → Jump Clone"
    return item, k


# ---- session log ----------------------------------------------------------------------------------
def log(event, **kw):
    HOME.mkdir(parents=True, exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps({"t": time.time(), "event": event, **kw}) + "\n")


def report():
    if not LOG_FILE.exists():
        return "No session logged yet."
    rows = [json.loads(line) for line in LOG_FILE.read_text().splitlines() if line.strip()]
    starts = [i for i, r in enumerate(rows) if r["event"] == "start"]
    rows = rows[starts[-1]:] if starts else [r for r in rows if time.time() - r["t"] < 4 * 3600]
    ticks = [r for r in rows if r["event"] == "tick" and r.get("on")]
    if not rows:
        return "No session logged yet."
    t0, t1 = rows[0]["t"], max(r["t"] for r in rows)
    fmt = lambda t: dt.datetime.fromtimestamp(t).strftime("%H:%M")
    done = sorted({r["n"] for r in ticks})
    last = max(done) if done else 0
    total = rows[-1].get("total") or next((r.get("total") for r in reversed(rows) if r.get("total")), "?")
    return (f"Online {dt.datetime.fromtimestamp(t0):%a %d %b} {fmt(t0)}–{fmt(t1)} "
            f"({(t1 - t0) / 60:.0f} min). Ticked {len(done)} steps, furthest step {last} of {total}. "
            f"Steps ticked: {', '.join(map(str, done)) or 'none'}.")


# ---- web page -------------------------------------------------------------------------------------
PAGE = """<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>ISK machine session</title><style>
body{font-family:system-ui,sans-serif;background:#111;color:#ddd;margin:16px;max-width:980px}
h1{font-size:20px} h2{font-size:17px;margin-top:22px;border-bottom:1px solid #444}
h3{font-size:14px;color:#aab;margin:14px 0 6px}
.row{display:flex;gap:10px;align-items:center;padding:6px 4px;border-bottom:1px solid #222}
.row.done{opacity:.45} .n{width:28px;color:#888;text-align:right} .item{width:290px;font-weight:600}
.what{flex:1;font-size:14px} button{background:#2a4a7a;color:#fff;border:0;border-radius:4px;padding:6px 10px;cursor:pointer}
button.ok{background:#2a6a3a} button.err{background:#7a2a2a} .top{display:flex;gap:10px;flex-wrap:wrap}
a{color:#8cf} .muted{color:#888;font-size:13px}
</style></head><body>%BODY%<script>
async function op(id,btn){btn.textContent='…';const r=await fetch('/open?type_id='+id);const t=await r.text();
 btn.className=r.ok?'ok':'err';btn.textContent=r.ok?'Opened ✓':'Failed';if(!r.ok)alert(t);}
async function tick(n,total,box){box.closest('.row').classList.toggle('done',box.checked);
 await fetch('/tick?n='+n+'&total='+total+'&on='+(box.checked?1:0));}
async function start(b){await fetch('/start');b.textContent='Session started ✓';}
async function report(b){const t=await (await fetch('/report')).text();
 try{await navigator.clipboard.writeText(t);b.textContent='Copied ✓';}catch(e){prompt('Copy this:',t);}}
</script></body></html>"""


def page_body():
    if not TOKEN_FILE.exists():
        return (f"<h1>ISK machine helper</h1><p>First, log in once with the <b>trading character</b> so the "
                f"buttons can open windows in your game client.</p><p><a href='{html.escape(login_url())}'>"
                "<button>Log in with EVE</button></a></p><p class='muted'>Only permission requested: open windows "
                "in your client. The token stays on this PC.</p>")
    try:
        plan, names = plan_and_names()
    except Exception as e:  # noqa: BLE001
        return f"<h1>ISK machine helper</h1><p>Couldn't load the checklist: {html.escape(str(e))}</p>"
    steps = plan.get("steps", [])
    total = len(steps)
    gen = dt.datetime.fromtimestamp(plan.get("generated", 0)).strftime("%a %d %b %H:%M")
    out = [f"<h1>Session checklist</h1><p class='muted'>Updated {gen} · {total} steps · about "
           f"{round(plan.get('est_secs', 0) / 60)} min · logged in as {html.escape(character())}</p>",
           "<div class='top'><button onclick='start(this)'>Start session</button>"
           "<button onclick='report(this)'>Copy session report</button>"
           "<a href='/'><button>Reload checklist</button></a></div>"]
    hub, blk = None, None
    for st in steps:
        if st["kind"] == "jump":
            hub, blk = None, None
        elif st["hub"] != hub:
            hub, blk = st["hub"], None
            out.append(f"<h2>At {html.escape(HUB_NAMES.get(hub, hub))}</h2>")
        if st["kind"] != "jump" and st.get("block") != blk:
            blk = st.get("block")
            out.append(f"<h3>{BLOCKS.get(blk, '')}</h3>")
        item, what = describe(st, names)
        btn = (f"<button onclick='op({int(st['type_id'])},this)'>Open in game</button>"
               if st.get("type_id") is not None and st["kind"] not in ("jump", "courier") else "")
        out.append(f"<div class='row'><input type='checkbox' onchange='tick({st['n']},{total},this)'>"
                   f"<span class='n'>{st['n']}</span><span class='item'>{html.escape(str(item))}</span>"
                   f"<span class='what'>{what}</span>{btn}</div>")
    if not steps:
        out.append("<p>Nothing to do this session.</p>")
    return "\n".join(out)


class Handler(http.server.BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802
        u = urllib.parse.urlparse(self.path)
        q = {k: v[0] for k, v in urllib.parse.parse_qs(u.query).items()}
        try:
            if u.path == "/":
                self._send(200, PAGE.replace("%BODY%", page_body()))
            elif u.path == "/callback":
                finish_login(q["code"], q.get("state", ""))
                self.send_response(302)
                self.send_header("Location", "/")
                self.end_headers()
            elif u.path == "/open":
                ok, msg = open_market(q["type_id"])
                log("open", type_id=int(q["type_id"]), ok=ok)
                self._send(200 if ok else 502, msg or "ok", "text/plain")
            elif u.path == "/tick":
                log("tick", n=int(q["n"]), total=int(q.get("total", 0)), on=q.get("on") == "1")
                self._send(200, "ok", "text/plain")
            elif u.path == "/start":
                log("start")
                self._send(200, "ok", "text/plain")
            elif u.path == "/report":
                self._send(200, report(), "text/plain")
            else:
                self._send(404, "not found", "text/plain")
        except Exception as e:  # noqa: BLE001
            self._send(500, f"Error: {e}", "text/plain")

    def log_message(self, *args):  # keep the console quiet
        pass


def main():
    server = http.server.ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"ISK machine helper running at http://localhost:{PORT}  (Ctrl+C to stop)")
    if "--no-browser" not in sys.argv:
        threading.Timer(0.5, lambda: webbrowser.open(f"http://localhost:{PORT}/")).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
