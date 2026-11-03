(() => {
  "use strict";
  const config = window.INTERNA_CONFIG || { mode: "demo" };
  const STORE = "interna-demo-v1";
  const icon = name => `<svg class="icon" aria-hidden="true"><use href="#i-${name}"/></svg>`;
  const esc = value => String(value ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const tasks = [
    { id: "TSK-01", short: "Tìm hiểu yêu cầu", title: "Tìm hiểu quy trình quản lý thực tập sinh", status: "done", due: "03/11", desc: "Đọc tài liệu onboarding, xác định các vai trò trong hệ thống và mô tả luồng từ giao nhiệm vụ đến đánh giá thực tập sinh.", checks: ["Xác định vai trò thực tập sinh và mentor", "Mô tả luồng giao việc → thực hiện → đánh giá", "Ghi lại các điểm cần hỏi mentor"], docs: ["onboarding", "requirements"], welcome: "Chào An! Với task này, em có thể bắt đầu từ tài liệu onboarding.\n\nEm đã phân biệt được trách nhiệm của thực tập sinh và mentor ở từng bước chưa? Hãy thử mô tả cách một nhiệm vụ được giao và hoàn tất.", prompts: ["Em nên bắt đầu từ đâu?", "Tài liệu nào cần đọc?"] },
    { id: "TSK-02", short: "Thiết kế dữ liệu", title: "Đề xuất cấu trúc dữ liệu cho hồ sơ thực tập sinh", status: "active", due: "04/11", desc: "Từ yêu cầu nghiệp vụ của dự án Intern Portal, đề xuất các trường dữ liệu cho hồ sơ thực tập sinh. Giải thích lựa chọn của em và cách xử lý dữ liệu không hợp lệ.", checks: ["Liệt kê các trường và ý nghĩa của từng trường", "Xác định quy tắc kiểm tra dữ liệu đầu vào", "Giải thích cách xử lý mã thực tập sinh bị trùng"], docs: ["requirements", "cpp"], welcome: "Chào An! Mình đang cùng em làm task thiết kế dữ liệu.\n\nTheo tài liệu yêu cầu, mã thực tập sinh phải duy nhất và ngày kết thúc không được trước ngày bắt đầu.\n\nEm đã nghĩ đến những trường dữ liệu nào? Hãy đưa ra đề xuất trước, mình sẽ cùng xem lại.", prompts: ["Em nên bắt đầu từ đâu?", "Mã thực tập sinh bị trùng thì sao?"] },
    { id: "TSK-03", short: "Kiểm thử đầu vào", title: "Lập danh sách tình huống kiểm thử dữ liệu đầu vào", status: "todo", due: "05/11", desc: "Dựa trên cấu trúc dữ liệu đã đề xuất, liệt kê các tình huống bình thường, thiếu dữ liệu và dữ liệu sai. Mỗi tình huống cần có kết quả mong đợi.", checks: ["Có trường hợp hợp lệ và trường hợp để trống", "Có trường hợp mã bị trùng, ngày tháng không hợp lệ", "Mô tả kết quả mong đợi cho từng tình huống"], docs: ["requirements", "testing"], welcome: "Ở task này, mình sẽ giúp em suy nghĩ về các trường hợp cần kiểm thử.\n\nHãy chọn một trường dữ liệu, rồi thử nghĩ theo ba hướng: giá trị hợp lệ, giá trị bị thiếu và giá trị vi phạm quy tắc. Em muốn bắt đầu với trường nào?", prompts: ["Gợi ý cách tìm trường hợp biên", "Một test case cần có gì?"] }
  ];
  const docs = {
    onboarding: { title: "Cẩm nang thực tập", file: "onboarding.md", category: "ONBOARDING", summary: "Vai trò, cách nhận việc và quy trình phối hợp cùng mentor.", sections: [["ONB-01 · Nhận và làm nhiệm vụ", "Thực tập sinh đọc yêu cầu, làm rõ điểm chưa hiểu, thực hiện và gửi kết quả để mentor xem. Cần nêu cách làm và các vấn đề còn vướng khi gửi bài."], ["ONB-02 · Sử dụng AI nội bộ", "AI hỗ trợ tìm hiểu tài liệu, đặt câu hỏi và gợi ý hướng giải quyết. Thực tập sinh tự thực hiện công việc. Lịch sử trao đổi theo task được cung cấp cho mentor để hiểu quá trình học tập."], ["ONB-03 · Vai trò mentor", "Mentor xem kết quả và quá trình làm việc để đưa ra phản hồi. Tổng hợp từ AI chỉ hỗ trợ; quyết định đánh giá thuộc về mentor."]] },
    requirements: { title: "Yêu cầu dự án Intern Portal", file: "intern_portal.md", category: "NGHIỆP VỤ", summary: "Phạm vi dự án, dữ liệu thực tập sinh và tiêu chí nghiệm thu.", sections: [["REQ-01 · Hồ sơ thực tập sinh", "Hồ sơ có mã thực tập sinh, họ tên, nhóm, mentor phụ trách, ngày bắt đầu, ngày kết thúc và trạng thái. Mã không được rỗng hoặc trùng. Ngày kết thúc không được trước ngày bắt đầu."], ["REQ-02 · Vòng đời nhiệm vụ", "Task đi qua các trạng thái: Chưa bắt đầu → Đang làm → Chờ mentor. Mentor có thể giải đáp mà giữ nguyên trạng thái, yêu cầu chỉnh sửa (Cần chỉnh sửa → nộp lại → Chờ mentor), hoặc duyệt Hoàn thành. Mỗi lần nộp giữ riêng kết quả, vướng mắc và phản hồi."], ["REQ-03 · Tiêu chí nghiệm thu", "Đề xuất dữ liệu phải giải thích được vai trò từng trường và quy tắc kiểm tra. Tình huống kiểm thử cần có đầu vào và kết quả mong đợi."]] },
    cpp: { title: "Quy chuẩn C++ của team", file: "cpp_rule.md", category: "KỸ THUẬT", summary: "Chuẩn C++17, quyền sở hữu tài nguyên và quy ước đặt tên.", sections: [["CPP-01 · Phiên bản", "Dự án demo thống nhất dùng C++17. Cấu hình build phải thể hiện chuẩn này."], ["CPP-02 · Quản lý tài nguyên", "Ưu tiên đối tượng tự quản lý tài nguyên và container chuẩn. Không dùng new/delete trực tiếp trong code ứng dụng. Khi cần cấp phát động có một chủ sở hữu, ưu tiên unique_ptr; chỉ dùng shared_ptr khi có nhu cầu chia sẻ quyền sở hữu."], ["CPP-04 · Đặt tên", "Biến và hàm dùng camelCase; class và struct dùng PascalCase. Tên phải thể hiện ý nghĩa."], ["CPP-05 · Kiểm tra đầu vào", "Dữ liệu bên ngoài cần được kiểm tra trước khi sử dụng. Lỗi phải được thông báo rõ, không báo thành công khi thao tác thất bại."]] },
    testing: { title: "Hướng dẫn viết test case", file: "testing_guide.md", category: "KIỂM THỬ", summary: "Cách mô tả đầu vào, thao tác và kết quả mong đợi.", sections: [["TEST-01 · Nội dung test case", "Mỗi test case có tên tình huống, điều kiện ban đầu, dữ liệu đầu vào, thao tác thực hiện và kết quả mong đợi."], ["TEST-02 · Nhóm tình huống", "Kiểm tra trường hợp hợp lệ, thiếu giá trị bắt buộc, giá trị không hợp lệ và ranh giới của quy tắc. Với mã duy nhất, cần xem xét trường hợp mã đã tồn tại."]] }
  };
  const students = [{id:"an",name:"Minh An",initial:"MA",color:"green",team:"Backend Intern"},{id:"linh",name:"Khánh Linh",initial:"KL",color:"pink",team:"Frontend Intern"},{id:"bao",name:"Gia Bảo",initial:"GB",color:"blue",team:"QA Intern"}];
  const statusNames = {todo:"Chưa bắt đầu",active:"Đang làm",review:"Chờ mentor",changes:"Cần chỉnh sửa",done:"Hoàn thành"};
  function seed() {
    return { version:1, taskId:"TSK-02", studentId:"an", tasks:Object.fromEntries(tasks.map(t=>[t.id,{status:t.status,checks:t.checks.map(()=>t.status==="done"),note:"",submission:"",submissions:[],discussion:[],blockerDraft:"",mentorDraft:"",replyDraft:""}])), chats:{}, drafts:{}, notes:{}, events:[
      {time:"2026-11-03T09:30:00+07:00",type:"done",task:"TSK-01",title:"Hoàn thành tìm hiểu yêu cầu",detail:"Mentor đã duyệt bản mô tả vai trò và luồng công việc. Dữ liệu mẫu.",student:"an"},
      {time:"2026-11-03T09:45:00+07:00",type:"start",task:"TSK-02",title:"Bắt đầu thiết kế dữ liệu",detail:"Nhận nhiệm vụ đề xuất cấu trúc hồ sơ thực tập sinh. Dữ liệu mẫu.",student:"an"}
    ]};
  }
  let state;
  try { const saved=JSON.parse(localStorage.getItem(STORE)||"null"); state=saved&&saved.version===1&&tasks.every(t=>saved.tasks?.[t.id])&&Array.isArray(saved.events)&&saved.chats&&saved.notes&&saved.drafts?saved:seed(); } catch {state=seed();}
  if(!tasks.some(t=>t.id===state.taskId))state.taskId="TSK-02";
  if(!students.some(s=>s.id===state.studentId))state.studentId="an";
  // Nâng cấp dữ liệu cũ ngay trong cùng khóa lưu, không xóa bài làm hay hội thoại.
  for(const task of tasks){
    const item=state.tasks[task.id];
    if(!Array.isArray(item.submissions))item.submissions=item.submission?[{version:1,result:item.submission,blocker:"",checks:[...item.checks],time:null,legacy:true}]:[];
    if(!Array.isArray(item.discussion))item.discussion=[];
    item.blockerDraft??="";item.mentorDraft??="";item.replyDraft??="";
  }
  let role="intern", view="work", pendingTask=null, chatErrors={}, toastTimer, epoch=0, reviewTaskId=null;
  const main=document.getElementById("main-content");
  function save(){try{localStorage.setItem(STORE,JSON.stringify(state));}catch{toast("Trình duyệt chưa cho phép lưu. Dữ liệu vẫn dùng được trong phiên này.");}}
  function toast(text){const el=document.getElementById("toast");el.textContent=text;el.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.hidden=true,3500);}
  function addEvent(type,title,detail,task=state.taskId,author="intern"){state.events.push({time:new Date().toISOString(),type,title,detail,task,student:"an",author});save();}
  const status = value => `<span class="status ${esc(value)}">${esc(statusNames[value]||value)}</span>`;
  const avatar = person => `<span class="avatar ${esc(person.color||"")}">${esc(person.initial)}</span>`;
  const currentTask=()=>tasks.find(t=>t.id===state.taskId)||tasks[1];
  const finished=()=>tasks.filter(t=>state.tasks[t.id].status==="done").length;
  function timeLabel(value){return new Date(value).toLocaleString("vi-VN",{day:"2-digit",month:"2-digit",hour:"2-digit",minute:"2-digit",timeZone:"Asia/Bangkok"});}
  function renderShell(){
    document.querySelectorAll("[data-role]").forEach(b=>b.setAttribute("aria-pressed",String(b.dataset.role===role)));
    const navs=role==="intern"?[["work","grid","Công việc của tôi"],["knowledge","book","Tài liệu công ty"],["activity","clock","Hoạt động của tôi"]]:[["work","users","Theo dõi thực tập sinh"],["knowledge","book","Tài liệu công ty"],["activity","clock","Nhật ký hoạt động"]];
    document.getElementById("main-nav").innerHTML=navs.map(([key,i,label])=>`<button class="nav-item ${view===key?"active":""}" data-view="${key}" ${view===key?'aria-current="page"':""}>${icon(i)}${label}</button>`).join("");
    document.getElementById("breadcrumb-label").textContent=navs.find(x=>x[0]===view)[2];
    document.getElementById("profile").innerHTML=role==="intern"?`${avatar(students[0])}<div><strong>Minh An</strong><small>Backend Intern · Dữ liệu mẫu</small></div>`:`<span class="avatar">TH</span><div><strong>Thanh Hà</strong><small>Mentor · Dữ liệu mẫu</small></div>`;
    document.getElementById("connection-badge").innerHTML=`<span></span>${config.mode==="api"?"Chế độ API":"AI giả lập"}`;
  }
  function render(){renderShell();if(view==="knowledge")renderKnowledge();else if(view==="activity")renderActivity();else if(role==="mentor")renderMentor();else renderIntern();}
  function heading(eyebrow,title,subtitle,aside=""){return `<div class="page-heading"><div><span class="eyebrow">${esc(eyebrow)}</span><h1>${esc(title)}</h1><p>${esc(subtitle)}</p></div>${aside}</div>`;}
  const latestSubmission=item=>item.submissions[item.submissions.length-1];
  const editable=item=>["active","changes"].includes(item.status);
  function submissionMarkup(submission){
    return `<article class="submission-snapshot"><h3>Lần nộp ${submission.version}${submission.time?` · ${esc(timeLabel(submission.time))}`:" · Dữ liệu chuyển từ bản cũ"}</h3><span class="mini-label">Kết quả / đường dẫn bài làm</span><p class="review-text">${esc(submission.result)}</p><span class="mini-label">Vướng mắc cần mentor giải đáp</span><p class="review-text">${esc(submission.blocker||(submission.legacy?"Bản cũ gộp vướng mắc trong ghi chú kết quả ở trên.":"Không có vướng mắc được ghi khi nộp."))}</p><small>Checklist tại lúc nộp: ${submission.checks.filter(Boolean).length}/${submission.checks.length} mục tự đánh dấu.</small></article>`;
  }
  function discussionMarkup(item){
    if(!item.discussion.length)return '<p class="review-help">Chưa có trao đổi với mentor về bài nộp này.</p>';
    const kinds={reply:"Giải đáp / phản hồi",changes:"Yêu cầu chỉnh sửa",approved:"Đã duyệt",question:"Trao đổi thêm"};
    return `<div class="review-thread">${item.discussion.map(m=>`<article class="review-message ${m.role=== "mentor"?"from-mentor":"from-intern"}"><div class="review-author">${m.role==="mentor"?"Thanh Hà · Mentor":"Minh An · Thực tập sinh"}<span>${esc(kinds[m.kind]||m.kind)} · Lần nộp ${m.version}</span></div><p class="review-text">${esc(m.text)}</p><small>${esc(timeLabel(m.time))}</small></article>`).join("")}</div>`;
  }
  function taskReviewMarkup(task,item){
    const submission=latestSubmission(item), canEdit=editable(item);
    const hints={todo:"Bắt đầu nhiệm vụ trước khi ghi và gửi kết quả.",active:"Gửi bài chỉ chuyển sang Chờ mentor, chưa tính hoàn thành.",changes:"Đọc phản hồi của mentor, chỉnh bài và gửi lại một phiên bản mới.",review:"Bài đã gửi được giữ nguyên. Em có thể trao đổi thêm với mentor bên dưới.",done:submission?"Mentor đã duyệt kết quả này.":"Nhiệm vụ này đã được mentor duyệt (dữ liệu mẫu)."};
    return `<div class="task-bottom">${submission?`<details class="submission-history" ${canEdit?"":"open"}><summary>${item.submissions.length} lần nộp · Xem nội dung đã gửi</summary>${item.submissions.map(submissionMarkup).join("")}</details>`:""}${canEdit?`<label for="submission-note">Kết quả / đường dẫn bài làm <span aria-hidden="true">*</span></label><textarea id="submission-note" placeholder="Em đã thực hiện được gì? Kết quả hoặc đường dẫn bài làm…">${esc(item.note)}</textarea><label for="submission-blocker">Vướng mắc cần mentor giải đáp (nếu có)</label><textarea id="submission-blocker" placeholder="Em còn chưa rõ điều gì, đã thử cách nào?">${esc(item.blockerDraft)}</textarea>`:""}<div class="task-actions"><small>${hints[item.status]}</small>${item.status==="todo"?`<button class="btn primary" data-action="start">Bắt đầu nhiệm vụ ${icon("arrow")}</button>`:canEdit?`<button class="btn primary" data-action="submit">${item.status==="changes"?"Gửi lại mentor":"Gửi mentor xem"} ${icon("arrow")}</button>`:status(item.status)}</div>${submission?`<section class="task-discussion"><h3>Trao đổi với mentor</h3><p class="review-help">Phản hồi trực tiếp từ mentor, tách biệt với trợ lý AI.</p>${discussionMarkup(item)}<label for="intern-reply">Câu hỏi hoặc phản hồi thêm</label><textarea id="intern-reply" placeholder="Hỏi lại phần chưa rõ hoặc trả lời mentor…">${esc(item.replyDraft)}</textarea><button class="btn soft" data-action="intern-reply">Gửi trao đổi</button></section>`:""}</div>`;
  }
  function renderIntern(){
    const task=currentTask(), item=state.tasks[task.id], complete=finished(), chatError=chatErrors[task.id]||"";
    main.innerHTML=heading("THỰC TẬP SINH / KHÔNG GIAN CÁ NHÂN","Chào An, cùng tiến thêm một bước.","Công việc, tài liệu và người đồng hành — tất cả ở một nơi.",`<div class="heading-aside">${icon("clock")} Đợt thực tập · Tháng 11/2026</div>`)+`
      <section class="project-banner"><div><span class="eyebrow">DỰ ÁN ĐANG THAM GIA</span><h2>Intern Portal</h2><p>Xây dựng hệ thống quản lý thực tập sinh của công ty.</p><div class="project-meta"><span><span class="avatar">TH</span>Thanh Hà · Mentor</span><span>•</span><span>Team Product Engineering</span></div></div><div class="banner-progress"><div class="progress-label"><span>Nhiệm vụ đã hoàn thành</span><strong>${complete}/3</strong></div><div class="progress-track" role="progressbar" aria-label="Tiến độ dự án" aria-valuemin="0" aria-valuemax="3" aria-valuenow="${complete}"><div class="progress-fill" style="width:${complete/3*100}%"></div></div><small>Tiếp tục từ nhiệm vụ gần nhất của em.</small></div></section>
      <div class="work-grid"><div><div class="section-title"><h2 class="section-name">Nhiệm vụ của tôi</h2><span>3 nhiệm vụ được giao</span></div><div class="task-tabs" role="group" aria-label="Chọn nhiệm vụ">${tasks.map(t=>`<button class="task-card ${task.id===t.id?"selected":""}" data-task="${t.id}" aria-pressed="${task.id===t.id}"><span class="task-id">${t.id} · HẠN ${t.due}</span><strong>${esc(t.short)}</strong>${status(state.tasks[t.id].status)}</button>`).join("")}</div>
      <section class="panel task-detail"><div class="panel-body"><span class="task-id">${task.id} / INTERN PORTAL</span><h2>${esc(task.title)}</h2><p class="task-description">${esc(task.desc)}</p><span class="mini-label">KẾT QUẢ CẦN ĐẠT</span><div class="checklist">${task.checks.map((check,i)=>`<label class="check-item"><input type="checkbox" data-check="${i}" ${item.checks[i]?"checked":""} ${!editable(item)?"disabled":""}><span>${esc(check)}</span></label>`).join("")}</div><span class="mini-label">TÀI LIỆU LIÊN QUAN</span><div class="document-links">${task.docs.map(id=>`<button class="doc-link" data-doc="${id}">${icon("file")}<span>${esc(docs[id].title)}</span>${icon("arrow")}</button>`).join("")}</div></div>
      ${taskReviewMarkup(task,item)}</section></div>
      <aside class="panel ai-panel" aria-label="Trợ lý AI nội bộ"><div class="ai-header"><span class="ai-mark">${icon("spark")}</span><div><h2>Trợ lý nội bộ</h2><p>Đồng hành cùng em trong từng nhiệm vụ</p></div><span class="status done">${config.mode==="api"?"API":"Demo"}</span></div><div class="context-strip">${icon("folder")}Ngữ cảnh:<strong>${task.id} · ${esc(task.short)}</strong></div><div class="chat-log" id="chat-log" role="log" aria-label="Lịch sử trao đổi theo nhiệm vụ" aria-live="polite"></div><div class="chat-prompts">${task.prompts.map(p=>`<button class="prompt-chip" data-prompt="${esc(p)}">${esc(p)}</button>`).join("")}</div><form class="composer" id="chat-form"><div class="chat-error" id="chat-error" role="alert" ${chatError?"":"hidden"}>${esc(chatError)}</div><div class="composer-row"><textarea id="chat-input" aria-label="Câu hỏi cho AI nội bộ" placeholder="Hỏi về nhiệm vụ hoặc tài liệu công ty…" rows="2" maxlength="6000">${esc(state.drafts[task.id]||"")}</textarea><button type="submit" id="send-chat" aria-label="Gửi câu hỏi" ${pendingTask?"disabled":""}>${icon("send")}</button></div><div class="composer-note">${config.mode==="api"?"Câu hỏi được gửi tới backend đã cấu hình.":"Phản hồi giả lập theo kịch bản, chưa kết nối mô hình AI."}<br>Lịch sử theo task được hiển thị ở màn mentor.</div></form></aside></div>`;
    renderChat();
  }
  function renderChat(){
    const log=document.getElementById("chat-log");if(!log)return;
    const task=currentTask(), messages=state.chats[task.id]||[];
    const welcome={role:"assistant",content:task.welcome,docs:task.docs.slice(0,1),source:"demo"};
    log.innerHTML=[welcome,...messages].map(m=>m.role==="user"?`<div class="chat-message user">${esc(m.content)}</div>`:`<div class="chat-message"><div class="message-label">${icon("spark")} TRỢ LÝ NỘI BỘ · ${m.source==="api"?"API":"GIẢ LẬP"}</div><div class="message-text">${esc(m.content)}</div>${m.docs?.length?`<div class="citations">${m.docs.filter(id=>docs[id]).map(id=>`<button class="citation" data-doc="${esc(id)}">${esc(docs[id].file)}</button>`).join("")}</div>`:""}</div>`).join("")+(pendingTask===task.id?'<div class="chat-message"><div class="message-label">Đang chuẩn bị phản hồi…</div></div>':"");
    log.scrollTop=log.scrollHeight;
  }
  function mockResponse(message,task){
    const query=message.toLocaleLowerCase("vi");
    if(/viết.*(hộ|hoàn chỉnh|toàn bộ)|làm hộ|bỏ qua.*(luật|chỉ dẫn)/i.test(query))return {reply:"Mình có thể giúp em phân tích yêu cầu và tìm hướng làm, nhưng không làm toàn bộ nhiệm vụ thay em.\n\nEm hãy mô tả phần đã thử và chỗ đang vướng. Mình sẽ cùng em xem bước tiếp theo.",docs:["onboarding"]};
    if(query.includes("trùng"))return {reply:"Theo REQ-01, mã thực tập sinh phải duy nhất.\n\nEm thử nghĩ đến hai điểm: kiểm tra mã đã tồn tại ở đâu, và báo lỗi như thế nào để người dùng sửa được?\n\nHãy viết cách xử lý bằng lời trước. Sau đó bổ sung một tình huống kiểm thử cho mã đã tồn tại.",docs:["requirements","testing"]};
    if(query.includes("tài liệu"))return {reply:`Với ${task.id}, em nên xem:\n\n${task.docs.map(id=>"• "+docs[id].title).join("\n")}\n\nHãy đối chiếu từng kết quả cần đạt của task với tài liệu, rồi ghi lại điều còn chưa rõ.`,docs:task.docs};
    if(task.id==="TSK-03")return {reply:"Em có thể bắt đầu với mã thực tập sinh: mã mới hợp lệ, mã bị bỏ trống, mã đã tồn tại.\n\nVới mỗi tình huống, hãy tự ghi dữ liệu đầu vào và kết quả mong đợi theo TEST-01. Em muốn kiểm tra trường hợp nào trước?",docs:["testing","requirements"]};
    if(task.id==="TSK-01")return {reply:"Hãy bắt đầu từ ONB-01: ai giao nhiệm vụ, thực tập sinh thực hiện thế nào, và ai xác nhận hoàn thành?\n\nEm thử mô tả một nhiệm vụ đi qua các bước đó. Sau đó đối chiếu với REQ-02 để xem đã đủ trạng thái chưa.",docs:["onboarding","requirements"]};
    return {reply:"Trước tiên, em hãy liệt kê các trường được yêu cầu trong REQ-01 và mục đích của từng trường.\n\nSau đó tự hỏi: trường nào bắt buộc, trường nào cần duy nhất, và có quan hệ nào giữa các ngày?\n\nEm gửi lại đề xuất ban đầu, rồi chúng ta cùng xem những điểm còn thiếu. Đây là phản hồi mẫu của bản demo.",docs:["requirements"]};
  }
  async function sendToMentor(message, task, history){
    if(config.mode!=="api"){await new Promise(resolve=>setTimeout(resolve,650));return mockResponse(message,task);}
    const controller=new AbortController(), timeout=setTimeout(()=>controller.abort(),config.timeoutMs||90000);
    try{
      const base=String(config.apiBaseUrl||"").replace(/\/$/,"");
      const response=await fetch(base+(config.chatPath||"/chat"),{method:"POST",headers:{"Content-Type":"application/json"},signal:controller.signal,body:JSON.stringify({code:"",message,history:history.map(m=>({role:m.role,content:m.content})),task_id:task.id,task_context:{title:task.title,description:task.desc,document_ids:task.docs}})});
      if(!response.ok)throw new Error(`Backend trả lỗi HTTP ${response.status}.`);
      const result=await response.json();if(typeof result.reply!=="string"||!result.reply.trim())throw new Error("Backend cần trả JSON có trường reply là chuỗi không rỗng.");
      return {reply:result.reply,docs:[]};
    }finally{clearTimeout(timeout);}
  }
  async function sendChat(){
    const input=document.getElementById("chat-input");if(!input||pendingTask)return;
    const message=input.value.trim();if(!message){toast("Nhập câu hỏi trước khi gửi nhé.");input.focus();return;}
    const task=currentTask(), runEpoch=epoch, history=[...(state.chats[task.id]||[])];
    pendingTask=task.id;delete chatErrors[task.id];state.drafts[task.id]="";
    state.chats[task.id]=[...history,{role:"user",content:message}];
    addEvent("question","Trao đổi với trợ lý nội bộ",message,task.id);
    render();
    try{
      const result=await sendToMentor(message,task,history);if(runEpoch!==epoch)return;
      state.chats[task.id].push({role:"assistant",content:result.reply,docs:result.docs,source:config.mode==="api"?"api":"demo"});
      addEvent("answer",config.mode==="api"?"Nhận phản hồi từ API":"Nhận gợi ý từ AI giả lập",result.reply,task.id,"ai");
    }catch(error){
      if(runEpoch!==epoch)return;
      state.chats[task.id]=history;
      // Không ghi đè bản nháp mới mà người dùng đã nhập trong lúc chờ.
      if(!state.drafts[task.id])state.drafts[task.id]=message;
      chatErrors[task.id]=error.name==="AbortError"?"AI chưa phản hồi trong thời gian chờ. Câu hỏi đã được giữ lại trong nhật ký.":`Chưa nhận được phản hồi. ${error.name==="TypeError"?"Kiểm tra địa chỉ backend, kết nối mạng và CORS.":error.message}`;
      addEvent("error","Gửi câu hỏi chưa thành công",chatErrors[task.id],task.id);
      toast("Chưa nhận được phản hồi; câu hỏi được giữ lại trong ô nhập.");
    }finally{if(runEpoch===epoch){pendingTask=null;save();render();}}
  }
  function timelineMarkup(events){
    if(!events.length)return '<div class="empty">Chưa có hoạt động. Thử trao đổi với AI ở màn thực tập sinh.</div>';
    return `<div class="timeline">${[...events].reverse().map(e=>`<div class="timeline-row"><div class="timeline-time">${esc(timeLabel(e.time))}</div><div class="timeline-title">${esc(e.title)}</div><div class="timeline-detail">${esc(e.detail)}</div><div class="activity-tag">${esc(e.task)} · ${e.author==="mentor"||["approved","done"].includes(e.type)?"Thanh Hà · Mentor":e.author==="ai"||e.type==="answer"?"Trợ lý AI":"Minh An · Thực tập sinh"}</div></div>`).join("")}</div>`;
  }
  function renderMentor(){
    const student=students.find(s=>s.id===state.studentId)||students[0], isAn=student.id==="an", events=isAn?state.events:[], questions=events.filter(e=>e.type==="question"), docReads=events.filter(e=>e.type==="doc"), waiting=tasks.filter(t=>state.tasks[t.id].status==="review");
    main.innerHTML=heading("MENTOR / THEO DÕI & ĐỒNG HÀNH","Hiểu quá trình. Đánh giá có căn cứ.","Theo dõi công việc và cách thực tập sinh sử dụng trợ lý nội bộ.",`<button class="btn" data-action="activity">${icon("clock")}Xem nhật ký</button>`)+`
      <div class="stats-grid"><div class="stat"><div><span class="stat-label">Thực tập sinh trong nhóm</span><strong>03</strong><small>1 hồ sơ có luồng demo tương tác</small></div><span class="stat-icon">${icon("users")}</span></div><div class="stat"><div><span class="stat-label">Nhiệm vụ chờ xem</span><strong>${String(waiting.length).padStart(2,"0")}</strong><small>Đã được thực tập sinh gửi kết quả</small></div><span class="stat-icon">${icon("file")}</span></div><div class="stat"><div><span class="stat-label">Đã hoàn thành · Minh An</span><strong>${finished()}<span style="font-size:16px;color:var(--muted)"> / 3</span></strong><small>Dựa trên nhiệm vụ được mentor duyệt</small></div><span class="stat-icon">${icon("check")}</span></div></div>
      <div class="section-title"><h2 class="section-name">Thực tập sinh của bạn</h2><span>Dự án Intern Portal</span></div><div class="roster">${students.map(s=>`<button class="person-card ${s.id===student.id?"active":""}" data-student="${s.id}" aria-pressed="${s.id===student.id}">${avatar(s)}<span><strong>${esc(s.name)}</strong><small>${esc(s.team)}</small></span></button>`).join("")}</div>
      ${!isAn?`<section class="panel"><div class="panel-header"><div class="student-header">${avatar(student)}<div><h2>${esc(student.name)}</h2><p>${esc(student.team)} · Hồ sơ minh họa</p></div></div></div><div class="empty">Chưa có dữ liệu hoạt động cho hồ sơ này trong bản demo.<br>Chọn Minh An để xem dữ liệu dùng chung với màn thực tập sinh.</div></section>`:`<div class="mentor-grid"><div><section class="panel"><div class="panel-header"><div class="student-header">${avatar(student)}<div><h2>Minh An</h2><p>Backend Intern · Thanh Hà phụ trách</p></div></div><span class="status done">Đang thực tập</span></div><div class="table-wrap"><table class="task-table"><thead><tr><th>NHIỆM VỤ</th><th>TRẠNG THÁI</th><th>KẾT QUẢ</th></tr></thead><tbody>${tasks.map(t=>`<tr><td>${esc(t.short)}<small>${t.id} · Hạn ${t.due}</small></td><td>${status(state.tasks[t.id].status)}</td><td>${state.tasks[t.id].submission?`<button class="btn" data-result="${t.id}">Xem bài gửi</button>`:`<small>${state.tasks[t.id].status==="done"?"Đã duyệt (mẫu)":"Chưa gửi"}</small>`}</td></tr>`).join("")}</tbody></table></div></section><div class="section-title" style="margin-top:24px"><h2 class="section-name">Dấu vết quá trình làm việc</h2><small>${questions.length} câu hỏi · ${docReads.length} lượt mở tài liệu</small></div><section class="panel"><div class="panel-body">${timelineMarkup(events.slice(-5))}</div></section></div>
      <div class="summary-column"><section class="summary-card"><div class="summary-top">${icon("spark")}Tổng hợp hỗ trợ mentor</div><p class="summary-meta">Tổng hợp theo quy tắc demo · Chưa có AI phân tích</p><div class="evidence-block"><h3>Tiến độ ghi nhận</h3><p>${finished()}/3 nhiệm vụ đã được duyệt. ${waiting.length} nhiệm vụ đang chờ mentor xem. Các ô checklist là thông tin tự khai của thực tập sinh.</p><span class="evidence-source">Nguồn: trạng thái nhiệm vụ</span></div><div class="evidence-block"><h3>Trao đổi gần nhất</h3><p>${questions.length?`“${esc(questions[questions.length-1].detail)}”`:"Chưa có câu hỏi mới. Thử gửi câu hỏi từ màn thực tập sinh để thấy bằng chứng tại đây."}</p><span class="evidence-source">${questions.length?`Nguồn: ${esc(questions[questions.length-1].task)} · ${esc(timeLabel(questions[questions.length-1].time))}`:"Nguồn: lịch sử chat theo task"}</span></div><div class="evidence-block"><h3>Gợi ý trao đổi khi review</h3><p>Đề nghị An giải thích lựa chọn, cách kiểm chứng kết quả và phần đã tự điều chỉnh sau khi nhận gợi ý.</p></div><p class="summary-disclaimer">Số lần hỏi AI không thể tự chứng minh năng lực hay mức độ phụ thuộc. Mentor cần xem bài làm và trao đổi trực tiếp trước khi đánh giá.</p></section><section class="panel mentor-note"><div class="panel-body"><label for="mentor-note">Ghi chú đánh giá riêng của mentor</label><p class="review-help">Chỉ hiện ở màn mentor. Để giải đáp cho An, mở Xem bài gửi.</p><textarea class="review-note" id="mentor-note" placeholder="Ghi nhận điểm làm tốt, điều cần làm rõ và bước cải thiện…">${esc(state.noteDraft ?? state.notes.an?.text ?? "")}</textarea><button class="btn primary" data-action="save-review">${icon("check")}Lưu ghi chú riêng</button>${state.notes.an?`<p class="note-saved">Đã lưu trong trình duyệt · ${esc(timeLabel(state.notes.an.time))}</p>`:""}</div></section></div></div>`}`;
  }
  function renderKnowledge(){main.innerHTML=heading("KNOWLEDGE BASE / NỘI BỘ","Tài liệu công ty","Nguồn tham chiếu cho công việc và trợ lý AI. Tất cả nội dung dưới đây là tài liệu mẫu.")+`<div class="knowledge-grid">${Object.entries(docs).map(([id,d])=>`<article class="knowledge-card"><span class="document-icon">${icon("file")}</span><span class="eyebrow" style="margin:0">${esc(d.category)}</span><h2>${esc(d.title)}</h2><p>${esc(d.summary)}</p><small>${esc(d.file)} · Nội bộ / Mẫu</small><button class="btn" data-doc="${id}">Đọc tài liệu ${icon("arrow")}</button></article>`).join("")}</div>`;}
  function renderActivity(){main.innerHTML=heading("ACTIVITY / MINH AN","Mỗi bước làm đều có ngữ cảnh.","Nhật ký demo gồm câu hỏi, phản hồi, tài liệu đã mở và kết quả gửi mentor.")+`<div class="activity-page"><div class="highlight-note">Dữ liệu chỉ lưu trên trình duyệt hiện tại. Đây chưa phải hệ thống theo dõi hay đồng bộ giữa nhiều tài khoản.</div><section class="panel"><div class="panel-header"><h2>Nhật ký hoạt động</h2><span class="status todo">${state.events.length} sự kiện</span></div><div class="panel-body">${timelineMarkup(state.events)}</div></section></div>`;}
  function showDoc(id){
    const doc=docs[id];if(!doc)return;
    document.getElementById("dialog-title").textContent=doc.title;
    document.getElementById("dialog-content").innerHTML=`<p class="doc-meta">${esc(doc.file)} · Tài liệu công ty giả lập</p>${doc.sections.map(([title,body])=>`<h3>${esc(title)}</h3><p>${esc(body)}</p>`).join("")}`;
    reviewTaskId=null;document.getElementById("detail-dialog").showModal();
    if(role==="intern"){addEvent("doc","Mở tài liệu nội bộ",`${doc.title} (${doc.file})`);}
  }
  function showResult(id){
    const task=tasks.find(t=>t.id===id),item=state.tasks[id];if(role!=="mentor"||state.studentId!=="an"||!task||!item.submissions.length)return;
    reviewTaskId=id;
    const submission=latestSubmission(item);
    document.getElementById("dialog-title").textContent=task.title;
    document.getElementById("dialog-content").innerHTML=`<p class="doc-meta">${esc(id)} · Minh An · ${status(item.status)}</p>${submissionMarkup(submission)}${item.submissions.length>1?`<details class="submission-history"><summary>Xem ${item.submissions.length-1} lần nộp trước</summary>${item.submissions.slice(0,-1).map(submissionMarkup).join("")}</details>`:""}<h3>Trao đổi theo nhiệm vụ</h3>${discussionMarkup(item)}<label class="review-label" for="mentor-feedback">Giải đáp / hướng dẫn cho thực tập sinh</label><textarea id="mentor-feedback" class="review-note" placeholder="Trả lời vướng mắc và chỉ rõ phần cần điều chỉnh…">${esc(item.mentorDraft)}</textarea><p class="review-help">${item.status==="review"?"Gửi giải đáp vẫn giữ bài ở Chờ mentor. Nếu bài cần sửa, nêu yêu cầu trước khi trả lại. Khi duyệt, mentor xác nhận bài đạt yêu cầu và vướng mắc đã được giải đáp.":item.status==="changes"?"Đang chờ thực tập sinh chỉnh sửa và nộp lại; chưa thể duyệt phiên bản cũ.":"Nhiệm vụ đã hoàn thành. Mentor vẫn có thể giải đáp thêm mà không thay đổi trạng thái."}</p><div class="review-actions"><button class="btn soft" data-review-action="reply" data-review-task="${id}" data-version="${submission.version}">Gửi giải đáp</button>${item.status==="review"?`<button class="btn" data-review-action="changes" data-review-task="${id}" data-version="${submission.version}">Yêu cầu chỉnh sửa</button><button class="btn primary" data-review-action="approved" data-review-task="${id}" data-version="${submission.version}">${icon("check")}Duyệt hoàn thành</button>`:""}</div>`;
    const dialog=document.getElementById("detail-dialog");if(!dialog.open)dialog.showModal();
  }
  function handleReview(action,id,version){
    const item=state.tasks[id];
    if(role!=="mentor"||state.studentId!=="an"||reviewTaskId!==id||!item)return;
    const submission=latestSubmission(item);
    if(!submission||submission.version!==Number(version)){toast("Phiên bản đã thay đổi. Hãy mở lại bài nộp mới nhất.");return;}
    if(!["reply","changes","approved"].includes(action))return;
    if(action!=="reply"&&item.status!=="review"){toast("Chỉ xử lý kết quả khi task đang Chờ mentor.");return;}
    const field=document.getElementById("mentor-feedback"),text=field.value.trim();
    const thread=item.discussion.filter(m=>m.version===submission.version);
    const awaitingReply=thread.length?thread[thread.length-1].role==="intern":Boolean(submission.blocker||submission.legacy);
    if(!text&&(action!=="approved"||awaitingReply)){
      toast(action==="changes"?"Nêu rõ phần cần chỉnh sửa trước khi trả lại bài.":action==="approved"?"Hãy giải đáp vướng mắc hoặc câu hỏi còn chờ trước khi duyệt.":"Nhập nội dung giải đáp trước khi gửi.");field.focus();return;
    }
    const content=text||(action==="approved"?"Mentor đã xác nhận kết quả đạt yêu cầu.":"");
    item.discussion.push({role:"mentor",kind:action,version:submission.version,text:content,time:new Date().toISOString()});
    item.mentorDraft="";
    if(action==="changes")item.status="changes";
    if(action==="approved")item.status="done";
    const titles={reply:"Mentor giải đáp vướng mắc",changes:"Mentor yêu cầu chỉnh sửa",approved:"Mentor xác nhận hoàn thành"};
    addEvent(action,titles[action],`Lần nộp ${submission.version}: ${content}`,id,"mentor");
    render();showResult(id);toast(action==="changes"?"Đã trả bài để chỉnh sửa. Thực tập sinh thấy yêu cầu trong task.":action==="approved"?"Đã duyệt hoàn thành và lưu phản hồi.":"Đã gửi giải đáp tới phần trao đổi của thực tập sinh.");
  }
  document.addEventListener("click",event=>{
    const button=event.target.closest("button");if(!button)return;
    if(button.dataset.role){role=button.dataset.role;view="work";reviewTaskId=null;document.getElementById("detail-dialog").close();render();return;}
    if(button.dataset.view){view=button.dataset.view;render();return;}
    if(button.dataset.task){state.taskId=button.dataset.task;save();render();return;}
    if(button.dataset.student){state.studentId=button.dataset.student;save();render();return;}
    if(button.dataset.doc){showDoc(button.dataset.doc);return;}
    if(button.dataset.result){showResult(button.dataset.result);return;}
    if(button.dataset.prompt){const input=document.getElementById("chat-input");input.value=button.dataset.prompt;state.drafts[state.taskId]=input.value;save();input.focus();return;}
    if(button.dataset.reviewAction){handleReview(button.dataset.reviewAction,button.dataset.reviewTask,button.dataset.version);return;}
    const action=button.dataset.action;
    if(action==="start"&&role==="intern"){const task=currentTask();if(state.tasks[task.id].status!=="todo")return;state.tasks[task.id].status="active";addEvent("start","Bắt đầu nhiệm vụ",task.title);render();}
    if(action==="submit"){
      const task=currentTask(),item=state.tasks[task.id];if(role!=="intern"||!editable(item))return;
      const note=document.getElementById("submission-note").value.trim(),blocker=document.getElementById("submission-blocker").value.trim();
      if(!note){toast("Thêm mô tả kết quả hoặc đường dẫn bài làm trước khi gửi.");document.getElementById("submission-note").focus();return;}
      const version=item.submissions.length+1;
      item.submissions.push({version,result:note,blocker,checks:[...item.checks],time:new Date().toISOString()});
      item.note=note;item.blockerDraft=blocker;item.submission=note;item.mentorDraft="";item.status="review";
      addEvent("submission",`Gửi kết quả lần ${version} để mentor xem`,`${note}${blocker?`\nVướng mắc: ${blocker}`:""}`);render();toast("Đã gửi. Mentor có thể giải đáp, yêu cầu sửa hoặc duyệt bài.");
    }
    if(action==="intern-reply"&&role==="intern"){
      const item=state.tasks[state.taskId],submission=latestSubmission(item),field=document.getElementById("intern-reply");if(!submission||!field)return;
      const text=field.value.trim();if(!text){toast("Nhập câu hỏi hoặc phản hồi trước khi gửi.");field.focus();return;}
      item.discussion.push({role:"intern",kind:"question",version:submission.version,text,time:new Date().toISOString()});item.replyDraft="";
      addEvent("intern-reply","Thực tập sinh trao đổi thêm với mentor",`Lần nộp ${submission.version}: ${text}`);render();toast("Đã gửi trao đổi trong nhiệm vụ này.");
    }
    if(action==="save-review"&&role==="mentor"&&state.studentId==="an"){
      const note=document.getElementById("mentor-note").value.trim();if(!note){toast("Nhập nhận xét trước khi lưu.");return;}
      state.notes.an={text:note,time:new Date().toISOString()};save();render();toast("Đã lưu nhận xét trên trình duyệt này.");
    }
    if(action==="activity"){view="activity";render();}
  });
  document.addEventListener("input",event=>{
    if(event.target.id==="chat-input"){state.drafts[state.taskId]=event.target.value;save();}
    if(event.target.id==="submission-note"&&role==="intern"&&editable(state.tasks[state.taskId])){state.tasks[state.taskId].note=event.target.value;save();}
    if(event.target.id==="submission-blocker"&&role==="intern"&&editable(state.tasks[state.taskId])){state.tasks[state.taskId].blockerDraft=event.target.value;save();}
    if(event.target.id==="intern-reply"&&role==="intern"){state.tasks[state.taskId].replyDraft=event.target.value;save();}
    if(event.target.id==="mentor-feedback"&&role==="mentor"&&reviewTaskId){state.tasks[reviewTaskId].mentorDraft=event.target.value;save();}
    if(event.target.id==="mentor-note"){state.noteDraft=event.target.value;save();}
  });
  document.addEventListener("change",event=>{
    if(event.target.matches("[data-check]")&&role==="intern"&&editable(state.tasks[state.taskId])){state.tasks[state.taskId].checks[Number(event.target.dataset.check)]=event.target.checked;save();}
  });
  document.addEventListener("submit",event=>{if(event.target.id==="chat-form"){event.preventDefault();sendChat();}});
  document.addEventListener("keydown",event=>{if(event.target.id==="chat-input"&&event.key==="Enter"&&!event.shiftKey&&!event.isComposing){event.preventDefault();sendChat();}});
  document.getElementById("close-dialog").addEventListener("click",()=>document.getElementById("detail-dialog").close());
  document.getElementById("detail-dialog").addEventListener("click",event=>{if(event.target===event.currentTarget){const r=event.currentTarget.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)event.currentTarget.close();}});
  document.querySelector(".brand").addEventListener("click",event=>{event.preventDefault();view="work";render();});
  document.getElementById("reset-demo").addEventListener("click",()=>{
    if(!window.confirm("Đặt lại dữ liệu demo? Hội thoại, kết quả và nhận xét đã lưu trên trình duyệt này sẽ bị xóa."))return;
    epoch++;state=seed();pendingTask=null;chatErrors={};reviewTaskId=null;role="intern";view="work";save();render();toast("Đã đặt lại dữ liệu demo.");
  });
  render();
})();




