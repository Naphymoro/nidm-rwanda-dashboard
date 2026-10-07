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
  open:new Map(), reviewing:new Set(), notify:new Set(), queuedNotes:[], agent:null, token:'', personal:null,
  journey:null, journeyProposal:null, recordsProposal:null, journeyGuide:null, journeyBusy:false, journeyError:null, journeyDraft:{}, journeyAnchor:null,
  correcting:new Set(), correctionDrafts:new Map(), feedbackError:new Map(),
  panel:{open:false, tab:'workbench', runId:null, section:null, query:'', toc:null}};
const agentOn = () => !!state.agent && (state.agent.available || !!state.personal?.key);
// "Use your own key": kept only in this browser and sent with each assistant message; the engine uses it for that reply
// and never stores it (agent.py PERSONAL), so a shared hosted engine never spends one visitor's key on another.
const PERSONAL_LABELS = {openrouter:'OpenRouter: one key for DeepSeek, GPT, Claude, Gemini and more (recommended)', openai:'OpenAI (ChatGPT models)',
  anthropic:'Anthropic (Claude models)', deepseek:'DeepSeek'};
function personalHeaders(){
  const p=state.personal;
  return p?.key?{'X-NDIM-User-Provider':p.provider,'X-NDIM-User-Key':p.key,...(p.model?{'X-NDIM-User-Model':p.model}:{})}:{};
}
function savePersonal(value){
  state.personal=value;
  try{value?localStorage.setItem('ndim-personal-key',JSON.stringify(value)):localStorage.removeItem('ndim-personal-key');}catch{}
  paintAgent();render();renderAISettings();
}
function openKeySettings(){
  // After the click that asked for it: the page closes menus on any click outside them.
  setTimeout(()=>{if($('settings-menu').hidden)toggleMenu('settings-btn','settings-menu');const key=$('personal-key');if(key){key.scrollIntoView({block:'center'});key.focus();}},0);
}
// An error from the free allowance (the Worker's daily or per-visitor limit) offers the visitor's own key.
function errorCallout(message){
  const box=callout('error','alert',message);
  if(!state.personal?.key&&/allowance|assistant messages/i.test(message))
    return el('div',{},box,el('div',{class:'actions'},el('button',{type:'button',class:'btn primary',onclick:openKeySettings},icon('plug'),'Add your own key')));
  return box;
}

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
  if(state.threadId&&(state.runs.length||state.messages.length||state.journey))params.set('chat',state.threadId);
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
// Math in replies: $$...$$ or \\[...\\] on display, \\(...\\) inline. Taken out before escaping, put back as KaTeX
// targets (renderTex); the LaTeX source shows if KaTeX cannot load.
const MATH_TOKEN=/\u0000M(\d+)\u0000/g;
function markdown(src){
  const maths=[];
  const hold=(tex,display)=>{maths.push({tex:tex.trim(),display});return `\u0000M${maths.length-1}\u0000`;};
  src=String(src).replace(/\$\$([\s\S]+?)\$\$|\\\[([\s\S]+?)\\\]/g,(m,a,b)=>hold(a??b,true)).replace(/\\\(([\s\S]+?)\\\)/g,(m,a)=>hold(a,false));
  const html=markdownBlocks(src);
  return maths.length?html.replace(MATH_TOKEN,(m,i)=>{const {tex,display}=maths[Number(i)];
    return display?`<span class="guide-formula md-math" data-tex="${escapeHTML(tex)}">${escapeHTML(tex)}</span>`:`<span data-tex-inline="${escapeHTML(tex)}">${escapeHTML(tex)}</span>`;}):html;
}
function markdownBlocks(src){
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
    const [runs,chats]=await Promise.all([api(runsURL()+'?offset=0&limit=100'),api(threadURL()).catch(()=>({threads:[]}))]);
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
  Object.assign(state,{threadId:null,runs:[],messages:[],local:[],evidence:null,lesson:null,pending:null,skill:'auto',streaming:false,busy:false,queuedNotes:[],
    journey:null,journeyProposal:null,recordsProposal:null,journeyError:null,journeyDraft:{}});
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
    Object.assign(state,{journeyDraft:{},journeyError:null,recordsProposal:null});await syncJourney(chat);
    if(!state.tour||state.tour.threadId!==id)restoreTour(id);
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
function hasContent(){return !!(state.runs.length||state.messages.length||state.local.length||state.journey||state.journeyProposal);}

// ---------- rendering ----------
function render(){
  const title=state.threads.find(t=>t.id===state.threadId)?.title||state.messages.find(m=>m.role==='user')?.content?.split('\n')[0]||state.runs[0]?.title||'New chat';
  $('chat-title').textContent=title;
  document.title='NDIM · '+(hasContent()?title:'Research chat');
  renderMessages();renderAttachments();renderSkill();renderThreads();renderPanel();renderTour();
}
function renderMessages(){
  state.journeyAnchor=state.messages.filter(m=>m.role==='tool'&&m.meta?.journey).at(-1)?.id||null;
  $('main').classList.toggle('empty',!hasContent());
  $('thread').replaceChildren(...timeline(),...state.local.map(localMessage));
  if($('thread').querySelector('[data-tex],[data-tex-inline]'))loadKatex().then(ok=>{if(ok)renderTex($('thread'));});
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
  if((state.journey||state.journeyProposal)&&!state.journeyAnchor)
    blocks.push({at:state.journey?.created_at||'',node:el('div',{class:'msg ai'},avatar(),el('div',{class:'ai-body'},journeyCard()))});
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
    if(message.error)body.append(errorCallout(message.error));
    if(message.check)body.append(checkCallout(message.check));
    for(const call of message.tool_calls||[]){
      const result=results.get(call.id);
      body.append(toolChip(call.name,result?(result.content.includes('"error"')&&!result.meta?'err':'done'):'done',toolLabel(call)));
      const meta=result?.meta||{};
      if(meta.library)body.append(refs(meta.library));
      if(meta.journey&&result.id===state.journeyAnchor)body.append(journeyCard());
      if(meta.run_id&&!meta.reference){const run=state.runs.find(item=>item.run_id===meta.run_id);if(run)body.append(runCard(run));}
    }
  }
  const last=[...parts].reverse().find(m=>m.role==='assistant'&&m.content);
  if(last)body.append(feedbackBar(last));
  return el('div',{class:'msg ai'},avatar(),body);
}
const TOOL_LABELS={plan_experiment:'Planned an experiment',get_run:'Read experiment results',compare_runs:'Compared experiments',list_runs:'Listed experiments',search_library:'Searched the library',read_library:'Read the library',list_lessons:'Listed guided labs',
  propose_journey:'Proposed a journey',propose_journey_records:'Filled the evidence form',journey_status:'Read the journey',run_journey_stage:'Ran a journey stage'};
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
// ---------- journey card ----------
// The 13-stage journey's controls. The assistant can only propose a question or records and run the stages that
// compute; starting the journey, adding records, accepting or rejecting them, entering field observations and approving
// the export happen only here, through the researcher's clicks. Each stage's explanation and limits are the engine's,
// shown as written; the assistant is not asked to explain results (small models invented them) but answers questions.
const NOTE = '(Note from the app, not typed by the researcher) ';
const journeyURL = (path='') => threadURL(state.threadId)+'/journey'+path;
const CONSENTS = [['','Choose permission…'],['research_use','Permission confirmed for research use'],['synthetic','Synthetic / demo data'],['unconfirmed','Permission not confirmed']];
const TOPICS = [['clean_cooking','Clean cooking'],['vaccines','Vaccines'],['ai_education','AI in the classroom'],['just_transition','Just transition']];
const GATE_LABEL = {eligible:'Passed the gate',review_before_accepting:'Check before accepting',blocked:'Blocked'};
// Start a journey without the assistant: the card opens in a new chat; the researcher types the question.
async function startJourney(question='',topic='clean_cooking'){
  newChat();
  state.threadId=newId();
  state.journeyProposal={question,topic};state.journeyDraft={question,topic};
  if(!state.journeyGuide){try{state.journeyGuide=await api('/engine/journey/stages');}catch{}}
  render();
  $('journey-card')?.querySelector('textarea')?.focus();
}
async function syncJourney(chat){
  state.journeyProposal=chat?.journey_proposal||null;
  const proposed=chat?.journey_records_proposal||null;
  if(JSON.stringify(proposed)!==JSON.stringify(state.recordsProposal)){state.recordsProposal=proposed;delete state.journeyDraft.records;}
  if(chat?.journey_id){
    try{state.journey=await api(`/engine/workspaces/${encodeURIComponent(state.workspace)}/journeys/${encodeURIComponent(chat.journey_id)}`);}
    catch(err){state.journeyError=err.message;}
  }else state.journey=null;
  if((state.journeyProposal||state.journey)&&!state.journeyGuide){try{state.journeyGuide=await api('/engine/journey/stages');}catch{}}
}
function rerenderJourney(){const old=$('journey-card');if(old)old.replaceWith(journeyCard());renderTour();}
function journeyLocked(){return state.journeyBusy||state.streaming;}
async function journeyAction(call,note){
  if(journeyLocked())return;
  state.journeyBusy=true;state.journeyError=null;rerenderJourney();
  try{
    const body=await call();
    if(body?.journey_id)state.journey=body;
    state.journeyProposal=null;
  }catch(err){state.journeyError=err.message;state.journeyBusy=false;rerenderJourney();return;}
  state.journeyBusy=false;state.journeyDraft={};rerenderJourney();loadThreads();setURL();
  if(note&&agentOn())await sendAgent(NOTE+note,{hidden:true});
}
const post=(path,body)=>api(journeyURL(path),{method:'POST',body:JSON.stringify(body)});
function field(label,input,hint){return el('label',{class:'jc-field'},el('span',{text:label}),input,hint?el('small',{class:'muted',text:hint}):null);}
function draftInput(key,props={}){
  const value=state.journeyDraft[key]??props.value??'';
  const input=el(props.tag||'input',{...props,tag:null,value:null,oninput:e=>{state.journeyDraft[key]=e.target.value;}});
  input.value=value;
  return input;
}
function journeyCard(){
  const j=state.journey, card=el('div',{class:'run-card ai-body journey-card',id:'journey-card'});
  card.append(el('div',{class:'skill-line'},el('span',{class:'skill'},icon('flask'),'NDIM journey'),el('span',{text:j?'13 stages · field notes to policy draft':'proposed, not started'})));
  if(state.journeyError)card.append(callout('error','alert',state.journeyError));
  // Over the internet a stage takes seconds; say so, so nobody clicks again (every button is disabled meanwhile).
  if(state.journeyBusy)card.append(el('div',{class:'callout'},el('span',{class:'st run'},icon('spin')),el('span',{text:'Working… this can take a few seconds.'})));
  if(!j){card.append(...proposalPart());return card;}
  card.append(callout('','check',j.presentation.opening));
  card.append(progressPart(j));
  const latest=latestStage(j);
  if(latest)card.append(stageResult(j,latest,true));
  card.append(...nextPart(j));
  const earlier=j.stages.filter(row=>row.status==='done'&&(j.presentation.stages[row.id]?.explanation||j.presentation.stages[row.id]?.sentences.length)&&row.id!==latest);
  if(earlier.length)card.append(disclosure('more','journey:earlier',false,'Earlier stage results',...earlier.map(row=>stageResult(j,row.id,false))));
  return card;
}
function proposalPart(){
  const p=state.journeyProposal;
  if(!p)return [el('p',{class:'muted',text:'No journey in this chat yet.'})];
  if(state.journeyDraft.question===undefined)state.journeyDraft.question=p.question;
  const area=draftInput('question',{tag:'textarea',rows:'2',maxlength:'1000','aria-label':'Research question',placeholder:'e.g. How might trusted messengers change clean cooking adoption?'});
  if(state.journeyDraft.topic===undefined)state.journeyDraft.topic=p.topic||'clean_cooking';
  const topic=el('select',{'aria-label':'Topic',onchange:e=>{state.journeyDraft.topic=e.target.value;}},TOPICS.map(([v,t])=>el('option',{value:v,text:t})));topic.value=state.journeyDraft.topic;
  return [el('div',{class:'md',html:markdown(state.journeyGuide?.intro||'')}),
    el('div',{class:'review-form'},field('Your question, as the journey will use it (edit if needed)',area),
      field('Topic',topic,'Adds this topic\'s word lists to the keyword encoder (for example vaccine rumours or device access).'),
      el('div',{class:'actions'},el('button',{type:'button',class:'btn primary',disabled:journeyLocked(),onclick:()=>{
        const question=(state.journeyDraft.question||'').trim();
        if(question.length<8){state.journeyError='The question needs at least 8 characters.';rerenderJourney();return;}
        journeyAction(()=>post('',{question,topic:state.journeyDraft.topic||'clean_cooking'}),'The researcher confirmed the question in the journey card and the journey started. In two sentences, ask for their field notes, pasted in this chat: each story with its place, source and period. When they give them, call propose_journey_records; they set permission in the card.');
      }},icon('check'),'Confirm question')))];
}
function progressPart(j){
  return el('ol',{class:'jc-progress'},j.stages.map(row=>el('li',{class:'jc-'+row.status,title:`${row.title}: ${row.status}${row.optional?' (optional)':''}`},
    row.status==='done'?el('span',{class:'st done'},icon('check')):el('span',{class:'st'}),el('span',{text:`${row.number} ${row.title}`}))));
}
function latestStage(j){
  const done=j.stages.filter(row=>row.status==='done'&&row.at&&(j.presentation.stages[row.id]?.explanation||j.presentation.stages[row.id]?.sentences.length));
  return done.length?done.reduce((a,b)=>a.at>b.at?a:b).id:null;
}
function stageResult(j,id,current){
  const row=j.stages.find(item=>item.id===id), view=j.presentation.stages[id];
  return el('div',{class:'jc-result'+(current?' current':'')},el('b',{text:`${row.number}. ${row.title}`}),
    ...(view.explanation?[el('p',{text:view.explanation})]:view.sentences.map(sentence=>el('p',{text:sentence}))),callout('warn','alert',view.limits),
    STAGE_MATH[id]?el('button',{type:'button',class:'btn ghost small',onclick:()=>openGuide(STAGE_MATH[id])},icon('cap'),'The math behind this step'):null);
}
function nextPart(j){
  if(!j.records.length)return [evidenceForm()];
  if(j.records.some(record=>!record.review)||j.next_stage==='repository')return [decisionsForm(j)];
  const next=j.next_stage, regional=j.stages.find(row=>row.id==='regional');
  const parts=[];
  if(next==='digital')parts.push(observationsForm());
  else if(next==='policy')parts.push(el('div',{class:'review-form'},el('p',{text:'The policy output assembles a draft for your team\'s review: options for discussion, not recommendations. It runs only when you approve it.'}),
    el('div',{class:'actions'},el('button',{type:'button',class:'btn primary',disabled:journeyLocked(),onclick:()=>journeyAction(()=>post('/stages/policy',{}),null)},icon('check'),'Approve export'))));
  else if(next){const row=j.stages.find(item=>item.id===next);parts.push(el('div',{class:'actions'},runButton(row,true)));}
  else parts.push(el('p',{class:'muted',text:'All required stages are done.'}));
  if(regional.status!=='done'&&!['intake','gate','repository','encoding'].includes(next||'')&&j.stages.find(row=>row.id==='encoding').status==='done')
    parts.push(el('div',{class:'actions'},runButton(regional,false,'Run regional analysis (optional)')));
  // Optional after stage 5: Sobol sensitivity analysis (about 11,000 runs), so the researcher chooses it.
  if(j.stages.find(row=>row.id==='compartmental').status==='done'&&!j.optional_done?.sensitivity)
    parts.push(el('div',{class:'review-form'},el('p',{class:'muted',text:'Optional: which inputs and which of the tool\'s own assumptions drive this result? NDIM varies them all at once and splits the variation between them (Sobol indices). It can take up to half a minute.'}),
      el('div',{class:'actions'},el('button',{type:'button',class:'btn',disabled:journeyLocked(),onclick:()=>journeyAction(()=>post('/sensitivity',{}),null)},icon('play'),'Which assumptions matter most? (optional)'))));
  // Optional after stage 12: 28 network simulations, slow over the internet, so the researcher chooses it.
  if(j.stages.find(row=>row.id==='inoculation').status==='done'&&!j.optional_done?.messenger_seeding)
    parts.push(el('div',{class:'review-form'},el('p',{class:'muted',text:'Optional: compare who a campaign recruits as messengers (at random, the best-connected households, or bridges between villages) on assumed network shapes. It can take up to half a minute.'}),
      el('div',{class:'actions'},el('button',{type:'button',class:'btn',disabled:journeyLocked(),onclick:()=>journeyAction(()=>post('/messenger-seeding',{}),null)},icon('play'),'Compare messenger recruiting (optional)'))));
  return parts;
}
function runButton(row,primary,label){
  return el('button',{type:'button',class:'btn'+(primary?' primary':''),disabled:journeyLocked(),onclick:()=>journeyAction(()=>post('/stages/'+row.id,{}),null)},icon('play'),label||`Run ${row.number}. ${row.title}`);
}
function evidenceForm(){
  const d=state.journeyDraft;
  // Tour records: a synthetic sample keeps its "synthetic" permission (true by construction); the researcher's own
  // uploaded notes start with no permission, which only they can set. NDIM's own proposals never set one.
  if(!d.records)d.records=(state.tourRecords||state.recordsProposal||[{text:''}]).map(r=>({text:r.text||'',admin_unit:r.admin_unit||'',source_name:r.source_name||'',period:r.period||'',
    consent:state.tourRecords&&r.consent==='synthetic'?'synthetic':'',language:state.tourRecords&&r.language?r.language:'en',
    ...(state.tourRecords&&r.translation_en?{translation_en:r.translation_en,translation_checked_by:r.translation_checked_by||''}:{})}));
  const allConsent=d.records.length>1?field('Permission for all records',(()=>{const s=el('select',{onchange:e=>{if(!e.target.value)return;d.records.forEach(r=>{r.consent=e.target.value;});rerenderJourney();}},
    [['','Set every record at once…'],...CONSENTS.slice(1)].map(([v,t])=>el('option',{value:v,text:t})));return s;})(),'Or set each record below.'):null;
  const rows=d.records.map((record,index)=>{
    const bind=(key,props)=>{const input=el(props.tag||'input',{...props,tag:null,oninput:e=>{record[key]=e.target.value;}});input.value=record[key]??'';return input;};
    return el('div',{class:'jc-record'},el('b',{text:`Record ${index+1}`}),
      field('Story or field note, unchanged',bind('text',{tag:'textarea',rows:'3',maxlength:'20000'})),
      el('div',{class:'jc-row'},field('Place',bind('admin_unit',{placeholder:'e.g. Kicukiro / Niboye'})),field('Source',bind('source_name',{placeholder:'e.g. Field team interview 4'})),
        field('Period',bind('period',{placeholder:'e.g. 2026-Q2'}))),
      el('div',{class:'jc-row'},field('Permission',(()=>{const s=el('select',{onchange:e=>{record.consent=e.target.value;}},CONSENTS.map(([v,t])=>el('option',{value:v,text:t})));s.value=record.consent;return s;})()),
        field('Language',(()=>{const s=el('select',{onchange:e=>{record.language=e.target.value;rerenderJourney();}},[['en','English'],['rw','Kinyarwanda'],['fr','French'],['other','Other']].map(([v,t])=>el('option',{value:v,text:t})));s.value=record.language;return s;})(),
          'The encoder reads English only: a record in another language needs an English translation that a person has checked.')),
      record.language==='en'?null:el('div',{class:'jc-row'},
        field('English translation, checked',bind('translation_en',{tag:'textarea',rows:'3',maxlength:'20000'}),'Trust, barrier and theme scores read this translation; sentiment reads the original.'),
        field('Translation checked by',bind('translation_checked_by',{placeholder:'Name of the person who checked it'}))));
  });
  return el('div',{class:'review-form'},el('b',{text:'Add your field notes'}),
    el('p',{class:'muted',text:state.tourRecords?'The guided tour filled this form. Check every field: nothing is added until you click Add to journey.':state.recordsProposal?'NDIM filled this form from your message. Check every field: nothing is added until you click Add to journey.':'Type your notes here, or paste them in the chat and NDIM fills this form for you to check.'}),
    allConsent,...rows,
    el('div',{class:'actions'},
      el('button',{type:'button',class:'btn',onclick:()=>{d.records.push({text:'',admin_unit:'',source_name:'',period:'',consent:'',language:'en'});rerenderJourney();}},icon('plus'),'Another record'),
      el('button',{type:'button',class:'btn primary',disabled:journeyLocked(),onclick:()=>{
        const missing=d.records.findIndex(r=>!r.text.trim()||!r.admin_unit.trim()||!r.source_name.trim()||!r.period.trim()||!r.consent);
        if(missing>=0){state.journeyError=`Record ${missing+1} needs its text, place, source, period and permission.`;rerenderJourney();return;}
        const half=d.records.findIndex(r=>r.language!=='en'&&!(r.translation_en||'').trim()!==!(r.translation_checked_by||'').trim());
        if(half>=0){state.journeyError=`Record ${half+1}: give the English translation and who checked it, or leave both empty.`;rerenderJourney();return;}
        const records=d.records.map(({translation_en,translation_checked_by,...r})=>{
          const out={...r,text:r.text.trim()};
          if(r.language!=='en'&&(translation_en||'').trim())Object.assign(out,{translation_en:translation_en.trim(),translation_checked_by:translation_checked_by.trim()});
          return out;});
        journeyAction(()=>post('/records',{records}),null).then(()=>{if(state.journey?.records.length)state.tourRecords=null;});
      }},icon('check'),'Add to journey')));
}
function decisionsForm(j){
  const d=state.journeyDraft.decisions||(state.journeyDraft.decisions={});
  const rows=j.records.map(record=>{
    const g=record.gate, flags=[...g.blockers,...g.warnings,...g.pii_flags,...g.quality_flags];
    const blocked=g.gate==='blocked', value=record.review?.decision||d[record.record_id]||'';
    const choice=(v,label)=>el('label',{class:'jc-choice'},el('input',{type:'radio',name:'decide-'+record.record_id,value:v,disabled:(blocked&&v==='accept')||!!record.review,checked:value===v,onchange:()=>{d[record.record_id]=v;}}),el('span',{text:label}));
    return el('div',{class:'jc-record'},el('div',{},el('b',{text:record.admin_unit}),el('small',{class:'muted',text:` · ${record.source_name} · ${record.period} · ${human(record.consent)}`})),
      el('p',{text:record.excerpt+(record.excerpt.length>=160?'…':'')}),
      record.translation_excerpt?el('p',{class:'muted',text:`English translation (checked by ${record.translation_checked_by}): ${record.translation_excerpt}${record.translation_excerpt.length>=160?'…':''}`}):null,
      el('div',{class:'small',text:`${GATE_LABEL[g.gate]||g.gate}${flags.length?': '+flags.join('; '):''}`}),
      el('div',{class:'jc-row'},choice('accept','Accept'),choice('reject','Reject')));
  });
  return el('div',{class:'review-form'},el('b',{text:'Accept or reject each record'}),el('p',{class:'muted',text:'Only accepted records reach any model. Decisions are frozen once encoding runs.'}),...rows,
    el('div',{class:'actions'},el('button',{type:'button',class:'btn primary',disabled:journeyLocked(),onclick:()=>{
      const decisions=j.records.filter(r=>!r.review&&d[r.record_id]).map(r=>({record_id:r.record_id,decision:d[r.record_id]}));
      if(!decisions.length){state.journeyError='Choose Accept or Reject for at least one record.';rerenderJourney();return;}
      journeyAction(()=>post('/review',decisions),null);
    }},icon('check'),'Save decisions')));
}
function observationsForm(){
  const num=(key,min,max,step)=>draftInput(key,{type:'number',min,max,step,inputmode:'decimal'});
  return el('div',{class:'review-form'},el('b',{text:'7. Digital twin: your field observations'}),
    el('p',{class:'muted',text:'The twin re-runs the model from what you observed. There are no defaults: enter your own numbers (0 for a shift you did not see).'}),
    el('div',{class:'jc-row'},field('Observed adoption share (0 to 1)',num('obs','0','1','0.01')),field('Change in trust (−1 to 1)',num('trust','-1','1','0.01')),field('Change in barriers (−1 to 1)',num('barrier','-1','1','0.01'))),
    field('Observed adoption over time (optional, 3 or more values, comma-separated)',draftInput('series',{placeholder:'e.g. 0.05, 0.08, 0.12, 0.2'})),
    el('div',{class:'actions'},el('button',{type:'button',class:'btn primary',disabled:journeyLocked(),onclick:()=>{
      const d=state.journeyDraft, read=key=>d[key]===undefined||String(d[key]).trim()===''?null:Number(d[key]);
      const body={observed_adoption:read('obs'),trust_shift:read('trust'),barrier_shift:read('barrier')};
      if(Object.values(body).some(v=>v===null||!Number.isFinite(v))){state.journeyError='Enter all three observations: adoption share, change in trust and change in barriers.';rerenderJourney();return;}
      if(String(d.series||'').trim()){const s=String(d.series).split(',').map(x=>Number(x.trim()));if(s.length<3||s.some(v=>!Number.isFinite(v))){state.journeyError='The series needs 3 or more numbers separated by commas.';rerenderJourney();return;}body.observed_series=s;}
      journeyAction(()=>post('/stages/digital',body),null);
    }},icon('play'),'Run the digital twin with these observations')));
}
// The engine checks each reply against its own results: numbers it never produced and claims its models cannot make.
function checkCallout(found){
  const parts=[];
  if(found.unverified_numbers?.length)parts.push(`mentions numbers the engine did not produce (${found.unverified_numbers.join(', ')})`);
  if(found.claim_words?.length)parts.push(`uses claims the illustrative models cannot support (${found.claim_words.map(w=>'“'+w+'”').join(', ')})`);
  return callout('warn','alert',`Check this reply: it ${parts.join(' and ')}. Rely on the journey card and the engine's results, not on these.`);
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
  items.push({section:'Tools',label:'Guided tour',desc:'The whole journey with Back and Next, on sample or your own data',slash:'/tour',pick:startTour});
  items.push({section:'Tools',label:'Start a journey',desc:'Field notes to a policy draft, 13 stages, step by step',slash:'/journey',pick:()=>startJourney()});
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
  if(!a.configurable&&a.personal)box.append(personalSettings(a));
  if(a.configurable){
    const provider=el('select',{'aria-label':'AI provider'},a.providers.map(name=>el('option',{value:name,text:name})));
    provider.value=a.provider||'anthropic';
    const key=el('input',{type:'password',placeholder:a.available?'API key (leave blank to keep)':'API key','aria-label':'API key',autocomplete:'off'});
    let model=el('input',{placeholder:'Model (optional)','aria-label':'Model',value:a.available?a.model:''});
    const note=el('span',{class:'small muted'});
    // With a local Ollama, pick from the models it has, labelled from NDIM's benchmarks (Tiny ... NDIM-tuned).
    if(a.provider==='ollama')api('/agent/models').then(data=>{
      if(!data.models?.length){if(data.error)note.textContent=data.error;return;}
      const hint=el('span',{class:'small muted'});
      const pick=el('select',{'aria-label':'Model',onchange:()=>{hint.textContent=data.models.find(m=>m.name===pick.value)?.note||'';}},
        data.models.map(m=>el('option',{value:m.name,text:`${m.label?m.label+' · ':''}${m.name} (${m.size_gb} GB)`})));
      pick.value=data.current;pick.dispatchEvent(new Event('change'));
      model.replaceWith(pick);model=pick;pick.closest('.row').after(hint);
    }).catch(()=>{});
    const keyRow=el('div',{class:'row'},key);
    const keyNote=el('span',{class:'small muted',text:'The key stays on this computer, in the NDIM data folder.'});
    const local=()=>{keyRow.hidden=keyNote.hidden=['ollama','lmstudio'].includes(provider.value);};  // local models need no key
    provider.addEventListener('change',local);local();
    box.append(el('label',{},'Provider',provider),keyRow,el('div',{class:'row'},model,el('button',{type:'button',class:'btn primary',onclick:async()=>{
      try{state.agent=await api('/agent/config',{method:'POST',body:JSON.stringify({provider:provider.value,api_key:key.value.trim()||null,model:model.value.trim()||null})});loadAgent();note.textContent=state.agent.available?'Saved. The assistant is on.':state.agent.reason;render();loadThreads();renderAISettings();}
      catch(err){note.textContent=err.message;}
    }},'Save')),note,keyNote);
  }
}
function personalSettings(a){
  const mine=state.personal;
  const defaults=Object.fromEntries(a.personal.map(p=>[p.provider,p.model]));
  const provider=el('select',{'aria-label':'Provider for your own key'},a.personal.map(p=>el('option',{value:p.provider,text:PERSONAL_LABELS[p.provider]||p.provider})));
  provider.value=mine?.provider||'openrouter';
  const model=el('input',{'aria-label':'Model','autocomplete':'off',value:mine?.model||''});
  const hint=()=>{model.placeholder=`Model (default ${defaults[provider.value]})`;};
  provider.addEventListener('change',hint);hint();
  const key=el('input',{id:'personal-key',type:'password',placeholder:mine?.key?'Key saved in this browser (type to replace)':'Your API key','aria-label':'Your API key',autocomplete:'off'});
  const note=el('span',{class:'small muted'});
  return el('div',{class:'personal-key'},
    el('div',{class:'menu-title'},'Use your own key',el('small',{text:mine?.key?`On: ${mine.provider}`:'Optional'})),
    el('span',{class:'small muted',text:'To chat with ChatGPT, Claude, DeepSeek or another model. The key stays in this browser and is sent with each message over HTTPS; NDIM uses it for that reply only and never stores it. Your messages then go to that company, which bills you. Do not paste field notes you may not share with it.'}),
    el('label',{},'Provider',provider),el('div',{class:'row'},key),
    el('div',{class:'row'},model,el('button',{type:'button',class:'btn primary',onclick:()=>{
      const typed=key.value.trim();
      if(!typed&&!(mine?.key&&mine.provider===provider.value)){note.textContent='Paste your API key first.';key.focus();return;}
      savePersonal({provider:provider.value,key:typed||mine.key,model:model.value.trim()||null});
    }},'Save'),mine?.key?el('button',{type:'button',class:'btn',onclick:()=>savePersonal(null)},'Remove'):null),
    el('span',{class:'small muted'},'New to this? ',el('a',{href:'https://openrouter.ai/keys',target:'_blank',rel:'noopener'},'Get an OpenRouter key'),', add credit there, then pick any model.'),
    note);
}
async function loadAgent(){
  try{state.agent=await api('/agent/status');}catch{state.agent=null;}
  paintAgent();
}
// Badge, greeting and disclaimer from what is known now (also straight after the own key changes, before any request).
function paintAgent(){
  const on=agentOn(), mine=state.personal?.key&&state.agent;
  const model=mine?(state.personal.model||state.agent.personal?.find(p=>p.provider===state.personal.provider)?.model||state.personal.provider):state.agent?.model;
  $('model-badge').hidden=!on;$('model-badge').textContent=on?(mine?`${model} · your key`:(state.agent.model_label||model)):'';$('model-badge').title=on?model:'';
  document.querySelector('.welcome p').textContent=on?'Ask a research question, explore the manual, or plan an experiment.':'What would you like to investigate?';
  document.querySelector('.disclaimer').textContent=on?`Answers are written by ${mine?model:(state.agent.model_label||model)}${mine?', with your own key':''}. Scientific results come only from NDIM's local tools, and nothing runs until you click Run.`:'NDIM runs local scientific tools, not an AI model. Scores are heuristics and scenarios are illustrative, so check them against the evidence.';
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
  if(!state.personal?.key&&state.agent?.personal&&MODEL_WISH.test(text)&&MODEL_NAME.test(text))return aboutModels(text);
  // Labs keep their fixed question and check, so they plan directly even when the assistant is on.
  if(agentOn()&&!state.lesson)return sendAgent(text);
  if(ABOUT.test(text))return aboutNDIM(text);
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
// Without the assistant, "tell me about NDIM" or "help" is not a research question: answer with fixed text and the
// engine's own journey intro instead of asking for evidence to plan an experiment.
const ABOUT=/^(help|hi|hello|hey|start|\?)\b|what can (you|it|ndim|nidm) do\??$|how (do i (use|start|begin)|does (this|it|ndim|nidm) work)\b|\b(about|what is|what's|explain|introduce|who are)\b.*\b(ndim|nidm|this tool|this app)\b|\b(about|are) you\??$|^(ndim|nidm)\??$/i;
async function aboutNDIM(text){
  pushLocal({role:'user',text});
  if(!state.journeyGuide){try{state.journeyGuide=await api('/engine/journey/stages');}catch{}}
  const intro=state.journeyGuide?.intro;
  pushLocal({role:'ai',
    text:'NDIM, the Narrative Diffusion and Inoculation Model, works from your field evidence (interview excerpts, field notes). It checks each record, scores trust, barriers and themes with a keyword heuristic, runs illustrative, uncalibrated adoption scenarios and drafts messages and a policy draft for your review, with an audit trail. No AI model is connected here, so this reply is fixed text: NDIM runs its own tools and you decide at each step.',
    node:intro?el('div',{class:'md',html:markdown(intro)}):null,
    actions:[{label:'Start a journey',icon:'flask',primary:true,run:()=>startJourney()},
             {label:'Use the sample field notes',icon:'file',run:useSample}]});
}
// "Can I use ChatGPT / Claude / DeepSeek?": a fixed answer with the own-key option, before any model is asked.
const MODEL_NAME=/\b(chat ?gpt|gpt[\w.-]*|openai|claude|anthropic|deepseek|gemini|openrouter|llama|mistral|grok|qwen)\b/i;
const MODEL_WISH=/\b(use|using|switch|want|prefer|connect|try|instead|change|via|through|with|can (i|you|it|ndim)|does (it|ndim))\b/i;
function aboutModels(text,{fromAgent=false}={}){
  pushLocal({role:'user',text});
  const builtIn=state.agent.available?`NDIM's own assistant runs on ${state.agent.model_label||state.agent.model}${/^@cf\//.test(state.agent.model)?', on Cloudflare, free within a daily allowance':''}.`:'This NDIM engine has no assistant model of its own switched on.';
  pushLocal({role:'ai',text:`${builtIn} To chat with ChatGPT, Claude, DeepSeek or another model instead, add your own API key. It stays in this browser, NDIM uses it only for your replies, and that company bills you. OpenRouter is the simplest: one key reaches DeepSeek, GPT, Claude, Gemini and many more.`,
    actions:[{label:'Add your own key',icon:'plug',primary:true,run:openKeySettings},
             ...(state.agent.available?[{label:`Ask NDIM's assistant instead`,icon:'send',run:()=>{state.local=[];render();sendAgent(text);}}]:[])]});
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
function setStreaming(on){state.streaming=on;$('send').disabled=on;$('send').title=on?'NDIM is answering…':'Send (Enter)';rerenderJourney();}
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
      await syncJourney(chat);
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
    const response=await fetch(apiBase+'/agent/chat',{method:'POST',headers:headers(personalHeaders()),body:JSON.stringify({workspace_id:state.workspace,thread_id:threadId,message:text,evidence:ev,settings,hidden})});
    if(!response.ok){const message=await errorText(response);typing.remove();body.append(errorCallout(message));setStreaming(false);state.queuedNotes=[];if(!hidden){$('prompt').value=text;autosize();}return;}
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
          if(event.meta?.journey){try{await syncJourney(await api(threadURL(threadId)));}catch{}$('journey-card')?.remove();body.append(journeyCard());}
          if(event.meta?.run_id&&!event.meta.reference){
            try{const run=await api(runsURL(event.meta.run_id));if(!state.runs.some(item=>item.run_id===run.run_id))state.runs.push(run);body.append(runCard(run));}catch{}
          }
        }else if(event.type==='check'){
          if(segment)segment.innerHTML=markdown(segmentText);
          body.append(checkCallout(event));
        }else if(event.type==='error'){
          typing.remove();body.append(errorCallout(event.message));
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

// ---------- learning: researchers teach the assistant ----------
// A thumbs-up approves a reply as written, Correct replaces it with the researcher's words, a thumbs-down alone is only
// logged. NDIM recalls what it was taught in its next answers; nothing is learned from replies nobody checked. With
// online sync on (off by default), only answers marked for sharing leave this computer, never questions or evidence.
const feedbackURL = id => threadURL(state.threadId)+'/messages/'+encodeURIComponent(id)+'/feedback';
async function sendFeedback(message,body){
  state.feedbackError.delete(message.id);
  try{
    const result=await api(feedbackURL(message.id),{method:'POST',body:JSON.stringify(body)});
    message.feedback={rating:body.rating,kind:result.kind,share:result.share,blocked:result.share_blocked};
    state.correcting.delete(message.id);
    if(state.panel.open&&state.panel.tab==='learning')renderLearning();
  }catch(err){state.feedbackError.set(message.id,err.message);}
  renderMessages();
}
function feedbackBar(message){
  if(!agentOn()||state.agent?.learning===false)return null;  // hosted engines do not learn (agent.py _learning_allowed)
  const fb=message.feedback, error=state.feedbackError.get(message.id);
  if(state.correcting.has(message.id)){
    const draft=state.correctionDrafts.get(message.id)??message.content;
    const area=el('textarea',{rows:'5',maxlength:'8000','aria-label':'Corrected answer',oninput:e=>state.correctionDrafts.set(message.id,e.target.value)});area.value=draft;
    const share=el('input',{type:'checkbox'});
    return el('div',{class:'review-form'},el('b',{text:'Write the answer NDIM should have given'}),
      el('small',{class:'muted',text:'NDIM uses your answer for similar questions from now on, and it becomes a training example.'}),area,
      el('label',{class:'jc-choice'},share,el('span',{text:'Share this answer when online sync is on (your question and notes never leave this computer)'})),
      error?callout('error','alert',error):null,
      el('div',{class:'actions'},el('button',{type:'button',class:'btn ghost',onclick:()=>{state.correcting.delete(message.id);renderMessages();}},'Cancel'),
        el('button',{type:'button',class:'btn primary',onclick:()=>{const text=(state.correctionDrafts.get(message.id)??message.content).trim();
          if(text.length<2)return;sendFeedback(message,{rating:'down',correction:text,share:share.checked});}},icon('check'),'Save correction')));
  }
  if(fb){
    const label=fb.kind==='correction'?'Your correction was learned':fb.kind==='answer'?'Approved: NDIM will reuse this answer':'Marked not helpful (not learned)';
    return el('div',{class:'fb-bar done'},icon(fb.kind==='flagged'?'x':'check'),el('span',{text:label+(fb.share?' · marked for sharing':'')}),
      fb.blocked?el('small',{class:'muted',text:' '+fb.blocked}):null,
      el('button',{type:'button',class:'btn ghost',onclick:()=>{state.correcting.add(message.id);renderMessages();}},icon('pencil'),'Correct'));
  }
  return el('div',{class:'fb-bar'},
    el('button',{type:'button',class:'btn ghost',title:message.check?'This reply has a warning: correct it instead':'Approve this answer',disabled:!!message.check,onclick:()=>sendFeedback(message,{rating:'up'})},'👍'),
    el('button',{type:'button',class:'btn ghost',title:'Not helpful',onclick:()=>sendFeedback(message,{rating:'down'})},'👎'),
    el('button',{type:'button',class:'btn ghost',onclick:()=>{state.correcting.add(message.id);renderMessages();}},icon('pencil'),'Correct'),
    error?el('small',{class:'muted',text:error}):null);
}
async function renderLearning(){
  const box=$('panel-learning');
  let data, sync;
  try{[data,sync]=await Promise.all([api('/agent/learning'),api('/agent/learning/sync')]);}catch(err){box.replaceChildren(callout('error','alert',err.message));return;}
  if(data.available===false){
    box.replaceChildren(el('h3',{text:'Feedback'}),
      el('p',{text:'In the NDIM desktop app, NDIM learns from you: 👍 approves a reply, Correct replaces it with your wording, and your team can add local terms (for example imbabura = improved cookstove). NDIM recalls them in later answers, and enough of them can train a new local model version.'}),
      el('p',{class:'muted',text:'This online demo is shared by everyone, so learning is switched off here: one visitor\'s corrections must not change what NDIM tells the others.'}));
    return;
  }
  const term=el('input',{placeholder:'Term, e.g. imbabura',maxlength:'120'}), meaning=el('input',{placeholder:'Meaning, e.g. improved cookstove',maxlength:'600'});
  const usable=data.usable_examples, ready=data.fine_tune_ready_at;
  box.replaceChildren(
    el('p',{text:`NDIM has learned ${data.lessons.answer} approved answer(s) and ${data.lessons.correction} correction(s) from your team, and ${data.terms} term(s). It recalls them in its answers straight away.`}),
    el('p',{class:'muted',text:usable>=ready?'There are enough examples to fine-tune a new model version.':`Fine-tuning a new model version needs about ${ready} examples (${usable} so far).`}),
    el('b',{text:'Your team’s terms'}),
    el('div',{class:'jc-row'},el('label',{class:'jc-field'},term),el('label',{class:'jc-field'},meaning),
      el('button',{type:'button',class:'btn',onclick:async()=>{if(!term.value.trim()||meaning.value.trim().length<2)return;
        await api('/agent/learning/terms',{method:'POST',body:JSON.stringify({term:term.value,meaning:meaning.value})});renderLearning();}},icon('plus'),'Add')),
    el('ul',{class:'learn-list'},data.term_list.map(t=>el('li',{},el('span',{},el('b',{text:t.term}),' = '+t.meaning),forgetButton(t.id)))),
    el('b',{text:'What NDIM learned from replies'}),
    data.items.length?el('ul',{class:'learn-list'},data.items.map(item=>el('li',{},
      el('span',{},el('span',{class:'tag',text:{answer:'approved',correction:'corrected',flagged:'not helpful'}[item.kind]}),item.share?el('span',{class:'tag',text:'marked for sharing'}):null,
        el('small',{class:'muted',text:' '+(item.question||'(after a journey step)').slice(0,120)}),el('p',{text:item.answer.slice(0,400)})),
      el('span',{class:'learn-actions'},item.kind!=='flagged'?shareButton(item.id,item.share):null,forgetButton(item.id))))):
      el('p',{class:'muted',text:'Nothing yet. Use 👍, 👎 or Correct under NDIM’s replies.'}),
    syncSection(sync));
}

// ---------- online sync: only answers the researcher marked for sharing leave this computer ----------
// Off by default. The list shows exactly what will be sent (only the answer text) and what is held back, and why.
function shareButton(id,shared){
  return el('button',{type:'button',class:'btn ghost small',title:shared?'Stop sharing this answer (it is deleted online at the next sync)':'Share this answer when online sync is on',
    onclick:async()=>{await api('/agent/learning/'+encodeURIComponent(id)+'/share',{method:'POST',body:JSON.stringify({share:!shared})});renderLearning();}},shared?'Stop sharing':'Share');
}
function syncSection(sync){
  const head=el('b',{text:'Online sync'});
  if(!sync.available)return el('div',{class:'sync-box'},head,el('p',{class:'muted',text:'Online sync is available in the desktop app only. What NDIM learns here stays here.'}));
  const save=async(body,button)=>{if(button)button.disabled=true;try{await api('/agent/learning/sync',{method:'PUT',body:JSON.stringify(body)});}catch(err){state.syncError=err.message;}renderLearning();};
  const toggle=el('input',{type:'checkbox',id:'sync-toggle',checked:sync.enabled});
  const key=el('input',{type:'password',placeholder:'Access key from your research team',maxlength:'300','aria-label':'Access key',autocomplete:'off'});
  toggle.addEventListener('change',()=>{state.syncError=null;
    if(toggle.checked&&!sync.has_token&&!key.value.trim()){toggle.checked=false;state.syncError='Enter the access key your research team was given, then turn sync on.';renderLearning();return;}
    save(toggle.checked?{enabled:true,...(key.value.trim()?{token:key.value.trim()}:{})}:{enabled:false});});
  const counts={shared:0,'will share':0,'held back':0};sync.outbox.forEach(row=>counts[row.status]++);
  const last=sync.last_sync;
  return el('div',{class:'sync-box'},head,
    el('p',{class:'muted',text:'When sync is on, the answers you mark for sharing are sent to the NDIM sync service after a privacy check, and answers other researchers shared are used here, below your own team’s answers. Only the answer text is sent: never your questions, field notes, workspace or names. Everything NDIM learned stays on this computer either way.'}),
    el('label',{class:'jc-choice'},toggle,el('span',{text:sync.enabled?'Online sync is on':'Online sync is off'})),
    !sync.has_token?el('label',{class:'jc-field'},key):null,
    state.syncError?callout('error','alert',state.syncError):null,
    last&&last.error?callout('warn','alert','Last sync failed: '+last.error):null,
    el('p',{class:'muted',text:`${counts.shared} shared · ${counts['will share']} waiting to be shared · ${counts['held back']} held back · ${sync.others} answer(s) from other researchers`+
      (last?` · last sync ${new Date(last.at).toLocaleString()}`:'')}),
    sync.withdraw?el('p',{class:'muted',text:`${sync.withdraw} answer(s) you stopped sharing will be deleted online at the next sync${sync.enabled?'':' (turn sync on to delete them)'}.`}):null,
    sync.enabled?el('button',{type:'button',class:'btn',onclick:e=>{e.target.disabled=true;api('/agent/learning/sync/run',{method:'POST'}).catch(err=>{state.syncError=err.message;}).finally(renderLearning);}},'Sync now'):null,
    el('b',{text:'What will be shared'}),
    sync.outbox.length?el('ul',{class:'learn-list',id:'sync-outbox'},sync.outbox.map(row=>el('li',{},
      el('span',{},el('span',{class:'tag'+(row.status==='held back'?' warn':''),text:row.status}),el('p',{text:row.answer}),
        row.reasons.length?el('small',{class:'muted',text:'Kept on this computer: '+row.reasons.join(' ')}):null),
      shareButton(row.id,true)))):
      el('p',{class:'muted',text:'Nothing is marked for sharing. Use Share on an approved or corrected answer above.'}));
}
function forgetButton(id){return el('button',{type:'button',class:'icon-btn',title:'Forget this','aria-label':'Forget this',onclick:async()=>{await api('/agent/learning/'+encodeURIComponent(id),{method:'DELETE'});renderLearning();}},icon('trash'));}

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
  for(const tab of ['guide','workbench','library','learning']){
    $('tab-'+tab).setAttribute('aria-selected',String(state.panel.tab===tab));
    $('panel-'+tab).hidden=state.panel.tab!==tab;
  }
  if(state.panel.tab==='workbench')renderWorkbench();else if(state.panel.tab==='learning')renderLearning();
  else if(state.panel.tab==='guide')renderGuide();else renderLibrary();
}
function paramForm(values,{skill}={}){
  const range=(name,label,value)=>{const out=el('output',{text:Number(value).toFixed(2)});const input=el('input',{type:'range',name,min:'0',max:'1',step:'0.01',value:String(value),oninput:()=>out.textContent=Number(input.value).toFixed(2)});return el('label',{class:'full'},el('span',{},label,' ',out),input);};
  const select=(name,label,value,options)=>{const node=el('select',{name},options.map(([v,t])=>el('option',{value:v,text:t})));node.value=value;return el('label',{},label,node);};
  return el('form',{class:'form'},
    skill!==undefined?select('skill','Workflow',skill==='auto'?'scenario':skill,[['evidence','Evidence interpretation'],['scenario','Scenario comparison'],['sensitivity','Sensitivity experiment']]):null,
    select('model','Model',values.model,[['compartmental','Compartmental'],['hybrid','Hybrid'],['agent_based','Agent-based (network)']]),
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
// ---------- Guided tour: Back / Next through the real journey, with sample or own data ----------
// The coach only narrates and points: every action is the researcher's click in the journey card, and every result is
// the engine's. Progress is kept per chat in this browser, so a reload carries on where it stopped.
const TOUR_STEPS=[
  {id:'choose'},
  {id:'question',title:'Your research question',what:'The journey starts from one question. NDIM uses it word for word in every result and in the policy draft, so it is worth reading carefully.',
    move:'Read the question in the card below, edit it if you like, then click Confirm question.',done:j=>!!j},
  {id:'notes',title:'Add the field notes',what:'Each note needs its place, source, period, language and permission. Nothing reaches a model yet: you decide in the next step.',
    move:t=>t.dataset?'The tour filled in the synthetic notes. Read them, then click Add to journey.':'Check your notes in the card (fill any empty place, source or period, and set the permission), then click Add to journey.',done:j=>j&&j.records.length>0},
  {id:'gate',stage:'repository',title:'The gate: you decide what counts as evidence',what:'NDIM checked each note for missing details, personal data and instruction-like text. It flags; it never edits. Only the notes you accept reach any model.',
    move:'Choose Accept or Reject for each record, then click Save decisions.'},
  {stage:'encoding',what:'NDIM cannot read meaning, so it counts words from fixed lists and turns the counts into a trust score and a barrier score for each note.',math:'guide-encoding',notice:true},
  {stage:'compartmental',what:'The population is split into five shares: not yet reached, misinformed, convinced, inoculated and settled adopters. Each day people move between them; adoption is convinced + inoculated + settled.',math:'guide-compartmental'},
  {stage:'agents',what:'1,000 simulated households on an assumed village network adopt through media, neighbours and outreach. Twenty runs show the range chance alone produces, and a robustness check tries seven network shapes.',math:'guide-network'},
  {stage:'digital',what:'The twin re-runs the model from what was observed in the field. There are no defaults: the numbers are your decision.',math:'guide-twin',twin:true,
    move:t=>t.dataset?'This is synthetic data, so the tour suggests teaching numbers. Fill them in with the button below (or type your own), then click Run the digital twin.':'Enter the adoption share you observed and the changes in trust and barriers you saw (0 if none), then run the twin.'},
  {stage:'bayes',what:'A Bayesian update moves a stated starting belief about trust and barriers towards what your notes and field changes say. More notes move it further.',math:'guide-bayes'},
  {stage:'rl',what:'Four illustrative actions are scored with fixed, assumed lifts and costs. The ranking restates those assumptions: it is not a recommendation.',math:'guide-ranking'},
  {stage:'graph',what:'A map of which places, themes and signals occur together. The card also offers the optional regional analysis.'},
  {stage:'inoculation',what:'NDIM drafts a pre-bunk, a refutation and a short counter-message for you to review and edit, and adds them to the twin. Nothing is ever sent.',math:'guide-inoculation'},
  {stage:'policy',what:'Assembles options for your team to discuss, with an evidence grade. It runs only when you approve it.',move:'Click Approve export in the card.',math:'guide-grade'},
  {id:'finish'}];
const TOUR_KEY='ndim-tour';
function saveTour(){try{state.tour?localStorage.setItem(TOUR_KEY,JSON.stringify({threadId:state.tour.threadId,datasetId:state.tour.dataset?.id||null,own:!!state.tour.own,step:state.tour.step})):localStorage.removeItem(TOUR_KEY);}catch{}}
async function restoreTour(threadId){
  let saved=null;try{saved=JSON.parse(localStorage.getItem(TOUR_KEY)||'null');}catch{}
  if(!saved||saved.threadId!==threadId)return;
  const samples=await loadSamples();
  state.tour={threadId,step:saved.step,own:saved.own,dataset:samples?.datasets.find(d=>d.id===saved.datasetId)||null};
  renderTour();
}
async function loadSamples(){if(!state.samples){try{state.samples=await api('/engine/samples');}catch{state.samples=null;}}return state.samples;}
async function startTour(){
  closePanel();newChat();
  state.tour={step:0,dataset:null,own:false,threadId:null};state.tourRecords=null;
  await loadSamples();renderTour();
}
function exitTour(){state.tour=null;state.tourRecords=null;saveTour();renderTour();}
async function tourWithData(dataset,own){
  state.tourRecords=dataset?dataset.records:own;
  await startJourney(dataset?dataset.question:'',dataset?.topic_id||'clean_cooking');
  state.tour={step:1,dataset:dataset||null,own:!dataset,threadId:state.threadId};
  saveTour();render();
}
function stageRow(j,id){return j?.stages.find(row=>row.id===id);}
function tourStep(t){
  const step=TOUR_STEPS[t.step], j=state.journey;
  const row=step.stage?stageRow(j,step.stage):null;
  const title=step.title||(row?`${row.title} (journey stage ${row.number} of 13)`:'');
  const done=step.done?!!step.done(j):row?row.status==='done':step.id==='finish';
  const move=typeof step.move==='function'?step.move(t):step.move||(row?`Click “Run ${row.number}. ${row.title}” in the card.`:'');
  return {step,title,done,move};
}
function tourShowMe(){
  const card=$('journey-card');if(!card)return;
  card.scrollIntoView({block:'center',behavior:'smooth'});
  const target=card.querySelector('.review-form .btn.primary, .actions .btn.primary');
  if(target){target.classList.remove('pulse');void target.offsetWidth;target.classList.add('pulse');}
}
function parseCSV(text){
  const rows=[];let row=[],cell='',quoted=false;
  for(let i=0;i<text.length;i++){
    const c=text[i];
    if(quoted){if(c==='"'&&text[i+1]==='"'){cell+='"';i++;}else if(c==='"')quoted=false;else cell+=c;}
    else if(c==='"')quoted=true;
    else if(c===','){row.push(cell);cell='';}
    else if(c==='\n'||c==='\r'){if(c==='\r'&&text[i+1]==='\n')i++;row.push(cell);if(row.some(v=>v.trim()))rows.push(row);row=[];cell='';}
    else cell+=c;
  }
  row.push(cell);if(row.some(v=>v.trim()))rows.push(row);
  return rows;
}
// Column names accepted from exports; author or handle columns are never read (the journey keeps no names).
const CSV_COLUMNS={text:['text','note','story','content','message','post','body','narrative'],admin_unit:['place','admin_unit','location','district','sector','region'],
  source_name:['source','source_name','channel','platform'],period:['period','date','month','quarter','collected'],language:['language','lang']};
async function readOwnData(file){
  if(!/\.(csv|txt)$/i.test(file.name))throw Error('Upload a .csv file (UTF-8). Download the template to see the columns.');
  if(file.size>2_000_000)throw Error('This file is over 2 MB. Upload up to 50 notes at a time.');
  const rows=parseCSV(await file.text());
  if(rows.length<2)throw Error('The file needs a header row and at least one note.');
  const header=rows[0].map(h=>h.trim().toLowerCase());
  const col=key=>header.findIndex(h=>CSV_COLUMNS[key].includes(h));
  const at={text:col('text'),admin_unit:col('admin_unit'),source_name:col('source_name'),period:col('period'),language:col('language')};
  if(at.text<0)throw Error(`No text column found. Name it one of: ${CSV_COLUMNS.text.join(', ')}.`);
  const notes=rows.slice(1).map(r=>{const get=k=>at[k]>=0?(r[at[k]]||'').trim():'';const lang=get('language').toLowerCase();
    return {text:get('text'),admin_unit:get('admin_unit'),source_name:get('source_name'),period:get('period'),language:['en','rw','fr'].includes(lang)?lang:lang?'other':'en'};}).filter(n=>n.text);
  if(!notes.length)throw Error('No rows with text were found.');
  if(notes.length>50)throw Error(`The file has ${notes.length} notes; a journey takes up to 50. Split the file and run one journey per part.`);
  return notes;
}
function downloadTemplate(){
  const csv='text,place,source,period,language\n"Paste one story or field note per row, unchanged.",Kicukiro / Niboye,Field team interview 1,2026-Q2,en\n';
  const a=el('a',{href:URL.createObjectURL(new Blob([csv],{type:'text/csv'})),download:'ndim-notes-template.csv'});document.body.append(a);a.click();a.remove();
}
function chooseData(){
  const s=state.samples;
  if(!s)return [callout('error','alert','The sample datasets could not be loaded from the engine.')];
  const topics=[...new Set(s.datasets.map(d=>d.topic))];
  const file=el('input',{type:'file',accept:'.csv,text/csv',hidden:true,onchange:async e=>{
    const f=e.target.files[0];e.target.value='';if(!f)return;
    try{await tourWithData(null,await readOwnData(f));}catch(err){state.tourError=err.message;renderTour();}}});
  return [
    el('p',{text:'Every step uses the real engine. Pick ready-made synthetic notes, or bring your own.'}),
    el('div',{class:'tour-topics'},topics.map(topic=>el('div',{class:'tour-topic'},el('b',{text:topic}),
      ...s.datasets.filter(d=>d.topic===topic).map(d=>el('button',{type:'button',class:'btn'+(d.level==='simple'?' primary':''),title:d.summary,onclick:()=>tourWithData(d)},
        d.level==='simple'?'Simple':'Thought-provoking',el('small',{text:' · '+d.title})))))),
    el('p',{class:'small muted',text:s.topic_note+' '+s.note}),
    el('div',{class:'tour-own'},el('b',{text:'Use my own data'}),
      el('div',{class:'actions'},
        el('button',{type:'button',class:'btn',onclick:()=>tourWithData(null,null)},icon('pencil'),'Type or paste my notes'),
        el('button',{type:'button',class:'btn',onclick:()=>file.click()},icon('clip'),'Upload a CSV (up to 50 notes)'),
        el('button',{type:'button',class:'btn ghost',onclick:downloadTemplate},icon('down'),'CSV template'),file),
      el('p',{class:'small muted',text:'Columns: text (required), place, source, period, language. Names of people or accounts are never read. You set the permission for every note in the next steps.'}))];
}
function renderTour(){
  const box=$('tour');if(!box)return;
  const t=state.tour;
  const visible=t&&(t.step===0||t.threadId===state.threadId);
  box.hidden=!visible;
  if(!visible){box.replaceChildren();return;}
  const total=TOUR_STEPS.length-2, n=Math.min(Math.max(t.step,0),total);
  const head=el('div',{class:'tour-head'},el('span',{class:'skill'},icon('cap'),'Guided tour'),
    t.dataset?el('span',{class:'tag',text:`${t.dataset.topic} · ${t.dataset.level} · synthetic`}):t.own?el('span',{class:'tag',text:'your own data'}):null,
    el('span',{class:'tour-count',text:t.step===0?'Choose your data':t.step>total?'Finished':`Step ${n} of ${total}`}),
    el('button',{type:'button',class:'icon-btn','aria-label':'Leave the tour',title:'Leave the tour',onclick:exitTour},icon('x')));
  const bar=el('div',{class:'tour-bar'},el('i',{style:`width:${Math.round(100*n/total)}%`}));
  const parts=[head,bar];
  if(state.tourError){parts.push(callout('error','alert',state.tourError));state.tourError=null;}
  if(t.step===0){parts.push(el('h4',{text:'Choose your data'}),...chooseData());box.replaceChildren(...parts);return;}
  const {step,title,done,move}=tourStep(t);
  if(step.id==='finish'){
    const other=t.dataset&&state.samples?.datasets.find(d=>d.topic===t.dataset.topic&&d.level!==t.dataset.level);
    parts.push(el('h4',{text:'You have run the whole journey'}),
      el('p',{text:'From notes to a policy draft: the gate, the scores, two models, the twin, the update, the ranking, the inoculation drafts and an evidence grade. Every number came from the engine; every decision was yours.'}),
      el('div',{class:'actions'},
        other?el('button',{type:'button',class:'btn primary',onclick:()=>{state.tour.step=0;tourWithData(other);}},icon('play'),`Try the ${other.level} version`):null,
        el('button',{type:'button',class:'btn',onclick:startTour},icon('file'),'Another topic or my own data'),
        el('button',{type:'button',class:'btn',onclick:()=>openGuide()},icon('cap'),'All the math'),
        el('button',{type:'button',class:'btn ghost',onclick:exitTour},'Close the tour')));
    box.replaceChildren(...parts);return;
  }
  parts.push(el('h4',{text:title}),el('p',{text:step.what}));
  if(step.notice&&done&&t.dataset?.notice)parts.push(el('div',{class:'callout'},el('span',{},el('b',{text:'What to notice: '}),t.dataset.notice)));
  parts.push(el('p',{class:'tour-move'},done?el('span',{class:'ok'},icon('check'),' Done. Read the result in the card, then click Next.'):el('span',{},el('b',{text:'Your move: '}),move)));
  const extras=[];
  if(step.twin&&!done&&t.dataset){const tw=t.dataset.twin;extras.push(el('button',{type:'button',class:'btn',onclick:()=>{Object.assign(state.journeyDraft,{obs:String(tw.obs),trust:String(tw.trust),barrier:String(tw.barrier)});rerenderJourney();tourShowMe();}},icon('pencil'),`Fill in the teaching numbers (${tw.obs}, ${tw.trust}, ${tw.barrier})`));}
  if(step.math)extras.push(el('button',{type:'button',class:'btn ghost',onclick:()=>openGuide(step.math)},icon('cap'),'The math'));
  parts.push(el('div',{class:'actions tour-nav'},
    el('button',{type:'button',class:'btn',disabled:t.step<=1,onclick:()=>{state.tour.step--;saveTour();renderTour();}},icon('back'),'Back'),
    done?null:el('button',{type:'button',class:'btn',onclick:tourShowMe},icon('search'),'Show me'),
    ...extras,
    el('span',{class:'spacer'}),
    el('button',{type:'button',class:'btn primary'+(done?' pulse':''),disabled:!done,title:done?'':'Do this step in the card first',onclick:()=>{state.tour.step++;saveTour();renderTour();if(state.tour.step<TOUR_STEPS.length-1)tourShowMe();}},'Next',icon('chev'))));
  box.replaceChildren(...parts);
}
// ---------- How it works: tutorials and the math (engine /engine/math, written from the engine's code) ----------
const STAGE_MATH={encoding:'guide-encoding',compartmental:'guide-compartmental',agents:'guide-network',digital:'guide-twin',
  bayes:'guide-bayes',rl:'guide-ranking',inoculation:'guide-inoculation',policy:'guide-grade'};
const KATEX='https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/';
let katexReady=null;
function loadKatex(){
  if(window.katex)return Promise.resolve(true);
  katexReady??=new Promise(resolve=>{
    const script=el('script',{src:KATEX+'katex.min.js',onload:()=>resolve(true),onerror:()=>resolve(false)});
    document.head.append(el('link',{rel:'stylesheet',href:KATEX+'katex.min.css'}),script);
  });
  return katexReady;
}
function openGuide(sectionId){state.panel.guideOpen=sectionId||null;state.panel.guideScroll=!!sectionId;openPanel('guide');}
async function renderGuide(){
  const box=$('panel-guide');
  if(!state.panel.guide){
    box.replaceChildren(el('p',{class:'small muted',text:'Loading…'}));
    try{state.panel.guide=await api('/engine/math');}catch(err){box.replaceChildren(callout('error','alert',err.message));return;}
  }
  const g=state.panel.guide;
  const teach=(section)=>{$('prompt').value=`Teach me step ${section.number}, “${section.title}”, using its worked example. Go one idea at a time and check that I follow.`;autosize();$('prompt').focus();};
  const academy=(config.routes&&config.routes.academy)||'/academy';
  const sections=g.sections.map(section=>el('details',{class:'guide-step',id:section.id,open:state.panel.guideOpen===section.id,
      ontoggle:event=>{if(event.target.open)state.panel.guideOpen=section.id;else if(state.panel.guideOpen===section.id)state.panel.guideOpen=null;}},
    el('summary',{},el('b',{text:`${section.number}. ${section.title}`})),
    el('p',{text:section.why}),
    el('p',{class:'guide-label',text:'The model'}),
    ...section.formulas.map(tex=>el('div',{class:'guide-formula','data-tex':tex,text:tex})),
    el('table',{class:'guide-symbols'},el('tbody',{},section.symbols.map(([sym,meaning])=>el('tr',{},el('td',{text:sym}),el('td',{text:meaning}))))),
    section.derivation?.length?el('p',{class:'guide-label',text:'Derivation'}):null,
    section.derivation?.length?el('ol',{class:'guide-derivation'},section.derivation.map(step=>el('li',{},el('span',{text:step.text}),
      step.tex?el('div',{class:'guide-formula','data-tex':step.tex,text:step.tex}):null))):null,
    section.parameters?.length?el('p',{class:'guide-label',text:'Values NDIM uses'}):null,
    section.parameters?.length?el('p',{class:'small muted',text:section.parameters_note}):null,
    section.parameters?.length?el('table',{class:'guide-symbols guide-values'},el('tbody',{},section.parameters.map(([sym,value,meaning])=>el('tr',{},
      el('td',{class:/\\|[_^]/.test(sym)?'tex-inline':'','data-tex-inline':/\\|[_^]/.test(sym)?sym:null,text:sym}),el('td',{text:String(value)}),el('td',{text:meaning}))))):null,
    el('p',{class:'guide-label',text:'Worked example (the numbers, computed by the engine)'}),
    el('ol',{class:'guide-example'},section.example.map(line=>el('li',{text:line}))),
    callout('warn','alert',section.limits),
    el('div',{class:'actions'},el('button',{type:'button',class:'btn',onclick:()=>teach(section)},icon('spark'),'Ask NDIM to teach me this'))));
  box.replaceChildren(
    el('div',{},el('h3',{text:'How it works'}),el('p',{class:'sub',text:'Tutorials to try, and the math NDIM really runs.'})),
    el('p',{class:'guide-label',text:'Tutorials'}),
    el('button',{type:'button',class:'btn primary guide-tour',onclick:startTour},icon('play'),'Start the guided tour',el('small',{text:' · step by step, with sample or your own data'})),
    el('div',{class:'guide-labs'},
      ...state.lessons.map(lesson=>el('button',{type:'button',class:'btn',onclick:()=>{closePanel();startLab(lesson);}},icon('cap'),`Lab ${lesson.number} · ${lesson.title}`,el('small',{text:` ${lesson.duration}`}))),
      el('button',{type:'button',class:'btn',onclick:()=>{closePanel();startJourney();}},icon('flask'),'The full journey (13 stages)'),
      el('a',{class:'btn ghost',href:academy,target:'_blank',rel:'noopener'},icon('book'),'Learning Academy ↗')),
    el('p',{class:'guide-label',text:'The math, step by step'}),
    el('p',{class:'small',text:g.intro}),
    ...sections);
  const open=state.panel.guideOpen&&$(state.panel.guideOpen);
  if(open&&state.panel.guideScroll){open.scrollIntoView({block:'start'});state.panel.guideScroll=false;}
  if(await loadKatex())renderTex(box);
}
// Display formulas ([data-tex]) and inline symbols ([data-tex-inline]) with KaTeX; the source stays visible offline.
function renderTex(root){
  if(!window.katex)return;
  root.querySelectorAll('[data-tex]').forEach(node=>{try{window.katex.render(node.dataset.tex,node,{displayMode:true,throwOnError:false,strict:'ignore'});}catch{}});
  root.querySelectorAll('[data-tex-inline]').forEach(node=>{try{window.katex.render(node.dataset.texInline,node,{displayMode:false,throwOnError:false,strict:'ignore'});}catch{}});
}
async function loadTOC(){if(!state.panel.toc){try{state.panel.toc=(await api('/agent/library')).sections;}catch(err){state.panel.toc=[];}}return state.panel.toc;}
async function renderLibrary(){
  const box=$('panel-library');
  if(state.panel.section?.startsWith('guide-')){const id=state.panel.section;state.panel.section=null;openGuide(id);return;}
  if(state.panel.section){
    box.replaceChildren(el('p',{class:'small muted',text:'Loading…'}));
    try{
      const section=await api('/agent/library/'+encodeURIComponent(state.panel.section));
      const isTex=line=>/\\(frac|beta|theta|lambda|Phi|tau|kappa|alpha|gamma|sigma|rho|iota|mu|eta|delta|phi|text|min|max|operatorname|leftarrow|qquad|sum)\b|\^\{|_\{/.test(line);
      const blocks=section.text.split('\n').reduce((acc,line)=>{if(line.startsWith('• ')){const last=acc.at(-1);if(last?.tagName==='UL')last.append(el('li',{text:line.slice(2)}));else acc.push(el('ul',{},el('li',{text:line.slice(2)})));}
        else if(isTex(line))acc.push(el('div',{class:'guide-formula','data-tex':line,text:line}));else acc.push(el('p',{text:line}));return acc;},[]);
      box.replaceChildren(el('button',{type:'button',class:'back-btn',onclick:()=>{state.panel.section=null;renderLibrary();}},icon('back'),'Library'),
        el('div',{},el('p',{class:'sub',text:section.source_label}),el('h3',{text:section.title})),
        el('div',{class:'lib-section'},blocks),
        el('div',{class:'actions'},el('button',{type:'button',class:'btn',onclick:()=>{$('prompt').value=`Explain “${section.title}” from the ${section.source_label.toLowerCase()} in plain language.`;autosize();$('prompt').focus();}},icon('spark'),'Ask NDIM about this')));
      if(await loadKatex())renderTex(box);
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
  box.append(el('button',{type:'button',onclick:startTour},icon('play'),'Take the guided tour'));
  box.append(el('button',{type:'button',onclick:()=>startJourney()},icon('flask'),'Start a journey'));
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
  try{state.personal=JSON.parse(localStorage.getItem('ndim-personal-key')||'null');}catch{state.personal=null;}
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
