// const API_BASE = "http://127.0.0.1:5500";

// const START_ENDPOINT = `${API_BASE}/start_chat`;
// const CHAT_ENDPOINT  = `${API_BASE}/chat_message`;
// const END_ENDPOINT   = `${API_BASE}/end_chat`;

// /* ================= ELEMENTS ================= */
// const launcher = document.getElementById("bp-launcher");
// const form     = document.getElementById("bp-form");
// const chat     = document.getElementById("bp-chat");
// const closeBtn = document.getElementById("bp-close");

// const msgs   = document.getElementById("bp-messages");
// const typingTemplate = document.getElementById("bp-typing");

// const input = document.getElementById("bp-input");
// const send  = document.getElementById("bp-send");

// const nameInput  = document.getElementById("bp-name");
// const emailInput = document.getElementById("bp-email");
// const phoneInput = document.getElementById("bp-phone");
// const ccSelect   = document.getElementById("bp-cc");

// /* ================= STATE ================= */
// let isBusy = false;
// let typingNode = null;

// /* ================= STORAGE ================= */
// function loadUser() {
//   try { return JSON.parse(sessionStorage.getItem("bp-user") || "{}"); }
//   catch { return {}; }
// }
// function saveUser(user) {
//   sessionStorage.setItem("bp-user", JSON.stringify(user));
// }

// /* ================= COUNTRY CODES ================= */
// ["+1","+92","+44","+971","+91","+61"].forEach(c=>{
//   ccSelect.innerHTML += `<option value="${c}">${c}</option>`;
// });
// ccSelect.value = "+1";

// /* ================= AUTOFILL ================= */
// (() => {
//   const s = loadUser();
//   if (s.name) nameInput.value = s.name;
//   if (s.email) emailInput.value = s.email;
//   if (s.phoneRaw) phoneInput.value = s.phoneRaw;
//   if (s.cc) ccSelect.value = s.cc;
// })();
// [nameInput,emailInput,phoneInput,ccSelect].forEach(el=>{
//   el.addEventListener("input",()=>{
//     saveUser({...loadUser(),
//       name:nameInput.value,
//       email:emailInput.value,
//       phoneRaw:phoneInput.value,
//       cc:ccSelect.value
//     });
//   });
// });

// /* ================= UI ================= */
// function showForm(){form.style.display="flex";}
// function hideForm(){form.style.display="none";}
// function showChat(){chat.style.display="flex";input.focus();}
// function hideChat(){chat.style.display="none";}

// function appendBubble(text,from="bot"){
//   const d=document.createElement("div");
//   d.className="bp-msg "+(from==="user"?"bp-user":"bp-bot");
//   d.textContent=text;
//   msgs.appendChild(d);
//   msgs.scrollTop=msgs.scrollHeight;
//   return d;
// }

// /* ================= CLEAN ================= */
// function cleanReply(t){
//   return (t||"")
//     .replace(/\*\*(.*?)\*\*/g,"$1")
//     .replace(/\*(.*?)\*/g,"$1")
//     .replace(/_(.*?)_/g,"$1")
//     .replace(/\r/g,"")
//     .replace(/[ \t]+/g," ")
//     .trim();
// }

// /* ================= TYPEWRITER ================= */
// async function typeMessage(div,text){
//   for(const c of text){
//     div.textContent+=c;
//     msgs.scrollTop=msgs.scrollHeight;
//     await new Promise(r=>setTimeout(r,10));
//   }
// }

// /* =================================================
//    ✅ FIX #1 — NO OVER-CHUNKING (STRICT)
//    ================================================= */
// async function printParagraphBubbles(fullText){

//   const clean = fullText
//     .replace(/<br\s*\/?>/gi,"\n")
//     .replace(/\r/g,"")
//     .trim();

//   const parts = clean.split(/\n{2,}/);

//   for(const part of parts){
//     const bubble=document.createElement("div");
//     bubble.className="bp-msg bp-bot";
//     msgs.appendChild(bubble);
//     await typeMessage(bubble,part.trim());
//     await new Promise(r=>setTimeout(r,200));
//   }

