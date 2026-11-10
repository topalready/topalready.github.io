"""Prototype: newest cloud-free Sentinel-2 picture (10 m per pixel, free and open) of a few sites."""
import json, sys, urllib.request, datetime, pathlib
import numpy as np, rasterio
from rasterio.warp import transform
from rasterio.windows import from_bounds
from PIL import Image

SITES = {"bayshore-vista": [1.3136, 103.9417], "plantation-edge-i-ii": [1.3568, 103.7334], "grand-dunman": [1.3081, 103.8913],
         "chencharu-grove": [1.4184, 103.8288], "sembawang-beacon": [1.4565, 103.8188]}
HALF = 400  # metres each side of the site
OUT = pathlib.Path("out/sentinel-test")

def search(lat, lng, start, end):
    body = {"collections": ["sentinel-2-l2a"], "intersects": {"type": "Point", "coordinates": [lng, lat]},
            "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z", "limit": 40,
            "sortby": [{"field": "properties.datetime", "direction": "desc"}]}
    req = urllib.request.Request("https://earth-search.aws.element84.com/v1/search", json.dumps(body).encode(), {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))["features"]

def crop(href, lat, lng):
    with rasterio.open(href) as ds:
        x, y = transform("EPSG:4326", ds.crs, [lng], [lat])
        w = from_bounds(x[0] - HALF, y[0] - HALF, x[0] + HALF, y[0] + HALF, ds.transform)
        return ds.read(window=w)

def best(lat, lng, start, end):
    for f in search(lat, lng, start, end):
        try:
            scl = crop(f["assets"]["scl"]["href"], lat, lng)[0]
            bad = np.isin(scl, [0, 1, 3, 8, 9, 10]).mean()
            print("  ", f["properties"]["datetime"][:10], "cloud/shadow in crop", round(float(bad), 2))
            if bad > 0.03:
                continue
            rgb = crop(f["assets"]["visual"]["href"], lat, lng)
            return f["properties"]["datetime"][:10], np.moveaxis(rgb, 0, -1)
        except Exception as e:
            print("   skip", e)
    return None, None

today = datetime.date.today()
OUT.mkdir(parents=True, exist_ok=True)
meta = {}
for slug, (lat, lng) in SITES.items():
    print(slug)
    meta[slug] = []
    for label, a, b in [("latest", today - datetime.timedelta(days=150), today),
                        ("year_ago", today - datetime.timedelta(days=520), today - datetime.timedelta(days=330)),
                        ("two_years_ago", today - datetime.timedelta(days=900), today - datetime.timedelta(days=700))]:
        d, img = best(lat, lng, a.isoformat(), b.isoformat())
        if img is None:
            print("  no clear picture for", label); continue
        Image.fromarray(img).resize((800, 800), Image.LANCZOS).save(OUT / f"{slug}_{label}_{d}.png")
        meta[slug].append({"label": label, "date": d})
(OUT / "meta.json").write_text(json.dumps(meta, indent=1))
print(meta)
