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
SHOTS=pathlib.Path(os.environ.get('SHOTS','/home/claude/shots'))/'2026-11-18'  # from the repo's "screens" branch
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



# POV: u search ur BTO at 2am (format b): map -> project page -> From above slider.
# Project: West Hill @ Bukit Batok. Facts from data.json (hdb checked 2026-11-17 10:12):
# data["hdb"]["West Hill @ Bukit Batok"] = [9, 11, 2026] -> 9 of 11 blocks completed. Not complete, so no "done" claim.
# Satellite photo dates from meta.json of the 2026-11-18 screenshots. Mar 2015 photo is partly cloudy, so skipped.
# The clock times (2:03am etc.) are a joke, not data.
CSS+="""
.pair{display:flex;gap:26px;margin-top:40px}
.pair figure{margin:0;flex:1}
.pair img{width:100%;aspect-ratio:1;border-radius:32px;display:block;border:4px solid #3d4475}
.pair figcaption{font:700 40px Fi;color:#FFD36E;margin-top:16px;text-align:center}
.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-top:40px}
.grid figure{margin:0}.grid img{width:100%;aspect-ratio:1;border-radius:24px;display:block;border:3px solid #3d4475}
.grid figcaption{font:700 32px Fi;color:#FFD36E;margin-top:8px;text-align:center}
.grid .fx{display:flex;align-items:center;justify-content:center;font:600 36px/1.25 Fr;text-align:center;color:#F7EFE2;padding:10px}
.clock{font:600 34px Fi;color:#FFD36E;letter-spacing:.04em}
.dark .small{color:#AFA6CF}.small{font-size:30px !important}
.s.sat .cred{bottom:118px}.dark .cred{color:#AFA6CF}
.facts{font:600 38px/1.4 Fi;margin-top:34px;color:#F7EFE2}.facts b{color:#FFD36E}
"""
SL='west-hill-bukit-batok';m=json.load(open(SHOTS/SL/'meta.json'));CR=m.get('credit') or 'Imagery: Esri, Vantor, Earthstar Geographics, via World Imagery Wayback'
F={f['date']:f for f in m['frames']}
N=6;P=[]
P.append(page(f'<div class="left" style="max-width:470px"><div class="clock">🌙 2:03am</div><h1 style="font-size:96px">POV: u should be <em>sleeping</em></h1><p>but instead u open the app to check ur BTO. again.</p></div>'
  f'<div class="phone" style="right:60px;top:120px;width:450px"><img src="{img(SL+"/map.png",900)}"></div>',dark=True,n=1,N=N,fly='left:80px;bottom:150px;width:250px;height:250px;transform:rotate(-12deg)'))
P.append(page(f'<div class="left" style="max-width:450px"><div class="clock">🌙 2:06am</div><h2>tap ur project</h2><p>West Hill @ Bukit Batok:</p><p style="margin-top:10px"><b style="font:600 64px Fr;color:#FFD36E">9 of 11</b><br>blocks completed, from HDB’s own list</p><p style="font-size:36px">which 2 ah. which 2 😶</p><div class="small" style="margin-top:20px">as of 17 Nov 2026</div></div>'
  f'<div class="phone" style="right:60px;top:120px;width:450px"><img src="{img(SL+"/sheet.png",900)}"></div>',dark=True,n=2,N=N))
P.append(page(f'<div class="left" style="max-width:450px"><div class="clock">🌙 2:11am</div><h2>scroll to <em>“From above”</em></h2><p>real satellite photos of the exact spot.</p><p>drag back to 2012. press play. no regrets</p></div>'
  f'<div class="phone" style="right:60px;top:120px;width:450px"><img src="{img(SL+"/aerial.png",900)}"></div><div class="cred" style="max-width:400px">{CR}.</div>',dark=True,n=3,N=N))
a,b=F['Apr 2012'],F['Aug 2025']
P.append(page(f'<div class="clock">🌙 2:17am</div><h2 style="font-size:70px">wait. ur BTO used to be <em>forest</em>??</h2><div class="pair"><figure><img src="{img(SL+"/"+a["file"],700)}"><figcaption>{a["date"]} photo</figcaption></figure><figure><img src="{img(SL+"/"+b["file"],700)}"><figcaption>{b["date"]} photo</figcaption></figure></div>'
  f'<div class="facts">West Hill @ Bukit Batok, same spot, 13 years apart</div><div class="cred">{CR}.</div>',dark=True,n=4,N=N,cls='sat'))
cells=''.join(f'<figure><img src="{img(SL+"/"+F[d]["file"],420)}"><figcaption>{d}</figcaption></figure>' for d in ['Apr 2012','Feb 2018','Jan 2020','Jan 2022','Aug 2025'])
P.append(page(f'<div class="clock">🌙 2:40am</div><h2 style="font-size:70px">u have now pressed play <em>6 times</em></h2><div class="grid">{cells}<div class="fx">same lah<br>but cannot stop 🪰</div></div>'
  f'<div class="cred">{CR}. Photo dates as shown in the app.</div>',dark=True,n=5,N=N,cls='sat'))
P.append(page(f'<div class="left"><div class="clock">🌙 3:02am</div><h2>ok ur turn. then <em>go sleep</em></h2><p>search ur BTO, scroll to “From above”, drag back to 2012.</p><p>free, no login. the fly will keep watching 🪰</p><div><span class="pill">link in bio</span></div></div>'
  f'<div class="phone" style="right:64px;top:170px"><img src="{img(SL+"/map.png",900)}"></div>',dark=True,n=N,N=N,fly='left:110px;bottom:140px;width:200px;height:200px;transform:rotate(8deg)'))
posts={'pov_2am':P}
async def main():

    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':1080,'height':1350})
        for name,slides in posts.items():
            out=pathlib.Path(name);out.mkdir(exist_ok=True)
            for i,s in enumerate(slides,1):
                await pg.set_content(f'<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{s}</body></html>');await pg.evaluate('document.fonts.ready');await pg.wait_for_timeout(150)
                await pg.screenshot(path=f'{name}/{i}.png');
                from PIL import Image;Image.open(f'{name}/{i}.png').convert('RGB').save(f'{name}/{name}_{i}.jpg',quality=93)
        await b.close()
asyncio.run(main())