//   msgs.scrollTop=msgs.scrollHeight;
// }

// /* =================================================
//    ✅ FIX #2 — TYPING EXACT POSITION
//    ================================================= */
// function showTypingAfterLastUser(){
//   hideTyping();

//   typingNode = typingTemplate.cloneNode(true);
//   typingNode.style.display="block";
//   typingNode.id="bp-typing-live";

//   const lastUser=[...msgs.children].reverse()
//     .find(n=>n.classList.contains("bp-user"));

//   if(lastUser){
//     lastUser.after(typingNode);
//   }else{
//     msgs.appendChild(typingNode);
//   }

//   msgs.scrollTop=msgs.scrollHeight;
// }

// function hideTyping(){
//   if(typingNode){
//     typingNode.remove();
//     typingNode=null;
//   }
// }

// /* ================= BACKEND ================= */
// async function callStartAPI(user){
//   try{
//     const r=await fetch(START_ENDPOINT,{
//       method:"POST",
//       headers:{"Content-Type":"application/json"},
//       body:JSON.stringify(user)
//     });
//     const d=await r.json();
//     saveUser({...loadUser(),session_id:d.session_id});
//     return d.welcome || `Welcome ${user.name}!`;
//   }catch{
//     return `Welcome ${user.name}!`;
//   }
// }

// async function callChatAPI(email,session_id,message){
//   try{
//     const r=await fetch(CHAT_ENDPOINT,{
//       method:"POST",
//       headers:{"Content-Type":"application/json"},
//       body:JSON.stringify({email,session_id,message})
//     });
//     const d=await r.json();
//     return d.reply || "Sorry, I couldn't understand.";
//   }catch{
//     return "Sorry, I couldn't understand.";
//   }
// }

// function callEndChat(email,session_id){
//   if(!email||!session_id) return;
//   navigator.sendBeacon(
//     END_ENDPOINT,
//     new Blob([JSON.stringify({email,session_id})],
//     {type:"application/json"})
//   );
// }

// /* ================= EVENTS ================= */
// launcher.onclick=async()=>{
//   const s=loadUser();
//   if(s.name&&s.email&&s.phoneRaw){
//     showChat();
//     msgs.innerHTML="";
//     const w=await callStartAPI({
//       name:s.name,
//       email:s.email,
//       phone:s.cc+" "+s.phoneRaw
//     });
//     await printParagraphBubbles(w);
//   }else showForm();
// };

// closeBtn.onclick=()=>{
//   const s=loadUser();
//   if(s.email&&s.session_id) callEndChat(s.email,s.session_id);
//   hideChat();
// };

// /* ================= START ================= */
// document.getElementById("bp-start").onclick = async () => {
//   const name = nameInput.value.trim();
//   const email = emailInput.value.trim();
//   const raw = phoneInput.value.trim();

//   if (!name || !email || !raw) return alert("Fill all fields");

//   saveUser({ name, email, phoneRaw: raw, cc: ccSelect.value });

//   hideForm();
//   showChat();
//   msgs.innerHTML = "";

//   const welcome = await callStartAPI({
//     name,
//     email,
//     phone: ccSelect.value + " " + raw
//   });

//   await printParagraphBubbles(welcome);
// };

// /* ================= SEND ================= */
// send.onclick=handleSend;
// input.onkeydown=e=>{
//   if(e.key==="Enter"){e.preventDefault();if(!isBusy)handleSend();}
// };

// async function handleSend(){
//   if(isBusy) return;
//   const text=input.value.trim();
//   if(!text) return;

//   const s=loadUser();
//   if(!s.session_id) return alert("Start chat first");

//   isBusy=true;send.disabled=true;
//   appendBubble(text,"user");
//   input.value="";
//   showTypingAfterLastUser();

//   try{
//     let reply=await callChatAPI(s.email,s.session_id,text);
//     reply=cleanReply(reply);
//     hideTyping();
//     await printParagraphBubbles(reply);
//   }catch{
//     hideTyping();
//     appendBubble("⚠ Unable to connect.","bot");
//   }

//   isBusy=false;send.disabled=false;input.focus();
// }

