"""Build this week's Instagram posts for TOP Already?

Pulls the newest community photos from Supabase and the latest project data,
renders 1080x1350 carousel slides in the app's style, and writes them to
social/<date>/ with a manifest.json describing each post (slides + caption).
Run by .github/workflows/social.yml every week.
"""
import asyncio, base64, datetime as dt, io, json, pathlib, sys, urllib.parse, urllib.request

from PIL import Image, ImageOps
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SB = "https://dykbqyaftkeiroyfzoqb.supabase.co"
KEY = "sb_publishable_6zJTBBa74WI7IueK3xdaUg_cvfxMSp2"
SITE = "https://topalready.github.io"
SGT = dt.timezone(dt.timedelta(hours=8))
TODAY = dt.datetime.now(SGT).date()
OUT = ROOT / "social" / TODAY.isoformat()
SCREENS = ROOT / "social" / "screens"
FONTS = ROOT / "assets" / "fonts"
MON = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
TAGS = "#BTO #BTOSingapore #HDB #SGHomes #NewLaunchCondo #KeyCollection #SingaporeProperty"


def get(url, raw=False):
    req = urllib.request.Request(url, headers={"apikey": KEY, "Authorization": f"Bearer {KEY}"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    return data if raw else json.loads(data)


def uri(data, mime="image/jpeg"):
    return f"data:{mime};base64," + base64.b64encode(data).decode()


def screen(name):
    return uri((SCREENS / name).read_bytes(), "image/png")


def ym(s):
    y, m = s[:7].split("-")
    return f"{MON[int(m) - 1]} {y}"


def day(s):
    d = dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(SGT)
    return f"{d.day} {MON[d.month - 1]}"


def project(key):
    kind, name = key.split(":")[:2]
    return kind, name


def photo_bytes(path):
    raw = get(f"{SB}/storage/v1/object/public/photos/{urllib.parse.quote(path)}", raw=True)
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
    im.thumbnail((1400, 1400))
    buf = io.BytesIO(); im.save(buf, "JPEG", quality=86)
    return buf.getvalue()


CSS = f"""
@font-face{{font-family:F;src:url(file://{FONTS}/Fraunces-SemiBold.ttf)}}
@font-face{{font-family:G;src:url(file://{FONTS}/Figtree-Medium.ttf);font-weight:500}}
@font-face{{font-family:G;src:url(file://{FONTS}/Figtree-SemiBold.ttf);font-weight:600}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1350px;overflow:hidden;font-family:G;color:#2E2A24;background:#F5EDDC;position:relative}}
.pad{{position:absolute;inset:0;padding:84px 80px}}
.tag{{display:inline-block;font:600 26px G;letter-spacing:.04em;text-transform:uppercase;color:#8A6A2E;background:#F0DDB4;padding:10px 20px;border-radius:999px}}
h1{{font:600 80px/1.04 F;margin-top:28px}}
h2{{font:600 64px/1.08 F;margin-top:24px}}
p.sub{{font:500 36px/1.38 G;color:#5E564A;margin-top:24px;max-width:860px}}
.amber{{color:#D98B1A}}
.phone{{position:absolute;border-radius:64px;background:#1F1C18;padding:14px;box-shadow:0 40px 80px rgba(80,55,15,.25)}}
.phone img{{width:100%;height:100%;object-fit:cover;object-position:top;border-radius:52px;display:block}}
.foot{{position:absolute;left:80px;right:80px;bottom:56px;display:flex;justify-content:space-between;align-items:center;font:600 28px G;color:#8A6A2E}}
.dots span{{display:inline-block;width:14px;height:14px;border-radius:50%;background:#E2CFA6;margin-left:10px}}
.dots span.on{{background:#D98B1A}}
.btn{{display:inline-block;background:#E9A23B;color:#2E2A24;font:600 40px G;padding:26px 48px;border-radius:999px;margin-top:44px}}
.row{{display:flex;justify-content:space-between;align-items:center;padding:22px 0;border-bottom:2px dashed #E0CFAE;font:600 36px G}}
.row b{{font:600 30px G;color:#2F7A4A;background:#DDF0E2;padding:8px 18px;border-radius:999px}}
.note{{font:500 26px/1.4 G;color:#8A7F6E;margin-top:26px}}
.blob{{position:absolute;border-radius:50%;background:#F0DDB4;opacity:.6}}
.photo{{position:absolute;left:60px;right:60px;top:60px;height:1040px;border-radius:44px;overflow:hidden;box-shadow:0 30px 70px rgba(80,55,15,.22)}}
.photo img{{width:100%;height:100%;object-fit:cover;display:block}}
.cap{{position:absolute;left:80px;right:80px;top:1130px}}
.cap h3{{font:600 52px/1.1 F}}
.cap p{{font:500 30px G;color:#6B6252;margin-top:10px}}
.pill{{position:absolute;left:90px;top:90px;background:#FFF8EA;font:600 28px G;padding:12px 22px;border-radius:999px;color:#2E2A24}}
.grid{{position:absolute;right:70px;top:260px;width:470px;display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.grid img{{width:100%;height:300px;object-fit:cover;border-radius:28px}}
"""


def page(body, n, total, blob=True):
    dots = '<div class="dots">' + "".join(f'<span class="{"on" if i == n else ""}"></span>' for i in range(total)) + "</div>"
    b = '<div class="blob" style="width:620px;height:620px;right:-220px;bottom:-200px"></div>' if blob else ""
    return f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{b}{body}<div class='foot'><span>TOP Already?</span>{dots}</div></body></html>"


def phone(shot, x, y, rot=0, w=430, h=930):
    return f'<div class="phone" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({rot}deg)"><img src="{screen(shot)}"></div>'


# ---------------------------------------------------------------- posts
def photos_post(photos):
    """Carousel of the newest community photos. photos: list of dicts with img bytes."""
    shown = photos[:8]
    total = len(shown) + 2
    names = []
    for p in shown:
        n = project(p["project_key"])[1]
        if n not in names:
            names.append(n)
    thumbs = "".join(f'<img src="{uri(p["img"])}">' for p in shown[:4])
    slides = [page(f"""<div class="pad"><span class="tag">Fresh from the sites</span>
        <h1 style="max-width:440px">Real photos.<br><span class="amber">Real people.</span></h1>
        <p class="sub" style="max-width:430px">{len(shown)} new snap{'s' if len(shown) != 1 else ''} from people passing {', '.join(names[:3])}{' and more' if len(names) > 3 else ''}.</p></div>
        <div class="grid">{thumbs}</div>""", 0, total)]
    for i, p in enumerate(shown, 1):
        kind, name = project(p["project_key"])
        slides.append(page(f"""<div class="photo"><img src="{uri(p['img'])}"></div>
            <div class="pill">Snapped {day(p['taken_at'])}</div>
            <div class="cap"><h3>{name}</h3><p>{kind} &middot; by someone passing by</p></div>""", i, total, blob=False))
    slides.append(page(f"""<div class="pad" style="text-align:center;padding-top:250px"><span class="tag">Your turn</span>
        <h1 style="font-size:84px">Passing a site?<br><span class="amber">Snap it.</span></h1>
        <p class="sub" style="margin:30px auto 0">Every photo joins that project's month-by-month album. No account needed.</p>
        <div class="btn">topalready.github.io</div></div>""", total - 1, total))
    caption = (f"Fresh from the sites 📸\n\n{len(shown)} candid snap{'s' if len(shown) != 1 else ''} from people passing "
               f"{', '.join(names)} lately.\n\nWaiting for your BTO or condo? See its month-by-month photo album, "
               f"and if you pass a site, add a photo so everyone waiting can see how it's really going.\n\n"
               f"No ads. No login. 🔗 topalready.github.io (link in bio)\n\n{TAGS}")
    return {"id": "fresh_photos", "title": "Fresh from the sites", "slides": slides, "caption": caption}


def finish_line_post(data):
    end = (TODAY.replace(day=1) + dt.timedelta(days=31 * 6)).strftime("%Y-%m")
    start = TODAY.strftime("%Y-%m")
    soon = sorted([(x[0], x[4] or x[3]) for x in data["bto"] if start <= (x[4] or x[3]) <= end], key=lambda s: (s[1], s[0]))[:9]
    if not soon:
        return None
    slides = [
        page(f"""<div class="pad"><span class="tag">Almost there</span>
        <h2 style="font-size:72px">{len(soon)} BTO{'s' if len(soon) != 1 else ''} due to<br>complete by {ym(soon[-1][1])}</h2>
        <div style="margin-top:40px">""" + "".join(f'<div class="row"><span>{n}</span><b>{ym(m)}</b></div>' for n, m in soon) +
             f"""</div><p class="note">Estimated completion dates as of {ym(data['updated'])}. Check your project for the latest.</p></div>""", 0, 2),
        page(f"""<div class="pad"><span class="tag">Is yours on the list?</span>
        <h2 style="max-width:470px">Check your<br>block's progress<br>anytime</h2>
        <p class="sub" style="max-width:470px">Search your project at topalready.github.io. Link in bio.</p></div>
        {phone("f_bto.png", 580, 300, 3)}""", 1, 2),
    ]
    caption = (f"{len(soon)} BTO projects are estimated to complete by {ym(soon[-1][1])} 🏁\n\n" + ", ".join(n for n, _ in soon) +
               ".\n\nIs yours one of them? Check your block's progress anytime at topalready.github.io 🔗 link in bio\n\n"
               "Dates are estimates and can change — check your project page for the latest.\n\n" + TAGS)
    return {"id": "finish_line", "title": "Almost there", "slides": slides, "caption": caption}


async def render(posts):
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = {"week_of": TODAY.isoformat(), "posts": []}
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        for post in posts:
            files = []
            for i, html in enumerate(post["slides"], 1):
                tmp = OUT / "_tmp.html"; tmp.write_text(html)
                await pg.goto(tmp.as_uri()); await pg.wait_for_timeout(500)
                png = await pg.screenshot()
                tmp.unlink()
                name = f"{post['id']}_{i}.jpg"
                Image.open(io.BytesIO(png)).convert("RGB").save(OUT / name, "JPEG", quality=90)
                files.append(f"{SITE}/social/{TODAY.isoformat()}/{name}")
            manifest["posts"].append({k: v for k, v in post.items() if k != "slides"} | {"images": files})
        await b.close()
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1, ensure_ascii=False))
    (ROOT / "social" / "latest.json").write_text(json.dumps({"week_of": TODAY.isoformat(), "manifest": f"social/{TODAY.isoformat()}/manifest.json"}))
    print(json.dumps(manifest, indent=1, ensure_ascii=False))


def main():
    data = json.loads((ROOT / "data.json").read_text())
    rows = get(f"{SB}/rest/v1/photos?select=id,path,taken_at,project_key,reports&order=taken_at.desc&limit=100")
    since = (TODAY - dt.timedelta(days=int(sys.argv[1]) if len(sys.argv) > 1 else 7)).isoformat()
    fresh = [r for r in rows if not r["project_key"].startswith("_") and not (r.get("reports") or 0) and r["taken_at"][:10] >= since]
    posts = []
    if fresh:
        for r in fresh[:8]:
            try:
                r["img"] = photo_bytes(r["path"])
            except Exception as e:
                print("skip photo", r["path"], e)
        fresh = [r for r in fresh if "img" in r]
        if fresh:
            posts.append(photos_post(fresh))
    fl = finish_line_post(data)
    if fl:
        posts.append(fl)
    asyncio.run(render(posts))


if __name__ == "__main__":
    main()
