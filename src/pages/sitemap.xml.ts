import type { APIRoute } from 'astro';
const pages = Object.values(import.meta.glob('./guide/*.md',{eager:true}));
export const GET:APIRoute = ({site}) => {
 const paths=['/','/company/','/job/','/guide/', ...pages.filter((p:any)=>['approved', 'conditionally-approved'].includes(p.frontmatter.editorialStatus)).map((p:any)=>p.url)];
 const xml='<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+paths.map(path=>'<url><loc>'+new URL(path,site).toString()+'</loc></url>').join('')+'</urlset>';
 return new Response(xml,{headers:{'Content-Type':'application/xml; charset=utf-8'}});
};

