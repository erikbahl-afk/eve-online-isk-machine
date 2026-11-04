"""EVE SSO for the trading character.

The app's secret key lives only in the ESI_CLIENT_SECRET GitHub Actions secret. The refresh token is
stored in state/sso_token.enc, encrypted with a key derived from that secret, so the public repo only
ever holds ciphertext.

python -m trader.sso url               print the login link (no secret needed)
python -m trader.sso exchange CODE     one-time: swap the login code for a refresh token (needs secret)
"""
import base64
import hashlib
import json
import os
import secrets
import sys
import time
import urllib.parse

import requests
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from .common import STATE, load_config

LOGIN = "https://login.eveonline.com/v2/oauth"
TOKEN_FILE = STATE / "sso_token.enc"


def _key(secret):
    return hashlib.sha256(("isk-machine:" + secret).encode()).digest()


def encrypt(obj, secret):
    nonce = os.urandom(12)
    ct = AESGCM(_key(secret)).encrypt(nonce, json.dumps(obj).encode(), None)
    return base64.b64encode(nonce + ct).decode()


def decrypt(blob, secret):
    raw = base64.b64decode(blob)
    return json.loads(AESGCM(_key(secret)).decrypt(raw[:12], raw[12:], None))


def auth_url(cfg, state=None):
    s = cfg["sso"]
    q = {"response_type": "code", "redirect_uri": s["callback"], "client_id": s["client_id"],
         "scope": " ".join(s["scopes"]), "state": state or secrets.token_urlsafe(8)}
    return f"{LOGIN}/authorize/?{urllib.parse.urlencode(q, quote_via=urllib.parse.quote)}"


def _token(cfg, secret, data):
    r = requests.post(f"{LOGIN}/token", data=data, auth=(cfg["sso"]["client_id"], secret),
                      headers={"Host": "login.eveonline.com"}, timeout=30)
    r.raise_for_status()
    return r.json()


def character_of(access_token):
    """Character id and name from the access token (a JWT issued by login.eveonline.com over TLS)."""
    payload = access_token.split(".")[1]
    claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    return int(claims["sub"].split(":")[-1]), claims.get("name", "")


def save(tok, secret):
    TOKEN_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOKEN_FILE.write_text(encrypt(tok, secret) + "\n")


def access_token(cfg, secret):
    """Fresh access token (refreshing, and re-saving the refresh token if it rotated)."""
    if not TOKEN_FILE.exists():
        return None, None
    tok = decrypt(TOKEN_FILE.read_text().strip(), secret)
    new = _token(cfg, secret, {"grant_type": "refresh_token", "refresh_token": tok["refresh_token"]})
    if new.get("refresh_token") and new["refresh_token"] != tok["refresh_token"]:
        save({**tok, "refresh_token": new["refresh_token"]}, secret)
    return new["access_token"], tok["character_id"]


def exchange(cfg, secret, code):
    t = _token(cfg, secret, {"grant_type": "authorization_code", "code": code})
    cid, name = character_of(t["access_token"])
    save({"refresh_token": t["refresh_token"], "character_id": cid, "connected": int(time.time())}, secret)
    return cid, name


def main():
    cfg = load_config()
    if sys.argv[1:2] == ["url"]:
        print(auth_url(cfg))
    elif sys.argv[1:2] == ["exchange"]:
        code = sys.argv[2].strip()
        if "code=" in code:  # the whole callback URL was pasted
            code = urllib.parse.parse_qs(urllib.parse.urlparse(code).query)["code"][0]
        exchange(cfg, os.environ["ESI_CLIENT_SECRET"], code)
        print("connected")  # deliberately no character name: the run log of a public repo is public
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
