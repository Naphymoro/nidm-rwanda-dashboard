'use strict';
// NDIM chat: conversations over the local scientific engine. Each message plans one experiment;
// runs that share a thread_id form one conversation. Replies are written from real tool outputs.
const $ = id => document.getElementById(id);
const config = window.NDIM_ENGINE || {};
const routes = config.routes || {studio:'/', workbench:'/workbench', academy:'/academy'};

// Static (Cloudflare Pages) builds have no backend of their own: the engine URL comes from ?api= or the last one used.
function resolveApiBase(){
  if(!config.static)return '';
  const key='ndim-api-base';
  const store=(action,value)=>{try{return action==='get'?localStorage.getItem(key)||'':value?localStorage.setItem(key,value):localStorage.removeItem(key);}catch{return '';}};
  const raw=new URLSearchParams(location.search).get('api');
  if(raw===null)return store('get');
  try{
    const url=new URL(raw);
    if(!/^https?:$/.test(url.protocol))throw Error('protocol');
    const value=url.origin+url.pathname.replace(/\/+$/,'');
    store('set',value);
    return value;
  }catch{store('set','');return '';}
}
const apiBase = resolveApiBase();
const ACTIVE = new Set(['queued','running','cancelling']);
const SKILLS = [
  {id:'auto', name:'Auto', desc:'NDIM picks a skill from your question'},
  {id:'evidence', name:'Evidence interpretation', desc:'Trust, barriers and narrative risks in the evidence'},
  {id:'scenario', name:'Scenario comparison', desc:'An intervention against a matched baseline'},
  {id:'sensitivity', name:'Sensitivity experiment', desc:'Sweep intervention strength across a grid'},
];
const DEFAULTS = {model:'compartmental', profile:'auto', horizon_days:90, intervention_strength:.3, initial_adoption:.1, narrative_influence:.38, language:'en', expertise:'guided'};
const state = {workspace:'', threads:[], threadId:null, runs:[], local:[], evidence:null, skill:'auto', lesson:null, pending:null,
  settings:{...DEFAULTS}, autorun:false, lessons:[], sample:'', online:false, busy:false, poll:null, gen:0, open:new Map(), reviewing:new Set(), capacity:null};

