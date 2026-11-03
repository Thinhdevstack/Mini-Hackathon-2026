const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const app = fs.readFileSync(path.resolve('frontend/app.js'), 'utf8');
const html = fs.readFileSync(path.resolve('frontend/index.html'), 'utf8');
const key = 'interna-demo-v1';
const sleep = ms => new Promise(resolve => setTimeout(resolve, ms));
function harness(mode='demo', store=new Map(), fetchImpl) {
  const nodes=new Map(), listeners={};
  const decode=s=>s.replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&#39;/g,"'").replace(/&amp;/g,'&');
  function node(id){if(!nodes.has(id))nodes.set(id,{id,dataset:{},value:'',hidden:false,disabled:false,style:{},scrollHeight:100,scrollTop:0,textContent:'',_html:'',handlers:{},set innerHTML(v){this._html=v;for(const m of v.matchAll(/<textarea[^>]*id="([^"]+)"[^>]*>([\s\S]*?)<\/textarea>/g))node(m[1]).value=decode(m[2]);},get innerHTML(){return this._html;},setAttribute(k,v){this[k]=v;},addEventListener(type,fn){this.handlers[type]=fn;},focus(){},showModal(){this.open=true;},close(){this.open=false;}});return nodes.get(id);}
  const roles=['intern','mentor'].map(role=>({dataset:{role},setAttribute(){}}));
  const document={getElementById:node,querySelectorAll:q=>q==='[data-role]'?roles:[],querySelector:()=>node('brand'),addEventListener:(t,fn)=>listeners[t]=fn};
  const context={console,document,localStorage:{getItem:k=>store.get(k),setItem:(k,v)=>store.set(k,v)},setTimeout,clearTimeout,AbortController,fetch:fetchImpl,window:{INTERNA_CONFIG:{mode,apiBaseUrl:'http://test.local',chatPath:'/chat',timeoutMs:3000},confirm:()=>true}};
  vm.runInNewContext(app,context,{filename:'app.js'});
  function click(data){return listeners.click({target:{closest:()=>({dataset:data})}});}
  function input(id,value){const n=node(id);n.value=value;listeners.input({target:n});}
  function send(value){input('chat-input',value);listeners.submit({target:{id:'chat-form'},preventDefault(){}});}
  return {node,store,click,input,send,listeners,state:()=>JSON.parse(store.get(key)),main:()=>node('main-content').innerHTML};
}
(async()=>{
  for(const asset of ['style.css','config.js','app.js'])assert.ok(fs.existsSync(path.resolve('frontend',asset)));
  const ids=[...html.matchAll(/\bid="([^"]+)"/g)].map(m=>m[1]);assert.equal(new Set(ids).size,ids.length,'No duplicate shell IDs');
  const h=harness();assert.match(h.main(),/Nhiệm vụ của tôi/);
  h.click({doc:'requirements'});assert.equal(h.node('detail-dialog').open,true);h.node('detail-dialog').close();
  assert.equal(h.state().events.at(-1).type,'doc');
  h.send('Mã thực tập sinh bị trùng thì sao?');
  await sleep(720);
  assert.equal(h.state().chats['TSK-02'].length,2);
  assert.match(h.state().chats['TSK-02'][1].content,/REQ-01/);
  h.click({task:'TSK-03'});assert.match(h.main(),/Lập danh sách tình huống/);assert.doesNotMatch(h.node('chat-log').innerHTML,/Mã thực tập sinh bị trùng thì sao/);
  h.click({task:'TSK-02'});
  h.input('submission-note','Đã đề xuất trường dữ liệu và kiểm tra mã trùng.');h.click({action:'submit'});
  assert.equal(h.state().tasks['TSK-02'].status,'review');
  h.click({role:'mentor'});assert.match(h.main(),/Đã đề xuất trường dữ liệu/);assert.match(h.main(),/Mã thực tập sinh bị trùng/);
  h.click({result:'TSK-02'});assert.match(h.node('dialog-content').innerHTML,/Duyệt hoàn thành/);
  h.click({reviewAction:'approved',reviewTask:'TSK-02',version:'1'});assert.equal(h.state().tasks['TSK-02'].status,'done');
  h.input('mentor-note','Cần giải thích lựa chọn dữ liệu ở buổi review.');h.click({action:'save-review'});assert.match(h.state().notes.an.text,/Cần giải thích/);
  h.click({student:'linh'});assert.match(h.main(),/Chưa có dữ liệu hoạt động/);h.click({student:'an'});
  const again=harness('demo',h.store);assert.equal(again.state().tasks['TSK-02'].status,'done');
  again.click({task:'TSK-03'});again.send('<img src=x onerror=alert(1)>');await sleep(720);assert.match(again.node('chat-log').innerHTML,/&lt;img/);assert.doesNotMatch(again.node('chat-log').innerHTML,/<img src/);
  let request;
  const api=harness('api',new Map(),async(url,opts)=>{request={url,body:JSON.parse(opts.body)};return {ok:true,json:async()=>({reply:'Phản hồi từ backend thử nghiệm'})};});
  api.send('Câu hỏi API');await sleep(20);assert.equal(request.url,'http://test.local/chat');assert.equal(request.body.history.length,0);assert.equal(request.body.task_id,'TSK-02');assert.equal(api.state().chats['TSK-02'][1].source,'api');
  api.send('Câu tiếp theo');await sleep(20);assert.equal(request.body.history.length,2);assert.equal(request.body.message,'Câu tiếp theo');
  const failed=harness('api',new Map(),async()=>{throw new TypeError('Network failed');});failed.send('Giữ câu hỏi này');await sleep(20);assert.equal(failed.state().drafts['TSK-02'],'Giữ câu hỏi này');assert.equal(failed.state().chats['TSK-02'].length,0);assert.match(failed.main(),/Kiểm tra địa chỉ backend/);

  // Full feedback cycle: blocker -> answer -> follow-up -> request changes -> resubmit -> approve.
  const flow=harness();
  const review=(action,version='1')=>flow.click({reviewAction:action,reviewTask:'TSK-02',version});
  flow.click({action:'submit'});assert.match(flow.node('toast').textContent,/Thêm mô tả/);
  flow.input('submission-note','Bài làm lần 1');flow.input('submission-blocker','Chưa rõ cách xử lý mã trùng <script>');
  flow.click({action:'submit'});
  assert.equal(flow.state().tasks['TSK-02'].submissions[0].blocker,'Chưa rõ cách xử lý mã trùng <script>');
  assert.doesNotMatch(flow.main(),/id="submission-note"/,'Submitted result is read-only');
  flow.input('submission-note','Không được sửa âm thầm');flow.click({action:'submit'});
  assert.equal(flow.state().tasks['TSK-02'].submissions.length,1);
  assert.equal(flow.state().tasks['TSK-02'].note,'Bài làm lần 1');
  flow.click({role:'mentor'});flow.click({result:'TSK-02'});
  assert.match(flow.node('dialog-content').innerHTML,/&lt;script&gt;/);
  review('approved');assert.equal(flow.state().tasks['TSK-02'].status,'review','Cannot silently approve unresolved blocker');
  review('changes');assert.equal(flow.state().tasks['TSK-02'].status,'review','Change request needs explanation');
  review('reply');assert.equal(flow.state().tasks['TSK-02'].discussion.length,0,'Empty replies blocked');
  flow.input('mentor-feedback','Kiểm tra mã đã tồn tại trước khi tạo hồ sơ.');
  flow.node('detail-dialog').close();flow.click({result:'TSK-02'});assert.equal(flow.node('mentor-feedback').value,'Kiểm tra mã đã tồn tại trước khi tạo hồ sơ.');
  review('reply');assert.equal(flow.state().tasks['TSK-02'].status,'review');
  flow.click({role:'intern'});assert.match(flow.main(),/Kiểm tra mã đã tồn tại trước khi tạo hồ sơ/);
  flow.input('intern-reply','Nếu hai yêu cầu tới cùng lúc thì sao?');flow.click({action:'intern-reply'});
  flow.click({role:'mentor'});flow.click({result:'TSK-02'});review('approved');
  assert.equal(flow.state().tasks['TSK-02'].status,'review','Latest intern follow-up must be answered');
  flow.input('mentor-feedback','Bổ sung cách bảo đảm mã duy nhất khi có hai yêu cầu đồng thời.');review('changes');
  assert.equal(flow.state().tasks['TSK-02'].status,'changes');assert.doesNotMatch(flow.node('dialog-content').innerHTML,/data-review-action="approved"/);
  review('approved');assert.equal(flow.state().tasks['TSK-02'].status,'changes','Cannot approve a returned version');
  flow.click({role:'intern'});assert.match(flow.main(),/Gửi lại mentor/);
  flow.input('submission-note','Bài làm lần 2: đã bổ sung ràng buộc duy nhất.');flow.input('submission-blocker','');flow.click({action:'submit'});
  assert.equal(flow.state().tasks['TSK-02'].submissions.length,2);assert.equal(flow.state().tasks['TSK-02'].submissions[0].result,'Bài làm lần 1');
  flow.click({role:'mentor'});flow.click({result:'TSK-02'});review('approved','1');assert.equal(flow.state().tasks['TSK-02'].status,'review','Stale review action blocked');
  flow.input('mentor-feedback','Đã đạt yêu cầu, cảm ơn em đã bổ sung.');review('approved','2');
  assert.equal(flow.state().tasks['TSK-02'].status,'done');
  assert.equal(flow.state().events.at(-1).author,'mentor');
  flow.click({role:'intern'});assert.match(flow.main(),/Đã đạt yêu cầu/);assert.doesNotMatch(flow.main(),/Nhiệm vụ này đã được mentor duyệt \(dữ liệu mẫu\)/);
  flow.click({task:'TSK-03'});assert.doesNotMatch(flow.main(),/Bài làm lần 2/,'Feedback stays within task');
  flow.click({action:'start'});assert.equal(flow.state().tasks['TSK-03'].status,'active');
  flow.click({task:'TSK-02'});flow.click({action:'start'});assert.equal(flow.state().tasks['TSK-02'].status,'done','Cannot restart completed task with stale action');
  const restored=harness('demo',flow.store);restored.click({role:'mentor'});restored.click({result:'TSK-02'});assert.match(restored.node('dialog-content').innerHTML,/Bài làm lần 1/);assert.match(restored.node('dialog-content').innerHTML,/Đã đạt yêu cầu/);

  // Existing demo storage is migrated, never wiped or silently treated as blocker-free.
  const legacy=JSON.parse(JSON.stringify(h.state()));
  for(const item of Object.values(legacy.tasks)){delete item.submissions;delete item.discussion;delete item.blockerDraft;delete item.mentorDraft;delete item.replyDraft;}
  legacy.tasks['TSK-02'].status='review';legacy.tasks['TSK-02'].submission='Bài cũ. Em còn vướng phần xác thực.';
  const migrated=harness('demo',new Map([[key,JSON.stringify(legacy)]]));migrated.click({role:'mentor'});migrated.click({result:'TSK-02'});
  assert.match(migrated.node('dialog-content').innerHTML,/Bản cũ gộp vướng mắc/);
  migrated.click({reviewAction:'approved',reviewTask:'TSK-02',version:'1'});assert.match(migrated.node('toast').textContent,/giải đáp/);
  migrated.input('mentor-feedback','Hướng dẫn cho bài cũ.');migrated.click({reviewAction:'reply',reviewTask:'TSK-02',version:'1'});
  assert.equal(migrated.state().tasks['TSK-02'].submissions[0].result,legacy.tasks['TSK-02'].submission);assert.equal(migrated.state().chats['TSK-02'].length,2);

  // A slow failed API request must not surface errors on another task or destroy a new draft.
  let rejectPending;
  const slow=harness('api',new Map(),()=>new Promise((resolve,reject)=>rejectPending=reject));
  slow.send('Câu đang gửi');slow.input('chat-input','Bản nháp tiếp theo');slow.click({task:'TSK-03'});rejectPending(new TypeError('Network failed'));await sleep(20);
  assert.doesNotMatch(slow.main(),/Chưa nhận được phản hồi/);slow.click({task:'TSK-02'});assert.match(slow.main(),/Chưa nhận được phản hồi/);assert.equal(slow.node('chat-input').value,'Bản nháp tiếp theo');
  flow.node('reset-demo').handlers.click();flow.input('submission-note','Sau reset');flow.click({action:'submit'});assert.equal(flow.state().tasks['TSK-02'].submissions.length,1);
  console.log('PASS: review/clarification/revision/resubmission/approval cycle, response guards, immutable submission history, drafts, state guards, persistence and v1 migration.');
  console.log('PASS: task-scoped data, API history and error recovery, async draft preservation, escaped content, activity authors, original smoke flows and reset.');
  console.log('DOM harness only; visual browser verification is separate.');
})().catch(e=>{console.error(e);process.exitCode=1;});
