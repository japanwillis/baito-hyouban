// Read-only regression of all approved articles and category navigation.
import { mkdir, writeFile, readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
const { chromium }=await import(pathToFileURL(process.env.PLAYWRIGHT_MODULE_PATH).href);
const canonicalOrigin='https://baito-hyouban.com';
const origin=process.env.QA_ORIGIN||'http://127.0.0.1:4321';
if(!['http://127.0.0.1:4321',canonicalOrigin].includes(origin))throw Error('Unapproved QA origin');
const approvals=JSON.parse(await readFile('ops/publication-approvals.json','utf8')).articles;
const pages=[['home','/'],['guide','/guide/'],['company','/company/'],['job','/job/'],['search','/search/'],...approvals.map(a=>[a.articleId,a.publicPath])];
const out='responsive-qa-evidence';await mkdir(out,{recursive:true});
// Full accessibility, metadata, image, navigation and overflow checks still cover ALL articles at ALL widths.
// Retain visual evidence at each width for the nine current publication candidates, and a 320px sample for older articles.
// This reduces redundant full-page screenshots and GitHub Actions artifact storage.
const visualSample=new Set(approvals.slice(-9).map(a=>a.articleId));
const legacyVisualSample=new Set(approvals.slice(0,2).map(a=>a.articleId));
const captureScreenshot=(label,width)=>!label.startsWith('BH-')||visualSample.has(label)||(width===320&&legacyVisualSample.has(label));
const browser=await chromium.launch();const results=[];
try{
 for(const width of [320,390,768,1366]){
  const context=await browser.newContext({viewport:{width,height:844},isMobile:width<800,hasTouch:width<800,deviceScaleFactor:1,locale:'ja-JP'});
  await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
  const page=await context.newPage();
  for(const [label,path] of pages){
   const response=await page.goto(origin+path,{waitUntil:'domcontentloaded',timeout:45000});
   // Force lazy images to load even below the fold without a long scroll on every page.
   // The image-ready check below still rejects broken or missing assets at every viewport.
   await page.evaluate(async()=>{document.querySelectorAll('img[loading="lazy"]').forEach(i=>i.loading='eager');await document.fonts.ready;});
   await page.waitForFunction(()=>[...document.images].every(i=>i.closest('[hidden]')||i.complete&&i.naturalWidth>0),null,{timeout:15000}).catch(async()=>{const missing=await page.evaluate(()=>[...document.images].filter(i=>!i.closest('[hidden]')&&(!i.complete||!i.naturalWidth)).map(i=>({src:i.src,complete:i.complete,width:i.naturalWidth})));throw Error(`Image readiness failed at ${label} ${path} width=${width}: ${JSON.stringify(missing)}`)});await page.evaluate(()=>scrollTo(0,0));
   const metrics=await page.evaluate(()=>({width:innerWidth,clientWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,h1:document.querySelectorAll('h1').length,canonical:document.querySelector('link[rel=canonical]')?.href,description:document.querySelector('meta[name=description]')?.content,heroAlt:document.querySelector('.hero-image')?.alt,images:[...document.images].map(i=>({loaded:!!i.closest('[hidden]')||(i.complete&&i.naturalWidth>0),width:i.naturalWidth,height:i.naturalHeight,hidden:!!i.closest('[hidden]')})),tables:[...document.querySelectorAll('table')].map(t=>({rows:t.querySelectorAll('tbody tr').length,cells:t.querySelectorAll('td').length}))}));
   const errors=[];if(response.status()!==200)errors.push(`HTTP ${response.status()}`);if(metrics.width!==width)errors.push('Viewport mismatch');if(metrics.scrollWidth>metrics.clientWidth+1)errors.push('Horizontal overflow');if(metrics.h1!==1||metrics.canonical!==canonicalOrigin+path||!metrics.description)errors.push('Metadata/heading mismatch');if(!metrics.images.every(i=>i.loaded))errors.push('Image failed');if(label.startsWith('BH-')&&!metrics.heroAlt)errors.push('Missing hero alt');if(label.startsWith('BH-')&&!metrics.images.some(i=>i.width===1200&&i.height===630))errors.push('Missing 1200x630 article hero image');
   const screenshot=captureScreenshot(label,width)?`${label}-${width}.jpg`:null;if(screenshot)await page.screenshot({path:`${out}/${screenshot}`,fullPage:true,type:'jpeg',quality:66});results.push({label,path,width,screenshot,metrics,errors});
  }
  // Check every article's category-link presence and filtering, then click one actual link per category.
  // Every article destination is also fully visited and checked above at all four widths.
  const byCategory=new Map();
  for(const a of approvals){
   const category=a.publicPath.startsWith('/company/')?'/company/':a.publicPath.startsWith('/job/')?'/job/':'/guide/';
   if(!byCategory.has(category))byCategory.set(category,[]);
   byCategory.get(category).push(a);
  }
  for(const [category,group] of byCategory){
   await page.goto(origin+category,{waitUntil:'domcontentloaded'});
   const filter=page.locator('#list-search');
   const hasFilter=(await filter.count())>0;
   for(const a of group){
    const target=page.locator(`a.feature-article[href="${a.publicPath}"]`);
    if((await target.count())!==1)throw Error(`Missing/duplicate category link ${a.articleId} ${a.publicPath} at ${width}`);
    if(hasFilter){
     await filter.fill(await target.getAttribute('data-title')||'');
     if(!(await target.isVisible()))throw Error(`Category filter hid article ${a.articleId} at ${width}`);
     await filter.fill('');
    }
    results.push({label:'category-to-article-navigation',articleId:a.articleId,width,errors:[]});
   }
   const first=group[0];
   if(hasFilter)await filter.fill(await page.locator(`a.feature-article[href="${first.publicPath}"]`).getAttribute('data-title')||'');
   await page.locator(`a.feature-article[href="${first.publicPath}"]`).click();
   await page.waitForURL(origin+first.publicPath);
  }
  await page.goto(origin+'/search/',{waitUntil:'domcontentloaded'});
  await page.locator('#article-search').fill('スターバックス');
  const searchTarget=page.locator('a.discovery-item[href="/company/starbucks/"]');
  if(!(await searchTarget.isVisible()))throw Error('Article search failed to reveal Starbucks at width='+width);
  if((await page.locator('a.discovery-item:visible').count())!==1)throw Error('Search unexpectedly returned extra articles at width='+width);
  await searchTarget.click();await page.waitForURL(origin+'/company/starbucks/');
  results.push({label:'keyword-search-navigation',width,errors:[]});
  await page.goto(origin+'/search/',{waitUntil:'domcontentloaded'});
  await page.locator('#article-category').selectOption('企業別');
  const wrongCategory=await page.locator('a.discovery-item[data-category="職種別"]:visible').count();
  if(wrongCategory!==0)throw Error('Category filter displayed wrong category');
  results.push({label:'search-category-filter',width,errors:[]});
  await context.close();
 }
}finally{await browser.close();await writeFile(`${out}/results.json`,JSON.stringify({checkedAt:new Date().toISOString(),environment:'GitHub Actions Chromium; viewport/touch emulation, not physical iPhone/Safari; third-party ads excluded',origin,productionModified:false,approvedArticles:approvals.length,results},null,2));}
const failed=results.filter(x=>x.errors.length);const expected=4*(pages.length+approvals.length+2);console.log(JSON.stringify({checks:results.length,expected,failed:failed.length,results},null,2));if(failed.length||results.length!==expected)process.exitCode=1;