// ---------- helpers ----------
function el(tag, props={}, ...children){
  const node=document.createElement(tag);
  for(const [key,value] of Object.entries(props)){
    if(value===undefined||value===null||value===false)continue;
    if(key==='class')node.className=value;
    else if(key==='text')node.textContent=value;
    else if(key.startsWith('on'))node.addEventListener(key.slice(2),value);
    else node.setAttribute(key,value===true?'':value);
  }
  for(const child of children.flat()){if(child!==null&&child!==undefined&&child!==false)node.append(child);}
  return node;
}
function icon(name,cls){const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');if(cls)svg.setAttribute('class',cls);svg.setAttribute('aria-hidden','true');const use=document.createElementNS('http://www.w3.org/2000/svg','use');use.setAttribute('href','#i-'+name);svg.append(use);return svg;}
function svgNode(tag,attrs){const node=document.createElementNS('http://www.w3.org/2000/svg',tag);Object.entries(attrs).forEach(([k,v])=>node.setAttribute(k,v));return node;}
const fmt = value => Number.isFinite(value) ? value.toFixed(3) : '—';
const human = value => String(value??'').replace(/_/g,' ');
const skillName = id => (SKILLS.find(skill=>skill.id===id)||{name:human(id)}).name;
const newId = () => (crypto.randomUUID ? crypto.randomUUID() : Array.from(crypto.getRandomValues(new Uint8Array(16)),b=>b.toString(16).padStart(2,'0')).join(''));
const finalAdoption = output => output?.trajectory?.at(-1)?.adoption;

async function api(url,options={}){
  const response=await fetch(apiBase+url,{...options,headers:{'Content-Type':'application/json',...options.headers}});
  if(!response.ok){
    let message=`The engine returned ${response.status}. Please retry.`;
    try{const data=await response.json();if(typeof data.detail==='string')message=data.detail;else if(Array.isArray(data.detail))message=data.detail.map(item=>item.msg||String(item)).join('; ');}catch{}
    throw Error(message);
  }
  return response.status===204?null:response.json();
}
const runsURL = (id) => `/engine/workspaces/${encodeURIComponent(state.workspace)}/runs${id?'/'+encodeURIComponent(id):''}`;
function pageURL(target){
  const params=new URLSearchParams();
  if(state.workspace)params.set('workspace',state.workspace);
  if(target==='studio'&&state.threadId&&state.runs.length)params.set('chat',state.threadId);
  if(apiBase)params.set('api',apiBase);
  const query=params.toString();
  return routes[target]+(query?'?'+query:'');
}
function syncLinks(){document.querySelectorAll('[data-route]').forEach(link=>link.href=pageURL(link.dataset.route));}
function setURL(){history.replaceState(null,'',pageURL('studio'));syncLinks();}
function scrollToEnd(){requestAnimationFrame(()=>{$('scroller').scrollTop=$('scroller').scrollHeight;});}
function nearEnd(){const s=$('scroller');return s.scrollHeight-s.scrollTop-s.clientHeight<160;}

// ---------- sidebar: conversations ----------
function groupThreads(rows){
  const map=new Map();
  for(const row of rows){
    const id=row.thread_id||row.run_id;
    if(!map.has(id))map.set(id,{id,runs:[]});
    map.get(id).runs.push(row);
  }
  return [...map.values()].map(thread=>{
    thread.runs.sort((a,b)=>a.created_at.localeCompare(b.created_at));
    thread.title=thread.runs[0].title;
    thread.updated=thread.runs.reduce((latest,run)=>run.updated_at>latest?run.updated_at:latest,'');
    thread.active=thread.runs.some(run=>ACTIVE.has(run.status));
    return thread;
  }).sort((a,b)=>b.updated.localeCompare(a.updated));
}
function bucket(iso){
  const day=86400000, start=new Date();start.setHours(0,0,0,0);
  const t=new Date(iso).getTime();
  if(t>=start.getTime())return 'Today';
  if(t>=start.getTime()-day)return 'Yesterday';
  if(t>=start.getTime()-7*day)return 'Previous 7 days';
  return 'Older';
}
function renderThreads(){
  const box=$('threads');box.replaceChildren();
  if(!state.threads.length){box.append(el('p',{class:'sb-empty',text:state.online?'No chats yet. Start one on the right.':'Chats appear here once the engine is connected.'}));return;}
  let current='';
  for(const thread of state.threads){
    const group=bucket(thread.updated);
    if(group!==current){box.append(el('div',{class:'thread-group',text:group}));current=group;}
    box.append(el('div',{class:'thread-item'+(thread.id===state.threadId?' active':'')},
      el('button',{type:'button',title:thread.title,'aria-current':thread.id===state.threadId?'page':null,onclick:()=>openThread(thread.id)},thread.active?el('i',{class:'live','aria-label':'Running'}):null,el('span',{text:thread.title})),
      el('button',{type:'button',class:'icon-btn del','aria-label':'Delete chat: '+thread.title,title:'Delete chat',onclick:()=>deleteThread(thread)},icon('trash'))));
  }
}
async function loadThreads(){
  if(!state.online)return;
  try{const data=await api(runsURL()+'?offset=0&limit=100');state.threads=groupThreads(data.runs);renderThreads();}
  catch(err){console.warn(err);}
}
async function deleteThread(thread){
  if(!confirm(`Delete “${thread.title}” and its ${thread.runs.length} experiment${thread.runs.length>1?'s':''}? Downloaded copies remain.`))return;
  try{
    for(const run of thread.runs)await api(runsURL(run.run_id),{method:'DELETE'});
    if(thread.id===state.threadId)newChat();
  }catch(err){pushLocal({role:'ai',tone:'error',text:err.message});}
  loadThreads();
}

// ---------- conversation state ----------
function closeSidebarOnMobile(){if(matchMedia('(max-width:820px)').matches)setSidebar(false);}
function newChat(){
  stopPoll();state.gen++;
  Object.assign(state,{threadId:null,runs:[],local:[],evidence:null,lesson:null,pending:null,skill:'auto'});
  state.open.clear();state.reviewing.clear();
  render();setURL();closeSidebarOnMobile();$('prompt').focus();
}
async function openThread(id){
  stopPoll();const gen=++state.gen;
  const thread=state.threads.find(item=>item.id===id);
  if(!thread){pushLocal({role:'ai',tone:'error',text:'That chat is not in this project any more.'});return;}
  try{
    const runs=await Promise.all(thread.runs.map(row=>api(runsURL(row.run_id))));
    if(gen!==state.gen)return;
    runs.sort((a,b)=>a.created_at.localeCompare(b.created_at));
    const last=runs.at(-1);
    Object.assign(state,{threadId:id,runs,local:[],lesson:null,pending:null,skill:'auto',
      evidence:{text:last.evidence,name:last.context.source_name,consent:last.context.consent,fromChat:true}});
    const request=last.request;
    state.settings={...DEFAULTS,...Object.fromEntries(Object.keys(DEFAULTS).map(key=>[key,request[key]??DEFAULTS[key]]))};
    state.open.clear();state.reviewing.clear();
    writeSettings();render();setURL();closeSidebarOnMobile();
    $('scroller').style.scrollBehavior='auto';$('scroller').scrollTop=$('scroller').scrollHeight;$('scroller').style.scrollBehavior='';
    const active=runs.find(run=>ACTIVE.has(run.status));
    if(active)poll(active.run_id);
  }catch(err){if(gen===state.gen)pushLocal({role:'ai',tone:'error',text:err.message});}
}
function pushLocal(message){state.local.push(message);renderMessages();scrollToEnd();}

// ---------- rendering ----------
function render(){
  $('main').classList.toggle('empty',!state.runs.length&&!state.local.length);
  $('chat-title').textContent=state.runs[0]?.title||'New chat';
  document.title='NDIM · '+(state.runs[0]?.title||'Research chat');
  renderMessages();renderAttachments();renderSkill();renderThreads();
}
function renderMessages(){
  $('main').classList.toggle('empty',!state.runs.length&&!state.local.length);
  $('thread').replaceChildren(...state.runs.map((run,index)=>turn(run,state.runs[index-1])),...state.local.map(localMessage));
}
function updateTurn(run){
  const index=state.runs.findIndex(item=>item.run_id===run.run_id);
  if(index<0)return;
  state.runs[index]=run;
  const old=$('thread').querySelector(`[data-run="${run.run_id}"]`);
  const follow=nearEnd();
  const fresh=turn(run,state.runs[index-1]);
  if(old){
    const focused=document.activeElement&&old.contains(document.activeElement)?document.activeElement.dataset.keep:null;
    const draft=old.querySelector('textarea[data-keep]')?.value;
    old.replaceWith(fresh);
    if(draft!==undefined){const area=fresh.querySelector('textarea[data-keep]');if(area)area.value=draft;}
    if(focused)fresh.querySelector(`[data-keep="${focused}"]`)?.focus();
  }else renderMessages();
  if(follow)scrollToEnd();
}
function remembered(key,fallback){return state.open.has(key)?state.open.get(key):fallback;}
function disclosure(cls,key,fallback,summary,...content){
  const details=el('details',{class:cls});
  details.open=remembered(key,fallback);
  // Only a person's click is remembered; setting .open programmatically also fires 'toggle'.
  details.append(el('summary',{onclick:()=>state.open.set(key,!details.open)},...[summary].flat()),...content);
  return details;
}
function attachmentChip(ev,{onEdit,onRemove,note='',compact=false}={}){
  return el('div',{class:'attach'+(compact?' compact':''),title:compact?`${ev.name} · ${ev.text.length.toLocaleString()} characters`:null},
    el('span',{class:'ico'},icon('file')),
    el('span',{},el('b',{text:ev.name}),el('small',{text:`${ev.text.length.toLocaleString()} characters${note?' · '+note:''}`})),
    onEdit?el('button',{type:'button','aria-label':'Edit evidence',title:'Edit evidence',onclick:onEdit},icon('pencil')):null,
    onRemove?el('button',{type:'button','aria-label':'Remove evidence',title:'Remove evidence',onclick:onRemove},icon('x')):null);
}

function turn(run,previous){
  const lesson=state.lessons.find(item=>item.id===run.lesson_id);
  const tags=[];
  if(run.request.skill!=='auto')tags.push(el('span',{class:'tag',text:skillName(run.request.skill)}));
  if(lesson)tags.push(el('span',{class:'tag',text:`Lab ${lesson.number}`}));
  const showEvidence=!previous||previous.evidence!==run.evidence;
  const user=el('div',{class:'msg user'},el('div',{class:'bubble'},
    showEvidence?el('div',{},attachmentChip({text:run.evidence,name:run.context.source_name})):null,
    el('p',{text:run.request.question}),
    tags.length?el('div',{class:'tags'},tags):null));
  const body=el('div',{class:'ai-body'});
  body.append(skillLine(run),stepsBlock(run));
  if(run.blockers.length)body.append(callout('error','alert',run.blockers.join(' ')));
  if(run.status==='planned')body.append(...plannedReply(run));
  else if(ACTIVE.has(run.status))body.append(el('div',{class:'actions'},el('button',{type:'button',class:'btn',disabled:run.status==='cancelling'||state.busy,onclick:()=>act(run,'cancel')},icon('stop'),run.status==='cancelling'?'Stopping…':'Stop')));
  else if(run.status==='completed')body.append(...completedReply(run,lesson));
  else body.append(...stoppedReply(run));
  return el('section',{class:'turn','data-run':run.run_id},user,el('div',{class:'msg ai'},el('span',{class:'avatar','aria-hidden':'true'},'n',el('span',{text:'·'})),body));
}
function skillLine(run){
  const bits=[el('span',{class:'skill'},icon('spark'),skillName(run.skill))];
  const detail=[run.request.skill==='auto'?'chosen from your question':'selected by you',run.request.model.replace('_',' '),run.execution.profile];
  if(run.context.prior_reviewed_findings.length)detail.push(`${run.context.prior_reviewed_findings.length} reviewed finding${run.context.prior_reviewed_findings.length>1?'s':''} as context`);
  return el('div',{class:'skill-line'},bits,el('span',{text:detail.join(' · ')}));
}
function stepsBlock(run){
  const started=[...run.events].reverse().find(item=>item.type==='tool_started');
  const done=run.plan.filter(step=>Object.hasOwn(run.outputs,step.id)).length;
  const current=run.plan.find(step=>!Object.hasOwn(run.outputs,step.id));
  const items=run.plan.map(step=>{
    const finished=Object.hasOwn(run.outputs,step.id);
    const running=!finished&&run.status==='running'&&started?.tool_id===step.id;
    const failed=!finished&&['failed','interrupted'].includes(run.status)&&step===current;
    const mark=finished?el('span',{class:'st done'},icon('check')):running?el('span',{class:'st run'},icon('spin')):failed?el('span',{class:'st fail'},icon('x')):el('span',{class:'st'});
    return el('li',{},mark,el('span',{},step.title,el('small',{text:step.reason})));
  });
  let lead, text;
  if(run.status==='planned'){lead=icon('list');text=`Plan · ${run.plan.length} steps`;}
  else if(run.status==='queued'){lead=el('span',{class:'st run'},icon('spin'));text='Queued…';}
  else if(run.status==='running'||run.status==='cancelling'){lead=el('span',{class:'st run'},icon('spin'));text=`${current?current.title:'Finishing'}… (${done}/${run.plan.length})`;}
  else if(run.status==='completed'){lead=el('span',{class:'st done'},icon('check'));text=`Ran ${run.plan.length} steps`;}
  else{lead=el('span',{class:'st fail'},icon('x'));text=`Stopped after ${done} of ${run.plan.length} steps`;}
  const budget=el('div',{class:'budget',text:`${run.plan.filter(step=>step.tool==='simulate').length} model evaluations · ${run.execution.profile} compute · no AI model calls${run.execution.sensitivity_grid.length?' · grid '+run.execution.sensitivity_grid.join(', '):''}`});
  return disclosure('steps',run.run_id+':steps',run.status!=='completed',[lead,el('span',{text}),icon('chev','chev')],el('ol',{},items),budget);
}
function callout(tone,name,text){return el('div',{class:'callout '+tone},icon(name),el('span',{text}));}
function plannedReply(run){
  const r=run.request, source=run.context.source_name;
  let what='read the evidence for trust signals, adoption barriers and narrative risks';
  if(run.skill==='scenario')what+=`, then compare a baseline with an intervention at strength ${r.intervention_strength} over ${r.horizon_days} model days`;
  if(run.skill==='sensitivity')what+=`, then sweep intervention strength across ${run.execution.sensitivity_grid.length} points from 0 to 1`;
  const parts=[el('p',{},`I'll ${what}, using “${source}”. `,el('span',{class:'muted',text:'Everything runs locally with deterministic tools.'}))];
  const unconfirmed=run.context.consent==='unconfirmed';
  if(unconfirmed)parts.push(callout('warn','alert','Permission for this source is not confirmed. Confirm research use before you keep or share the results.'));
  parts.push(el('p',{text:run.blockers.length?'This plan is blocked. Change the settings and send your question again.':'Shall I run it?'}));
  parts.push(el('div',{class:'actions'},
    el('button',{type:'button',class:'btn primary',disabled:!!run.blockers.length||state.busy,onclick:()=>act(run,'start')},icon('play'),'Run'),
    el('button',{type:'button',class:'btn',disabled:state.busy,onclick:()=>editPlanned(run)},icon('pencil'),'Edit')));
  return parts;
}
function stoppedReply(run){
  const failure=[...run.events].reverse().find(item=>['tool_failed','failed','interrupted','cancelled'].includes(item.type));
  const text=run.status==='cancelled'?'You stopped this run. Completed steps are saved.':`The run ${run.status}${failure?': '+failure.message:''}. Completed steps are saved.`;
  return [el('p',{text}),el('div',{class:'actions'},el('button',{type:'button',class:'btn primary',disabled:state.busy,onclick:()=>act(run,'resume')},icon('resume'),'Resume from checkpoint'))];
}
function completedReply(run,lesson){
  const o=run.outputs, e=o.encode, d=o.diagnose, r=run.request, parts=[];
  const prose=el('div',{class:'prose'});
  if(e)prose.append(el('p',{},'The evidence scores ',el('strong',{text:fmt(e.trust_score)}),' on trust and ',el('strong',{text:fmt(e.adoption_barrier_score)}),` on adoption barriers (keyword heuristics, confidence ${fmt(e.confidence)}).${e.themes.length?' Themes: '+e.themes.map(human).join(', ')+'.':''}`));
  if(d&&d.threat_type)prose.append(el('p',{text:`The main narrative risk looks like ${human(d.threat_type)}${d.misinformation_mechanism?' through '+human(d.misinformation_mechanism):''}${d.susceptible_group?', most relevant to '+d.susceptible_group:''}. Misinformation risk ${fmt(d.misinformation_risk_score)}${d.trusted_messenger?'; a likely trusted messenger is '+d.trusted_messenger:''}.`}));
  if(d?.counter_narrative)prose.append(el('blockquote',{text:d.counter_narrative}));
  const base=finalAdoption(o.baseline), intv=finalAdoption(o.intervention);
  if(Number.isFinite(base)&&Number.isFinite(intv)){
    const diff=intv-base;
    prose.append(el('p',{},`With intervention strength ${r.intervention_strength}, final adoption reaches `,el('strong',{text:fmt(intv)}),` against ${fmt(base)} with no intervention (${diff>=0?'+':''}${fmt(diff)}) after ${r.horizon_days} model days.`));
  }
  const sweep=run.plan.filter(step=>step.id.startsWith('sweep_')&&o[step.id]);
  if(sweep.length){
    const values=sweep.map(step=>finalAdoption(o[step.id]));
    prose.append(el('p',{text:`Across ${sweep.length} intervention strengths, final adoption ranges from ${fmt(Math.min(...values))} to ${fmt(Math.max(...values))}.`}));
  }
  parts.push(prose);
  if(e)parts.push(el('div',{class:'metrics'},[[e.trust_score,'Trust'],[e.adoption_barrier_score,'Adoption barriers'],[d?.misinformation_risk_score,'Misinformation risk'],[e.confidence,'Heuristic confidence']].filter(([value])=>Number.isFinite(value)).map(([value,label])=>el('div',{class:'metric'},el('b',{text:fmt(value)}),el('span',{text:label})))));
  if(o.baseline&&o.intervention)parts.push(el('div',{class:'chart-card'},chart(o.baseline,o.intervention),el('div',{class:'legend'},el('span',{},el('i',{class:'base'}),`Baseline ${fmt(base)}`),el('span',{},el('i'),`Intervention ${fmt(intv)}`))));
  if(sweep.length)parts.push(el('div',{class:'table-card'},el('table',{},el('thead',{},el('tr',{},el('th',{text:'Strength'}),el('th',{text:'Final adoption'}),el('th',{text:'Change from baseline'}))),el('tbody',{},sweep.map(step=>{const value=finalAdoption(o[step.id]);return el('tr',{},el('td',{text:String(step.strength)}),el('td',{text:fmt(value)}),el('td',{text:(value-base>=0?'+':'')+fmt(value-base)}));})))));
  const checks=o.check;
  parts.push(el('p',{class:'small muted',text:`${checks?(checks.passed?'Numerical checks passed. ':'Some numerical checks failed; see Details. '):''}These are heuristic scores and an uncalibrated illustrative model. Use them to frame questions, not to predict outcomes.`}));
  if(lesson)parts.push(quiz(run,lesson));
  const reviewing=state.reviewing.has(run.run_id);
  parts.push(el('div',{class:'actions'},
    el('a',{class:'btn',href:apiBase+runsURL(run.run_id)+'/artifacts/brief',download:''},icon('down'),'Brief'),
    el('a',{class:'btn',href:apiBase+runsURL(run.run_id)+'/artifacts/json',download:''},icon('down'),'Audit JSON'),
    el('button',{type:'button',class:'btn',onclick:()=>{reviewing?state.reviewing.delete(run.run_id):state.reviewing.add(run.run_id);updateTurn(run);}},icon(run.review?'check':'pencil'),run.review?'Reviewed':'Add review note')));
  if(reviewing)parts.push(reviewForm(run));
  parts.push(details(run));
  return parts;
}
function chart(baseline,intervention){
  const svg=svgNode('svg',{viewBox:'0 0 660 230',role:'img','aria-label':'Illustrative adoption over model days: baseline and intervention',class:'chart'});
  for(const value of [0,.25,.5,.75,1]){const y=200-value*180;svg.append(svgNode('line',{x1:40,x2:650,y1:y,y2:y,class:'grid'}));const label=svgNode('text',{x:0,y:y+4});label.textContent=(value*100)+'%';svg.append(label);}
  [[baseline,'base'],[intervention,'intv']].forEach(([series,cls])=>{const rows=series.trajectory;svg.append(svgNode('polyline',{points:rows.map((row,i)=>`${40+i/Math.max(1,rows.length-1)*610},${200-row.adoption*180}`).join(' '),fill:'none',class:cls,'stroke-width':2.5}));});
  const label=svgNode('text',{x:650,y:224,'text-anchor':'end'});label.textContent=`Model day ${baseline.trajectory.at(-1)?.day??''}`;svg.append(label);
  return svg;
}
function quiz(run,lesson){
  const result=run.lesson_check;
  const form=el('form',{class:'quiz'},el('h3',{text:`Lab ${lesson.number} check: ${lesson.check}`}),
    lesson.choices.map((choice,index)=>el('label',{},el('input',{type:'radio',name:'choice-'+run.run_id,value:String(index),required:true,checked:String(result?.choice)===String(index)}),el('span',{text:choice}))),
    el('div',{class:'actions'},el('button',{type:'submit',class:'btn'},'Check my answer')),
    result?el('p',{class:'small',text:(result.correct?'Correct. ':'Not quite. ')+result.explanation}):null);
  form.addEventListener('submit',async event=>{
    event.preventDefault();
    const choice=new FormData(form).get('choice-'+run.run_id);
    if(choice===null)return;
    try{const response=await api(`/engine/workspaces/${encodeURIComponent(state.workspace)}/lessons/${lesson.id}/check`,{method:'POST',body:JSON.stringify({run_id:run.run_id,choice:Number(choice)})});run.lesson_check={...response,choice:Number(choice)};updateTurn(run);loadThreads();}
    catch(err){pushLocal({role:'ai',tone:'error',text:err.message});}
  });
  return form;
}
function reviewForm(run){
  const area=el('textarea',{'data-keep':'review-'+run.run_id,minlength:'12',maxlength:'2000',rows:'3',placeholder:'The evidence suggests… The model assumes… We still need to check…','aria-label':'Review note'});
  area.value=run.review?.note||'';
  const form=el('form',{class:'review-form'},el('span',{class:'small muted',text:'A review note records what you can responsibly conclude. Reviewed findings carry into later messages in this chat as explicit context.'}),area,
    el('div',{class:'actions'},el('button',{type:'submit',class:'btn primary'},'Save note'),run.review?el('span',{class:'small muted',text:'Saved '+new Date(run.review.at).toLocaleString()}):null));
  form.addEventListener('submit',async event=>{
    event.preventDefault();
    if(area.value.trim().length<12){area.focus();return;}
    try{const updated=await api(runsURL(run.run_id)+'/review',{method:'POST',body:JSON.stringify({note:area.value})});state.reviewing.delete(run.run_id);updateTurn(updated);loadThreads();}
    catch(err){pushLocal({role:'ai',tone:'error',text:err.message});}
  });
  return form;
}
function details(run){
  const o=run.outputs;
  const checks=o.check?el('ul',{},o.check.checks.map(check=>el('li',{text:`${check.tool}: finite ${check.finite?'✓':'✗'} · adoption within bounds ${check.bounded_adoption?'✓':'✗'} · compartment total ${check.normalized_compartment_sum===null?'n/a':check.normalized_compartment_sum?'✓':'✗'}`}))):null;
  const prov=[['Evidence',run.context.source_name],['Permission',human(run.context.consent)],['Planner',run.provenance.planner],['Code fingerprint',run.provenance.code_version],['Python',run.provenance.environment.python],['Attempt',String(run.attempt)]];
  return disclosure('more',run.run_id+':details',false,'Details: methods, limitations, tool outputs and log',
    checks,
    el('ul',{},run.warnings.map(text=>el('li',{text}))),
    el('dl',{class:'prov'},prov.map(([k,v])=>[el('dt',{text:k}),el('dd',{text:v})])),
    disclosure('more',run.run_id+':raw',false,'Tool outputs (JSON)',el('pre',{text:JSON.stringify(o,null,2)})),
    disclosure('more',run.run_id+':log',false,'Execution log',el('ol',{},run.events.map(event=>el('li',{text:`${new Date(event.at).toLocaleTimeString()} · ${event.message}`})))));
}
function localMessage(message){
  if(message.role==='user')return el('div',{class:'msg user'},el('div',{class:'bubble'},el('p',{text:message.text})));
  const body=el('div',{class:'ai-body'});
  if(message.typing)body.append(el('div',{class:'typing','aria-label':'NDIM is planning'},el('i'),el('i'),el('i')));
  if(message.tone==='error')body.append(callout('error','alert',message.text));
  else if(message.text)body.append(el('p',{text:message.text}));
  if(message.node)body.append(message.node);
  if(message.actions)body.append(el('div',{class:'actions'},message.actions.map(action=>el('button',{type:'button',class:'btn'+(action.primary?' primary':''),onclick:action.run},action.icon?icon(action.icon):null,action.label))));
  return el('div',{class:'msg ai'},el('span',{class:'avatar','aria-hidden':'true'},'n',el('span',{text:'·'})),body);
}

// ---------- composer ----------
function renderAttachments(){
  const box=$('attachments');box.replaceChildren();
  if(state.evidence){
    const ev=state.evidence;
    const note=ev.fromChat?'from this chat':ev.consent==='unconfirmed'?'permission not confirmed':ev.consent==='synthetic'?'synthetic example':'research use confirmed';
    box.append(attachmentChip(ev,{note,compact:!!ev.fromChat,onEdit:openEvidenceEditor,onRemove:()=>{state.evidence=null;renderAttachments();}}));
  }
  if(state.lesson)box.append(el('div',{class:'attach'},el('span',{class:'ico'},icon('cap')),el('span',{},el('b',{text:`Lab ${state.lesson.number} · ${state.lesson.title}`}),el('small',{text:skillName(state.lesson.skill)})),el('button',{type:'button','aria-label':'Leave lab',title:'Leave lab',onclick:()=>{state.lesson=null;renderAttachments();renderSkill();}},icon('x'))));
}
function renderSkill(){
  $('prompt').placeholder=state.runs.length?'Ask a follow-up…  (/ for skills)':'Ask a research question…  (/ for skills)';
  const label=state.lesson?`Lab ${state.lesson.number}`:state.skill==='auto'?'Skills':skillName(state.skill);
  $('skill-label').textContent=label;
  $('skill-btn').classList.toggle('set',!!state.lesson||state.skill!=='auto');
}
function skillItems(filter=''){
  const query=filter.toLowerCase();
  const items=[];
  for(const skill of SKILLS)items.push({section:'Skills',key:skill.id,label:skill.name,desc:skill.desc,slash:'/'+skill.id,active:!state.lesson&&state.skill===skill.id,pick:()=>{state.skill=skill.id;state.lesson=null;}});
  for(const lesson of state.lessons)items.push({section:'Guided labs',key:'lab'+lesson.number,label:`Lab ${lesson.number} · ${lesson.title}`,desc:`${lesson.subtitle} · ${lesson.duration}`,slash:'/lab'+Number(lesson.number),active:state.lesson?.id===lesson.id,pick:()=>startLab(lesson)});
  return items.filter(item=>!query||item.slash.slice(1).startsWith(query)||item.label.toLowerCase().includes(query));
}
function fillMenu(menu,items,{onPick,activeIndex=-1}={}){
  menu.replaceChildren();
  let section='';
  items.forEach((item,index)=>{
    if(item.section!==section){menu.append(el('div',{class:'section',text:item.section}));section=item.section;}
    menu.append(el('button',{type:'button',role:'menuitem',class:index===activeIndex?'active':'',onclick:()=>{item.pick();onPick?.();closeMenus();renderSkill();renderAttachments();$('prompt').focus();}},
      icon(item.section==='Skills'?'spark':'cap'),el('span',{},item.label,el('small',{text:item.desc})),item.active?icon('check','tick'):el('kbd',{text:item.slash})));
  });
  if(!items.length)menu.append(el('div',{class:'section',text:'No matching skill'}));
}
let slashIndex=0;
function updateSlash(){
  const value=$('prompt').value;
  const match=/^\/(\w*)$/.exec(value);
  if(!match){$('slash-menu').hidden=true;return;}
  const items=skillItems(match[1]);
  slashIndex=Math.min(slashIndex,Math.max(0,items.length-1));
  fillMenu($('slash-menu'),items,{activeIndex:slashIndex,onPick:()=>{if(!state.lesson)$('prompt').value='';autosize();}});
  $('slash-menu').hidden=false;
}
function autosize(){const p=$('prompt');p.style.height='auto';p.style.height=Math.min(p.scrollHeight,240)+'px';}
function closeMenus(except){
  for(const [button,menu] of [['attach-btn','attach-menu'],['skill-btn','skill-menu'],['settings-btn','settings-menu']]){
    if(menu===except)continue;
    $(menu).hidden=true;$(button).setAttribute('aria-expanded','false');
  }
  if(except!=='slash-menu')$('slash-menu').hidden=true;
}
function toggleMenu(button,menu){
  const opening=$(menu).hidden;
  closeMenus(menu);
  if(menu==='skill-menu'&&opening)fillMenu($('skill-menu'),skillItems());
  $(menu).hidden=!opening;$(button).setAttribute('aria-expanded',String(opening));
}
function readSettings(){
  state.settings={model:$('set-model').value,profile:$('set-profile').value,horizon_days:Number($('set-horizon').value),
    intervention_strength:Number($('set-intervention').value),initial_adoption:Number($('set-initial').value),
    narrative_influence:Number($('set-influence').value),language:$('set-language').value,expertise:$('set-expertise').value};
  state.autorun=$('set-autorun').checked;
  try{localStorage.setItem('ndim-autorun',state.autorun?'1':'');}catch{}
  markSettings();
}
function writeSettings(){
  const s=state.settings;
  $('set-model').value=s.model;$('set-profile').value=s.profile;$('set-horizon').value=s.horizon_days;
  $('set-intervention').value=s.intervention_strength;$('set-initial').value=s.initial_adoption;$('set-influence').value=s.narrative_influence;
  $('set-language').value=s.language;$('set-expertise').value=s.expertise;$('set-autorun').checked=state.autorun;
  markSettings();
}
function markSettings(){
  for(const [id,out] of [['set-intervention','out-intervention'],['set-initial','out-initial'],['set-influence','out-influence']])$(out).textContent=Number($(id).value).toFixed(2);
  const changed=Object.keys(DEFAULTS).some(key=>state.settings[key]!==DEFAULTS[key]);
  $('settings-btn').classList.toggle('changed',changed);
}

// ---------- evidence ----------
function useSample(){state.evidence={text:state.sample,name:'Synthetic NIDM teaching example',consent:'synthetic'};afterEvidence();}
function openEvidenceEditor(){
  closeMenus();
  const ev=state.evidence;
  $('evidence-input').value=ev?ev.text:'';
  $('source-name').value=ev?ev.name:'Researcher-supplied field note';
  $('consent').value=ev?ev.consent:'unconfirmed';
  $('evidence-editor').hidden=false;$('evidence-input').focus();
}
function saveEvidence(){
  const text=$('evidence-input').value.trim();
  if(text.length<20){$('evidence-input').focus();$('evidence-input').setCustomValidity('Paste at least 20 characters of source evidence.');$('evidence-input').reportValidity();$('evidence-input').setCustomValidity('');return;}
  state.evidence={text,name:$('source-name').value.trim()||'Researcher-supplied field note',consent:$('consent').value};
  $('evidence-editor').hidden=true;afterEvidence();
}
async function readFile(file){
  if(!/\.(txt|md)$/i.test(file.name))throw Error('Attach a UTF-8 .txt or .md file. Structured sources go through the research workbench.');
  if(file.size>80000)throw Error('This file is over the 80 KB limit. Attach an excerpt.');
  const text=(await file.text()).trim();
  if(text.length>20000)throw Error('Use an excerpt of at most 20,000 characters.');
  if(text.length<20)throw Error('This file has less than 20 characters of text.');
  state.evidence={text,name:file.name,consent:'unconfirmed'};
  afterEvidence();
}
function afterEvidence(){
  renderAttachments();
  if(state.pending){const question=state.pending;state.pending=null;state.local=[];send(question);}
  else $('prompt').focus();
}
const evidenceActions=()=>[
  {label:'Use the sample field notes',icon:'file',primary:true,run:useSample},
  {label:'Upload a file',icon:'clip',run:()=>$('file-input').click()},
  {label:'Paste evidence',icon:'paste',run:openEvidenceEditor}];

// ---------- sending and running ----------
function startLab(lesson){
  newChat();
  state.lesson=lesson;state.skill=lesson.skill;
  state.evidence={text:state.sample,name:'Synthetic NIDM teaching example',consent:'synthetic'};
  state.local=[{role:'ai',node:el('div',{class:'lesson-card'},el('h3',{text:`Lab ${lesson.number} · ${lesson.title}`}),el('p',{class:'small muted',text:lesson.concept}),el('ol',{},lesson.instructions.map(text=>el('li',{text})))),text:'The sample field notes are attached and the lab question is in the box below. Send it to begin.'}];
  $('prompt').value=lesson.question;autosize();render();
}
async function send(text){
  text=(text??$('prompt').value).trim();
  if(!text||state.busy)return;
  const slash=/^\/(\w+)\s+([\s\S]+)$/.exec(text);
  if(slash){const skill=SKILLS.find(item=>item.id===slash[1]);if(skill){state.skill=skill.id;state.lesson=null;text=slash[2].trim();renderSkill();}}
  $('prompt').value='';autosize();closeMenus();
  if(!state.online){pushLocal({role:'user',text});pushLocal({role:'ai',tone:'error',text:'I am not connected to an NDIM engine. Connect one first (see the welcome screen), then send your question again.'});$('prompt').value=text;return;}
  if(text.length<8){pushLocal({role:'user',text});pushLocal({role:'ai',text:'Could you ask that as a research question? For example: “What trust signals and barriers appear in these field notes?” or “What if the intervention were weaker?”'});return;}
  if(!state.evidence){
    state.pending=text;
    pushLocal({role:'user',text});
    pushLocal({role:'ai',text:'I need source evidence to work from: an interview excerpt, a field note or other material. Add some and I will plan the experiment for your question.',actions:evidenceActions()});
    return;
  }
  if(state.settings.language!=='en'){pushLocal({role:'user',text});pushLocal({role:'ai',text:'The offline encoder reads English only. Attach an English translation of the evidence and set Evidence language to English in settings.'});$('prompt').value=text;return;}
  state.busy=true;
  const gen=state.gen, threadId=state.threadId||newId();
  state.local=[{role:'user',text},{role:'ai',typing:true}];
  render();scrollToEnd();
  const prior=state.runs.filter(run=>run.status==='completed'&&run.review).slice(-3).map(run=>run.run_id);
  const ev=state.evidence, lesson=state.lesson;
  const payload={workspace_id:state.workspace,question:text,evidence:ev.text,source_name:ev.name,consent:ev.consent,
    skill:lesson?lesson.skill:state.skill,...state.settings,lesson_id:lesson?.id||null,prior_run_ids:prior,thread_id:threadId};
  try{
    const run=await api('/engine/plans',{method:'POST',body:JSON.stringify(payload)});
    if(gen!==state.gen)return;
    state.busy=false;state.threadId=threadId;state.runs.push(run);state.local=[];state.lesson=null;
    state.evidence={...ev,fromChat:true};
    render();setURL();loadThreads();scrollToEnd();
    if(state.autorun&&!run.blockers.length)act(run,'start');
  }catch(err){
    if(gen!==state.gen)return;
    state.busy=false;
    state.local=[{role:'user',text},{role:'ai',tone:'error',text:err.message}];
    $('prompt').value=text;autosize();render();
  }finally{if(gen===state.gen)state.busy=false;}
}
async function act(run,name){
  if(state.busy)return;
  state.busy=true;updateTurn(run);
  const gen=state.gen;
  try{const updated=await api(runsURL(run.run_id)+'/'+name,{method:'POST'});if(gen!==state.gen)return;state.busy=false;updateTurn(updated);poll(updated.run_id);loadThreads();}
  catch(err){if(gen===state.gen){state.busy=false;updateTurn(run);pushLocal({role:'ai',tone:'error',text:err.message});}}
  finally{if(gen===state.gen)state.busy=false;}
}
async function editPlanned(run){
  try{
    await api(runsURL(run.run_id),{method:'DELETE'});
    state.runs=state.runs.filter(item=>item.run_id!==run.run_id);
    $('prompt').value=run.request.question;autosize();
    if(!state.runs.length){state.threadId=null;setURL();}
    render();loadThreads();
    toggleMenu('settings-btn','settings-menu');$('prompt').focus();
  }catch(err){pushLocal({role:'ai',tone:'error',text:err.message});}
}
function stopPoll(){clearTimeout(state.poll);state.poll=null;}
function poll(runId){
  stopPoll();
  const run=state.runs.find(item=>item.run_id===runId);
  if(!run||!ACTIVE.has(run.status))return;
  const gen=state.gen;
  state.poll=setTimeout(async()=>{
    try{
      const updated=await api(runsURL(runId));
      if(gen!==state.gen)return;
      updateTurn(updated);
      if(ACTIVE.has(updated.status))poll(runId);else loadThreads();
    }catch{if(gen===state.gen)state.poll=setTimeout(()=>poll(runId),2000);}
  },500);
}

// ---------- workspace, sidebar, theme ----------
function setSidebar(open){
  $('app').classList.toggle('collapsed',!open);
  $('scrim').hidden=!(open&&matchMedia('(max-width:820px)').matches);
  try{if(!matchMedia('(max-width:820px)').matches)localStorage.setItem('ndim-sidebar',open?'':'closed');}catch{}
}
async function createWorkspace(){
  const name=prompt('Project name','Energy Just Transition');
  if(!name?.trim())return;
  const domain=prompt('Research domain','energy just transition');
  if(!domain?.trim())return;
  try{
    const workspace=await api('/workspaces',{method:'POST',body:JSON.stringify({name:name.trim(),domain:domain.trim(),country:'Rwanda',description:`${name.trim()} research workspace.`})});
    $('workspace').add(new Option(workspace.name,workspace.workspace_id));
    $('workspace').value=workspace.workspace_id;state.workspace=workspace.workspace_id;
    state.threads=[];newChat();loadThreads();
  }catch(err){pushLocal({role:'ai',tone:'error',text:err.message});}
}
function greet(){const hour=new Date().getHours();$('greeting').textContent=hour<12?'Good morning':hour<18?'Good afternoon':'Good evening';}
function suggestions(){
  const box=$('suggestions');box.replaceChildren();
  const quick=[
    ['spark','Interpret a field note','evidence','What trust signals and adoption barriers appear in these field notes?'],
    ['spark','Compare an intervention','scenario',state.lessons.find(item=>item.skill==='scenario')?.question||'How does an intervention change illustrative adoption?'],
    ['spark','Stress-test an assumption','sensitivity',state.lessons.find(item=>item.skill==='sensitivity')?.question||'How sensitive is adoption to intervention strength?'],
  ];
  for(const [name,label,skill,question] of quick)box.append(el('button',{type:'button',onclick:()=>{state.skill=skill;state.lesson=null;if(!state.evidence)state.evidence={text:state.sample,name:'Synthetic NIDM teaching example',consent:'synthetic'};renderSkill();send(question);}},icon(name),label));
  if(state.lessons[0])box.append(el('button',{type:'button',onclick:()=>startLab(state.lessons[0])},icon('cap'),'Start a guided lab'));
}
function showConnect(message){
  const box=$('connect');box.hidden=false;
  const input=el('input',{type:'url',value:apiBase||'http://127.0.0.1:8010','aria-label':'NDIM engine address'});
  box.replaceChildren(el('div',{class:'connect-card'},
    el('p',{},el('strong',{text:'Connect an NDIM engine. '}),'This page is the chat interface only. Start the NDIM desktop app or local backend, then enter the address it reports.'),
    el('form',{class:'row',onsubmit:event=>{event.preventDefault();const params=new URLSearchParams(location.search);params.set('api',input.value.trim());location.search=params.toString();}},input,el('button',{type:'submit',class:'btn primary'},icon('plug'),'Connect')),
    message?el('p',{class:'err',text:message}):null));
}

// ---------- events ----------
$('composer').addEventListener('submit',event=>{event.preventDefault();send();});
$('prompt').addEventListener('input',()=>{autosize();slashIndex=0;updateSlash();});
$('prompt').addEventListener('keydown',event=>{
  const menu=$('slash-menu');
  if(!menu.hidden){
    const buttons=[...menu.querySelectorAll('button')];
    if(event.key==='ArrowDown'||event.key==='ArrowUp'){event.preventDefault();slashIndex=(slashIndex+(event.key==='ArrowDown'?1:-1)+buttons.length)%Math.max(1,buttons.length);updateSlash();return;}
    if((event.key==='Enter'||event.key==='Tab')&&buttons[slashIndex]){event.preventDefault();buttons[slashIndex].click();return;}
    if(event.key==='Escape'){event.preventDefault();menu.hidden=true;return;}
  }
  if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing){event.preventDefault();send();}
});
$('attach-btn').onclick=()=>toggleMenu('attach-btn','attach-menu');
$('skill-btn').onclick=()=>toggleMenu('skill-btn','skill-menu');
$('settings-btn').onclick=()=>toggleMenu('settings-btn','settings-menu');
document.querySelectorAll('[data-attach]').forEach(button=>button.onclick=()=>{
  closeMenus();
  if(button.dataset.attach==='file')$('file-input').click();
  else if(button.dataset.attach==='paste')openEvidenceEditor();
  else useSample();
});
$('file-input').onchange=async event=>{const file=event.target.files[0];event.target.value='';if(!file)return;try{await readFile(file);}catch(err){pushLocal({role:'ai',tone:'error',text:err.message});}};
$('evidence-save').onclick=saveEvidence;
$('evidence-cancel').onclick=()=>{$('evidence-editor').hidden=true;$('prompt').focus();};
$('settings-menu').addEventListener('input',readSettings);
$('settings-menu').addEventListener('change',readSettings);
document.addEventListener('click',event=>{if(!event.target.closest('.anchor')&&!event.target.closest('#slash-menu'))closeMenus();});
document.addEventListener('keydown',event=>{
  if(event.key==='Escape'){closeMenus();if(matchMedia('(max-width:820px)').matches)setSidebar(false);}
  const typing=['INPUT','TEXTAREA','SELECT'].includes(document.activeElement?.tagName);
  if(event.key==='n'&&!typing&&!event.ctrlKey&&!event.metaKey&&!event.altKey)newChat();
});
$('new-chat').onclick=newChat;
$('new-workspace').onclick=createWorkspace;
$('workspace').onchange=()=>{state.workspace=$('workspace').value;state.threads=[];newChat();loadThreads();};
$('collapse').onclick=()=>setSidebar(false);
$('menu').onclick=()=>setSidebar(true);
$('scrim').onclick=()=>setSidebar(false);
$('theme-toggle').onclick=()=>{
  const root=document.documentElement;
  const dark=root.dataset.theme?root.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
  root.dataset.theme=dark?'light':'dark';
  try{localStorage.setItem('ndim-theme',root.dataset.theme);}catch{}
};

