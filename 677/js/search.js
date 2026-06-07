
const resultsEl=document.getElementById('results');
function card(i){return `<div class="card"><h3>${i.title}</h3><p>${i.content}</p><div>${i.tags.map(t=>`<span class='tag'>${t}</span>`).join('')}</div></div>`}
function renderResults(items){resultsEl.innerHTML=items.map(card).join(''); if(window.renderResonance)renderResonance(items)}
document.getElementById('search').addEventListener('input',e=>{
if(!fuse)return; const q=e.target.value.trim();
renderResults(q?fuse.search(q).map(r=>r.item):archive);
});
gridBtn.onclick=()=>resultsEl.className='grid';
tableBtn.onclick=()=>resultsEl.className='table';
