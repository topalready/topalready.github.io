import pathlib, asyncio
from playwright.async_api import async_playwright
FM='/root/vid/node_modules/@fontsource/'
import base64
b64=lambda p:base64.b64encode(open(p,'rb').read()).decode()
FLY=open('/root/vid/fly.svg').read().replace('width="60" height="60"','width="100%" height="100%"')
CSS=f"""
@font-face{{font-family:Fr;src:url(data:font/woff2;base64,{b64(FM+'fraunces/files/fraunces-latin-600-normal.woff2')});font-weight:600}}
@font-face{{font-family:Fr;src:url(data:font/woff2;base64,{b64(FM+'fraunces/files/fraunces-latin-500-normal.woff2')});font-weight:500}}
@font-face{{font-family:Fi;src:url(data:font/woff2;base64,{b64(FM+'figtree/files/figtree-latin-500-normal.woff2')});font-weight:500}}
@font-face{{font-family:Fi;src:url(data:font/woff2;base64,{b64(FM+'figtree/files/figtree-latin-600-normal.woff2')});font-weight:600}}
@font-face{{font-family:Fi;src:url(data:font/woff2;base64,{b64(FM+'figtree/files/figtree-latin-700-normal.woff2')});font-weight:700}}
*{{box-sizing:border-box}}body{{margin:0}}
.s{{width:1080px;height:1350px;position:relative;overflow:hidden;background:#FFF8EC;color:#3A2C26;font-family:Fi;padding:110px 96px;display:flex;flex-direction:column}}
.s.dark{{background:#262C52;color:#F7EFE2}}
.k{{font:700 30px Fi;letter-spacing:.08em;text-transform:uppercase;color:#B0763A}}.dark .k{{color:#FFD36E}}
h1{{font:600 104px/1.02 Fr;margin:26px 0 0;letter-spacing:-.01em}}h2{{font:600 76px/1.08 Fr;margin:18px 0 6px}}
h1 em,h2 em{{font-style:normal;color:#E39A2A}}.dark h1 em,.dark h2 em{{color:#FFD36E}}
p{{font:500 40px/1.4 Fi;margin:30px 0 0;color:#6E5A4E}}.dark p{{color:#D9CFE6}}
.fly{{position:absolute;width:300px;height:300px}}
.foot{{position:absolute;left:96px;right:96px;bottom:70px;display:flex;justify-content:space-between;font:600 28px Fi;color:#9A7B5F}}.dark .foot{{color:#AFA6CF}}
.dots{{letter-spacing:6px}}
.row{{background:#fff;border:2px solid #EFE3CF;border-radius:30px;padding:24px 36px;margin-top:18px}}
.row b{{font:600 46px Fr;display:block}}.row span{{font:600 30px Fi;color:#7A6658}}
.bar{{height:18px;border-radius:9px;background:#EFE3CF;margin:12px 0 8px;overflow:hidden}}.bar i{{display:block;height:100%;background:#F2B33D;border-radius:9px}}
.note{{font:500 26px/1.4 Fi;color:#9A8B7E;margin-top:auto;padding:20px 0 70px}}
.pill{{display:inline-block;margin-top:44px;background:#F2B33D;color:#3A2C26;font:700 46px Fi;padding:22px 44px;border-radius:99px}}
.big{{font-size:300px;line-height:1;margin:auto 0;text-align:center}}.st h2{{font-size:96px}}.st p{{font-size:52px}}
"""
def page(body,dark=False,n=1,N=1,fly=None,cls=''):
    f=f'<div class="fly" style="{fly}">{FLY}</div>' if fly else ''
    d=''.join('●' if i==n else '○' for i in range(1,N+1))
    return f'<div class="s{" dark" if dark else ""} {cls}">{body}{f}<div class="foot"><span>TOP Already?</span><span class="dots">{d}</span></div></div>'
