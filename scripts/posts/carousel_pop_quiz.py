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
SHOTS=pathlib.Path(os.environ.get('SHOTS','/home/claude/shots'))/'2026-11-27'  # from the repo's "screens" branch
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



# The fly's pop quiz: guess the estate from one old satellite photo (multiple choice), answer on the next slide.
# Facts from data.json (checked 27 Nov 2026 10:02): launch month + HDB est. completion, no delay, none on HDB's completed-blocks list.
# Photo dates from meta.json of the 2026-11-27 screenshots. % figures are what the app's own sheets show.
N=7
ASOF='27 Nov 2026'
CR='Imagery: Esri, Vantor, Earthstar Geographics, via World Imagery Wayback.'
CSS+="""
.s.q{padding-top:80px}.s.q h1{font-size:84px;margin-top:14px}
.qimg{width:700px;height:700px;border-radius:36px;display:block;margin:34px auto 0;border:4px solid #3d4475;object-fit:cover}
.opts{display:flex;gap:18px;margin-top:30px;justify-content:center}
.opts div{background:#F7EFE2;color:#3A2C26;border-radius:26px;padding:18px 26px;font:700 36px Fi;white-space:nowrap}
.opts div i{font-style:normal;color:#B0763A;margin-right:10px}
.q .cred{bottom:116px;color:#AFA6CF}
.s.a{padding-top:80px}.s.a h2{font-size:62px;margin:10px 0 0}
.pr.two{justify-content:center;gap:60px}.pr.two div{flex:none;width:400px}.pr.two .arr{right:-60px}
.qsub{font:600 32px Fi;color:#AFA6CF;text-align:center;margin-top:22px}
.pr{display:flex;gap:24px;margin-top:28px}.pr div{flex:1;position:relative}
.pr img{width:100%;border-radius:28px;display:block;border:3px solid #EFE3CF}
.pr b{display:block;font:600 36px Fr;margin-top:10px}.pr span{font:600 24px Fi;color:#7A6658}
.pr .arr{position:absolute;right:-42px;top:var(--t,170px);width:60px;height:60px;border-radius:50%;background:#F2B33D;font:700 36px/60px Fi;text-align:center;z-index:2;color:#3A2C26;font-style:normal}
.btm{display:flex;gap:34px;margin-top:30px;align-items:flex-start}
.btm .fr{flex:none;width:300px;height:400px;border-radius:30px;border:9px solid #1c2040;overflow:hidden;box-shadow:0 14px 34px rgba(0,0,0,.22);background:#fff}
.btm .fr img{width:100%;display:block}
.btm p{margin:0;font-size:36px;line-height:1.38}
.a .cred{bottom:116px}
.tick{display:inline-block;background:#2E9C6B;color:#fff;font:700 30px Fi;padding:10px 22px;border-radius:99px;margin-top:16px}
"""
def meta(sl): return json.load(open(SHOTS/sl/'meta.json'))
def fr(sl,date): return [x for x in meta(sl)['frames'] if x['date']==date][0]
def photos(sl,dates,top=170):
    out=[]
    for k,d in enumerate(dates):
        F=fr(sl,d);arr=f'<i class="arr" style="--t:{top}px">→</i>' if k<len(dates)-1 else ''
        out.append(f'<div><img src="{img(sl+"/"+F["file"],700)}"><b>{d} photo</b><span>{F["rel"]}</span>{arr}</div>')
    return f'<div class="pr{" two" if len(dates)==2 else ""}">'+''.join(out)+'</div>'
def sheet(sl,crop=0.62):
    # top part of the real project page (name, % elapsed, HDB estimate)
    from PIL import Image as I
    im=I.open(SHOTS/sl/'sheet.png').convert('RGB');w,h=im.size;im=im.crop((0,int(h*0.10),w,int(h*0.10)+int(w*4/3)))
    im.thumbnail((600,800));b=io.BytesIO();im.save(b,'JPEG',quality=90)
    return '<div class="fr"><img src="data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()+'"></div>'
