
/* Read-only public GitHub Stars import for the standalone prototype; facts remain source snapshots. */
(() => {
'use strict';
const starCategories=[...categories.filter(([id])=>id!=='all'),['unclassified','待分类 / 其他']];
const storageKey='ai-project-workbench-stars-v1';
const categoryName=id=>starCategories.find(([key])=>key===id)?.[1]||'待分类 / 其他';
function suggestCategory(repo,description,topics){
const text=[repo,description,...topics].join(' ').toLowerCase();
const rules=[
['security',/pyrit|garak|ai[- ]?safety|llm[- ]?security|prompt[- ]?injection|red[- ]?team/],
['eval',/promptfoo|ragas|deepeval|lm[-_]evaluation|llm[- ]?eval|ai[- ]?eval|llm[- ]?observability|langfuse/],
['training',/llama[-_]factory|axolotl|unsloth|fine[- ]?tun|finetun|model[- ]?training|vllm|sglang|llm[- ]?inference/],
['media',/comfyui|wan2|wan[- ]?video|diffusers|stable[- ]?diffusion|text[- ]?to[- ]?(image|video)|image[- ]?generation|video[- ]?generation/],
['knowledge',/graphiti|qdrant|milvus|weaviate|chroma|lightrag|graphrag|knowledge[- ]?graph|knowledge[- ]?base|retrieval[- ]?augmented|\brag\b|vector[- ]?database/],
['skills',/spec[-_]kit|agent[- ]?skills|claude[- ]?skills|ai[- ]?skills|ui[-_]ux[-_]pro/],
['agent',/langgraph|smolagents|autogen|crewai|openhands|openai\/codex|swe[- ]?agent|ai[- ]?agent|agentic|llm[- ]?agent|deepagents|opencode/],
['apps',/trendradar|dify|open[- ]?webui|anythingllm|ai[- ]?app|ai[- ]?assistant|llm[- ]?app/]
];
return rules.find(([,pattern])=>pattern.test(text))?.[0]||'unclassified';
}
function normalizeStar(entry,account,fetchedAt,origin){
if(!entry||typeof entry!=='object')throw new Error('清单中有无效的仓库记录。');
const raw=entry.repo&&typeof entry.repo==='object'?entry.repo:entry;
const full=raw.full_name||raw.repo;
if(typeof full!=='string'||!/^[-A-Za-z0-9_.]+\/[-A-Za-z0-9_.]+$/.test(full)||full.split('/').some(p=>p==='.'||p==='..'))throw new Error('清单中缺少有效的 owner/repo。');
const number=value=>typeof value==='number'&&Number.isFinite(value)&&value>=0?value:null;
const time=value=>typeof value==='string'&&Number.isFinite(Date.parse(value))?new Date(value).toISOString():null;
const topics=Array.isArray(raw.topics)?raw.topics.filter(t=>typeof t==='string'):[];
const description=typeof raw.description==='string'?raw.description:'';
const license=typeof raw.license==='string'?raw.license:raw.license?.spdx_id;
const id=raw.repository_id??raw.id;
const suggestion=suggestCategory(full,description,topics);
const manual=raw.classification_source==='manual'&&starCategories.some(([key])=>key===raw.category);
return {
repository_id:Number.isSafeInteger(id)&&id>0?id:null,
repo:full,name:full.split('/')[1],description,topics,
language:typeof raw.language==='string'?raw.language:null,
license:license&&license!=='NOASSERTION'?String(license):null,
stars:number(raw.stargazers_count??raw.stars),forks:number(raw.forks_count??raw.forks),
archived:typeof raw.archived==='boolean'?raw.archived:null,
pushed_at:time(raw.pushed_at),starred_at:time(entry.starred_at??raw.starred_at),
fetched_at:time(raw.fetched_at)||fetchedAt,
account:String(raw.account||account||'').slice(0,39),
origin:origin==='restore'?raw.origin||'file':origin,
suggested_category:suggestion,category:manual?raw.category:suggestion,
classification_source:manual?'manual':'rule',
personal_note:typeof raw.personal_note==='string'?raw.personal_note:''
};
}
const recordKey=p=>p.repository_id!==null?'id:'+p.repository_id:'repo:'+p.repo.toLowerCase();
function uniqueStars(records){
const result=[];
for(const record of records){
const index=result.findIndex(p=>recordKey(p)===recordKey(record)||p.repo.toLowerCase()===record.repo.toLowerCase());
if(index<0)result.push(record);else result[index]=record;
}
return result;
}
function decodeStarFile(value){
const source=Array.isArray(value)?value:value?.repositories;
if(!Array.isArray(source))throw new Error('请选择 GitHub API 的 JSON 数组，或研究台导出的 JSON 清单。');
return source.flat(1);
}
async function readStarPages(account,onProgress,signal){
if(!/^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/.test(account))throw new Error('请输入有效的 GitHub 用户名。');
const fetchedAt=new Date().toISOString();
const collected=[];
for(let page=1;;page++){
const url='https://api.github.com/users/'+encodeURIComponent(account)+'/starred?per_page=100&sort=created&direction=desc&page='+page;
const response=await fetch(url,{headers:{Accept:'application/vnd.github.star+json'},credentials:'omit',signal});
if(!response.ok){
if(response.status===403||response.status===429)throw new Error('GitHub API 暂时限制了请求（HTTP '+response.status+'）。请稍后重试，或导入已导出的 JSON。');
if(response.status===404)throw new Error('GitHub 用户不存在或公开资料不可读取。');
throw new Error('GitHub API 返回 HTTP '+response.status+'，本次读取未完成。');
}
const data=await response.json();
if(!Array.isArray(data))throw new Error('GitHub 返回的数据格式不符合预期。');
collected.push(...data.map(item=>normalizeStar(item,account,fetchedAt,'api')));
onProgress(page,collected.length);
const next=/(?:^|,)\s*<[^>]+>;\s*rel="next"/.test(response.headers.get('link')||'');
if(!next&&data.length<100)break;
}
return uniqueStars(collected);
}
/* UI */
let ledger=[];
let storageMessage='';
try{
const saved=localStorage.getItem(storageKey);
if(saved)ledger=uniqueStars(decodeStarFile(JSON.parse(saved)).map(p=>normalizeStar(p,'',new Date().toISOString(),'restore')));
}catch{storageMessage='本浏览器未能恢复本地清单。可重新读取或导入 JSON。';}
const view={records:[],selected:new Set(),query:'',category:'all',page:0,account:'hobbytp'};
let controller=null;
function attachCandidate(record){
let candidate=candidates.find(p=>(p.starMeta?.repository_id!=null&&p.starMeta.repository_id===record.repository_id)||p.repo.toLowerCase()===record.repo.toLowerCase());
if(candidate){
record.personal_note=candidate.note||record.personal_note;
candidate.starMeta=record;candidate.source='GitHub Stars · '+(record.account||'JSON 清单');
}else{
candidate={repo:record.repo,name:record.name,source:'GitHub Stars · '+(record.account||'JSON 清单'),note:record.personal_note,starMeta:record};candidates.push(candidate);
}
candidate.repo=record.repo;
return candidate;
}
ledger.forEach(attachCandidate);
const style=document.createElement('style');
style.textContent='.stars-toolbar{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0}.stars-toolbar input{flex:1;min-width:180px}.stars-summary{display:flex;gap:12px;flex-wrap:wrap;font-size:12px;color:var(--muted);margin:12px 0}.stars-table{min-width:710px}.stars-table td{padding:12px}.stars-table .stars-description{max-width:320px;font-size:12px;color:var(--muted);margin:4px 0}.stars-table select{max-width:160px}.stars-table small{font-size:10px;color:var(--muted)}.stars-notice{font-size:12px;line-height:1.8;background:var(--wash);border-radius:6px;padding:12px}.stars-pages{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:15px 0;font-size:12px}.stars-facts{display:grid;grid-template-columns:1fr 1fr;gap:12px;font-size:13px}.stars-facts b{display:block;font-size:11px;color:var(--muted);font-weight:500}.stars-source{font-size:11px;color:var(--muted);overflow-wrap:anywhere}.stars-file{display:none}@media(max-width:720px){.stars-facts{grid-template-columns:1fr}.stars-pages{flex-wrap:wrap}}';
document.head.append(style);
const importButton=document.createElement('button');importButton.className='button';importButton.textContent='↓ 导入 GitHub Stars';importButton.id='stars-import';el('add-project').parentElement.append(importButton);
const demoNote=document.querySelector('main > .demo-note');
if(demoNote)demoNote.textContent='示例表中的评分、变化与判断均为演示。GitHub Stars 导入的是仓库事实快照，存入当前浏览器的候选箱，可导出 JSON；持续监测和 AI 推荐尚未接入。';
function known(record){return ledger.some(p=>recordKey(p)===recordKey(record)||p.repo.toLowerCase()===record.repo.toLowerCase());}
function categoryOptions(value,all){return (all?'<option value="all">全部分类</option>':'')+starCategories.map(([id,label])=>'<option value="'+id+'"'+(value===id?' selected':'')+'>'+label+'</option>').join('');}
function matches(){const query=view.query.trim().toLowerCase();return view.records.filter(p=>(view.category==='all'||p.category===view.category)&&[p.repo,p.description,...p.topics].join(' ').toLowerCase().includes(query));}
function snapshotValue(value){return value===null||value===undefined?'未提供':esc(value);}
function calendar(value){return value?esc(value.slice(0,10)):'未提供';}
function selectRecords(records){
view.records=records.map(p=>{const previous=ledger.find(old=>recordKey(old)===recordKey(p)||old.repo.toLowerCase()===p.repo.toLowerCase());return previous?.classification_source==='manual'&&p.classification_source!=='manual'?{...p,category:previous.category,classification_source:'manual'}:p;});
view.selected=new Set(view.records.filter(p=>!known(p)).map(recordKey));view.query='';view.category='all';view.page=0;
}
function openImport(){
if(controller)return;
show('从 GitHub Stars 收集项目',
'<p>输入用户名，读取公开 Stars。你的 GitHub 收藏保持原状。</p><form id="stars-fetch-form"><label class="field">GitHub 用户名<input name="account" value="'+esc(view.account)+'" maxlength="39" required autocomplete="off"></label><div class="actions"><button class="button primary" type="submit" id="stars-fetch-button">读取公开 Stars</button><button class="button" type="button" id="stars-open-file">导入 JSON 清单</button>'+(ledger.length?'<button class="button" type="button" id="stars-show-saved">查看已保存 '+ledger.length+' 项</button>':'')+'</div></form><p id="stars-progress" class="muted" role="status">'+esc(storageMessage)+'</p><div class="stars-notice">读取 → 预览与分类 → 选择 → 加入候选箱。分类来自本地关键词规则，可以修改；活跃度、社区和持续性不会由 Stars 数量直接推算。</div><p class="stars-source"><a target="_blank" rel="noopener noreferrer" href="https://docs.github.com/en/rest/activity/starring#list-repositories-starred-by-a-user">公开 Stars API 说明 ↗</a></p>');
el('stars-fetch-form').addEventListener('submit',async event=>{
event.preventDefault();if(controller)return;
view.account=String(new FormData(event.target).get('account')).trim();
const active=new AbortController();controller=active;el('stars-fetch-button').disabled=true;el('stars-progress').textContent='正在读取第 1 页；完成前不会写入候选箱。';
try{
const records=await readStarPages(view.account,(page,count)=>{if(el('stars-progress'))el('stars-progress').textContent='已读取 '+page+' 页，共 '+count+' 条；仍在核对后续分页。';},active.signal);
if(active.signal.aborted)return;
selectRecords(records);controller=null;renderPreview(records.length?'':'没有读到公开 Stars。资料设置可能影响可见性，也可以导入 JSON 清单。');
}catch(error){if(error.name!=='AbortError'&&el('stars-progress'))el('stars-progress').textContent=error.message||'网络读取失败。可重试或导入 JSON 清单。';}
finally{if(controller===active){controller=null;if(el('stars-fetch-button'))el('stars-fetch-button').disabled=false;}}
});
el('stars-open-file').addEventListener('click',()=>fileInput.click());
if(el('stars-show-saved'))el('stars-show-saved').addEventListener('click',()=>{selectRecords(ledger.map(p=>({...p})));renderPreview();});
}
function renderPreview(message=''){
const list=matches(),pages=Math.max(1,Math.ceil(list.length/40));view.page=Math.min(view.page,pages-1);const portion=list.slice(view.page*40,(view.page+1)*40);
show('GitHub Stars · 导入预览',
'<div class="stars-summary"><span>本次清单 '+view.records.length+' 项</span><span>已保存 '+ledger.length+' 项</span><span>已选择 '+view.selected.size+' 项</span></div><p class="stars-notice">仓库描述、Stars 和时间为来源快照；分类为规则建议。候选尚未进行实际使用评估，示例表继续保留演示数据。</p><div class="stars-toolbar"><input id="stars-search" type="search" aria-label="搜索导入清单" placeholder="搜索名称、描述、Topics" value="'+esc(view.query)+'"><select id="stars-category" aria-label="筛选导入分类">'+categoryOptions(view.category,true)+'</select></div><div class="actions"><button class="button" id="stars-select-visible">选择当前筛选结果</button><button class="button" id="stars-clear-selection">清空选择</button><button class="button" id="stars-export">导出本次清单 JSON</button></div><p id="stars-import-status" class="muted" role="status">'+esc(message||storageMessage)+'</p><div class="table-wrap"><table class="stars-table"><thead><tr><th>选择</th><th>项目与描述</th><th>分类</th><th>Stars 快照</th><th>最近推送</th><th>状态</th></tr></thead><tbody>'+
portion.map(p=>'<tr><td><input type="checkbox" data-stars-select="'+esc(recordKey(p))+'" aria-label="选择 '+esc(p.repo)+'" '+(view.selected.has(recordKey(p))?'checked':'')+'></td><td><button class="project-name" data-stars-detail="'+esc(recordKey(p))+'">'+esc(p.repo)+'</button><p class="stars-description">'+esc(p.description||'来源未提供描述')+'</p><small>'+esc(p.topics.join(' · '))+'</small></td><td><select data-stars-classify="'+esc(recordKey(p))+'" aria-label="'+esc(p.repo)+' 的分类">'+categoryOptions(p.category,false)+'</select><small>'+(p.classification_source==='manual'?'人工选择':'规则建议 · 待核验')+'</small></td><td>'+snapshotValue(p.stars)+'</td><td>'+calendar(p.pushed_at)+'</td><td>'+(p.archived===true?'已归档':p.archived===false?'未归档':'状态未知')+'<small>'+(known(p)?'已保存 · 可更新':'新增候选')+'</small></td></tr>').join('')+
'</tbody></table>'+(list.length?'':'<div class="empty">当前清单没有匹配项目。</div>')+'</div><div class="stars-pages"><span>筛选结果 '+list.length+' 项 · 第 '+(view.page+1)+' / '+pages+' 页</span><div class="actions"><button class="button" id="stars-prev" '+(view.page===0?'disabled':'')+'>上一页</button><button class="button" id="stars-next" '+(view.page>=pages-1?'disabled':'')+'>下一页</button></div></div><div class="actions"><button class="button primary" id="stars-commit" '+(view.selected.size?'':'disabled')+'>加入 / 更新候选（'+view.selected.size+'）</button><button class="button" id="stars-reload">重新读取</button><button class="button" id="stars-to-inbox">查看候选箱</button></div><p class="stars-source">公开 API：'+esc(view.account)+' · 原始收藏时间在 API 提供时保留 · 本地清单不会自动发布到博客。</p>');
el('stars-search').addEventListener('input',event=>{view.query=event.target.value;view.page=0;renderPreview();el('stars-search').focus();el('stars-search').setSelectionRange(view.query.length,view.query.length);});
el('stars-category').addEventListener('change',event=>{view.category=event.target.value;view.page=0;renderPreview();});
el('stars-select-visible').addEventListener('click',()=>{matches().forEach(p=>view.selected.add(recordKey(p)));renderPreview();});
el('stars-clear-selection').addEventListener('click',()=>{view.selected.clear();renderPreview();});
el('stars-export').addEventListener('click',exportData);
el('stars-prev').addEventListener('click',()=>{view.page--;renderPreview();});
el('stars-next').addEventListener('click',()=>{view.page++;renderPreview();});
el('stars-commit').addEventListener('click',commitSelected);el('stars-reload').addEventListener('click',openImport);el('stars-to-inbox').addEventListener('click',inbox);
}
function commitSelected(){
const selected=view.records.filter(p=>view.selected.has(recordKey(p)));let added=0,updated=0;
for(const record of selected){
const index=ledger.findIndex(p=>recordKey(p)===recordKey(record)||p.repo.toLowerCase()===record.repo.toLowerCase());
const copy={...record,topics:[...record.topics]};if(index<0){ledger.push(copy);added++;}else{ledger[index]=copy;updated++;}attachCandidate(copy);
}
try{localStorage.setItem(storageKey,JSON.stringify({version:1,repositories:ledger}));storageMessage='已保存到当前浏览器。';}
catch{storageMessage='当前浏览器无法保存本地清单，请导出 JSON；本次会话里的候选仍可查看。';}
renderPreview('新增 '+added+' 项，更新 '+updated+' 项。'+storageMessage);
}
function exportData(){
const records=view.records.map(p=>{const old=ledger.find(item=>recordKey(item)===recordKey(p));return old?{...p,personal_note:old.personal_note}:p;});
const url=URL.createObjectURL(new Blob([JSON.stringify({version:1,exported_at:new Date().toISOString(),repositories:records},null,2)],{type:'application/json;charset=utf-8'}));
const link=document.createElement('a');link.href=url;link.download='github-stars-'+(view.account||'import')+'-'+new Date().toISOString().slice(0,10)+'.json';document.body.append(link);link.click();link.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function showStarDetail(record,backToPreview){
const candidate=candidates.find(p=>p.repo.toLowerCase()===record.repo.toLowerCase());
show(record.name+' · 来源快照',
'<p class="muted">'+esc(record.repo)+' · '+categoryName(record.category)+'（'+(record.classification_source==='manual'?'人工选择':'规则建议')+'）</p><section class="panel"><h3>仓库事实</h3><p>'+esc(record.description||'来源未提供描述')+'</p><div class="stars-facts">'+[
['Stars',snapshotValue(record.stars)],['Forks',snapshotValue(record.forks)],['主要语言',snapshotValue(record.language)],['许可证标识',record.license?esc(record.license):'未识别 · 待核验'],['归档状态',record.archived===true?'已归档':record.archived===false?'未归档':'未提供'],['最近推送',calendar(record.pushed_at)],['你的收藏时间',calendar(record.starred_at)],['采集时间',snapshotValue(record.fetched_at)]
].map(([label,value])=>'<div><b>'+label+'</b>'+value+'</div>').join('')+'</div><p class="muted">'+esc(record.topics.join(' · '))+'</p></section><section class="panel"><h3>研究判断</h3><p>'+esc(candidate?.note||record.personal_note||'尚未补充关注理由与实测体验。')+'</p><p class="muted">采用优先级：尚未判断 · 活跃度、社区、影响力与持续性：待补充证据。</p></section><p class="stars-source">来源：'+(record.origin==='api'?'GitHub 公开 Stars API':'导入或恢复的 JSON 清单，尚未在线复核')+' · 帐户：'+esc(record.account||'未提供')+'</p><p><a target="_blank" rel="noopener noreferrer" href="https://github.com/'+esc(record.repo)+'">查看仓库 ↗</a></p>'+(backToPreview?'<button class="button" id="stars-back-preview">返回导入预览</button>':''));
if(backToPreview)el('stars-back-preview').addEventListener('click',()=>renderPreview());
}
const fileInput=document.createElement('input');fileInput.type='file';fileInput.accept='.json,application/json';fileInput.className='stars-file';fileInput.setAttribute('aria-label','选择 Stars JSON 清单');document.body.append(fileInput);
fileInput.addEventListener('change',async()=>{
const file=fileInput.files[0];if(!file)return;if(controller){controller.abort();controller=null;}
try{const value=JSON.parse(await file.text());const records=uniqueStars(decodeStarFile(value).map(p=>normalizeStar(p,view.account,new Date().toISOString(),'file')));selectRecords(records);renderPreview('已读取文件 '+file.name+'。文件中的记录尚未在线复核。');}
catch(error){if(el('stars-progress'))el('stars-progress').textContent=error.message||'JSON 文件无法读取。';else toast(error.message||'JSON 文件无法读取。');}
finally{fileInput.value='';}
});
document.addEventListener('change',event=>{
const key=event.target.dataset.starsSelect;if(key!==undefined){event.target.checked?view.selected.add(key):view.selected.delete(key);renderPreview();}
const categoryKey=event.target.dataset.starsClassify;if(categoryKey!==undefined){const p=view.records.find(p=>recordKey(p)===categoryKey);p.category=event.target.value;p.classification_source='manual';renderPreview();}
});
document.addEventListener('click',event=>{
const button=event.target.closest('button');if(!button)return;
if(button.dataset.starsDetail!==undefined){const p=view.records.find(p=>recordKey(p)===button.dataset.starsDetail);if(p)showStarDetail(p,true);}
if(button.dataset.candidate!==undefined){const p=candidates[Number(button.dataset.candidate)];if(p?.starMeta)showStarDetail(p.starMeta,false);}
});
el('dialog').addEventListener('close',()=>{if(controller){controller.abort();controller=null;}});
importButton.addEventListener('click',openImport);
})();

