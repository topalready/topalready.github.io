"""Take real screenshots of the live app for Instagram posts.

Runs in GitHub Actions (.github/workflows/screens.yml), because the map and
satellite imagery need open internet. The workflow puts the results on the
"screens" branch (not main, so the published site stays small). For each
project slug it saves, under <tag>/<slug>/:
  sheet.png    the project sheet as it opens on a phone
  aerial.png   the same sheet scrolled to the "From above" satellite timeline
  sat_<i>.png  each satellite photo on its own (the square viewer only)
  space.png    the "Latest from space" block (newest Sentinel-2 picture and its date)
  map.png      the map with the sheet closed
  meta.json    project name plus the date shown on each satellite photo
Usage: python scripts/posts/screens.py <tag> <slug>[,<slug>...]
"""
import asyncio, json, pathlib, sys
from playwright.async_api import async_playwright

SITE = "https://topalready.github.io/"
ROOT = pathlib.Path(__file__).resolve().parent.parent.parent


async def shoot(cx, slug, out):
    out.mkdir(parents=True, exist_ok=True)
    pg = await cx.new_page()
    await pg.goto(f"{SITE}?p={slug}", wait_until="networkidle", timeout=90000)
    await pg.wait_for_selector("#sheetbody h2, #sheetbody h1", timeout=30000)
    await pg.wait_for_timeout(2500)
    await pg.screenshot(path=str(out / "sheet.png"))
    meta = {"slug": slug, "name": (await pg.locator("#sheetbody h2, #sheetbody h1").first.inner_text()).split("\n")[0].strip(), "frames": []}
    try:
        await pg.wait_for_selector(".aerial .aslide", timeout=20000)
        n = await pg.evaluate("+document.querySelector('.aerial .aslide').max+1")
        for i in range(n):
            ground = await pg.evaluate("""i=>{const s=document.querySelector('.aerial .aslide');s.value=i;s.dispatchEvent(new Event('input'));
                return document.querySelector(`.aerial .aframe[data-f="${i}"]`).classList.contains('aground')}""", i)
            if ground:
                continue  # community photo, not a satellite image
            try:
                await pg.wait_for_function("""i=>{const m=[...document.querySelectorAll(`.aerial .aframe[data-f="${i}"] img`)];
                    return m.length>0&&m.every(x=>x.complete&&x.naturalWidth>0)}""", arg=i, timeout=30000)
            except Exception:
                print("tiles incomplete", slug, i)
                continue
            await pg.wait_for_timeout(700)
            if i == 0:
                await pg.evaluate("document.querySelector('.aerial').scrollIntoView({block:'start'})")
                await pg.wait_for_timeout(600)
                await pg.screenshot(path=str(out / "aerial.png"))
            await pg.locator(".aerial .aview").screenshot(path=str(out / f"sat_{i}.png"))
            meta["frames"].append({"i": i, "file": f"sat_{i}.png",
                                   "date": await pg.locator(".aerial .adate").inner_text(),
                                   "rel": await pg.locator(".aerial .arel").inner_text()})
        meta["credit"] = (await pg.locator(".aerial .acredit").inner_text()).split(".")[0]
    except Exception as e:
        print("no satellite timeline for", slug, e)
    try:  # "Latest from space": newest Sentinel-2 picture, with its date
        sp = pg.locator(".aerial .space:not([hidden])")
        await sp.wait_for(timeout=8000)
        await sp.scroll_into_view_if_needed()
        await pg.wait_for_function("(()=>{const i=document.querySelector('.aerial .space img');return i&&i.complete&&i.naturalWidth>0})()", timeout=15000)
        await pg.wait_for_timeout(400)
        await sp.screenshot(path=str(out / "space.png"))
        meta["space"] = {"file": "space.png", "date": await sp.locator(".acap b").inner_text(), "ago": await sp.locator(".acap span").inner_text()}
    except Exception as e:
        print("no latest-from-space picture for", slug, e)
    await pg.keyboard.press("Escape")
    await pg.wait_for_timeout(2500)
    await pg.screenshot(path=str(out / "map.png"))
    (out / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=1))
    await pg.close()
    print("ok", slug, len(meta["frames"]), "satellite photos")


async def main():
    tag, slugs = sys.argv[1], [s.strip() for s in sys.argv[2].split(",") if s.strip()]
    async with async_playwright() as p:
        b = await p.chromium.launch()
        cx = await b.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True,
                                 locale="en-SG", timezone_id="Asia/Singapore")
        for s in slugs:
            try:
                await shoot(cx, s, ROOT / "social" / "screens" / tag / s)
            except Exception as e:
                print("failed", s, e)
        await b.close()

asyncio.run(main())
