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
SHOTS=pathlib.Path(os.environ.get('SHOTS','/home/claude/shots'))/'2026-11-28b'  # from the repo's "screens" branch
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




# "every family gathering": answering the relatives' BTO questions with the app. One project: Queen's Arc.
# Facts from data.json checked 28 Nov 2026 09:59: launched Aug 2021, HDB est. Sept 2027, no delay, 6 blocks,
# none on HDB's completed-blocks list. 88% is what the app's own sheet shows. Photo dates from meta.json (2026-11-28b).
N=6
ASOF='28 Nov 2026'
SL='queen-s-arc'
CR='Imagery: Esri, Vantor, Earthstar Geographics, via World Imagery Wayback.'
CSS+="""
.s.g{padding-top:84px}
.ask{background:#fff;border:2px solid #EFE3CF;border-radius:40px 40px 40px 10px;padding:30px 40px;font:600 54px/1.25 Fr;color:#3A2C26;margin-top:22px;max-width:900px}
.ask small{display:block;font:700 28px Fi;letter-spacing:.06em;text-transform:uppercase;color:#B0763A;margin-bottom:8px}
.dark .ask{background:#F7EFE2}
.me{background:#F2B33D;border-radius:40px 40px 10px 40px;padding:26px 36px;font:600 42px/1.3 Fi;color:#3A2C26;margin-top:22px;align-self:flex-start}
.ph{flex:none;border-radius:50px;border:11px solid #1c2040;box-shadow:0 26px 60px rgba(0,0,0,.3);overflow:hidden;background:#fff}
.dark .ph{border-color:#F7EFE2}
.ph img{width:100%;display:block}
.row2{display:flex;gap:40px;margin-top:34px;align-items:flex-start}.row2 .tx{flex:1}.row2 .tx p:first-child{margin-top:6px}
.tx p{font-size:40px;margin-top:28px}.tx p b{color:#3A2C26}.dark .tx p b{color:#FFD36E}
.cred2{position:absolute;left:96px;right:96px;bottom:118px;font:500 21px/1.35 Fi;color:#9A8B7E}
.dark .cred2{color:#AFA6CF}
.two{display:flex;gap:28px;margin-top:34px}.two div{flex:1;position:relative}
.two img{width:100%;border-radius:30px;display:block;border:3px solid #EFE3CF}
.two b{display:block;font:600 42px Fr;margin-top:14px}.two span{font:600 28px Fi;color:#7A6658}
.arr{position:absolute;right:-46px;top:200px;width:64px;height:64px;border-radius:50%;background:#F2B33D;font:700 38px/64px Fi;text-align:center;z-index:2;font-style:normal}
.lead{font:500 38px/1.4 Fi;color:#6E5A4E;margin-top:30px}
.spc{width:560px;height:560px;border-radius:34px;display:block;border:3px solid #EFE3CF;object-fit:cover;object-position:top}
"""
def ph(rel,style,crop=None):
    from PIL import Image as I
    im=I.open(SHOTS/rel).convert('RGB')
    if crop: w,h=im.size;im=im.crop((0,int(h*crop[0]),w,int(h*crop[1])))
    im.thumbnail((900,2000));b=io.BytesIO();im.save(b,'JPEG',quality=90)
    return f'<div class="ph" style="{style}"><img src="data:image/jpeg;base64,{base64.b64encode(b.getvalue()).decode()}"></div>'
def fr(date): return [x for x in json.load(open(SHOTS/SL/'meta.json'))['frames'] if x['date']==date][0]
S=[]
# 1 hook
S.append(page('<div class="k">every family gathering</div>'
  '<div class="ask" style="font-size:72px;max-width:760px"><small>auntie</small>“eh ur BTO TOP already or not?”</div>'
  '<div class="row2"><div class="tx"><div class="me" style="margin-top:0">me: wait ah. let me show u 📱</div>'
  '<p style="font-size:40px;margin-top:44px">4 relatives.<br>4 questions.<br>1 app.</p><p style="font-size:40px">swipe →</p></div>'
  + ph(f'{SL}/map.png','width:400px',(0,0.80)) + '</div>'
  + '<div class="cred2">Real screenshot of the app’s map, Queen’s Arc.</div>',
  dark=True,n=1,N=N,cls='g',fly='right:70px;top:120px;width:200px;height:200px;transform:rotate(12deg)'))
