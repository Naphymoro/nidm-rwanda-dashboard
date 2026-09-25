'use strict';
// NDIM chat. With an AI provider configured, the research assistant converses, searches the library and plans
// experiments through the engine; without one, each message plans one experiment directly. Experiments that share a
// thread_id belong to one conversation. The Workbench and Library live in a side panel, not on separate pages.
const $ = id => document.getElementById(id);
const config = window.NDIM_ENGINE || {};

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
const state = {workspace:'', threads:[], threadId:null, runs:[], messages:[], local:[], evidence:null, skill:'auto', lesson:null, pending:null,
  settings:{...DEFAULTS}, autorun:false, lessons:[], sample:'', online:false, busy:false, streaming:false, poll:null, gen:0,
  open:new Map(), reviewing:new Set(), notify:new Set(), queuedNotes:[], agent:null, token:'',
  panel:{open:false, tab:'workbench', runId:null, section:null, query:'', toc:null}};
const agentOn = () => !!state.agent?.available;

// ---------- helpers ----------
function el(tag, props={}, ...children){
  const node=document.createElement(tag);
  for(const [key,value] of Object.entries(props)){
    if(value===undefined||value===null||value===false)continue;
    if(key==='class')node.className=value;
    else if(key==='text')node.textContent=value;
    else if(key==='html')node.innerHTML=value;
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
const avatar = () => el('span',{class:'avatar','aria-hidden':'true'},'n',el('span',{text:'·'}));

function headers(extra={}){const h={'Content-Type':'application/json',...extra};if(state.token)h['X-NDIM-Agent-Token']=state.token;return h;}
async function errorText(response){
  let message=`The engine returned ${response.status}. Please retry.`;
  try{const data=await response.json();if(typeof data.detail==='string')message=data.detail;else if(Array.isArray(data.detail))message=data.detail.map(item=>item.msg||String(item)).join('; ');}catch{}
  return message;
}
async function api(url,options={}){
  const response=await fetch(apiBase+url,{...options,headers:headers(options.headers)});
  if(!response.ok)throw Error(await errorText(response));
  return response.status===204?null:response.json();
}
const runsURL = (id) => `/engine/workspaces/${encodeURIComponent(state.workspace)}/runs${id?'/'+encodeURIComponent(id):''}`;
const threadURL = (id) => `/agent/workspaces/${encodeURIComponent(state.workspace)}/threads${id?'/'+encodeURIComponent(id):''}`;
function pageURL(){
  const params=new URLSearchParams();
  if(state.workspace)params.set('workspace',state.workspace);
  if(state.threadId&&(state.runs.length||state.messages.length))params.set('chat',state.threadId);
  if(apiBase)params.set('api',apiBase);
  const query=params.toString();
  return location.pathname+(query?'?'+query:'');
}
function setURL(){history.replaceState(null,'',pageURL());}
function scrollToEnd(){requestAnimationFrame(()=>{$('scroller').scrollTop=$('scroller').scrollHeight;});}
function nearEnd(){const s=$('scroller');return s.scrollHeight-s.scrollTop-s.clientHeight<160;}

// Minimal, safe Markdown: everything is escaped first, then a small set of constructs is restored.
function escapeHTML(text){return String(text).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
function inline(text){
  return text.replace(/`([^`]+)`/g,'<code>$1</code>').replace(/\*\*([^*]+)\*\*/g,'<strong>$1</strong>')
    .replace(/(^|[^*])\*([^*\s][^*]*)\*/g,'$1<em>$2</em>')
    .replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,'<a href="$2" target="_blank" rel="noreferrer">$1</a>');
}
function markdown(src){
  const lines=escapeHTML(src).split('\n');
  const out=[];let i=0;
  while(i<lines.length){
    const line=lines[i];
    if(/^```/.test(line)){const code=[];i++;while(i<lines.length&&!/^```/.test(lines[i]))code.push(lines[i++]);i++;out.push(`<pre><code>${code.join('\n')}</code></pre>`);continue;}
    const heading=/^(#{1,4})\s+(.*)$/.exec(line);
    if(heading){out.push(`<h${heading[1].length+1}>${inline(heading[2])}</h${heading[1].length+1}>`);i++;continue;}
    if(/^\s*\|.*\|\s*$/.test(line)){
      const rows=[];while(i<lines.length&&/^\s*\|.*\|\s*$/.test(lines[i]))rows.push(lines[i++]);
      const cells=row=>row.trim().replace(/^\||\|$/g,'').split('|').map(cell=>inline(cell.trim()));
      const body=rows.filter(row=>!/^\s*\|[\s:|-]+\|\s*$/.test(row));
      out.push('<table><thead><tr>'+cells(body[0]).map(c=>`<th>${c}</th>`).join('')+'</tr></thead><tbody>'+body.slice(1).map(row=>'<tr>'+cells(row).map(c=>`<td>${c}</td>`).join('')+'</tr>').join('')+'</tbody></table>');
      continue;
    }
    if(/^\s*([-*]|\d+\.)\s+/.test(line)){
      const ordered=/^\s*\d+\./.test(line);const items=[];
      while(i<lines.length&&/^\s*([-*]|\d+\.)\s+/.test(lines[i]))items.push(lines[i++].replace(/^\s*([-*]|\d+\.)\s+/,''));
      out.push(`<${ordered?'ol':'ul'}>${items.map(item=>`<li>${inline(item)}</li>`).join('')}</${ordered?'ol':'ul'}>`);continue;
    }
    if(/^&gt;\s?/.test(line)){const quote=[];while(i<lines.length&&/^&gt;\s?/.test(lines[i]))quote.push(lines[i++].replace(/^&gt;\s?/,''));out.push(`<blockquote>${inline(quote.join(' '))}</blockquote>`);continue;}
    if(!line.trim()){i++;continue;}
    const para=[];while(i<lines.length&&lines[i].trim()&&!/^(#{1,4}\s|```|\s*([-*]|\d+\.)\s+|\s*\||&gt;)/.test(lines[i]))para.push(lines[i++]);
    out.push(`<p>${inline(para.join('<br>'))}</p>`);
  }
  return out.join('');
}

