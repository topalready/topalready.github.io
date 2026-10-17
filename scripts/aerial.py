"""List the dated satellite snapshots for every project site (writes aerial.json).

Uses Esri's World Imagery Wayback. For each site we only record *which* archived
release shows a different picture of that spot and when it was captured; the
app then loads the tiles live from Esri (no imagery is stored here).

Incremental: when Esri publishes a new release we ask once per site whether the
newest release changed that spot; full lookups only run for new sites.
"""
import json, math, os, re, sys, datetime, urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "aerial.json")
Z = 18
HDR = {"Origin": "https://topalready.github.io", "Referer": "https://topalready.github.io/",
       "User-Agent": "Mozilla/5.0 (TOP Already? satellite timeline)"}
CONFIG = "https://s3-us-west-2.amazonaws.com/config.maptiles.arcgis.com/waybackconfig.json"
TILEMAP = "https://wayback.maptiles.arcgis.com/arcgis/rest/services/World_Imagery/MapServer/tilemap/{r}/{z}/{y}/{x}/1/1"


def get(url, tries=3):
    for t in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=HDR), timeout=20) as r:
                return json.load(r)
        except Exception:
            if t == tries - 1:
                raise


def tile(lat, lng):
    n = 2 ** Z
    x = int((lng + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
    return x, y


def releases():
    c = get(CONFIG)
    rel = []
    for v in c.values():
        m = re.search(r"\d{4}-\d\d-\d\d", v["itemTitle"])
        rid = re.search(r"tile/(\d+)/", v["itemURL"])
        if m and rid:
            rel.append((m.group(0), int(rid.group(1)), v["metadataLayerUrl"]))
    rel.sort()
    return rel


def captured(meta_url, lat, lng):
    for layer in (3, 4, 5, 6):  # 15 cm .. 1.2 m resolution layers
        q = (f"{meta_url}/{layer}/query?f=json&where=1%3D1&geometry={lng},{lat}&geometryType=esriGeometryPoint"
             "&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=SRC_DATE2&returnGeometry=false")
        f = get(q).get("features") or []
        if f and f[0]["attributes"].get("SRC_DATE2"):
            return datetime.datetime.fromtimestamp(f[0]["attributes"]["SRC_DATE2"] / 1000, datetime.UTC).strftime("%Y-%m-%d")
    return None


def selected(rid, x, y):
    t = get(TILEMAP.format(r=rid, z=Z, y=y, x=x))
    if not (t.get("data") or [0])[0]:
        return None
    return (t.get("select") or [rid])[0]


def chain(rel, idx, lat, lng, stop_at=None):
    """Newest-first list of [release, capture date] where the picture changed."""
    x, y = tile(lat, lng)
    out, seen, i = [], set(), len(rel) - 1
    while i >= 0:
        s = selected(rel[i][1], x, y)
        if s is None or s not in idx:
            break
        if s == stop_at:
            return out, True
        k = idx[s]
        d = captured(rel[k][2], lat, lng)
        if d and d not in seen:
            seen.add(d)
            out.append([s, d])
        i = k - 1
    return out, False


def main():
    data = json.load(open(os.path.join(ROOT, "data.json")))
    sites = set()
    for row in data["bto"] + data["condo"]:
        ll = row[-1]
        if isinstance(ll, list) and len(ll) == 2:
            sites.add(f"{ll[0]:.4f},{ll[1]:.4f}")
    try:
        old = json.load(open(OUT))
    except Exception:
        old = {"latest": None, "sites": {}}
    rel = releases()
    idx = {r[1]: i for i, r in enumerate(rel)}
    latest = rel[-1][1]

    def work(key):
        lat, lng = map(float, key.split(","))
        prev = old["sites"].get(key)
        try:
            if prev:
                if old.get("latest") == latest:
                    return key, prev
                newer, joined = chain(rel, idx, lat, lng, stop_at=prev[0][0])
                if joined:
                    return key, newer + [p for p in prev if p[1] not in {n[1] for n in newer}]
            full, _ = chain(rel, idx, lat, lng)
            return key, full
        except Exception as e:
            print("skip", key, e, file=sys.stderr)
            return key, prev

    with ThreadPoolExecutor(8) as ex:
        res = dict(ex.map(work, sorted(sites)))
    res = {k: v for k, v in res.items() if v}
    out = {"latest": latest, "checked": datetime.date.today().isoformat(), "sites": res}
    if out["sites"] == old.get("sites") and old.get("latest") == latest:
        print("aerial: no change")
        return
    json.dump(out, open(OUT, "w"), separators=(",", ":"))
    print(f"aerial: {len(res)} sites, {sum(len(v) for v in res.values())} snapshots")


if __name__ == "__main__":
    main()
