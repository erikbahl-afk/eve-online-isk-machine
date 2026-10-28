import json
import math
import pathlib
import tomllib

ROOT = pathlib.Path(__file__).resolve().parent.parent
STATE = ROOT / "state"
DATA = ROOT / "data"
CACHE = ROOT / "cache"

HUBS = {
    "jita": {"name": "Jita IV - Moon 4 - Caldari Navy Assembly Plant", "station": 60003760, "region": 10000002},
    "amarr": {"name": "Amarr VIII (Oris) - Emperor Family Academy", "station": 60008494, "region": 10000043},
    "dodixie": {"name": "Dodixie IX - Moon 20 - Federation Navy Assembly Plant", "station": 60011866, "region": 10000032},
    "rens": {"name": "Rens VI - Moon 8 - Brutor Tribe Treasury", "station": 60004588, "region": 10000030},
    "hek": {"name": "Hek VIII - Moon 12 - Boundless Creation Factory", "station": 60005686, "region": 10000042},
}


def load_config(path=None):
    with open(path or ROOT / "config.toml", "rb") as f:
        return tomllib.load(f)


def load_json(path, default):
    try:
        return json.loads(pathlib.Path(path).read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path, obj):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, sort_keys=True))


def isk(x):
    """12345678 -> '12.35M'."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "-"
    a = abs(x)
    for div, suf in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "k")):
        if a >= div:
            return f"{x / div:.2f}{suf}"
    return f"{x:.2f}"


def price_str(p):
    """Exact in-game price with thousands separators."""
    return f"{p:,.2f}" if p < 1000 else f"{p:,.0f}"
