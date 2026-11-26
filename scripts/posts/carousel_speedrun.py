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
SHOTS=pathlib.Path(os.environ.get('SHOTS','/home/claude/shots'))/'2026-11-26'  # from the repo's "screens" branch
def img(rel,w=1100):
    im=_I.open(SHOTS/rel).convert('RGB');im.thumbnail((w,w*3));b=io.BytesIO();im.save(b,'JPEG',quality=90)
    return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
def satf(slug,date):
    f=[x for x in json.load(open(SHOTS/slug/'meta.json'))['frames'] if x['date']==date][0];return img(f'{slug}/{f["file"]}',760)
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



# BTO speedrun: biggest visible change between two satellite photos the app has, for 3 BTOs + 1 that hasn't started.
# Facts from data.json as of 26 Nov 2026 (launch month, HDB est. completion; no delay; none on HDB's completed-blocks list).
# Photo dates from meta.json of the 2026-11-26 screenshots. % figures are what the app's own sheets show.
N=6
ASOF='26 Nov 2026'
CR='Imagery: Esri, Vantor, Earthstar Geographics, via World Imagery Wayback.'
CSS+="""
.pr{display:flex;gap:24px;margin-top:34px}.pr div{flex:1;position:relative}
.pr img{width:100%;border-radius:30px;display:block;border:3px solid #EFE3CF}
.dark .pr img{border-color:#3d4475}
.pr b{display:block;font:600 40px Fr;margin-top:12px}.pr span{font:600 26px Fi;color:#7A6658}.dark .pr span{color:#AFA6CF}
.pr .arr{position:absolute;right:-46px;top:200px;width:68px;height:68px;border-radius:50%;background:#F2B33D;font:700 40px/68px Fi;text-align:center;z-index:2;color:#3A2C26}
.rate{display:inline-block;margin-top:30px;background:#262C52;color:#FFD36E;font:700 34px Fi;padding:14px 28px;border-radius:99px}
.dark .rate{background:#F2B33D;color:#3A2C26}
.s.gp{padding-top:84px}.s.gp h2{font-size:62px;margin:8px 0 0}.s.gp p{font-size:38px;margin-top:22px;line-height:1.35}
.gp .cred{bottom:118px}.dark .cred{color:#AFA6CF}
.ph3{display:flex;gap:22px;margin-top:40px}.ph3 div{flex:1}
.ph3 .fr{border-radius:34px;border:9px solid #1c2040;overflow:hidden;box-shadow:0 18px 40px rgba(0,0,0,.25);background:#fff}
.ph3 img{width:100%;display:block}
.ph3 b{display:block;font:600 34px/1.1 Fr;margin-top:16px}.ph3 span{display:block;font:600 24px/1.3 Fi;color:#7A6658;margin-top:6px}
"""
def meta(sl): return json.load(open(SHOTS/sl/'meta.json'))
def fr(sl,date): return [x for x in meta(sl)['frames'] if x['date']==date][0]
def pair(sl,a,b):
    A,B=fr(sl,a),fr(sl,b)
    return (f'<div class="pr"><div><img src="{img(sl+"/"+A["file"],700)}"><b>{a}</b><span>{A["rel"]}</span><i class="arr" style="font-style:normal">→</i></div>'
            f'<div><img src="{img(sl+"/"+B["file"],700)}"><b>{b}</b><span>{B["rel"]}</span></div></div>')
def cred(): return f'<div class="cred">Satellite photos as shown in the app, date on each photo. {CR}</div>'
S=[]
S.append(page(f'<div class="k">BTO speedrun 🏁 · Parc Meadow @ Tengah</div><h1 style="font-size:86px">fly blinked. <em>forest became blocks.</em></h1>{pair("parc-meadow-tengah","Jan 2022","Aug 2025")}<p style="font-size:36px">Jan 2022 photo: trees + 1 dirt path. Aug 2025 photo: blocks everywhere. same exact spot.</p>{cred()}',dark=True,n=1,N=N,cls='gp',fly='right:60px;top:40px;width:150px;height:150px;transform:rotate(14deg)'))
S.append(page(f'<div class="k">Runner #2 · Queensway Canopy</div><h2>green patch → <em>construction site</em></h2>{pair("queensway-canopy","Aug 2022","Oct 2024")}<p>only 2 yrs 2 months between these 2 photos. somebody very motivated.</p><div class="rate">fly’s split time: 2y 2m ⏱️</div>{cred()}',n=2,N=N,cls='gp',fly='right:70px;bottom:168px;width:125px;height:125px;transform:rotate(-10deg)'))
S.append(page(f'<div class="k">Runner #3 · Tanjong Rhu Riverfront I &amp; II</div><h2>trees → <em>dug up, full action</em></h2>{pair("tanjong-rhu-riverfront-i-ii","Aug 2022","May 2025")}<p>2 yrs 9 months between photos. May 2025 photo was 11 months after launch.</p><div class="rate">fly’s split time: 2y 9m ⏱️</div>{cred()}',n=3,N=N,cls='gp',fly='right:70px;bottom:168px;width:125px;height:125px;transform:scaleX(-1) rotate(-8deg)'))
S.append(page(f'<div class="k">Still at the start line · Lakeview Cascadia</div><h2>field → <em>…still field</em> 🌱</h2>{pair("lakeview-cascadia","Jun 2012","Feb 2025")}<p>relax, not late one. Feb 2025 photo was 1 yr <b>before</b> launch. it only launched Jun 2026, race haven’t start.</p>{cred()}',dark=True,n=4,N=N,cls='gp',fly='right:70px;bottom:168px;width:125px;height:125px;transform:rotate(12deg)'))
def ph(sl,name,pc,est):
    return f'<div><div class="fr"><img src="{img(sl+"/sheet.png",600)}"></div><b>{name}</b><span>{pc} of est. timeline · HDB est. {est}</span></div>'
S.append(page(f'<div class="k">Real talk, as of {ASOF}</div><h2 style="font-size:60px">nobody crossed the <em>finish line</em> yet</h2><div class="ph3">{ph("parc-meadow-tengah","Parc Meadow","88%","Jun 2027")}{ph("queensway-canopy","Queensway Canopy","67%","Dec 2028")}{ph("tanjong-rhu-riverfront-i-ii","Tanjong Rhu Riverfront","45%","Dec 2029")}</div><p style="font-size:29px">no delay announced for any. “split times” = just the gap between 2 satellite photos, not how fast they built. % = time since launch vs HDB’s estimate. dates are estimates.</p><div class="cred">Real screenshots of the app’s project pages.</div>',n=5,N=N,cls='gp'))
S.append(page(f'<div class="left"><div class="k">Ur turn</div><h2>time <em>ur</em> BTO’s speedrun</h2><p>search ur BTO, scroll to “From above”, drag the slider from 2012 to now.</p><p>which BTO should the fly time next? 👇</p><div><span class="pill">link in bio 🪰</span></div></div><div class="phone" style="right:60px;top:150px"><img src="{img("tanjong-rhu-riverfront-i-ii/aerial.png",900)}"></div><div class="cred" style="color:#AFA6CF;right:600px;bottom:118px">{CR} Tanjong Rhu Riverfront I &amp; II, Jun 2012 photo.</div>',dark=True,n=6,N=N))
posts={'speedrun':S}
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
