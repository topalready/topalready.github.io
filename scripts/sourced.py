"""Find free-to-reuse photos of each project on Wikimedia Commons (writes sourced.json).

Only photos whose licence allows reuse (CC BY, CC BY-SA, CC0, public domain) are
listed, and only when the photo is clearly of the project: its name is in the
photo's title, description or categories, and it was taken at the site (or, for
photos without GPS, the page says Singapore). Nothing is copied: the app shows
the picture straight from Wikimedia with the author, licence and a link.
Run by .github/workflows/update.yml on scheduled/manual runs.
"""
import json, math, os, re, sys, time, html, urllib.parse, urllib.request

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "sourced.json")
API = "https://commons.wikimedia.org/w/api.php"
UA = {"User-Agent": "TOPAlready/1.0 (https://topalready.github.io; site photo finder)"}
OK_LICENCE = re.compile(r"^(cc0|cc[ -]by(-sa)?[ -]\d|public domain|pd\b)", re.I)
DEBUG = "--debug" in sys.argv


def api(**q):
    q.update(action="query", format="json", formatversion="2")
    url = API + "?" + urllib.parse.urlencode(q)
    for t in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r).get("query", {}).get("pages", [])
        except Exception as e:
            if t == 2:
                print("commons failed", e, file=sys.stderr)
                return None
            time.sleep(2)


PROPS = dict(prop="imageinfo|categories|coordinates", iiprop="url|extmetadata|mime|size", iiurlwidth="1280",
             iiextmetadatafilter="LicenseShortName|LicenseUrl|Artist|DateTimeOriginal|DateTime|ImageDescription|Credit",
             cllimit="max", colimit="max")
norm = lambda s: re.sub(r"[^a-z0-9]+", " ", (s or "").lower().replace("’", "'").replace("'", "")).strip()
text = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


def dist(a, b):
    R, p = 6371000, math.pi / 180
    x = (b[1] - a[1]) * p * math.cos((a[0] + b[0]) / 2 * p)
    return math.hypot(x, (b[0] - a[0]) * p) * R


def short(name):
    n = re.sub(r"\(.*?\)", "", name)
    n = re.sub(r"\s+I\s*&\s*II", "", n)
    return norm(n.split("@")[0])


def candidates(name, ll):
    seen, out = set(), []
    calls = [dict(generator="search", gsrsearch=f'"{re.sub(r"[()]", "", name.split("(")[0]).strip()}" Singapore', gsrnamespace="6", gsrlimit="30")]
    if ll:
        calls.append(dict(generator="geosearch", ggscoord=f"{ll[0]}|{ll[1]}", ggsradius="500", ggsnamespace="6", ggslimit="60"))
    for c in calls:
        pages = api(**c, **PROPS)
        if pages is None:
            return None
        for p in pages:
            if p.get("pageid") in seen or not p.get("imageinfo"):
                continue
            seen.add(p["pageid"]); out.append(p)
        time.sleep(0.15)
    return out


def pick(p, name, ll, launch):
    ii = p["imageinfo"][0]; m = ii.get("extmetadata", {})
    g = lambda k: text((m.get(k) or {}).get("value", ""))
    if ii.get("mime") not in ("image/jpeg", "image/png") or ii.get("width", 0) < 800:
        return None, "type"
    lic = g("LicenseShortName")
    if not OK_LICENCE.match(lic):
        return None, "licence " + lic
    d = re.search(r"(19|20)\d\d-\d\d(-\d\d)?", g("DateTimeOriginal"))
    if not d:
        return None, "no photo date"
    date = d.group(0)
    if launch and date[:7] < launch:
        return None, "before launch"
    sn = short(name)
    where = norm(p["title"]) + " | " + norm(g("ImageDescription")) + " | " + " | ".join(norm(c["title"]) for c in p.get("categories", []))
    if not re.search(r"\b" + re.escape(sn) + r"\b", where):
        return None, "name not on page"
    co = (p.get("coordinates") or [None])[0]
    if co and ll:
        if dist(ll, [co["lat"], co["lon"]]) > 800:
            return None, "too far"
    elif "singapore" not in where or len(sn) < 9:
        return None, "no location"
    return {"img": ii.get("thumburl") or ii["url"], "page": ii["descriptionurl"], "by": g("Artist")[:80] or "Unknown author",
            "licence": lic, "licence_url": g("LicenseUrl"), "date": date, "title": re.sub(r"^File:|\.\w+$", "", p["title"])[:120]}, "ok"


def main():
    data = json.load(open(os.path.join(ROOT, "data.json")))
    try:
        old = json.load(open(OUT))
    except Exception:
        old = {"photos": {}}
    res, failed = {}, 0
    rows = [("BTO", r[0], r[2], r[9]) for r in data["bto"]] + [("Condo", r[0], r[1], r[4]) for r in data["condo"]]
    for kind, name, launch, ll in rows:
        key = f"{kind}:{name}"
        cands = candidates(name, ll)
        if cands is None:
            failed += 1
            if key in old["photos"]:
                res[key] = old["photos"][key]
            continue
        got, why = [], {}
        for p in cands:
            x, w = pick(p, name, ll, launch)
            why[w] = why.get(w, 0) + 1
            if x:
                got.append(x)
        got.sort(key=lambda x: x["date"], reverse=True)
        if got:
            res[key] = got[:8]
        if DEBUG:
            print(key, len(cands), "candidates", why, [g["title"] for g in got[:3]])
    if failed > len(rows) * 0.3:
        print("Wikimedia Commons looks unreachable, keeping previous sourced.json")
        return
    import datetime
    out = {"checked": datetime.date.today().isoformat(), "source": "Wikimedia Commons", "photos": res}
    if DEBUG:
        print("TOTAL", sum(len(v) for v in res.values()), "photos for", len(res), "projects")
        print(json.dumps(res, ensure_ascii=False)[:6000])
        return
    if out["photos"] != old.get("photos"):
        json.dump(out, open(OUT, "w"), ensure_ascii=False, separators=(",", ":"))
    print("sourced:", sum(len(v) for v in res.values()), "photos for", len(res), "projects")


if __name__ == "__main__":
    main()