def bto(name,done,total,est):
    pct=0 if not total else done/total*100
    st=f'{done} of {total} blocks completed' if total else 'no blocks on HDB’s list yet'
    return f'<div class="row"><b>{name}</b><div class="bar"><i style="width:{max(pct,2):.0f}%"></i></div><span>{st} · est. {est}</span></div>'
SRC='<div class="note">Estimated dates from HDB (via BTO HQ). Block counts from HDB’s official list of completed blocks on data.gov.sg, as of 7 Nov 2026. Dates can change.</div>'
BUB=".bub{{background:#fff;border:2px solid #EFE3CF;border-radius:36px 36px 36px 8px;padding:34px 40px;font:500 46px/1.35 Fi;color:#3A2C26;margin-top:56px;max-width:860px}}.bub small{{display:block;font:700 28px Fi;color:#2E9C6B;margin-bottom:10px}}"

EXTRA="""
.vs{display:flex;gap:30px;margin-top:60px;flex:1}
.col{flex:1;background:#fff;border:2px solid #EFE3CF;border-radius:36px;padding:44px 36px;display:flex;flex-direction:column;align-items:center;text-align:center}
.col.f{background:#262C52;color:#F7EFE2;border-color:#262C52}
.col .who{font:700 30px Fi;letter-spacing:.08em;text-transform:uppercase;color:#B0763A}.col.f .who{color:#FFD36E}
.col .e{font-size:190px;line-height:1;margin:40px 0}
.col .t{font:600 50px/1.2 Fr}
.todo{margin-top:40px}
.todo div{display:flex;gap:28px;align-items:flex-start;background:#fff;border:2px solid #EFE3CF;border-radius:30px;padding:30px 36px;margin-top:20px;font:600 44px/1.25 Fi}
.todo div i{font-style:normal;flex:none;width:64px;height:64px;border-radius:50%;background:#F2B33D;font:700 36px/64px Fi;text-align:center}
.todo small{display:block;font:500 30px Fi;color:#7A6658;margin-top:6px}
.stat{margin-top:34px;font:600 40px/1.35 Fi;color:#3A2C26}.stat b{color:#E39A2A;font:600 56px Fr}
.huge{font:600 520px/1 Fr;color:#E39A2A;margin:10px 0 0;text-align:center}
.bub2{align-self:flex-end;background:#F2B33D;border-radius:36px 36px 8px 36px;padding:34px 40px;font:600 46px/1.35 Fi;color:#3A2C26;margin-top:30px;max-width:820px}
.bub2 small{display:block;font:700 28px Fi;color:#6B4A12;margin-bottom:10px}
"""
CSS+=BUB.replace('{{','{').replace('}}','}')+EXTRA
import io, json
from PIL import Image as _I
import os
SHOTS=pathlib.Path(os.environ.get('SHOTS','/home/claude/shots'))/'2026-11-20'  # from the repo's "screens" branch
def img(rel,w=1100):
    im=_I.open(SHOTS/rel).convert('RGB');im.thumbnail((w,w*3));b=io.BytesIO();im.save(b,'JPEG',quality=90)
    return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
def sat(slug,which):
    f=json.load(open(SHOTS/slug/'meta.json'))['frames'];return img(f'{slug}/{f[0 if which=="then" else -1]["file"]}',760)
CSS+="""
.tn{display:flex;gap:34px;margin-top:26px;align-items:center}
.tn img{width:456px;height:456px;border-radius:34px;display:block;border:3px solid #EFE3CF}
.tn div{flex:1}.tn b{display:block;font:600 76px/1 Fr}.tn span{display:block;font:600 34px/1.3 Fi;color:#7A6658;margin-top:14px}
.tn+.tn{margin-top:22px}
.s.sat{padding-top:76px}.s.sat h2{font-size:64px;margin:10px 0 0}
.cred{position:absolute;left:96px;right:96px;bottom:120px;font:500 21px/1.35 Fi;color:#9A8B7E}
.phone{position:absolute;width:470px;border-radius:54px;border:12px solid #1c2040;box-shadow:0 30px 70px rgba(0,0,0,.35);overflow:hidden;background:#fff}
.phone img{width:100%;display:block}
.dark .phone{border-color:#F7EFE2}
.left{max-width:420px}.left h2{font-size:70px}.left p{font-size:36px}
"""