// ---------- start ----------
async function init(){
  greet();
  try{state.autorun=localStorage.getItem('ndim-autorun')==='1';}catch{}
  let closed=false;try{closed=localStorage.getItem('ndim-sidebar')==='closed';}catch{}
  setSidebar(!matchMedia('(max-width:820px)').matches&&!closed);
  writeSettings();render();syncLinks();
  if(config.static&&!apiBase){$('engine-status').textContent='Engine not connected';document.body.dataset.engine='offline';showConnect();return;}
  try{
    const [workspaces,capabilities,lessons]=await Promise.all([api('/workspaces'),api('/engine/capabilities'),api('/engine/lessons')]);
    state.lessons=lessons.lessons;state.sample=lessons.sample;state.online=true;
    workspaces.workspaces.forEach(workspace=>$('workspace').add(new Option(workspace.name,workspace.workspace_id)));
    const params=new URLSearchParams(location.search);
    const requested=params.get('workspace');
    state.workspace=requested&&workspaces.workspaces.some(item=>item.workspace_id===requested)?requested:'ndim-core';
    $('workspace').value=state.workspace;
    const r=capabilities.resources;
    $('engine-status').textContent=`Engine connected · ${r.recommended_profile}`;document.body.dataset.engine='online';
    $('capacity').textContent=`This engine: ${r.cpu_available} CPU available, ${r.memory_available_mb===null?'unknown':r.memory_available_mb+' MB'} memory, recommends ${r.recommended_profile}. No AI model calls.`;
    suggestions();
    await loadThreads();
    const chat=params.get('chat')||params.get('run');
    const target=chat&&state.threads.find(thread=>thread.id===chat||thread.runs.some(run=>run.run_id===chat));
    if(target)await openThread(target.id);
    else{render();setURL();}
  }catch(err){
    $('engine-status').textContent='Engine unavailable';document.body.dataset.engine='error';
    const message=config.static&&err instanceof TypeError?`Could not reach the NDIM engine at ${apiBase}. Check that it is running and that it allows requests from this site.`:err.message;
    if(config.static)showConnect(message);else pushLocal({role:'ai',tone:'error',text:message});
  }
}
init();
