// Read-only regression of all approved articles and category navigation.
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
const { chromium }=await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE_PATH).href);
const canonicalOrigin='https://baito-hyouban.com';
const origin=process.env.QA_ORIGIN||'http://127.0.0.1:4321';
if(!['http://127.0.0.1:4321',canonicalOrigin].includes(origin))throw Error('Unapproved QA origin');
const approvals=JSON.parse(await readFile('ops/publication-approvals.json','utf8')).articles;
const pages=[['home','/'],['guide','/guide/'],['company','/company/'],['job','/job/'],...approvals.map(a=>[a.articleId,a.publicPath])];
const out='responsive-qa-evidence';await mkdir(out,{recursive:true});
const browser=await chromium.launch();const results=[];
try{
 for(const width of [320,390,768,1366]){
  const context=await browser.newContext({viewport:{width,height:844},isMobile:width<800,hasTouch:width<800,deviceScaleFactor:1,locale:'ja-JP'});
  await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
  const page=await context.newPage();
  for(const [label,path] of pages){
   const response=await page.goto(origin+path,{waitUntil:'networkidle',timeout:45000});
   await page.evaluate(async()=>{await document.fonts.ready;});await page.evaluate(async()=>{const height=document.documentElement.scrollHeight;const step=Math.max(350,Math.floor(innerHeight*0.75));for(let y=0;y<height;y+=step){scrollTo(0,y);await new Promise(resolve=>setTimeout(resolve,40));}scrollTo(0,height);});await page.locator('footer').scrollIntoViewIfNeeded();
   await page.waitForFunction(()=>[...document.images].every(i=>i.complete&&i.naturalWidth>0),null,{timeout:15000}).catch(async()=>{const missing=await page.evaluate(()=>[...document.images].filter(i=>!i.complete||!i.naturalWidth).map(i=>({src:i.src,complete:i.complete,width:i.naturalWidth})));throw Error(`Image readiness failed at ${label} ${path} width=${width}: ${JSON.stringify(missing)}`)});await page.evaluate(()=>scrollTo(0,0));
   const metrics=await page.evaluate(()=>({width:innerWidth,clientWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,h1:document.querySelectorAll('h1').length,canonical:document.querySelector('link[rel=canonical]')?.href,description:document.querySelector('meta[name=description]')?.content,heroAlt:document.querySelector('.hero-image')?.alt,images:[...document.images].map(i=>({loaded:i.complete&&i.naturalWidth>0,width:i.naturalWidth,height:i.naturalHeight})),tables:[...document.querySelectorAll('table')].map(t=>({rows:t.querySelectorAll('tbody tr').length,cells:t.querySelectorAll('td').length}))}));
   const errors=[];if(response.status()!==200)errors.push(`HTTP ${response.status()}`);if(metrics.width!==width)errors.push('Viewport mismatch');if(metrics.scrollWidth>metrics.clientWidth+1)errors.push('Horizontal overflow');if(metrics.h1!==1||metrics.canonical!==canonicalOrigin+path||!metrics.description)errors.push('Metadata/heading mismatch');if(!metrics.images.every(i=>i.loaded))errors.push('Image failed');if(label.startsWith('BH-')&&!metrics.heroAlt)errors.push('Missing hero alt');if(label.startsWith('BH-')&&!metrics.images.some(i=>i.width===1200&&i.height===630))errors.push('Missing 1200x630 article hero image');
   const screenshot=`${label}-${width}.jpg`;await page.screenshot({path:`${out}/${screenshot}`,fullPage:true,type:'jpeg',quality:90});results.push({label,path,width,screenshot,metrics,errors});
  }
  for(const a of approvals){
   const category=a.publicPath.startsWith('/company/')?'/company/':a.publicPath.startsWith('/job/')?'/job/':'/guide/';await page.goto(origin+category,{waitUntil:'networkidle'});await page.locator(`a.feature-article[href="${a.publicPath}"]`).click();await page.waitForURL(origin+a.publicPath);results.push({label:'category-to-article-navigation',articleId:a.articleId,width,errors:[]});
  }
  await context.close();
 }
}finally{await browser.close();await writeFile(`${out}/results.json`,JSON.stringify({checkedAt:new Date().toISOString(),environment:'GitHub Actions Chromium; viewport/touch emulation, not physical iPhone/Safari; third-party ads excluded',origin,productionModified:false,approvedArticles:approvals.length,results},null,2));}
const failed=results.filter(x=>x.errors.length);const expected=4*(pages.length+approvals.length);console.log(JSON.stringify({checks:results.length,expected,failed:failed.length,results},null,2));if(failed.length||results.length!==expected)process.exitCode=1;
