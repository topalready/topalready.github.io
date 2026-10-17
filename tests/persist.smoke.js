// Closes and reopens a real browser profile to confirm the watchlist and settings survive.
// Run from the folder above the repo: node topalready.github.io/tests/persist.smoke.js
const {chromium}=require('playwright');const fs=require('fs');
const R='topalready.github.io/';
const shots='/tmp/claude-0/ui/';fs.mkdirSync(shots,{recursive:true});
const ago=d=>new Date(Date.now()-d*864e5).toISOString();
const DIR='/tmp/claude-0/profile-persist';require('fs').rmSync(DIR,{recursive:true,force:true});
async function open(origin='https://x.test/'){
  const ctx=await chromium.launchPersistentContext(DIR,{args:['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'],viewport:{width:390,height:844},geolocation:{latitude:1.3778,longitude:103.7625},permissions:['geolocation']});
  await ctx.route('**/*',async r=>{const u=r.request().url();
    if(u.includes('maplibre-gl.min.js'))return r.fulfill({body:fs.readFileSync('node_modules/maplibre-gl/dist/maplibre-gl.js'),contentType:'application/javascript'});
    if(u.includes('maplibre-gl.min.css'))return r.fulfill({body:fs.readFileSync('node_modules/maplibre-gl/dist/maplibre-gl.css'),contentType:'text/css'});
    if(u.match(/^https:\/\/[xy]\.test\/data\.json/))return r.fulfill({body:fs.readFileSync(R+'data.json'),contentType:'application/json'});
    if(u.match(/^https:\/\/[xy]\.test\/icon/))return r.fulfill({body:fs.readFileSync(R+u.split('/').pop().split('?')[0]),contentType:'image/png'});
    if(u.match(/^https:\/\/[xy]\.test\//))return r.fulfill({body:fs.readFileSync(R+'index.html'),contentType:'text/html'});
    if(u.includes('supabase.co')){if(r.request().method()==='POST')return r.fulfill({status:201,body:''});if(u.includes('storage/v1/object/public'))return r.fulfill({body:fs.readFileSync(R+'icon-192.png'),contentType:'image/png'});return r.fulfill({body:'[]',contentType:'application/json'})}
    return r.fulfill({status:404,body:''})});
  const pg=ctx.pages()[0]||await ctx.newPage();const errs=[];pg.on('pageerror',e=>errs.push(e.message));
  await pg.goto(origin);await pg.waitForTimeout(2500);return {ctx,pg,errs};
}
const snap=pg=>pg.evaluate(()=>{const ls={};for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.startsWith('storeys'))ls[k]=localStorage.getItem(k)}
  return{ls,watch:tracked.slice(),light:LIGHT,welcomeHidden:$('#welcome').hidden,found:found.size}});
(async()=>{
 // ---- session 1: earn things ----
 let {ctx,pg,errs}=await open();
 await pg.evaluate(async()=>{hideWelcome();
   tracked=[P.find(p=>p.name==='Bangkit Breeze').key];saveTracked();
   LIGHT='night';localStorage.setItem('storeys.light','night');
   store('storeys.reported',['abc']);found.add(P[0].key);store(FOUND_KEY,[...found]);
 });
 await pg.waitForTimeout(500);const before=await snap(pg);
 console.log('SESSION 1 saved keys:',Object.keys(before.ls).join(', '));
 console.log('  errors',JSON.stringify(errs));
 await ctx.close(); // full browser shutdown
 // ---- session 2: reopen same browser profile ----
 ({ctx,pg,errs}=await open());const after=await snap(pg);
 const same=k=>JSON.stringify(before[k])===JSON.stringify(after[k]);
 for(const k of Object.keys(before.ls))console.log((before.ls[k]===after.ls[k]?'PASS ':'FAIL ')+'kept '+k);
 for(const k of ['watch','light','welcomeHidden','found'])console.log((same(k)?'PASS ':'FAIL ')+k+' = '+JSON.stringify(after[k]));
 // ---- different origin (like a custom domain) ----
 const p2=await ctx.newPage();await p2.goto('https://y.test/');await p2.waitForTimeout(2000);const other=await snap(p2);
 console.log('OTHER ORIGIN y.test sees: watch',other.watch.length,'keys',Object.keys(other.ls).length);
 // ---- clearing site data ----
 await pg.evaluate(()=>localStorage.clear());await pg.reload();await pg.waitForTimeout(2000);const cleared=await snap(pg);
 console.log('AFTER CLEARING SITE DATA: watch',cleared.watch.length);
 console.log('persist() granted?',await pg.evaluate(async()=>navigator.storage&&navigator.storage.persisted?await navigator.storage.persisted():'n/a'));
 await ctx.close();
})();
