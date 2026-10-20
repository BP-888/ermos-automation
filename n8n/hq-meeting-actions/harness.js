const fs=require('fs');const {DateTime,Settings}=require('luxon');
function run(file, inputItems, nodes, now){
  const ms=now?Date.parse(now):Date.now(); Settings.now=()=>ms;
  const body=fs.readFileSync(file,'utf8').split('// ---8<---')[1];
  const $input={all:()=>inputItems,first:()=>inputItems[0]};
  const $=(n)=>({first:()=>nodes[n][0],all:()=>nodes[n],item:nodes[n][0]});
  return new Function('$input','$','DateTime',body)($input,$,DateTime);
}
module.exports=run;
