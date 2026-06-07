
function overlap(a,b){return a.filter(x=>b.includes(x)).length}
window.renderResonance=(results)=>{
const out=[];
archive.forEach(a=>{
let s=0;results.forEach(r=>s+=overlap(a.tags,r.tags));
if(s>0)out.push({a,s});
});
out.sort((x,y)=>y.s-x.s);
resonanceNodes.innerHTML=out.slice(0,12).map(x=>`<div class='res'>${x.a.title} · ${x.s}</div>`).join('');
}