# 2 auntie: when can move in -> project page
S.append(page('<div class="k">Question 1</div><div class="ask"><small>auntie</small>“so when can move in?”</div>'
  '<div class="row2"><div class="tx"><p>open ur BTO’s page:</p><p><b>HDB est. Sept 2027.</b><br>no delay announced.</p>'
  '<p>88% of the estimated timeline gone liao 🪰</p><p style="font-size:34px">“estimated” ah auntie. not promise.</p></div>'
  + ph(f'{SL}/sheet.png','width:440px',(0.03,0.90)) + '</div>'
  + f'<div class="cred2">Real screenshot of the app, Queen’s Arc, as of {ASOF}. Estimated date from HDB (via BTO HQ).</div>',n=2,N=N,cls='g'))
# 3 uncle: got build or not -> then vs now
a,b=fr('Aug 2022'),fr('Oct 2024')
S.append(page('<div class="k">Question 2</div><div class="ask"><small>uncle</small>“got build already or not?”</div>'
  f'<div class="two"><div><img src="{img(SL+"/"+a["file"],700)}"><b>Aug 2022 photo</b><span>{a["rel"].replace("1 yrs","1 yr")}</span><i class="arr">→</i></div>'
  f'<div><img src="{img(SL+"/"+b["file"],700)}"><b>Oct 2024 photo</b><span>{b["rel"]}</span></div></div>'
  '<p class="lead" style="font-size:42px;color:#3A2C26"><b>got.</b> Aug 2022 photo: flat land. Oct 2024 photo: blocks.</p><p class="lead" style="font-size:36px;margin-top:18px">scroll to “From above”, drag the slider. uncle can see for himself 👀</p>'
  f'<div class="cred2">Satellite photos as shown in the app, date on each photo. {CR}</div>',n=3,N=N,cls='g'))
# 4 cousin: that photo old leh -> latest from space
sp=json.load(open(SHOTS/SL/'meta.json'))['space']
from PIL import Image as I
im=I.open(SHOTS/SL/'space.png').convert('RGB');w,h=im.size
# keep only the photo square (drop the explainer text above and credit below)
top=int(h*0.235);im=im.crop((0,top,w,top+w));bb=io.BytesIO();im.save(bb,'JPEG',quality=92)
spimg='data:image/jpeg;base64,'+base64.b64encode(bb.getvalue()).decode()
S.append(page('<div class="k">Question 3</div><div class="ask"><small>cousin</small>“wah that photo 2024 leh. now how?”</div>'
  f'<div style="display:flex;gap:34px;margin-top:34px;align-items:flex-start"><img class="spc" src="{spimg}">'
  f'<p style="margin:0;font-size:40px">“Latest from space”: newest clear satellite picture.<br><br><b style="color:#3A2C26">{sp["date"]}</b>.<br><br>blur blur one (each dot ~10 m), but fresh 🛰️</p></div>'
  f'<div class="cred2">Real “Latest from space” picture as shown in the app, Queen’s Arc. Contains modified Copernicus Sentinel data 2026 (Sentinel-2, European Space Agency).</div>',
  n=4,N=N,cls='g',fly='right:60px;top:40px;width:150px;height:150px;transform:rotate(10deg)'))
# 5 ah ma: show me video -> aerial slider with play
S.append(page('<div class="k">Question 4</div><div class="ask"><small>ah ma</small>“aiyo so small. got video or not?”</div>'
  '<div class="row2"><div class="tx"><p><b>got.</b> press ▶ on “From above”.</p><p>2012 to now, play like a video.</p>'
  '<p>can even share the timelapse to the family chat 📲</p></div>'
  + ph(f'{SL}/aerial.png','width:440px',(0.03,0.80)) + '</div>'
  + f'<div class="cred2">Real screenshot of the app, Queen’s Arc. {CR}</div>',n=5,N=N,cls='g'))
# 6 CTA
S.append(page('<div class="k">next gathering</div><h1>just pass them <em>ur phone</em></h1>'
  '<p style="font-size:46px;margin-top:50px">1. search ur BTO<br>2. scroll to “From above”<br>3. press ▶</p><p style="font-size:46px">then go eat in peace 🍊</p>'
  '<div><span class="pill">link in bio 🪰</span></div>'
  '<p style="font-size:40px;margin-top:60px">which relative always asks?<br>tag them 👇</p>',
  dark=True,n=6,N=N,fly='right:90px;bottom:200px;width:260px;height:260px;transform:rotate(-8deg)'))
posts={'relatives':S}
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
