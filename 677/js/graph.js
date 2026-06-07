
function renderGraph(data){
const svg=d3.select('#graph'); const w=900,h=500;
svg.attr('viewBox',[0,0,w,h]);
const nodes=data.map(d=>({id:d.id,label:d.title}));
const links=[];
for(let i=0;i<data.length-1;i++) links.push({source:data[i].id,target:data[i+1].id});
const sim=d3.forceSimulation(nodes).force('link',d3.forceLink(links).id(d=>d.id))
.force('charge',d3.forceManyBody().strength(-120)).force('center',d3.forceCenter(w/2,h/2));
const line=svg.append('g').selectAll('line').data(links).enter().append('line');
const node=svg.append('g').selectAll('circle').data(nodes).enter().append('circle').attr('r',8);
sim.on('tick',()=>{
line.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y).attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
node.attr('cx',d=>d.x).attr('cy',d=>d.y);
});
}
graphBtn.onclick=()=>document.getElementById('graphView').hidden=!document.getElementById('graphView').hidden;
