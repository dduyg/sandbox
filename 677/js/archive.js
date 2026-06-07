
let archive=[];let fuse;
fetch('archive-index.json').then(r=>r.json()).then(data=>{
archive=data;
fuse=new Fuse(data,{keys:['title','content','tags'],threshold:.35});
renderResults(data);renderGraph(data);
});
