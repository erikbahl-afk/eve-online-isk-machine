import base64
import json
import urllib.parse

import trader.character as character
from trader import sso
from trader.common import load_config

CFG = load_config()


def test_encrypt_roundtrip():
    blob = sso.encrypt({"refresh_token": "abc", "character_id": 1}, "s3cret")
    assert "abc" not in blob and sso.decrypt(blob, "s3cret")["refresh_token"] == "abc"


def test_auth_url():
    q = urllib.parse.parse_qs(urllib.parse.urlparse(sso.auth_url(CFG, "st")).query)
    assert q["client_id"] == [CFG["sso"]["client_id"]] and q["redirect_uri"] == [CFG["sso"]["callback"]]
    assert "esi-markets.read_character_orders.v1" in q["scope"][0].split()


def test_character_of():
    claims = base64.urlsafe_b64encode(json.dumps({"sub": "CHARACTER:EVE:123", "name": "X"}).encode()).decode()
    assert sso.character_of(f"h.{claims.rstrip('=')}.sig") == (123, "X")


class R:
    def __init__(self, data):
        self.data, self.status_code = data, 200

    def json(self):
        return self.data

    def raise_for_status(self):
        pass


class FakeESI:
    def request(self, method, path, **kw):
        if path == "/universe/ids/":
            return R({"inventory_types": [{"name": n, "id": i} for i, n in enumerate(kw["json"], 1)]})
        if path.startswith("/universe/types/"):
            return R({"dogma_attributes": [{"attribute_id": 275, "value": 1}, {"attribute_id": 180, "value": 164},
                                           {"attribute_id": 181, "value": 166}]})
        if path.endswith("/skills/"):
            return R({"skills": [{"skill_id": 1, "trained_skill_level": 4, "skillpoints_in_skill": 45255}],
                      "total_sp": 500000, "unallocated_sp": 0})
        if path.endswith("/skillqueue/"):
            return R([{"skill_id": 1, "finished_level": 5, "queue_position": 0, "finish_date": "2026-11-10T00:00:00Z"}])
        if path.endswith("/attributes/"):
            return R({"charisma": 27, "intelligence": 17, "memory": 21, "perception": 17, "willpower": 17,
                      "bonus_remaps": 1})
        if path.endswith("/standings/"):
            return R([{"from_type": "faction", "from_id": 500001, "standing": 2.0}])
        return R({"jump_clones": [{}]})


def test_character_report(tmp_path, monkeypatch):
    monkeypatch.setattr(character, "DATA", tmp_path)
    cfg = {**CFG, "training": {"plan": [["Trade", 4], ["Trade", 5], ["Retail", 2]]}}
    out = character.report(cfg, FakeESI(), "tok", 123, tmp_path / "c.json")
    trade = next(r for r in out["plan"] if r["skill"] == "Trade")
    assert trade["target"] == 5 and trade["sp_left"] == 256000 - 45255
    assert out["queue"][0]["skill"] == "Trade" and out["jump_clones"] == 1 and out["eta_days"] > 0
    assert "123" not in (tmp_path / "c.json").read_text()  # no character ID written
