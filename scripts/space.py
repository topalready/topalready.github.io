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
CLOUD_MAX = 0.01  # at most this share of the crop may look like cloud (white roofs count a little)
STAC = "https://earth-search.aws.element84.com/v1/search"
SG = [103.59, 1.20, 104.05, 1.48]
BAD = [0, 1, 3, 8, 9, 10]  # no data, saturated, cloud shadow, cloud (medium/high), cirrus


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


def refl(ds, lat, lng, half):
    """Surface reflectance (0..1) around the site from one colour band."""
    dn = window(ds, lat, lng, half)[0].astype("float32")
    sc, off = (ds.scales[0] or 1), (ds.offsets[0] or 0)
    if sc == 1:  # no scale in the file: Sentinel-2 L2A stores reflectance x 10000 (minus 1000 since 2022)
        sc, off = 0.0001, -0.1
    return dn * sc + off


def hazy(blue, red):
    """Share of a wider area that looks like thin cloud."""
    return float((((blue - 0.5 * red) > 0.08) & (blue > 0.15)).mean())


def cloudy(blue, red):
    """Share of the crop that looks like cloud or haze. Cloud is bright in blue; sand, soil and concrete are redder than they are blue."""
    hot = blue - 0.5 * red
    return float(((hot > 0.11) & (blue > 0.2)).mean())


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
            A = f["assets"]
            with rasterio.open(A["scl"]["href"]) as scl, rasterio.open(A["visual"]["href"]) as vis, \
                    rasterio.open(A["blue"]["href"]) as bb, rasterio.open(A["red"]["href"]) as rr:
                got = 0
                for k, ll in inside.items():
                    try:
                        m = window(scl, ll[0], ll[1], HALF + 200)[0]
                        if np.isin(m, BAD).mean() > 0.004:
                            continue
                        cl = cloudy(refl(bb, ll[0], ll[1], HALF + 100), refl(rr, ll[0], ll[1], HALF + 100))
                        if cl > CLOUD_MAX:
                            continue
                        hz = hazy(refl(bb, ll[0], ll[1], HALF + 400), refl(rr, ll[0], ll[1], HALF + 400))
                        rgb = window(vis, ll[0], ll[1], HALF)
                        if not clear(m, rgb):
                            continue
                        name = k.replace(",", "_") + ".jpg"
                        Image.fromarray(np.moveaxis(rgb, 0, -1)).resize((480, 480), Image.LANCZOS).save(OUT / name, "JPEG", quality=86)
                        done[k] = {"d": day, "f": name, "c": round(cl, 4), "w": round(hz, 4)}; del todo[k]; got += 1
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
