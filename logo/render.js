const {chromium}=require('playwright');(async()=>{const b=await chromium.launch();const p=await b.newPage({deviceScaleFactor:1,viewport:{width:1024,height:1100}});
for(const n of ['toy-driver-logo','toy-driver-logo-dark','toy-driver-icon']){await p.goto('file://'+__dirname+'/'+n+'.svg');await p.waitForTimeout(1500);await p.screenshot({path:__dirname+'/'+n+'.png',fullPage:false,clip:{x:0,y:0,width:1024,height:n.includes('icon')?1024:1100}});}
await b.close();})();
