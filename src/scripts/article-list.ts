const input=document.querySelector<HTMLInputElement>('#list-search');
const cards=Array.from(document.querySelectorAll<HTMLElement>('.list-item'));
const count=document.querySelector<HTMLElement>('#list-count');
const more=document.querySelector<HTMLButtonElement>('#list-more');
const empty=document.querySelector<HTMLElement>('#list-empty');
let limit=12;
const norm=(s:string)=>s.normalize('NFKC').toLocaleLowerCase('ja').replace(/\s+/g,' ').trim();
function render(){
 const terms=norm(input?.value||'').split(' ').filter(Boolean);
 let matches=0;
 for(const el of cards){
  const text=norm((el.dataset.title||'')+' '+(el.dataset.description||''));
  const found=terms.every(t=>text.includes(t));
  if(found)matches++;
  el.hidden=!found||matches>limit;
  el.style.display=el.hidden?'none':'';
 }
 if(count)count.textContent=matches+'件の記事';
 if(more)more.hidden=matches<=limit;
 if(empty)empty.hidden=matches!==0;
}
input?.addEventListener('input',()=>{limit=12;render()});
more?.addEventListener('click',()=>{limit+=12;render()});
render();
