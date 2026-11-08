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
posts={
'keys_before_cny':[
 page('<div class="k">BTO check 🧧</div><h1>keys before <em>CNY</em> or not?</h1><p>these BTOs are estimated to finish around end-2026. the fly went to check 👀</p>',n=1,N=4,fly='right:70px;bottom:170px;transform:rotate(12deg)'),
 page('<div class="k">Estimated Dec 2026</div><h2>almost there</h2>'+bto('Towner Residences',2,3,'Dec 2026')+bto('Kent Heights',1,2,'Dec 2026')+bto('Lakeside View',3,11,'Dec 2026')+bto('Keat Hong Grange',0,0,'Dec 2026')+SRC,n=2,N=4),
 page('<div class="k">Past the estimate</div><h2>still finishing up</h2>'+bto('Bishan Ridges',6,7,'Oct 2026, after delay')+bto('Kovan Wellspring',4,6,'Sep 2026')+bto('Heart of Yew Tee',0,0,'Sep 2026')+SRC,n=3,N=4),
 page('<div class="k">Yours not here?</div><h1>search your <em>BTO</em> or condo</h1><p>blocks completed, delays, satellite photos since 2012. free, no ads, no login.</p><div><span class="pill">topalready.github.io</span></div>',dark=True,n=4,N=4,fly='right:80px;bottom:150px;transform:rotate(-10deg)'),
],
'stages_of_waiting':[
 page('<div class="k">BTO life</div><h1>the 5 stages of waiting for your <em>BTO</em></h1><p>which stage are you at? 👇</p>',n=1,N=7,fly='right:60px;bottom:170px;transform:rotate(14deg)'),
 page('<div class="k">Stage 1</div><h2>ballot success 🎉</h2><p>"wah finally. got house liao"</p><div class="big">🥳</div>',n=2,N=7,cls='st'),
 page('<div class="k">Stage 2</div><h2>see the completion date</h2><p>"wait... 2030 ah?"</p><div class="big">🫠</div>',n=3,N=7,cls='st'),
 page('<div class="k">Stage 3</div><h2>the group chat era</h2><p>"anyone pass by the site today?" × 500 messages</p><div class="big">📱</div>',n=4,N=7,cls='st'),
 page('<div class="k">Stage 4</div><h2>"may delay up to 4 months"</h2><p>reading it 10 times hoping it changes</p><div class="big">😶</div>',n=5,N=7,cls='st'),
 page('<div class="k">Stage 5</div><h2>checking every night at 2am</h2><p>"TOP already or not??"</p><div class="big">🌙</div>',dark=True,n=6,N=7,cls='st'),
 page('<div class="k">Skip the 2am checks</div><h1>let the <em>fly</em> check for you</h1><p>every BTO & new condo. blocks completed from HDB’s list, checked daily. free, no login.</p><div><span class="pill">topalready.github.io</span></div>',dark=True,n=7,N=7,fly='right:80px;bottom:150px;transform:rotate(-10deg)'),
]}
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
