
let archive=[];
fetch('archive-index.json')
.then(r=>r.json())
.then(data=>{
 archive=data;
 renderResults(data);
});
