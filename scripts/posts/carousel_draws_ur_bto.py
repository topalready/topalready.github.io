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
SHOTS=pathlib.Path(os.environ.get('SHOTS','/home/claude/shots'))/'2026-11-19'  # from the repo's "screens" branch
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




# Format (g): the app's own illustration and the fly. The drawing on each project page grows with the
# share of the estimated timeline that has passed (it says so on the page: "Illustration of the estimated timeline",
# "doesn't measure work on site"). Facts, all from data.json / overrides.json as read on 19 Nov 2026 (checked 2026-11-19 10:02):
#  Chencharu Acres  BTO, launch 2026-11, est 2030-12 -> 1% of estimated timeline (as shown in the app)
#  Jurong West Crystal BTO, launch 2023-02, est 2027-09 -> 83%
#  MacPherson Weave BTO, data["hdb"] = [7, 8, 2025] -> 7 of 8 blocks completed; est whole project Sept 2027 (delayed date)
#  Hillock Green  condo, overrides.json top 2026-09 ("owners and agent listings") -> app shows "TOP obtained, Sept 2026"
# Satellite: Jurong West Crystal Jun 2012 + May 2025 photos (dates from meta.json).
CSS+="""
.g4{display:grid;grid-template-columns:1fr 1fr;gap:22px 34px;margin:36px auto 0;width:760px}
.g4 figure{margin:0}.g4 img{width:100%;border-radius:28px;display:block;border:3px solid #EFE3CF}
.g4 figcaption{font:700 34px Fi;margin-top:8px;text-align:center}.g4 figcaption span{display:block;font:600 26px Fi;color:#7A6658}
.mood{margin-top:34px;background:#fff;border:2px solid #EFE3CF;border-radius:30px;padding:24px 30px;font:600 36px/1.3 Fi;color:#3A2C26}
.mood small{display:block;font:700 24px Fi;letter-spacing:.08em;text-transform:uppercase;color:#B0763A;margin-bottom:6px}
.dark .mood{background:#323873;border-color:#3d4475;color:#F7EFE2}.dark .mood small{color:#FFD36E}
.asof{font:600 26px Fi;color:#9A8B7E;margin-top:22px}.dark .asof{color:#AFA6CF}
.pair{display:flex;gap:26px;margin-top:40px}
.pair figure{margin:0;flex:1}
.pair img{width:100%;aspect-ratio:1;border-radius:32px;display:block;border:4px solid #3d4475}
.pair figcaption{font:700 40px Fi;color:#FFD36E;margin-top:16px;text-align:center}
.s.sat .cred{bottom:118px}.dark .cred{color:#AFA6CF}
.facts{font:600 38px/1.4 Fi;margin-top:34px;color:#F7EFE2}.facts b{color:#FFD36E}
.num{font:600 150px/1 Fr;color:#E39A2A;margin-top:24px}.num small{font:600 40px Fi;color:#7A6658;display:block;margin-top:8px}
"""
from PIL import Image as PI
def crop(slug,w=700):
    im=PI.open(SHOTS/slug/'sheet.png').convert('RGB').crop((36,440,1134,1230));im.thumbnail((w,w));b=io.BytesIO();im.save(b,'JPEG',quality=90)
    return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
CR='Imagery: Esri, Vantor, Earthstar Geographics, via World Imagery Wayback'
m=json.load(open(SHOTS/'jurong-west-crystal'/'meta.json'));CR=m.get('credit') or CR;F={f['date']:f for f in m['frames']}
N=7;P=[];AS='as of 19 Nov 2026'
def phone_slide(slug,k,name,numhtml,line,mood,n,fly=None):
    return page(f'<div class="left" style="max-width:450px"><div class="k">{k}</div><h2 style="font-size:66px">{name}</h2>{numhtml}<p style="font-size:34px;margin-top:20px">{line}</p>'
      f'<div class="mood"><small>owner mood</small>{mood}</div><div class="asof">{AS}</div></div>'
      f'<div class="phone" style="right:60px;top:110px;width:450px"><img src="{img(slug+"/sheet.png",900)}"></div>',n=n,N=N,fly=fly)
cells=[('chencharu-acres','1%','of est. timeline'),('jurong-west-crystal','83%','of est. timeline'),('macpherson-weave','7 of 8','blocks done (HDB)'),('hillock-green','TOP','obtained (condo)')]
g=''.join(f'<figure><img src="{crop(s,520)}"><figcaption>{a}<span>{b}</span></figcaption></figure>' for s,a,b in cells)
P.append(page(f'<div class="k">real screenshots · {AS}</div><h1 style="font-size:78px;max-width:800px">the app <em>draws</em> ur BTO. more time pass, more floors</h1><div class="g4">{g}</div>',n=1,N=N,fly='right:40px;top:40px;width:170px;height:170px;transform:rotate(14deg)'))
P.append(phone_slide('chencharu-acres','just launched','Chencharu Acres','<div class="num">1%<small>of est. timeline passed</small></div>','launched Nov 2026. HDB est. completion Dec 2030.','still saving tiles on pinterest. got time 😌',2))
P.append(phone_slide('jurong-west-crystal','getting tall','Jurong West Crystal','<div class="num">83%<small>of est. timeline passed</small></div>','HDB est. completion Sept 2027.','group chat suddenly very active',3))
P.append(phone_slide('macpherson-weave','almost there','MacPherson Weave','<div class="num">7 of 8<small>blocks completed, HDB’s own list</small></div>','once HDB’s list shows blocks done, the app shows the real count. est. whole project Sept 2027.','which block ah. WHICH BLOCK',4))
P.append(phone_slide('hillock-green','lights on','Hillock Green','<div class="num" style="font-size:120px">TOP<small>obtained Sept 2026 (condo)</small></div>','reported by owners and agent listings. in the drawing, the windows light up at night 🌙','choosing curtains for 3 weeks liao',5))
a,b=F['Jun 2012'],F['May 2025']
P.append(page(f'<div class="k">ok but real talk</div><h2 style="font-size:66px">the drawing is <em>maths</em>, not a photo. for the real thing:</h2><div class="pair"><figure><img src="{img("jurong-west-crystal/"+a["file"],700)}"><figcaption>{a["date"]} photo</figcaption></figure><figure><img src="{img("jurong-west-crystal/"+b["file"],700)}"><figcaption>{b["date"]} photo</figcaption></figure></div>'
  f'<div class="facts">Jurong West Crystal, same spot. scroll to <b>“From above”</b> in the app</div><div class="cred">{CR}.</div>',dark=True,n=6,N=N,cls='sat'))
P.append(page(f'<div class="left"><h2>what floor is <em>ur</em> BTO at?</h2><p>search ur BTO. see the drawing, then scroll to “From above” for real satellite photos.</p><p>free, no login 🪰</p><div><span class="pill">link in bio</span></div></div>'
  f'<div class="phone" style="right:64px;top:170px"><img src="{img("macpherson-weave/map.png",900)}"></div>',n=N,N=N,fly='left:110px;bottom:140px;width:200px;height:200px;transform:rotate(8deg)'))
posts={'draws_ur_bto':P}
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
