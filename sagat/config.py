"""Paths and constants. Databases default to ./data/ (village.db, traces.db,
built with `uv run python -m sagat build-data --raw <hf files> --out data`).
Override with env vars VILLAGE_DB, TRACES_DB, and SAGAT_WORK (scratch dir,
default ./work)."""
import os
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parent.parent
# default: ./data inside the repo (where `sagat build-data --out data` puts
# the two databases); falls back to the original workspace layout
_WORKSPACE = REPO.parents[2] / "data" if len(REPO.parents) > 2 else REPO / "data"
_DATA = REPO / "data" if (REPO / "data" / "traces.db").exists() else _WORKSPACE
VILLAGE_DB = Path(os.environ.get("VILLAGE_DB", _DATA / "village.db"))
TRACES_DB = Path(os.environ.get("TRACES_DB", _DATA / "traces.db"))
WORK = Path(os.environ.get("SAGAT_WORK", REPO / "work"))
RESULTS = REPO / "results"
CACHE_DB = WORK / "source_cache.db"

PT = ZoneInfo("America/Los_Angeles")
TS_FMT = "%Y-%m-%d %H:%M:%S"


def parse_ts(s):
    """Dataset timestamps are naive UTC strings, with or without microseconds."""
    s = s.replace("T", " ").rstrip("Z")
    fmt = TS_FMT + (".%f" if "." in s else "")
    return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)


def to_db(dt):
    """UTC datetime -> dataset string form (sorts correctly against stored values)."""
    return dt.astimezone(timezone.utc).strftime(TS_FMT + ".%f")


def to_pt(dt_or_s):
    dt = parse_ts(dt_or_s) if isinstance(dt_or_s, str) else dt_or_s
    return dt.astimezone(PT).strftime(TS_FMT)
