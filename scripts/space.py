"""Newest clear picture of every project site from the Sentinel-2 satellite ("Latest from space").

Sentinel-2 photographs Singapore every few days at 10 m per pixel: much blurrier
than the dated Esri photos in aerial.json, but far newer. For each site we take the
newest pass where the site is free of cloud, shadow and haze, crop 800 m around it
and save a small JPEG plus index.json into the folder given as argv[1]. The data is
free and open (Copernicus Sentinel data, read from the public AWS copy via the
Earth Search catalogue). Run by .github/workflows/space.yml, which publishes the
folder on the "space" branch; update.yml copies it into the site as /space/.
"""
import datetime, json, os, pathlib, sys, urllib.request
import numpy as np, rasterio
from rasterio.warp import transform
from rasterio.windows import from_bounds
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else "space_out")
HALF = 400        # metres shown each side of the site
LOOKBACK = 400    # days to search back for a clear pass
STAC = "https://earth-search.aws.element84.com/v1/search"
SG = [103.59, 1.20, 104.05, 1.48]
BAD = [0, 1, 3, 7, 8, 9, 10]  # no data, saturated, cloud shadow, unclassified (often cloud edges), cloud, cirrus
WIDE = 1200       # metres each side that must be free of cloud (small clouds are easy to miss up close)


def scenes(start, end):
    out, body = [], {"collections": ["sentinel-2-l2a"], "bbox": SG, "datetime": f"{start}T00:00:00Z/{end}T23:59:59Z",
                     "limit": 100, "sortby": [{"field": "properties.datetime", "direction": "desc"}]}
    url = STAC
    while url:
        req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
        j = json.load(urllib.request.urlopen(req, timeout=90))
        out += j["features"]
        nxt = next((l for l in j.get("links", []) if l.get("rel") == "next"), None)
        url, body = (nxt["href"], nxt.get("body", body)) if nxt else (None, body)
    return out


def window(ds, lat, lng, half):
    x, y = transform("EPSG:4326", ds.crs, [lng], [lat])
    return ds.read(window=from_bounds(x[0] - half, y[0] - half, x[0] + half, y[0] + half, ds.transform), boundless=True, fill_value=0)


def clear(scl, rgb):
    if scl.size == 0 or rgb.size == 0:
        return False
    if (rgb.max(axis=0) == 0).mean() > 0.01:      # edge of the satellite's swath
        return False
    dark = np.percentile(rgb.min(axis=0), 5)      # a clear picture always has some dark pixels (shade, trees, water)
    return dark < 75 and rgb.mean() < 190         # otherwise it is haze or thin cloud


def main():
    data = json.load(open(ROOT / "data.json"))
    sites = {}
    for row in data["bto"] + data["condo"]:
        ll = row[-1]
        if isinstance(ll, list) and len(ll) == 2:
            sites[f"{ll[0]:.4f},{ll[1]:.4f}"] = ll
    OUT.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today()
    feats = scenes((today - datetime.timedelta(days=LOOKBACK)).isoformat(), today.isoformat())
    print(len(sites), "sites,", len(feats), "satellite passes to try")
    done, todo = {}, dict(sites)
    for f in feats:
        if not todo:
            break
        day = f["properties"]["datetime"][:10]
        if f["properties"].get("eo:cloud_cover", 0) > 90:
            continue
        w, s, e, n = f["bbox"]
        inside = {k: ll for k, ll in todo.items() if s <= ll[0] <= n and w <= ll[1] <= e}
        if not inside:
            continue
        try:
            with rasterio.open(f["assets"]["scl"]["href"]) as scl, rasterio.open(f["assets"]["visual"]["href"]) as vis:
                got = 0
                for k, ll in inside.items():
                    try:
                        m = window(scl, ll[0], ll[1], WIDE)[0]
                        if np.isin(m, BAD).mean() > 0.01:
                            continue
                        rgb = window(vis, ll[0], ll[1], HALF)
                        if not clear(m, rgb):
                            continue
                        name = k.replace(",", "_") + ".jpg"
                        Image.fromarray(np.moveaxis(rgb, 0, -1)).resize((480, 480), Image.LANCZOS).save(OUT / name, "JPEG", quality=86)
                        done[k] = {"d": day, "f": name}; del todo[k]; got += 1
                    except Exception as ex:
                        print("  site failed", k, ex)
                print(day, f["id"], "clear for", got, "of", len(inside), "| still waiting:", len(todo))
        except Exception as ex:
            print("pass failed", f.get("id"), ex)
    if len(done) < 0.5 * len(sites):
        sys.exit(f"only {len(done)} of {len(sites)} sites got a picture; not publishing")
    json.dump({"checked": today.isoformat(), "sites": done}, open(OUT / "index.json", "w"), separators=(",", ":"))
    print("space:", len(done), "of", len(sites), "sites have a picture; none for", sorted(todo))
    ages = sorted((today - datetime.date.fromisoformat(v["d"])).days for v in done.values())
    print("age in days: newest", ages[0], "median", ages[len(ages) // 2], "oldest", ages[-1])


if __name__ == "__main__":
    main()
