
window.renderResonance=function(results){
 const el=document.getElementById('resonanceNodes');
 el.innerHTML='';
 results.forEach(r=>{
   const span=document.createElement('span');
   span.textContent=r.tags.join(', ')+' ';
   el.appendChild(span);
 });
}