// window.onbeforeunload=()=>{
//   const s=loadUser();
//   if(s.email&&s.session_id) callEndChat(s.email,s.session_id);
// };

const API_BASE = "http://127.0.0.1:5500";

const START_ENDPOINT = `${API_BASE}/start_chat`;
const CHAT_ENDPOINT  = `${API_BASE}/chat_message`;
const END_ENDPOINT   = `${API_BASE}/end_chat`;

/* ================= ELEMENTS ================= */
const launcher = document.getElementById("bp-launcher");
const form     = document.getElementById("bp-form");
const chat     = document.getElementById("bp-chat");
const closeBtn = document.getElementById("bp-close");

const msgs   = document.getElementById("bp-messages");
const typingTemplate = document.getElementById("bp-typing");

const input = document.getElementById("bp-input");
const send  = document.getElementById("bp-send");

const nameInput  = document.getElementById("bp-name");
const emailInput = document.getElementById("bp-email");
const phoneInput = document.getElementById("bp-phone");
const ccSelect   = document.getElementById("bp-cc");
const consentCheckbox = document.getElementById("bp-consent");

/* ================= STATE ================= */
let isBusy = false;
let typingNode = null;

/* ================= STORAGE ================= */
function loadUser() {
  try { return JSON.parse(sessionStorage.getItem("bp-user") || "{}"); }
  catch { return {}; }
}
function saveUser(user) {
  sessionStorage.setItem("bp-user", JSON.stringify(user));
}

/* ================= COUNTRY CODES ================= */
["+1","+92","+44","+971","+91","+61"].forEach(c=>{
  ccSelect.innerHTML += `<option value="${c}">${c}</option>`;
});
ccSelect.value = "+1";

/* ================= AUTOFILL ================= */
(() => {
  const s = loadUser();
  if (s.name) nameInput.value = s.name;
  if (s.email) emailInput.value = s.email;
  if (s.phoneRaw) phoneInput.value = s.phoneRaw;
  if (s.cc) ccSelect.value = s.cc;
})();
[nameInput,emailInput,phoneInput,ccSelect].forEach(el=>{
  el.addEventListener("input",()=>{
    saveUser({...loadUser(),
      name:nameInput.value,
      email:emailInput.value,
      phoneRaw:phoneInput.value,
      cc:ccSelect.value
    });
  });
});

/* ================= UI ================= */
function showForm(){form.style.display="flex";}
function hideForm(){form.style.display="none";}
function showChat(){chat.style.display="flex";input.focus();}
function hideChat(){chat.style.display="none";}

function appendBubble(text,from="bot"){
  const d=document.createElement("div");
  d.className="bp-msg "+(from==="user"?"bp-user":"bp-bot");
  d.textContent=text;
  msgs.appendChild(d);
  msgs.scrollTop=msgs.scrollHeight;
  return d;
}

/* ================= CLEAN ================= */
function cleanReply(t){
  return (t||"")
    .replace(/\*\*(.*?)\*\*/g,"$1")
    .replace(/\*(.*?)\*/g,"$1")
    .replace(/_(.*?)_/g,"$1")
    .replace(/\r/g,"")
    .replace(/[ \t]+/g," ")
    .trim();
}

/* ================= TYPEWRITER ================= */
async function typeMessage(div,text){
  for(const c of text){
    div.textContent+=c;
    msgs.scrollTop=msgs.scrollHeight;
    await new Promise(r=>setTimeout(r,10));
  }
}

/* =================================================
   ✅ EMBEDDED CHUNKING LOGIC (ONLY CHANGE)
   ================================================= */
async function printParagraphBubbles(fullText){

  const clean = fullText
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/\r/g, "")
    .trim();

  // Paragraph-based chunking (2+ newlines)
  let chunks = clean
    .split(/\n{2,}/)
    .map(p => p.trim())
    .filter(Boolean);

  // Sentence fallback if only one paragraph
  if (chunks.length === 1) {
    chunks = clean
      .split(/(?<=[.!?])\s+(?=[A-Z])/)
      .map(s => s.trim())
      .filter(Boolean);
  }

  for (const chunk of chunks) {
    const bubble=document.createElement("div");
    bubble.className="bp-msg bp-bot";
    msgs.appendChild(bubble);
    await typeMessage(bubble,chunk);
    await new Promise(r=>setTimeout(r,200));
  }

  msgs.scrollTop=msgs.scrollHeight;
}