def q(sl,date,round_,opts,n,hook=False):
    F=fr(sl,date)
    o=''.join(f'<div><i>{l}</i>{t}</div>' for l,t in zip('ABC',opts))
    head=(f'<div class="k">The fly’s pop quiz 🛰️ · round {round_} of 3</div><h1>which estate is <em>this</em>?</h1>' if hook
          else f'<div class="k">Round {round_} of 3</div><h1 style="font-size:76px">{ {2:"ok this one <em>harder</em>",3:"last round <em>liao</em>"}[round_] }</h1>')
    return page(f'{head}<img class="qimg" src="{img(sl+"/"+F["file"],900)}"><div class="opts">{o}</div><div class="qsub">answer on next slide. no peeking ah 👀</div><div class="cred">{date} satellite photo, as shown in the app. {CR}</div>',
                dark=True,n=n,N=N,cls='q',fly='right:56px;top:40px;width:150px;height:150px;transform:rotate(14deg)')
S=[]
S.append(q('ghim-moh-natura','Jun 2012',1,['Bishan','Ghim Moh','Punggol'],1,hook=True))
S.append(page(f'<div class="k">Answer 1 · B) Ghim Moh</div><h2>old blocks → <em>flat land</em> → new blocks</h2>{photos("ghim-moh-natura",["Jun 2012","Mar 2015","Jul 2025"],120)}'
  f'<div class="btm">{sheet("ghim-moh-natura")}<p>the blocks in the 2012 photo r gone by the Mar 2015 photo. Jul 2025 photo: new blocks going up. that’s <b>Ghim Moh Natura</b>, HDB est. Mar 2028, no delay announced.</p></div>'
  f'<div class="cred">Satellite photos as shown in the app, date on each photo. {CR} Real screenshot of the app’s project page, as of {ASOF}.</div>',n=2,N=N,cls='a'))
S.append(q('rail-green-i-ii-cck','Apr 2012',2,['Sentosa','Marine Parade','Choa Chu Kang'],3))
S.append(page(f'<div class="k">Answer 2 · C) Choa Chu Kang</div><h2>forest → <em>construction site</em></h2>{photos("rail-green-i-ii-cck",["Apr 2012","Aug 2025"],160)}'
  f'<div class="btm">{sheet("rail-green-i-ii-cck")}<p><b>Rail Green I &amp; II @ CCK</b>. launched Oct 2023, HDB est. Sept 2028, no delay announced. someone even shared a site photo in the app 📸</p></div>'
  f'<div class="cred">Satellite photos as shown in the app. {CR} Real screenshot of the app’s project page as of {ASOF}; site photo shared by a TOP Already? user.</div>',n=4,N=N,cls='a'))
S.append(q('tampines-greentopaz','Jun 2012',3,['Clementi','Tampines','Yishun'],5))
S.append(page(f'<div class="k">Answer 3 · B) Tampines</div><h2>field → <em>construction site</em></h2>{photos("tampines-greentopaz",["Jun 2012","Aug 2025"],160)}'
  f'<div class="btm">{sheet("tampines-greentopaz")}<p><b>Tampines GreenTopaz</b>. launched Jun 2024, HDB est. Jun 2028, no delay announced. Aug 2025 photo taken 1.3 yrs after launch.</p></div>'
  f'<div class="cred">Satellite photos as shown in the app. {CR} Real screenshot of the app’s project page, as of {ASOF}.</div>',n=6,N=N,cls='a'))
S.append(page(f'<div class="left"><div class="k">Ur turn</div><h2>quiz ur friends with <em>their</em> BTO</h2><p>search their BTO, scroll to “From above”, drag the slider back to 2012. screenshot. ask “where is this?”</p><p>how many u got? comment ur score 👇</p><div><span class="pill">link in bio 🪰</span></div></div><div class="phone" style="right:60px;top:150px"><img src="{img("rail-green-i-ii-cck/aerial.png",900)}"></div><div class="cred" style="color:#AFA6CF;right:600px;bottom:118px">{CR} Real screenshot of the app, Rail Green I &amp; II @ CCK.</div>',dark=True,n=7,N=N))
posts={'pop-quiz':S}
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