// ---------- sidebar: conversations ----------
function groupThreads(rows,agentThreads=[]){
  const map=new Map();
  for(const row of rows){
    const id=row.thread_id||row.run_id;
    if(!map.has(id))map.set(id,{id,runs:[],agent:false});
    map.get(id).runs.push(row);
  }
  for(const chat of agentThreads){
    if(!map.has(chat.thread_id))map.set(chat.thread_id,{id:chat.thread_id,runs:[],agent:true});
    Object.assign(map.get(chat.thread_id),{agent:true,agentTitle:chat.title,agentUpdated:chat.updated_at});
  }
  return [...map.values()].map(thread=>{
    thread.runs.sort((a,b)=>a.created_at.localeCompare(b.created_at));
    thread.title=thread.agentTitle||thread.runs[0]?.title||'New chat';
    thread.updated=[thread.agentUpdated||'',...thread.runs.map(run=>run.updated_at)].reduce((a,b)=>b>a?b:a,'');
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
  try{
    const [runs,chats]=await Promise.all([api(runsURL()+'?offset=0&limit=100'),agentOn()?api(threadURL()).catch(()=>({threads:[]})):{threads:[]}]);
    state.threads=groupThreads(runs.runs,chats.threads);renderThreads();
  }catch(err){console.warn(err);}
}
async function deleteThread(thread){
  const count=thread.runs.length;
  if(!confirm(`Delete “${thread.title}”${count?` and its ${count} experiment${count>1?'s':''}`:''}? Downloaded copies remain.`))return;
  try{
    for(const run of thread.runs)await api(runsURL(run.run_id),{method:'DELETE'});
    if(thread.agent)await api(threadURL(thread.id),{method:'DELETE'});
    if(thread.id===state.threadId)newChat();
  }catch(err){pushLocal({role:'ai',tone:'error',text:err.message});}
  loadThreads();
}

// ---------- conversation state ----------
function closeSidebarOnMobile(){if(matchMedia('(max-width:820px)').matches)setSidebar(false);}
function newChat(){
  stopPoll();state.gen++;
  Object.assign(state,{threadId:null,runs:[],messages:[],local:[],evidence:null,lesson:null,pending:null,skill:'auto',streaming:false,busy:false,queuedNotes:[]});
  state.open.clear();state.reviewing.clear();state.panel.runId=null;setStreaming(false);
  render();setURL();closeSidebarOnMobile();$('prompt').focus();
}
async function openThread(id){
  stopPoll();const gen=++state.gen;
  const thread=state.threads.find(item=>item.id===id);
  if(!thread){pushLocal({role:'ai',tone:'error',text:'That chat is not in this project any more.'});return;}
  try{
    const [runs,chat]=await Promise.all([Promise.all(thread.runs.map(row=>api(runsURL(row.run_id)))),thread.agent?api(threadURL(id)):null]);
    if(gen!==state.gen)return;
    runs.sort((a,b)=>a.created_at.localeCompare(b.created_at));
    const last=runs.at(-1);
    const evidence=chat?.evidence||(last&&{text:last.evidence,name:last.context.source_name,consent:last.context.consent});
    Object.assign(state,{threadId:id,runs,messages:chat?.messages||[],local:[],lesson:null,pending:null,skill:'auto',streaming:false,busy:false,
      evidence:evidence?{...evidence,fromChat:true}:null});
    if(last){const request=last.request;state.settings={...DEFAULTS,...Object.fromEntries(Object.keys(DEFAULTS).map(key=>[key,request[key]??DEFAULTS[key]]))};}
    state.open.clear();state.reviewing.clear();state.panel.runId=null;setStreaming(false);
    writeSettings();render();setURL();closeSidebarOnMobile();
    $('scroller').style.scrollBehavior='auto';$('scroller').scrollTop=$('scroller').scrollHeight;$('scroller').style.scrollBehavior='';
    const active=runs.find(run=>ACTIVE.has(run.status));
    if(active)poll(active.run_id);
  }catch(err){if(gen===state.gen)pushLocal({role:'ai',tone:'error',text:err.message});}
}
function pushLocal(message){state.local.push(message);renderMessages();scrollToEnd();}
function hasContent(){return !!(state.runs.length||state.messages.length||state.local.length);}

// ---------- rendering ----------
function render(){
  const title=state.threads.find(t=>t.id===state.threadId)?.title||state.messages.find(m=>m.role==='user')?.content?.split('\n')[0]||state.runs[0]?.title||'New chat';
  $('chat-title').textContent=title;
  document.title='NDIM · '+(hasContent()?title:'Research chat');
  renderMessages();renderAttachments();renderSkill();renderThreads();renderPanel();
}
function renderMessages(){
  $('main').classList.toggle('empty',!hasContent());
  $('thread').replaceChildren(...timeline(),...state.local.map(localMessage));
}
// Agent messages form turns (user bubble + assistant block). Experiments the assistant planned appear inside its
// reply; experiments planned directly (workbench, labs, no-AI mode) appear as their own turns, in time order.
function timeline(){
  const referenced=new Set(state.messages.filter(m=>m.role==='tool'&&m.meta?.run_id&&!m.meta.reference).map(m=>m.meta.run_id));
  const blocks=[];
  let turnParts=null;
  const flush=()=>{if(turnParts&&turnParts.parts.length)blocks.push({at:turnParts.at,node:aiBlock(turnParts.parts)});turnParts=null;};
  for(const message of state.messages){
    if(message.role==='user'){flush();blocks.push({at:message.at,node:userBubble(message.content,message.evidence)});turnParts={at:message.at,parts:[]};}
    else if(message.role==='note'){flush();turnParts={at:message.at,parts:[]};}
    else{if(!turnParts)turnParts={at:message.at,parts:[]};turnParts.parts.push(message);}
  }
  flush();
  state.runs.forEach((run,index)=>{if(!referenced.has(run.run_id))blocks.push({at:run.created_at,node:turn(run,state.runs[index-1])});});
  return blocks.sort((a,b)=>a.at.localeCompare(b.at)).map(block=>block.node);
}
function userBubble(text,evidence){
  return el('div',{class:'msg user'},el('div',{class:'bubble'},
    evidence?el('div',{class:'attach-line'},attachmentChip({name:evidence.name,text:{length:evidence.chars}})):null,
    el('p',{text})));
}
function aiBlock(parts){
  const body=el('div',{class:'ai-body'});
  const results=new Map(parts.filter(m=>m.role==='tool').map(m=>[m.tool_call_id,m]));
  for(const message of parts){
    if(message.role!=='assistant')continue;
    if(message.content)body.append(el('div',{class:'md',html:markdown(message.content)}));
    if(message.error)body.append(callout('error','alert',message.error));
    for(const call of message.tool_calls||[]){
      const result=results.get(call.id);
      body.append(toolChip(call.name,result?(result.content.includes('"error"')&&!result.meta?'err':'done'):'done',toolLabel(call)));
      const meta=result?.meta||{};
      if(meta.library)body.append(refs(meta.library));
      if(meta.run_id&&!meta.reference){const run=state.runs.find(item=>item.run_id===meta.run_id);if(run)body.append(runCard(run));}
    }
  }
  return el('div',{class:'msg ai'},avatar(),body);
}
const TOOL_LABELS={plan_experiment:'Planned an experiment',get_run:'Read experiment results',compare_runs:'Compared experiments',list_runs:'Listed experiments',search_library:'Searched the library',read_library:'Read the library',list_lessons:'Listed guided labs'};
function toolLabel(call){
  const a=call.arguments||{};
  if(call.name==='search_library'&&a.query)return `Searched the library for “${a.query}”`;
  if(call.name==='plan_experiment'&&a.skill)return `Planned a ${skillName(a.skill).toLowerCase()}`;
  return TOOL_LABELS[call.name]||call.name;
}
function toolChip(name,status,label){
  const mark=status==='run'?el('span',{class:'st run'},icon('spin')):status==='err'?el('span',{class:'st fail'},icon('x')):el('span',{class:'st done'},icon('check'));
  return el('div',{class:'tool-chip'+(status==='err'?' err':''),'data-tool':name},mark,el('span',{text:label}));
}
function refs(items){return el('div',{class:'refs'},items.map(item=>el('button',{type:'button',class:'ref',title:'Open in the Library',onclick:()=>openSection(item.id)},icon('book'),`${item.source}: ${item.title}`)));}

function updateTurn(run){
  const index=state.runs.findIndex(item=>item.run_id===run.run_id);
  if(index<0)return;
  state.runs[index]=run;
  const old=$('thread').querySelector(`[data-run="${run.run_id}"]`);
  const follow=nearEnd();
  if(old){
    const fresh=old.dataset.kind==='card'?runCard(run):turn(run,state.runs[index-1]);
    const focused=document.activeElement&&old.contains(document.activeElement)?document.activeElement.dataset.keep:null;
    const draft=old.querySelector('textarea[data-keep]')?.value;
    old.replaceWith(fresh);
    if(draft!==undefined){const area=fresh.querySelector('textarea[data-keep]');if(area)area.value=draft;}
    if(focused)fresh.querySelector(`[data-keep="${focused}"]`)?.focus();
  }else renderMessages();
  if(follow)scrollToEnd();
  if(state.panel.open&&state.panel.tab==='workbench')renderPanel();
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
  const chars=(ev.text?.length??0).toLocaleString();
  return el('div',{class:'attach'+(compact?' compact':''),title:compact?`${ev.name} · ${chars} characters`:null},
    el('span',{class:'ico'},icon('file')),
    el('span',{},el('b',{text:ev.name}),el('small',{text:`${chars} characters${note?' · '+note:''}`})),
    onEdit?el('button',{type:'button','aria-label':'Edit evidence',title:'Edit evidence',onclick:onEdit},icon('pencil')):null,
    onRemove?el('button',{type:'button','aria-label':'Remove evidence',title:'Remove evidence',onclick:onRemove},icon('x')):null);
}

// A turn: the researcher's question as a bubble, then the run as NDIM's reply (no-AI mode, workbench, labs).
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
  const body=el('div',{class:'ai-body'},...runParts(run,{prose:true}));
  return el('section',{class:'turn','data-run':run.run_id,'data-kind':'turn'},user,el('div',{class:'msg ai'},avatar(),body));
}
// A card: the same run inside an assistant reply. The assistant explains results, so the card skips the prose.
function runCard(run){return el('div',{class:'run-card ai-body','data-run':run.run_id,'data-kind':'card'},...runParts(run,{prose:!agentOn()}));}
function runParts(run,{prose}){
  const lesson=state.lessons.find(item=>item.id===run.lesson_id);
  const parts=[skillLine(run),stepsBlock(run)];
  if(run.blockers.length)parts.push(callout('error','alert',run.blockers.join(' ')));
  if(run.status==='planned')parts.push(...plannedReply(run,prose));
  else if(ACTIVE.has(run.status))parts.push(el('div',{class:'actions'},el('button',{type:'button',class:'btn',disabled:run.status==='cancelling'||state.busy,onclick:()=>act(run,'cancel')},icon('stop'),run.status==='cancelling'?'Stopping…':'Stop')));
  else if(run.status==='completed')parts.push(...completedReply(run,lesson,prose));
  else parts.push(...stoppedReply(run));
  return parts;
}
function skillLine(run){
  const bits=[el('span',{class:'skill'},icon('spark'),skillName(run.skill))];
  const detail=[run.request.skill==='auto'?'chosen from your question':'selected',run.request.model.replace('_',' '),`strength ${run.request.intervention_strength}`,run.execution.profile];
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
  const budget=el('div',{class:'budget',text:`${run.plan.filter(step=>step.tool==='simulate').length} model evaluations · ${run.execution.profile} compute · local deterministic tools${run.execution.sensitivity_grid.length?' · grid '+run.execution.sensitivity_grid.join(', '):''}`});
  return disclosure('steps',run.run_id+':steps',run.status!=='completed',[lead,el('span',{text}),icon('chev','chev')],el('ol',{},items),budget);
}
function callout(tone,name,text){return el('div',{class:'callout '+tone},icon(name),el('span',{text}));}
function workbenchButton(run){return el('button',{type:'button',class:'btn',onclick:()=>openWorkbench(run.run_id)},icon('sliders'),'Workbench');}
function plannedReply(run,prose){
  const r=run.request, parts=[];
  if(prose){
    let what='read the evidence for trust signals, adoption barriers and narrative risks';
    if(run.skill==='scenario')what+=`, then compare a baseline with an intervention at strength ${r.intervention_strength} over ${r.horizon_days} model days`;
    if(run.skill==='sensitivity')what+=`, then sweep intervention strength across ${run.execution.sensitivity_grid.length} points from 0 to 1`;
    parts.push(el('p',{},`I'll ${what}, using “${run.context.source_name}”. `,el('span',{class:'muted',text:'Everything runs locally with deterministic tools.'})));
  }
  if(run.context.consent==='unconfirmed')parts.push(callout('warn','alert','Permission for this source is not confirmed. Confirm research use before you keep or share the results.'));
  if(prose)parts.push(el('p',{text:run.blockers.length?'This plan is blocked. Change the settings and send your question again.':'Shall I run it?'}));
  parts.push(el('div',{class:'actions'},
    el('button',{type:'button',class:'btn primary',disabled:!!run.blockers.length||state.busy,onclick:()=>act(run,'start')},icon('play'),'Run'),
    agentOn()?null:el('button',{type:'button',class:'btn',disabled:state.busy,onclick:()=>editPlanned(run)},icon('pencil'),'Edit'),
    workbenchButton(run)));
  return parts;
}
function stoppedReply(run){
  const failure=[...run.events].reverse().find(item=>['tool_failed','failed','interrupted','cancelled'].includes(item.type));
  const text=run.status==='cancelled'?'You stopped this run. Completed steps are saved.':`The run ${run.status}${failure?': '+failure.message:''}. Completed steps are saved.`;
  return [el('p',{text}),el('div',{class:'actions'},el('button',{type:'button',class:'btn primary',disabled:state.busy,onclick:()=>act(run,'resume')},icon('resume'),'Resume from checkpoint'),workbenchButton(run))];
}
function completedReply(run,lesson,prose){
  const o=run.outputs, e=o.encode, d=o.diagnose, r=run.request, parts=[];
  const base=finalAdoption(o.baseline), intv=finalAdoption(o.intervention);
  const sweep=run.plan.filter(step=>step.id.startsWith('sweep_')&&o[step.id]);
  if(prose){
    const text=el('div',{class:'prose'});
    if(e)text.append(el('p',{},'The evidence scores ',el('strong',{text:fmt(e.trust_score)}),' on trust and ',el('strong',{text:fmt(e.adoption_barrier_score)}),` on adoption barriers (keyword heuristics, confidence ${fmt(e.confidence)}).${e.themes.length?' Themes: '+e.themes.map(human).join(', ')+'.':''}`));
    if(d&&d.threat_type)text.append(el('p',{text:`The main narrative risk looks like ${human(d.threat_type)}${d.misinformation_mechanism?' through '+human(d.misinformation_mechanism):''}${d.susceptible_group?', most relevant to '+d.susceptible_group:''}. Misinformation risk ${fmt(d.misinformation_risk_score)}${d.trusted_messenger?'; a likely trusted messenger is '+d.trusted_messenger:''}.`}));
    if(d?.counter_narrative)text.append(el('blockquote',{text:d.counter_narrative}));
    if(Number.isFinite(base)&&Number.isFinite(intv)){const diff=intv-base;text.append(el('p',{},`With intervention strength ${r.intervention_strength}, final adoption reaches `,el('strong',{text:fmt(intv)}),` against ${fmt(base)} with no intervention (${diff>=0?'+':''}${fmt(diff)}) after ${r.horizon_days} model days.`));}
    if(sweep.length){const values=sweep.map(step=>finalAdoption(o[step.id]));text.append(el('p',{text:`Across ${sweep.length} intervention strengths, final adoption ranges from ${fmt(Math.min(...values))} to ${fmt(Math.max(...values))}.`}));}
    parts.push(text);
  }
  if(e)parts.push(el('div',{class:'metrics'},[[e.trust_score,'Trust'],[e.adoption_barrier_score,'Adoption barriers'],[d?.misinformation_risk_score,'Misinformation risk'],[e.confidence,'Heuristic confidence']].filter(([value])=>Number.isFinite(value)).map(([value,label])=>el('div',{class:'metric'},el('b',{text:fmt(value)}),el('span',{text:label})))));
  if(o.baseline&&o.intervention)parts.push(el('div',{class:'chart-card'},chart(o.baseline,o.intervention),el('div',{class:'legend'},el('span',{},el('i',{class:'base'}),`Baseline ${fmt(base)}`),el('span',{},el('i'),`Intervention ${fmt(intv)}`))));
  if(sweep.length)parts.push(el('div',{class:'table-card'},el('table',{},el('thead',{},el('tr',{},el('th',{text:'Strength'}),el('th',{text:'Final adoption'}),el('th',{text:'Change from baseline'}))),el('tbody',{},sweep.map(step=>{const value=finalAdoption(o[step.id]);return el('tr',{},el('td',{text:String(step.strength)}),el('td',{text:fmt(value)}),el('td',{text:(value-base>=0?'+':'')+fmt(value-base)}));})))));
  if(prose){const checks=o.check;parts.push(el('p',{class:'small muted',text:`${checks?(checks.passed?'Numerical checks passed. ':'Some numerical checks failed; see Details. '):''}These are heuristic scores and an uncalibrated illustrative model. Use them to frame questions, not to predict outcomes.`}));}
  if(lesson)parts.push(quiz(run,lesson));
  const reviewing=state.reviewing.has(run.run_id);
  parts.push(el('div',{class:'actions'},
    el('a',{class:'btn',href:apiBase+runsURL(run.run_id)+'/artifacts/brief',download:''},icon('down'),'Brief'),
    el('a',{class:'btn',href:apiBase+runsURL(run.run_id)+'/artifacts/json',download:''},icon('down'),'Audit JSON'),
    el('button',{type:'button',class:'btn',onclick:()=>{reviewing?state.reviewing.delete(run.run_id):state.reviewing.add(run.run_id);updateTurn(run);}},icon(run.review?'check':'pencil'),run.review?'Reviewed':'Add review note'),
    workbenchButton(run)));
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
  if(message.typing)body.append(el('div',{class:'typing','aria-label':'NDIM is thinking'},el('i'),el('i'),el('i')));
  if(message.tone==='error')body.append(callout('error','alert',message.text));
  else if(message.text)body.append(el('p',{text:message.text}));
  if(message.node)body.append(message.node);
  if(message.actions)body.append(el('div',{class:'actions'},message.actions.map(action=>el('button',{type:'button',class:'btn'+(action.primary?' primary':''),onclick:action.run},action.icon?icon(action.icon):null,action.label))));
  return el('div',{class:'msg ai'},avatar(),body);
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
  const follow=hasContent();
  $('prompt').placeholder=agentOn()?(follow?'Reply to NDIM…  (/ for skills)':'Ask anything about your research…  (/ for skills)'):(follow?'Ask a follow-up…  (/ for skills)':'Ask a research question…  (/ for skills)');
  const label=state.lesson?`Lab ${state.lesson.number}`:state.skill==='auto'?'Skills':skillName(state.skill);
  $('skill-label').textContent=label;
  $('skill-btn').classList.toggle('set',!!state.lesson||state.skill!=='auto');
}
function skillItems(filter=''){
  const query=filter.toLowerCase();
  const items=[];
  for(const skill of SKILLS)items.push({section:'Skills',label:skill.name,desc:skill.desc,slash:'/'+skill.id,active:!state.lesson&&state.skill===skill.id,pick:()=>{state.skill=skill.id;state.lesson=null;}});
  for(const lesson of state.lessons)items.push({section:'Guided labs',label:`Lab ${lesson.number} · ${lesson.title}`,desc:`${lesson.subtitle} · ${lesson.duration}`,slash:'/lab'+Number(lesson.number),active:state.lesson?.id===lesson.id,pick:()=>startLab(lesson)});
  items.push({section:'Tools',label:'Workbench',desc:'Inspect, adjust and re-plan experiments',slash:'/workbench',pick:()=>openPanel('workbench')});
  items.push({section:'Tools',label:'Library',desc:'Field manual and reference curriculum',slash:'/library',pick:()=>openPanel('library')});
  return items.filter(item=>!query||item.slash.slice(1).startsWith(query)||item.label.toLowerCase().includes(query));
}
function fillMenu(menu,items,{onPick,activeIndex=-1}={}){
  menu.replaceChildren();
  let section='';
  items.forEach((item,index)=>{
    if(item.section!==section){menu.append(el('div',{class:'section',text:item.section}));section=item.section;}
    menu.append(el('button',{type:'button',role:'menuitem',class:index===activeIndex?'active':'',onclick:()=>{item.pick();onPick?.();closeMenus();renderSkill();renderAttachments();$('prompt').focus();}},
      icon(item.section==='Skills'?'spark':item.section==='Tools'?(item.slash==='/library'?'book':'flask'):'cap'),el('span',{},item.label,el('small',{text:item.desc})),item.active?icon('check','tick'):el('kbd',{text:item.slash})));
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
  if(menu==='settings-menu'&&opening)renderAISettings();
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

// ---------- AI assistant settings ----------
function renderAISettings(){
  const box=$('ai-settings');box.replaceChildren();
  const a=state.agent;
  if(!a){box.hidden=true;return;}
  box.hidden=false;
  box.append(el('div',{class:'menu-title'},'Research assistant',el('small',{text:a.available?`${a.provider} · ${a.model}`:'Off: experiments only'})));
  if(a.available)box.append(el('span',{class:'ok',text:'On. NDIM answers, searches the library and plans experiments for you to run.'}));
  else box.append(el('span',{class:'warn',text:a.reason||'Not configured.'}));
  if(a.token_required){
    const token=el('input',{type:'password',placeholder:'Access token',value:state.token,'aria-label':'Assistant access token'});
    box.append(el('div',{class:'row'},token,el('button',{type:'button',class:'btn',onclick:()=>{state.token=token.value.trim();try{localStorage.setItem('ndim-agent-token',state.token);}catch{}loadAgent().then(()=>{render();renderAISettings();loadThreads();});}},'Save')));
  }
  if(a.configurable){
    const provider=el('select',{'aria-label':'AI provider'},a.providers.map(name=>el('option',{value:name,text:name})));
    provider.value=a.provider||'anthropic';
    const key=el('input',{type:'password',placeholder:a.available?'API key (leave blank to keep)':'API key','aria-label':'API key',autocomplete:'off'});
    const model=el('input',{placeholder:'Model (optional)','aria-label':'Model',value:a.available?a.model:''});
    const note=el('span',{class:'small muted'});
    box.append(el('label',{},'Provider',provider),el('div',{class:'row'},key),el('div',{class:'row'},model,el('button',{type:'button',class:'btn primary',onclick:async()=>{
      try{state.agent=await api('/agent/config',{method:'POST',body:JSON.stringify({provider:provider.value,api_key:key.value.trim()||null,model:model.value.trim()||null})});note.textContent=state.agent.available?'Saved. The assistant is on.':state.agent.reason;render();loadThreads();renderAISettings();}
      catch(err){note.textContent=err.message;}
    }},'Save')),note,el('span',{class:'small muted',text:'The key stays on this computer, in the NDIM data folder.'}));
  }
}
async function loadAgent(){
  try{state.agent=await api('/agent/status');}catch{state.agent=null;}
  const on=agentOn();
  $('model-badge').hidden=!on;$('model-badge').textContent=on?state.agent.model:'';
  document.querySelector('.welcome p').textContent=on?'Ask a research question, explore the manual, or plan an experiment.':'What would you like to investigate?';
  document.querySelector('.disclaimer').textContent=on?`Answers are written by ${state.agent.model}. Scientific results come only from NDIM's local tools, and nothing runs until you click Run.`:'NDIM runs local scientific tools, not an AI model. Scores are heuristics and scenarios are illustrative, so check them against the evidence.';
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
  if(!/\.(txt|md)$/i.test(file.name))throw Error('Attach a UTF-8 .txt or .md file.');
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

// ---------- sending ----------
function startLab(lesson){
  newChat();
  state.lesson=lesson;state.skill=lesson.skill;
  state.evidence={text:state.sample,name:'Synthetic NIDM teaching example',consent:'synthetic'};
  state.local=[{role:'ai',node:el('div',{class:'lesson-card'},el('h3',{text:`Lab ${lesson.number} · ${lesson.title}`}),el('p',{class:'small muted',text:lesson.concept}),el('ol',{},lesson.instructions.map(text=>el('li',{text})))),text:'The sample field notes are attached and the lab question is in the box below. Send it to begin.'}];
  $('prompt').value=lesson.question;autosize();render();
}
async function send(text){
  text=(text??$('prompt').value).trim();
  if(!text||state.busy||state.streaming)return;
  const slash=/^\/(\w+)\s+([\s\S]+)$/.exec(text);
  if(slash){const skill=SKILLS.find(item=>item.id===slash[1]);if(skill){state.skill=skill.id;state.lesson=null;text=slash[2].trim();renderSkill();}}
  $('prompt').value='';autosize();closeMenus();
  if(!state.online){pushLocal({role:'user',text});pushLocal({role:'ai',tone:'error',text:'I am not connected to an NDIM engine. Connect one first (see the welcome screen), then send your message again.'});$('prompt').value=text;return;}
  // Labs keep their fixed question and check, so they plan directly even when the assistant is on.
  if(agentOn()&&!state.lesson)return sendAgent(text);
  if(text.length<8){pushLocal({role:'user',text});pushLocal({role:'ai',text:'Could you ask that as a research question? For example: “What trust signals and barriers appear in these field notes?” or “What if the intervention were weaker?”'});return;}
  if(!state.evidence){
    state.pending=text;
    pushLocal({role:'user',text});
    pushLocal({role:'ai',text:'I need source evidence to work from: an interview excerpt, a field note or other material. Add some and I will plan the experiment for your question.',actions:evidenceActions()});
    return;
  }
  if(state.settings.language!=='en'){pushLocal({role:'user',text});pushLocal({role:'ai',text:'The offline encoder reads English only. Attach an English translation of the evidence and set Evidence language to English in settings.'});$('prompt').value=text;return;}
  const ev=state.evidence, lesson=state.lesson;
  const run=await planDirect({question:text,skill:lesson?lesson.skill:state.skill,...state.settings,lesson_id:lesson?.id||null},ev,{bubble:text});
  if(run){state.lesson=null;renderAttachments();renderSkill();if(state.autorun&&!run.blockers.length)act(run,'start');}
}
// Plan without the assistant: no-AI mode, labs, and the Workbench panel.
async function planDirect(params,ev,{bubble}={}){
  state.busy=true;
  const gen=state.gen, threadId=state.threadId||newId();
  state.local=bubble?[{role:'user',text:bubble},{role:'ai',typing:true}]:[];
  render();scrollToEnd();
  const prior=state.runs.filter(run=>run.status==='completed'&&run.review).slice(-3).map(run=>run.run_id);
  const payload={workspace_id:state.workspace,evidence:ev.text,source_name:ev.name,consent:ev.consent,prior_run_ids:prior,thread_id:threadId,...params};
  try{
    const run=await api('/engine/plans',{method:'POST',body:JSON.stringify(payload)});
    if(gen!==state.gen)return null;
    state.busy=false;state.threadId=threadId;state.runs.push(run);state.local=[];
    state.evidence={...ev,fromChat:true};
    render();setURL();loadThreads();scrollToEnd();
    return run;
  }catch(err){
    if(gen!==state.gen)return null;
    state.busy=false;
    state.local=bubble?[{role:'user',text:bubble},{role:'ai',tone:'error',text:err.message}]:[{role:'ai',tone:'error',text:err.message}];
    if(bubble){$('prompt').value=bubble;autosize();}
    render();return null;
  }
}
// While NDIM is answering, the send button is disabled, as in other chat apps; typing ahead is still allowed.
function setStreaming(on){state.streaming=on;$('send').disabled=on;$('send').title=on?'NDIM is answering…':'Send (Enter)';}
// Stream one assistant turn. Text arrives as deltas; tool steps and planned experiments render as they happen.
async function sendAgent(text,{hidden=false}={}){
  // A run can finish while a reply is still streaming; its note waits for that reply instead of being dropped.
  if(state.streaming){if(hidden)state.queuedNotes.push(text);return;}
  setStreaming(true);
  const gen=state.gen, threadId=state.threadId||newId();
  state.threadId=threadId;
  // Send evidence when it is new, or when this chat has no assistant history yet (e.g. an older experiments-only chat).
  const ev=state.evidence&&(!state.evidence.fromChat||!state.messages.length)?{text:state.evidence.text,name:state.evidence.name,consent:state.evidence.consent}:null;
  const body=el('div',{class:'ai-body'});
  const typing=el('div',{class:'typing','aria-label':'NDIM is thinking'},el('i'),el('i'),el('i'));
  body.append(typing);
  const live=el('div',{class:'msg ai'},avatar(),body);
  if(!hidden)$('thread').append(userBubble(text,ev?{name:ev.name,chars:ev.text.length}:null));
  $('thread').append(live);
  $('main').classList.remove('empty');
  scrollToEnd();
  let segment=null, segmentText='';
  const chips=new Map();
  const settings={...state.settings};
  if(state.skill!=='auto')settings.preferred_skill=state.skill;
  const finish=async()=>{
    if(gen!==state.gen){setStreaming(false);return;}
    try{
      const [chat]=await Promise.all([api(threadURL(threadId)),loadThreads()]);
      if(gen!==state.gen)return;
      state.messages=chat.messages;
      if(ev)state.evidence={...ev,fromChat:true};
      const known=new Set(state.runs.map(run=>run.run_id));
      const ids=[...new Set(chat.messages.filter(m=>m.meta?.run_id&&!m.meta.reference).map(m=>m.meta.run_id))].filter(id=>!known.has(id));
      const fresh=await Promise.all(ids.map(id=>api(runsURL(id)).catch(()=>null)));
      state.runs.push(...fresh.filter(Boolean));
      state.runs.sort((a,b)=>a.created_at.localeCompare(b.created_at));
      const follow=nearEnd();
      render();setURL();
      if(follow)scrollToEnd();
      setStreaming(false);
      const planned=fresh.filter(run=>run&&run.status==='planned'&&!run.blockers.length);
      if(state.autorun)for(const run of planned)await act(run,'start');
    }catch(err){setStreaming(false);pushLocal({role:'ai',tone:'error',text:err.message});}
    const next=state.queuedNotes.shift();
    if(next&&gen===state.gen)await sendAgent(next,{hidden:true});
  };
  try{
    const response=await fetch(apiBase+'/agent/chat',{method:'POST',headers:headers(),body:JSON.stringify({workspace_id:state.workspace,thread_id:threadId,message:text,evidence:ev,settings,hidden})});
    if(!response.ok){const message=await errorText(response);typing.remove();body.append(callout('error','alert',message));setStreaming(false);state.queuedNotes=[];if(!hidden){$('prompt').value=text;autosize();}return;}
    const reader=response.body.getReader();const decoder=new TextDecoder();let buffer='';
    for(;;){
      const {value,done}=await reader.read();
      if(done)break;
      buffer+=decoder.decode(value,{stream:true});
      let cut;
      while((cut=buffer.indexOf('\n\n'))>=0){
        const raw=buffer.slice(0,cut);buffer=buffer.slice(cut+2);
        const line=raw.split('\n').find(item=>item.startsWith('data:'));
        if(!line)continue;
        let event;try{event=JSON.parse(line.slice(5));}catch{continue;}
        if(gen!==state.gen)return;
        const follow=nearEnd();
        if(event.type==='text'){
          typing.remove();
          if(!segment){segment=el('div',{class:'md'});segmentText='';body.append(segment);}
          segmentText+=event.delta;
          segment.innerHTML=markdown(segmentText)+'<span class="cursor"></span>';
        }else if(event.type==='tool_start'){
          typing.remove();
          if(segment)segment.innerHTML=markdown(segmentText);
          segment=null;
          const chip=toolChip(event.name,'run',event.label+'…');
          chips.set(event.id,{chip,call:{name:event.name,arguments:event.args}});body.append(chip);
        }else if(event.type==='tool_end'){
          const entry=chips.get(event.id);
          if(entry){const done=toolChip(event.name,event.ok?'done':'err',event.ok?toolLabel(entry.call):(event.error||'Tool error'));entry.chip.replaceWith(done);entry.chip=done;}
          if(event.meta?.library)body.append(refs(event.meta.library));
          if(event.meta?.run_id&&!event.meta.reference){
            try{const run=await api(runsURL(event.meta.run_id));if(!state.runs.some(item=>item.run_id===run.run_id))state.runs.push(run);body.append(runCard(run));}catch{}
          }
        }else if(event.type==='error'){
          typing.remove();body.append(callout('error','alert',event.message));
        }
        if(follow)scrollToEnd();
      }
    }
  }catch(err){
    typing.remove();body.append(callout('error','alert',`The connection to the engine was interrupted (${err.message}).`));
  }
  await finish();
}
async function act(run,name){
  if(state.busy)return;
  state.busy=true;updateTurn(run);
  const gen=state.gen;
  try{
    const updated=await api(runsURL(run.run_id)+'/'+name,{method:'POST'});
    if(gen!==state.gen)return;
    if(name!=='cancel'&&agentOn())state.notify.add(updated.run_id);
    state.busy=false;updateTurn(updated);loadThreads();
    if(ACTIVE.has(updated.status))poll(updated.run_id);else await finished(updated);
  }catch(err){if(gen===state.gen){state.busy=false;updateTurn(run);pushLocal({role:'ai',tone:'error',text:err.message});}}
  finally{if(gen===state.gen)state.busy=false;}
}
async function editPlanned(run){
  try{
    await api(runsURL(run.run_id),{method:'DELETE'});
    state.runs=state.runs.filter(item=>item.run_id!==run.run_id);
    $('prompt').value=run.request.question;autosize();
    if(!state.runs.length&&!state.messages.length){state.threadId=null;setURL();}
    render();loadThreads();
    toggleMenu('settings-btn','settings-menu');$('prompt').focus();
  }catch(err){pushLocal({role:'ai',tone:'error',text:err.message});}
}
// Let the assistant read and explain a run the researcher started, as a new reply in the same chat.
async function finished(run){
  if(!state.notify.delete(run.run_id)||!agentOn())return;
  await sendAgent(`(Note from the app, not typed by the researcher) The researcher clicked Run on experiment ${run.run_id} and it finished with status ${run.status}. Read it with get_run and explain the result.`,{hidden:true});
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
      if(ACTIVE.has(updated.status))return poll(runId);
      loadThreads();
      await finished(updated);
    }catch{if(gen===state.gen)state.poll=setTimeout(()=>poll(runId),2000);}
  },500);
}

// ---------- side panel: workbench and library ----------
function openPanel(tab){
  state.panel.open=true;if(tab)state.panel.tab=tab;
  renderPanel();
  if(matchMedia('(max-width:820px)').matches)setSidebar(false);
}
function closePanel(){state.panel.open=false;renderPanel();}
function openWorkbench(runId){state.panel.runId=runId;openPanel('workbench');}
function renderPanel(){
  const panel=$('panel'), open=state.panel.open;
  panel.hidden=!open;
  $('panel-toggle').setAttribute('aria-expanded',String(open));
  document.querySelectorAll('[data-open-panel]').forEach(button=>button.classList.toggle('on',open&&state.panel.tab===button.dataset.openPanel));
  if(!open)return;
  for(const tab of ['workbench','library']){
    $('tab-'+tab).setAttribute('aria-selected',String(state.panel.tab===tab));
    $('panel-'+tab).hidden=state.panel.tab!==tab;
  }
  if(state.panel.tab==='workbench')renderWorkbench();else renderLibrary();
}
function paramForm(values,{skill}={}){
  const range=(name,label,value)=>{const out=el('output',{text:Number(value).toFixed(2)});const input=el('input',{type:'range',name,min:'0',max:'1',step:'0.01',value:String(value),oninput:()=>out.textContent=Number(input.value).toFixed(2)});return el('label',{class:'full'},el('span',{},label,' ',out),input);};
  const select=(name,label,value,options)=>{const node=el('select',{name},options.map(([v,t])=>el('option',{value:v,text:t})));node.value=value;return el('label',{},label,node);};
  return el('form',{class:'form'},
    skill!==undefined?select('skill','Workflow',skill==='auto'?'scenario':skill,[['evidence','Evidence interpretation'],['scenario','Scenario comparison'],['sensitivity','Sensitivity experiment']]):null,
    select('model','Model',values.model,[['compartmental','Compartmental'],['hybrid','Hybrid'],['agent_based','Agent-based proxy']]),
    range('intervention_strength','Intervention strength',values.intervention_strength),
    range('initial_adoption','Initial adoption',values.initial_adoption),
    range('narrative_influence','Narrative influence',values.narrative_influence),
    el('label',{},'Horizon (days)',el('input',{type:'number',name:'horizon_days',min:'7',max:'365',value:String(values.horizon_days)})),
    select('profile','Compute',values.profile,[['auto','Auto'],['economy','Economy · 3'],['balanced','Balanced · 7'],['thorough','Thorough · 11']]));
}
function formValues(form){
  const data=Object.fromEntries(new FormData(form));
  for(const key of ['intervention_strength','initial_adoption','narrative_influence','horizon_days'])if(key in data)data[key]=Number(data[key]);
  return data;
}
function renderWorkbench(){
  const box=$('panel-workbench');box.replaceChildren();
  box.append(el('div',{},el('h3',{text:'Workbench'}),el('p',{class:'sub',text:'Inspect any experiment in this chat, change its settings and plan a new version. Nothing runs until you click Run.'})));
  if(!state.runs.length){
    box.append(el('p',{class:'small muted',text:'No experiments in this chat yet. These are the defaults for the next plan:'}));
    const form=paramForm(state.settings);
    form.addEventListener('input',()=>{Object.assign(state.settings,formValues(form));writeSettings();});
    box.append(form);
  }else{
    const selected=state.runs.find(run=>run.run_id===state.panel.runId)||state.runs.at(-1);
    state.panel.runId=selected.run_id;
    box.append(el('div',{class:'run-pick'},state.runs.map(run=>el('button',{type:'button',class:run===selected?'active':'',onclick:()=>{state.panel.runId=run.run_id;renderWorkbench();}},el('span',{text:run.title}),el('i',{class:'status-pill '+run.status,text:run.status})))));
    const r=selected.request;
    const question=el('textarea',{name:'question',rows:'2',maxlength:'1000','aria-label':'Research question'});question.value=r.question;
    const form=paramForm(r,{skill:selected.skill});
    form.prepend(el('label',{class:'full'},'Research question',question));
    const note=el('p',{class:'small muted'});
    const planBtn=el('button',{type:'button',class:'btn primary',onclick:async()=>{
      const values=formValues(form);
      if(!values.question||values.question.trim().length<8){note.textContent='Enter a question of at least 8 characters.';return;}
      planBtn.disabled=true;
      const ev={text:selected.evidence,name:selected.context.source_name,consent:selected.context.consent};
      const run=await planDirect({...values,question:values.question.trim(),language:r.language,expertise:r.expertise},ev);
      planBtn.disabled=false;
      if(run){state.panel.runId=run.run_id;renderWorkbench();note.textContent='Planned. Review it in the chat and click Run.';}
    }},icon('list'),'Plan with these settings');
    box.append(form,el('div',{class:'actions'},planBtn,ACTIVE.has(selected.status)?null:selected.status==='planned'?el('button',{type:'button',class:'btn',onclick:()=>act(selected,'start')},icon('play'),'Run'):null),note);
    box.append(el('div',{class:'ai-body'},stepsBlock(selected),details(selected)));
  }
  box.append(el('p',{class:'panel-foot'},'Evidence ledger, SDMX intake, repository and policy export are still in the ',el('a',{href:apiBase+(config.static?'/classic-workbench':'/classic-workbench'),target:'_blank',rel:'noreferrer'},'classic workbench ↗'),'.'));
}
async function loadTOC(){if(!state.panel.toc){try{state.panel.toc=(await api('/agent/library')).sections;}catch(err){state.panel.toc=[];}}return state.panel.toc;}
async function renderLibrary(){
  const box=$('panel-library');
  if(state.panel.section){
    box.replaceChildren(el('p',{class:'small muted',text:'Loading…'}));
    try{
      const section=await api('/agent/library/'+encodeURIComponent(state.panel.section));
      const blocks=section.text.split('\n').reduce((acc,line)=>{if(line.startsWith('• ')){const last=acc.at(-1);if(last?.tagName==='UL')last.append(el('li',{text:line.slice(2)}));else acc.push(el('ul',{},el('li',{text:line.slice(2)})));}else acc.push(el('p',{text:line}));return acc;},[]);
      box.replaceChildren(el('button',{type:'button',class:'back-btn',onclick:()=>{state.panel.section=null;renderLibrary();}},icon('back'),'Library'),
        el('div',{},el('p',{class:'sub',text:section.source_label}),el('h3',{text:section.title})),
        el('div',{class:'lib-section'},blocks),
        el('div',{class:'actions'},el('button',{type:'button',class:'btn',onclick:()=>{$('prompt').value=`Explain “${section.title}” from the ${section.source_label.toLowerCase()} in plain language.`;autosize();$('prompt').focus();}},icon('spark'),'Ask NDIM about this')));
    }catch(err){box.replaceChildren(callout('error','alert',err.message));}
    return;
  }
  const search=el('input',{type:'search',placeholder:'Search the manual and curriculum','aria-label':'Search the library',value:state.panel.query});
  const list=el('div',{class:'lib-list'});
  const show=async()=>{
    const query=search.value.trim();state.panel.query=query;
    list.replaceChildren();
    if(query){
      let hits=[];try{hits=(await api('/agent/library?q='+encodeURIComponent(query))).sections;}catch{}
      if(!hits.length)list.append(el('p',{class:'small muted',text:'No matching sections.'}));
      hits.forEach(hit=>list.append(el('button',{type:'button',onclick:()=>openSection(hit.id)},`${hit.title}`,el('small',{text:`${hit.source} · ${hit.snippet}`}))));
      return;
    }
    let current='';
    for(const item of await loadTOC()){
      if(item.source_label!==current){list.append(el('div',{class:'lib-group',text:item.source_label}));current=item.source_label;}
      list.append(el('button',{type:'button',onclick:()=>openSection(item.id)},item.title));
    }
  };
  let timer=null;
  search.addEventListener('input',()=>{clearTimeout(timer);timer=setTimeout(show,200);});
  box.replaceChildren(el('div',{},el('h3',{text:'Library'}),el('p',{class:'sub',text:'The field manual and reference curriculum. NDIM cites these when it explains methods.'})),el('label',{class:'lib-search'},icon('search'),search),list);
  show();
}
function openSection(id){state.panel.section=id;openPanel('library');}

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
  const sample=()=>{if(!state.evidence)state.evidence={text:state.sample,name:'Synthetic NIDM teaching example',consent:'synthetic'};};
  const quick=[
    ['spark','Interpret a field note','evidence','What trust signals and adoption barriers appear in these field notes?'],
    ['spark','Compare an intervention','scenario','How might training more community health workers change adoption of clean cooking?'],
    ['spark','Stress-test an assumption','sensitivity',state.lessons.find(item=>item.skill==='sensitivity')?.question||'How sensitive is adoption to intervention strength?'],
  ];
  for(const [name,label,skill,question] of quick)box.append(el('button',{type:'button',onclick:()=>{state.skill=skill;state.lesson=null;sample();renderSkill();send(question);}},icon(name),label));
  if(agentOn())box.append(el('button',{type:'button',onclick:()=>send('How does the Bayesian update in NDIM change confidence, and when should I use it?')},icon('book'),'Explain a method'));
  if(state.lessons[0])box.append(el('button',{type:'button',onclick:()=>startLab(state.lessons[0])},icon('cap'),'Start a guided lab'));
}
function showConnect(message){
  const box=$('connect');box.hidden=false;
  const input=el('input',{type:'url',value:apiBase||'http://127.0.0.1:8010','aria-label':'NDIM engine address'});
  box.replaceChildren(el('div',{class:'connect-card'},
    el('p',{},el('strong',{text:'Connect an NDIM engine. '}),'This page is the chat interface only. Start the NDIM desktop app or local backend, then enter the address it reports. Your browser may ask to allow access to devices on your local network: allow it.'),
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
$('settings-menu').addEventListener('input',event=>{if(!event.target.closest('#ai-settings'))readSettings();});
$('settings-menu').addEventListener('change',event=>{if(!event.target.closest('#ai-settings'))readSettings();});
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
$('panel-toggle').onclick=()=>state.panel.open?closePanel():openPanel();
$('panel-close').onclick=closePanel;
document.querySelectorAll('[data-open-panel]').forEach(button=>button.onclick=()=>{if(state.panel.open&&state.panel.tab===button.dataset.openPanel)closePanel();else{if(button.dataset.openPanel==='library')state.panel.section=null;openPanel(button.dataset.openPanel);}});
document.querySelectorAll('[data-tab]').forEach(button=>button.onclick=()=>{state.panel.tab=button.dataset.tab;renderPanel();});
$('theme-toggle').onclick=()=>{
  const root=document.documentElement;
  const dark=root.dataset.theme?root.dataset.theme==='dark':matchMedia('(prefers-color-scheme: dark)').matches;
  root.dataset.theme=dark?'light':'dark';
  try{localStorage.setItem('ndim-theme',root.dataset.theme);}catch{}
};

// ---------- start ----------
async function init(){
  greet();
  try{state.autorun=localStorage.getItem('ndim-autorun')==='1';state.token=localStorage.getItem('ndim-agent-token')||'';}catch{}
  let closed=false;try{closed=localStorage.getItem('ndim-sidebar')==='closed';}catch{}
  setSidebar(!matchMedia('(max-width:820px)').matches&&!closed);
  writeSettings();render();
  if(config.static&&!apiBase){$('engine-status').textContent='Engine not connected';document.body.dataset.engine='offline';showConnect();return;}
  try{
    const [workspaces,capabilities,lessons]=await Promise.all([api('/workspaces'),api('/engine/capabilities'),api('/engine/lessons'),loadAgent()]);
    state.lessons=lessons.lessons;state.sample=lessons.sample;state.online=true;
    workspaces.workspaces.forEach(workspace=>$('workspace').add(new Option(workspace.name,workspace.workspace_id)));
    const params=new URLSearchParams(location.search);
    const requested=params.get('workspace');
    state.workspace=requested&&workspaces.workspaces.some(item=>item.workspace_id===requested)?requested:'ndim-core';
    $('workspace').value=state.workspace;
    const r=capabilities.resources;
    $('engine-status').textContent=`Engine connected · ${r.recommended_profile}`;document.body.dataset.engine='online';
    $('capacity').textContent=`This engine: ${r.cpu_available} CPU available, ${r.memory_available_mb===null?'unknown':r.memory_available_mb+' MB'} memory, recommends ${r.recommended_profile}.`;
    suggestions();
    await loadThreads();
    const chat=params.get('chat')||params.get('run');
    const target=chat&&state.threads.find(thread=>thread.id===chat||thread.runs.some(run=>run.run_id===chat));
    if(target)await openThread(target.id);
    else render();
    const panel=params.get('panel');
    if(panel==='workbench'||panel==='library')openPanel(panel);
    setURL();
  }catch(err){
    $('engine-status').textContent='Engine unavailable';document.body.dataset.engine='error';
    const message=config.static&&err instanceof TypeError?`Could not reach the NDIM engine at ${apiBase}. Check that it is running and that it allows requests from this site.`:err.message;
    if(config.static)showConnect(message);else pushLocal({role:'ai',tone:'error',text:message});
  }
}
init();