# Format (d): real data through the app's own project pages: "X of Y blocks completed".
# Facts from data.json (hdb checked 2026-11-20 09:01), data["hdb"] = [completed, total, year]:
#   Bishan Ridges 6/7 (est Jun 2026, delayed est Oct 2026), Kovan Wellspring 4/6 (est Sep 2026),
#   Towner Residences 2/3, Kent Heights 1/2, Lakeside View 3/11 (all est Dec 2026). None complete, so no "done" claims.
# Satellite dates from meta.json of the 2026-11-20 screenshots (screens branch). Group chat on slide 3 is made up (labelled).
CSS+="""
.pair{display:flex;gap:26px;margin-top:40px}
.pair figure{margin:0;flex:1}
.pair img{width:100%;aspect-ratio:1;border-radius:32px;display:block;border:4px solid #3d4475;object-fit:cover}
.pair figcaption{font:700 38px Fi;color:#FFD36E;margin-top:16px;text-align:center}
.pair figcaption small{display:block;font:500 28px Fi;color:#AFA6CF;margin-top:4px}
.s.sat .cred{bottom:118px}.dark .cred{color:#AFA6CF}
.facts{font:600 40px/1.4 Fi;margin-top:30px;color:#F7EFE2}.facts b{color:#FFD36E}
.asof{font:600 28px Fi;color:#9A8B7E;margin-top:22px}.dark .asof{color:#AFA6CF}
.row{padding:14px 34px;margin-top:14px}.row b{font-size:40px}.row .bar{margin:8px 0 6px}
.chat{margin-top:40px;max-width:460px}
.chat .bub{margin-top:22px;font-size:40px;padding:26px 32px}
.chat .bub2{font-size:40px;padding:26px 32px;margin-top:22px}
.tag{font:500 26px Fi;color:#9A8B7E;margin-top:18px}
"""
CR='Imagery: Esri, Vantor, Earthstar Geographics, via World Imagery Wayback'
def M(sl):return json.load(open(SHOTS/sl/'meta.json'))
def fr(sl,d):return next(f for f in M(sl)['frames'] if f['date']==d)
N=6;P=[]
# 1 hook
P.append(page(f'<div class="left" style="max-width:440px"><div class="k">BTO life</div><h1 style="font-size:82px">when the block <em>beside</em> urs finish first 🫠</h1>'
  f'<p style="font-size:34px">Bishan Ridges: <b style="color:#3A2C26">6 of 7</b> blocks completed on HDB’s own list.</p><p style="font-size:34px">if urs is the 7th… stay strong</p><div class="asof">as of 20 Nov 2026</div></div>'
  f'<div class="phone" style="right:50px;top:110px;width:420px"><img src="{img("bishan-ridges/sheet.png",900)}"></div>',n=1,N=N,fly='left:70px;bottom:120px;width:210px;height:210px;transform:rotate(-10deg)'))
# 2 the list
rows=bto('Bishan Ridges',6,7,'Oct 2026')+bto('Kovan Wellspring',4,6,'Sept 2026')+bto('Towner Residences',2,3,'Dec 2026')+bto('Kent Heights',1,2,'Dec 2026')+bto('Lakeside View',3,11,'Dec 2026')
P.append(page(f'<div class="k">the app counts block by block</div><h2 style="font-size:68px">who’s <em>almost</em> there</h2>{rows}'
  '<div class="note" style="padding-bottom:96px">“est.” = HDB’s estimated completion for the whole project. Block counts from HDB’s official list of completed blocks, as of 20 Nov 2026. Dates can change.</div>',n=2,N=N))