/* ================= TYPING INDICATOR ================= */
function showTypingAfterLastUser(){
  hideTyping();

  typingNode = typingTemplate.cloneNode(true);
  typingNode.style.display="block";
  typingNode.id="bp-typing-live";

  const lastUser=[...msgs.children].reverse()
    .find(n=>n.classList.contains("bp-user"));

  if(lastUser){
    lastUser.after(typingNode);
  }else{
    msgs.appendChild(typingNode);
  }

  msgs.scrollTop=msgs.scrollHeight;
}

function hideTyping(){
  if(typingNode){
    typingNode.remove();
    typingNode=null;
  }
}

/* ================= BACKEND ================= */
async function callStartAPI(user){
  try{
    const r=await fetch(START_ENDPOINT,{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(user)
    });
    const d=await r.json();
    saveUser({...loadUser(),session_id:d.session_id});
    return d.welcome || `Welcome ${user.name}!`;
  }catch{
    return `Welcome ${user.name}!`;
  }
}

async function callChatAPI(email,session_id,message){
  try{
    const r=await fetch(CHAT_ENDPOINT,{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify({email,session_id,message})
    });
    const d=await r.json();
    return d.reply || "Sorry, I couldn't understand.";
  }catch{
    return "Sorry, I couldn't understand.";
  }
}

function callEndChat(email,session_id){
  if(!email||!session_id) return;
  navigator.sendBeacon(
    END_ENDPOINT,
    new Blob([JSON.stringify({email,session_id})],
    {type:"application/json"})
  );
}

/* ================= EVENTS ================= */
launcher.onclick=async()=>{
  const s=loadUser();
  if(s.name&&s.email&&s.phoneRaw){
    showChat();
    msgs.innerHTML="";
    const w=await callStartAPI({
      name:s.name,
      email:s.email,
      phone:s.cc+" "+s.phoneRaw
    });
    await printParagraphBubbles(w);
  }else showForm();
};

closeBtn.onclick=()=>{
  const s=loadUser();
  if(s.email&&s.session_id) callEndChat(s.email,s.session_id);
  hideChat();
};

/* ================= START ================= */
document.getElementById("bp-start").onclick = async () => {
  const name = nameInput.value.trim();
  const email = emailInput.value.trim();
  const raw = phoneInput.value.trim();

  if (!name || !email || !raw)
  return alert("Fill all fields");

if (!consentCheckbox.checked)
  return alert("Please agree to be contacted before starting the chat.");


  saveUser({ name, email, phoneRaw: raw, cc: ccSelect.value });

  hideForm();
  showChat();
  msgs.innerHTML = "";

  const welcome = await callStartAPI({
    name,
    email,
    phone: ccSelect.value + " " + raw
  });

  await printParagraphBubbles(welcome);
};

/* ================= SEND ================= */
send.onclick=handleSend;
input.onkeydown=e=>{
  if(e.key==="Enter"){e.preventDefault();if(!isBusy)handleSend();}
};

async function handleSend(){
  if(isBusy) return;
  const text=input.value.trim();
  if(!text) return;

  const s=loadUser();
  if(!s.session_id) return alert("Start chat first");

  isBusy=true;send.disabled=true;
  appendBubble(text,"user");
  input.value="";
  showTypingAfterLastUser();

  try{
    let reply=await callChatAPI(s.email,s.session_id,text);
    reply=cleanReply(reply);
    hideTyping();
    await printParagraphBubbles(reply);
  }catch{
    hideTyping();
    appendBubble("⚠ Unable to connect.","bot");
  }

  isBusy=false;send.disabled=false;input.focus();
}

window.onbeforeunload=()=>{
  const s=loadUser();
  if(s.email&&s.session_id) callEndChat(s.email,s.session_id);
};
