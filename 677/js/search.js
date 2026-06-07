
const resultsEl=document.getElementById('results');

function renderResults(items){
 resultsEl.innerHTML='';
 items.forEach(item=>{
   const div=document.createElement('div');
   div.className='card';
   div.innerHTML=`<h3>${item.title}</h3><p>${item.content}</p>`;
   resultsEl.appendChild(div);
 });
 if(window.renderResonance) renderResonance(items);
}

document.addEventListener('input',e=>{
 if(e.target.id==='search'){
  const q=e.target.value.toLowerCase();
  renderResults(archive.filter(x=>
   x.title.toLowerCase().includes(q)||
   x.content.toLowerCase().includes(q)||
   x.tags.join(' ').toLowerCase().includes(q)
  ));
 }
});

gridBtn.onclick=()=>resultsEl.className='grid';
tableBtn.onclick=()=>resultsEl.className='table';
