const run=require('./harness');const assert=require('assert');
const mcpWrap=(o)=>({content:[{type:'text',text:JSON.stringify(o)}]});
// pick
const found=mcpWrap({meetings:[
 {id:'m1',title:'Team sync',start_time:'2026-10-19T22:00:00Z',end_time:'2026-10-19T23:00:00Z',has_transcript:true,share_link:'https://notes.wisprflow.ai/shared/m1'},
 {id:'m2',title:'Old',start_time:'2026-10-18T22:00:00Z',end_time:'2026-10-18T23:00:00Z',has_transcript:true},
 {id:'m3',title:'No transcript',end_time:'2026-10-19T23:00:00Z',has_transcript:false},
 {id:'m4',title:'Future',end_time:'2099-01-01T00:00:00Z',has_transcript:true}],has_more:false});
const done={results:[{properties:{'Meeting ID':{rich_text:[{plain_text:'m2'}]}}}]};
let p=run('pick.js',[],{'Find meetings':[{json:found}],'Read done meetings':[{json:done}]})[0].json;
assert.deepEqual(p.meetings.map(m=>m.meeting_id),['m1']); assert.equal(p.skipped.length,3);
p=run('pick.js',[],{'Find meetings':[{json:mcpWrap({meetings:[]})}],'Read done meetings':[{json:{results:[]}}]})[0].json; assert.equal(p.count,0);
p=run('pick.js',[],{'Find meetings':[{json:{structuredContent:{meetings:[{id:'m9',title:'Real shape',end_time:'2026-10-19T23:00:00Z',has_transcript:true}]},content:[{type:'text',text:{meetings:[]}}]}}],'Read done meetings':[{json:{results:[]}}]})[0].json; assert.equal(p.count,1);
p=run('pick.js',[],{'Find meetings':[{json:{content:[{type:'text',text:{meetings:[{id:'m8',end_time:'2026-10-19T23:00:00Z',has_transcript:true}]}}]}}],'Read done meetings':[{json:{results:[]}}]})[0].json; assert.equal(p.count,1);
console.log('pick ok');
// assemble
const split=[{json:{meeting_id:'m1',title:'Team sync',start:'2026-10-19T22:00:00Z',share_link:'https://x/m1'}}];
const t1=[{json:mcpWrap({transcript:'[00:01] Brad: Will, can you send the proposal by Friday?\n[00:02] Will: Yes I will. [truncated: continue with start_char=40000]',summary:'Sum'})}];
const t2=[{json:mcpWrap({transcript:'[40:00] David: done.'})}];
const t3=[{json:{error:'out of range'}}];
const who=[{json:mcpWrap({participants:[{name:'Will',relationship:'colleague',spoke:true}]})}];
let a2;
let a=run('assemble.js',[],{'Split meetings':split,'Transcript part 1':t1,'Transcript part 2':t2,'Transcript part 3':t3,'Who was there':who})[0].json;
assert.ok(a.transcript.includes('Yes I will.')&&a.transcript.includes('David: done.')&&!a.transcript.includes('truncated'));
assert.equal(a.transcript_cut,false); assert.equal(a.attendees[0].name,'Will');
a2=run('assemble.js',[],{'Split meetings':split,'Transcript part 1':[{json:{structuredContent:{transcript:'[00:01] hello',summary:'S'}}}],'Transcript part 2':t3,'Transcript part 3':t3,'Who was there':[{json:{structuredContent:{participants:[{name:'Will'}]}}}]})[0].json;
assert.equal(a2.transcript,'[00:01] hello'); assert.equal(a2.attendees[0].name,'Will');
console.log('assemble ok');
// rows
const ai={personal:false,meeting_type:'Team',decisions:['Go with Smartlead'],open_questions:[],parked:[],flags_for_brad:[],actions:[
 {action:'Send the proposal to Mayweathers',owner:'Will',owner_confidence:'Stated',due:'2026-10-24',why:'Brad asked.',done_when:'Proposal in their inbox',considered_dropped:'',timestamp:'00:01'},
 {action:'Book the venue',owner:'David',owner_confidence:'Inferred',due:'Friday',why:'',done_when:'Booked'},
 {action:'Check the numbers',owner:'Speaker 2',owner_confidence:'Stated',why:'x',done_when:'y'},
 {action:'Write the brief',owner:'Brad',owner_confidence:'Stated',why:'x',done_when:'y'}]};
const claude=[{json:{content:[{type:'thinking'},{type:'text',text:JSON.stringify(ai)}]}}];
let rows=run('rows.js',claude,{'Assemble the meeting':[{json:a}]}).map(x=>x.json);
assert.equal(rows.length,5);
assert.equal(rows[0].allocation,'Email drafted'); assert.equal(rows[0].body.properties.Due.date.start,'2026-10-24');
assert.equal(rows[1].allocation,'Needs Brad'); assert.ok(!rows[1].body.properties.Due);
assert.equal(rows[2].owner,'Unassigned'); assert.equal(rows[2].body.properties['Owner confidence'].select.name,'Unassigned');
assert.equal(rows[3].allocation,"Brad's own");
assert.equal(rows[4].kind,'Meeting summary'); assert.ok(rows[4].body.properties.Why.rich_text[0].text.content.includes('Go with Smartlead'));
let bad=run('rows.js',[{json:{content:[{type:'text',text:'oops'}]}}],{'Assemble the meeting':[{json:a}]}).map(x=>x.json);
assert.equal(bad.length,1); assert.ok(bad[0].body.properties.Why.rich_text[0].text.content.includes('did not return readable JSON'));
console.log('rows ok');
// drafts
let d=run('drafts.js',[],{'Build the Notion rows':rows.map(j=>({json:j}))}).map(x=>x.json);
assert.equal(d.length,1); assert.equal(d[0].to,'will@ermos.com.au'); assert.ok(d[0].subject.startsWith('Actions from Team sync, 20 Oct'),d[0].subject);
assert.ok(d[0].message.includes('Due: Sat 24 Oct')); assert.ok(!d[0].message.includes('Book the venue'));
d=run('drafts.js',[],{'Build the Notion rows':[rows[3]].map(j=>({json:j}))}).map(x=>x.json); assert.equal(d[0].none,true);
console.log('drafts ok');
// log
let l=run('malog.js',[],{'Pick new meetings':[{json:{seen:4,skipped:[1,2,3]}}],'Build the Notion rows':rows.map(j=>({json:j})),'Save the row':rows.map(()=>({json:{id:'pg',object:'page'}})),'Draft the email':[{json:{id:'r1'}}]})[0].json;
assert.equal(l.result,'Waiting approval'); assert.ok(l.summary.startsWith('1 meetings processed, 4 actions recorded, 1 email drafts'),l.summary);
console.log('log ok');
console.log('hq-meeting-actions: all tests pass');