# 3 group chat + Kovan page
P.append(page(f'<div class="chat"><div class="k">meanwhile in the group chat</div>'
  '<div class="bub"><small>neighbour</small>other block collect keys liao!! 🎉</div>'
  '<div class="bub2"><small>u</small>congrats ah 🙂🙂🙂</div>'
  '<div class="bub2"><small>u, 2 mins later</small>ok but ours when</div>'
  '<div class="tag">(made-up chat. the feeling is real)</div></div>'
  f'<div class="phone" style="right:50px;top:110px;width:390px"><img src="{img("kovan-wellspring/sheet.png",900)}"></div>'
  '<div style="position:absolute;right:50px;top:1000px;width:390px;font:600 32px/1.35 Fi;color:#6E5A4E;text-align:center">Kovan Wellspring: 4 of 6 blocks completed (HDB, as of 20 Nov 2026)</div>',n=3,N=N,fly='left:110px;bottom:150px;width:220px;height:220px;transform:rotate(-8deg)'))
# 4 Lakeside View then vs now
a,b=fr('lakeside-view','Jun 2012'),fr('lakeside-view','Aug 2025')
P.append(page(f'<div class="k">from above</div><h2 style="font-size:66px">Lakeside View: <em>3 of 11</em> done. here’s the spot</h2><div class="pair"><figure><img src="{img("lakeside-view/"+a["file"],700)}"><figcaption>{a["date"]} photo</figcaption></figure><figure><img src="{img("lakeside-view/"+b["file"],700)}"><figcaption>{b["date"]} photo</figcaption></figure></div>'
  f'<div class="facts">same spot, in the app’s “From above” slider. <b>8 more blocks</b> to go on HDB’s list (as of 20 Nov 2026)</div><div class="cred">{CR}.</div>',dark=True,n=4,N=N,cls='sat'))
# 5 Kent Heights: last sharp photo vs latest from space
k=fr('kent-heights','May 2025');sp=M('kent-heights')['space']
P.append(page(f'<div class="k">new in the app</div><h2 style="font-size:64px">Kent Heights, <em>1 of 2</em> done. got newer photo or not?</h2><div class="pair"><figure><img src="{img("kent-heights/"+k["file"],700)}"><figcaption>{k["date"]} photo<small>sharp but old</small></figcaption></figure><figure><img src="{img("kent-heights/space.png",900)}" style="object-position:center 62%"><figcaption>{sp["date"]}<small>“Latest from space”: blur but fresh</small></figcaption></figure></div>'
  f'<div class="facts">each dot from space is about 10 m, so cannot see who already collect keys lah 🪰</div><div class="cred">Left: {CR}. Right: contains modified Copernicus Sentinel data 2026 (Sentinel-2, European Space Agency). Block count from HDB, as of 20 Nov 2026.</div>',dark=True,n=5,N=N,cls='sat'))
# 6 CTA
P.append(page(f'<div class="left" style="max-width:430px"><div class="k">ur turn</div><h2>how many of ur blocks <em>done</em> already?</h2><p style="font-size:38px">search ur BTO. the page shows HDB’s block count, checked daily.</p><p style="font-size:38px">then scroll to “From above”</p><div><span class="pill">link in bio</span></div></div>'
  f'<div class="phone" style="right:56px;top:150px;width:440px"><img src="{img("kent-heights/map.png",900)}"></div>',n=N,N=N,fly='left:300px;bottom:150px;width:200px;height:200px;transform:rotate(14deg)'))
posts={'blocks_race':P}
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':1080,'height':1350})
        for name,slides in posts.items():
            out=pathlib.Path(name);out.mkdir(exist_ok=True)
            for i,s in enumerate(slides,1):
                await pg.set_content(f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{s}</body></html>');await pg.evaluate('document.fonts.ready');await pg.wait_for_timeout(150)
                await pg.screenshot(path=f'{name}/{i}.png')
                from PIL import Image;Image.open(f'{name}/{i}.png').convert('RGB').save(f'{name}/{name}_{i}.jpg',quality=93)
        await b.close()
asyncio.run(main())
