/* Thunai accounts UI: login (phone + PIN), history, delete my data, helper source check. Uses globals from app.js + phase2.js. */
Object.assign(T.ta, {
  login: "உள்நுழை", logout: "வெளியேறு", history: "முந்தைய உரையாடல்கள்", register: "புதிய பதிவு", guest: "விருந்தினராகத் தொடர்",
  phone: "கைபேசி எண் (உதவியாளர்: பயனர் பெயர்)", pin: "4 இலக்க PIN (உதவியாளர்: கடவுச்சொல்)", close: "மூடு",
  consentLogin: "என் குடும்ப விவரங்கள் இந்தக் கைபேசி எண்ணின் கீழ் சேமிக்கப்படுவதை ஏற்கிறேன். ஆதார், வங்கி எண், OTP ஒருபோதும் சேமிக்கப்படாது. எப்போது வேண்டுமானாலும் நீக்கலாம்.",
  loginNote: "OTP வேண்டாம்: OTP-ஐ யாரிடமும் பகிர வேண்டாம் என்பதால் PIN பயன்படுத்துகிறோம்.",
  noChats: "சேமித்த உரையாடல்கள் இல்லை.", deleteMe: "என் விவரங்கள் அனைத்தையும் நீக்கு", deleted: "உங்கள் விவரங்கள் நீக்கப்பட்டன.",
  confirmDelete: "உங்கள் கணக்கு மற்றும் சேமித்த உரையாடல்கள் அனைத்தும் நீக்கப்படும். தொடரவா?", saved: "சேமிக்கப்பட்டது", loggedIn: "உள்நுழைந்துள்ளீர்கள்",
  sourcesTitle: "அதிகாரப்பூர்வ ஆதாரச் சரிபார்ப்பு", checkSources: "ஆதாரங்களைச் சரிபார்", sources: { baseline: "அடிப்படை பதிவு", unchanged: "மாற்றமில்லை", changed: "மாறியுள்ளது: சரிபார்க்க வேண்டும்", unreachable: "அணுக முடியவில்லை" },
  stale: "தகவல் பழையதாக இருக்கலாம்", reopened: "முந்தைய உரையாடல் மீண்டும் திறக்கப்பட்டது.",
  rematchTitle: "புதிய திட்டங்கள்: சேமித்த குடும்பங்களை மறுசரிபார்", rematchBtn: "சேமித்த குடும்பங்களை மறுசரிபார்",
  rematchNote: "திட்ட விதிகள் புதுப்பிக்கப்பட்ட பின், சேமித்த ஒவ்வொரு குடும்பத்தையும் முகவர் மீண்டும் சரிபார்த்து, புதிதாகத் தகுதி பெறுபவர்களுக்குக் குறுஞ்செய்தி தயாரிக்கிறது.",
  rmChecked: "சரிபார்த்த குடும்பங்கள்", rmAlerted: "புதிதாகத் தகுதி பெற்றவை", rmNone: "புதிதாகத் தகுதி பெற்ற குடும்பம் இல்லை.", rmSchemes: "செயலில் உள்ள திட்டங்கள்",
  gateTitle: "துணையில் உள்நுழையவும்", gateSub: "உங்கள் குடும்பத்தின் முன்னேற்றம் சேமிக்கப்படும்; எப்போது வேண்டுமானாலும் தொடரலாம்.",
  or: "அல்லது", guestNote: "விருந்தினர் முறையில் எதுவும் சேமிக்கப்படாது. மாதிரி குடும்பங்களைப் பார்க்க இது போதும்.",
  needConsent: "பதிவு செய்ய ஒப்புதல் பெட்டியைத் தேர்ந்தெடுக்கவும்.",
  gateInfoTitle: "துணை என்ன செய்கிறது", gFind: "கண்டறி", gFindT: "தமிழில் பேசுங்கள்; குடும்பத்துக்குரிய அனைத்துத் திட்டங்களையும் அதிகாரப்பூர்வ விதிகளின்படி சரிபார்க்கிறது.",
  gFix: "சரிசெய்", gFixT: "ஆவணங்களில் உள்ள பெயர் வேறுபாடு, இல்லாத ஆவணங்களைக் கண்டறிந்து குறைந்த பயணங்களில் சரிசெய்யத் திட்டமிடுகிறது.",
  gFollow: "பின்தொடர்", gFollowT: "கடிதங்களைத் தயாரிக்கிறது (உதவியாளர் ஒப்புதலுடன்), பணம் நின்றால் காரணம் கண்டறிகிறது, நினைவூட்டுகிறது.",
  gRule: "விதிகள் முடிவு செய்கின்றன · AI புரிந்துகொள்கிறது · மனிதர்கள் ஒப்புதல் அளிக்கின்றனர்",
  gPrivacy: ["ஆதார் எண், வங்கிக் கணக்கு எண், OTP ஒருபோதும் கேட்கப்படாது.", "PIN மறைகுறியாக்கப்பட்டு (hash) சேமிக்கப்படுகிறது.", "உங்கள் விவரங்களை எப்போது வேண்டுமானாலும் நீக்கலாம்."],
});
Object.assign(T.en, {
  login: "Login", logout: "Logout", history: "Previous conversations", register: "Register", guest: "Continue as guest",
  phone: "Mobile number (helper: username)", pin: "4-digit PIN (helper: password)", close: "Close",
  consentLogin: "I agree that my family's details are saved under this mobile number. Aadhaar, bank numbers and OTPs are never stored. I can delete them at any time.",
  loginNote: "No OTP: we use a PIN because you should never share an OTP with anyone.",
  noChats: "No saved conversations.", deleteMe: "Delete all my data", deleted: "Your data has been deleted.",
  confirmDelete: "Your account and all saved conversations will be deleted. Continue?", saved: "Saved", loggedIn: "Logged in",
  sourcesTitle: "Official source check", checkSources: "Check sources", sources: { baseline: "Baseline recorded", unchanged: "Unchanged", changed: "Changed: needs review", unreachable: "Unreachable" },
  stale: "Information may be old", reopened: "Previous conversation reopened.",
  rematchTitle: "New schemes: re-check saved families", rematchBtn: "Re-check saved families",
  rematchNote: "After the scheme rules are updated, the agent re-checks every saved family and prepares an SMS for families who now qualify.",
  rmChecked: "Families checked", rmAlerted: "Newly eligible", rmNone: "No family is newly eligible.", rmSchemes: "Schemes active",
  gateTitle: "Sign in to Thunai", gateSub: "Your family's progress is saved so you can continue any time.",
  or: "or", guestNote: "Nothing is saved in guest mode. Enough to try the demo families.",
  needConsent: "Please tick the consent box to register.",
  gateInfoTitle: "What Thunai does", gFind: "Find", gFindT: "Talk in Tamil; every scheme your family qualifies for is checked against official rules.",
  gFix: "Fix", gFixT: "Finds name mismatches and missing documents, and plans the fixes in the fewest office visits.",
  gFollow: "Follow", gFollowT: "Drafts letters (approved by a helper), finds why a payment stopped, and reminds you.",
  gRule: "Rules decide · AI understands · Humans approve",
  gPrivacy: ["Aadhaar numbers, bank account numbers and OTPs are never asked for.", "Your PIN is stored only as a secure hash.", "You can delete your data at any time."],
});

const acct = { token: null, user: null, timer: null };
try { acct.token = sessionStorage.getItem("thunai.token"); acct.user = JSON.parse(sessionStorage.getItem("thunai.user") || "null"); } catch (e) { /* ignore */ }

async function authApi(method, path, body) {
  const r = await fetch(path, { method, headers: { "Content-Type": "application/json", ...(acct.token ? { Authorization: `Bearer ${acct.token}` } : {}) },
    body: body ? JSON.stringify(body) : undefined });
  if (!r.ok) {
    if (r.status === 401 && acct.token && !path.includes("/auth/")) setUser(null, null);
    throw new Error((await r.json().catch(() => ({}))).detail || r.statusText);
  }
  return r.json();
}

function setUser(token, user) {
  acct.token = token; acct.user = user;
  try {
    if (token) { sessionStorage.setItem("thunai.token", token); sessionStorage.setItem("thunai.user", JSON.stringify(user)); }
    else { sessionStorage.removeItem("thunai.token"); sessionStorage.removeItem("thunai.user"); }
  } catch (e) { /* ignore */ }
  if (user && user.role === "helper" && typeof p2 !== "undefined") p2.helper = user.name || "Helper";
  renderAccount();
  if (typeof renderPhase2 === "function") renderPhase2();
}

function renderAccount() {
  const box = $("#acctBox");
  if (!box) return;
  if (acct.user) {
    box.innerHTML = `<span class="muted small">${esc(acct.user.role === "helper" ? acct.user.name || "Helper" : acct.user.phone_masked)}</span>
      <button class="link-btn" id="histBtn">${esc(t("history"))}</button><button class="link-btn" id="logoutBtn">${esc(t("logout"))}</button>`;
    $("#histBtn").onclick = openHistory;
    $("#logoutBtn").onclick = async () => {
      try { await authApi("POST", "/api/auth/logout"); } catch (e) { /* ignore */ }
      setUser(null, null); setGuest(false); startSession(); showGate();
    };
  } else {
    box.innerHTML = `<button class="link-btn" id="loginBtn">${esc(t("login"))}</button>`;
    $("#loginBtn").onclick = openLogin;
  }
}

function modal(html) {
  closeModal();
  const m = document.createElement("div");
  m.id = "modal";
  m.className = "modal-back";
  m.innerHTML = `<div class="modal" role="dialog" aria-modal="true">${html}</div>`;
  m.onclick = (e) => { if (e.target === m) closeModal(); };
  document.body.appendChild(m);
  return m;
}
function closeModal() { $("#modal")?.remove(); }

function openLogin() { showGate(); }

function isGuest() { try { return sessionStorage.getItem("thunai.guest") === "1"; } catch (e) { return false; } }
function setGuest(on) { try { on ? sessionStorage.setItem("thunai.guest", "1") : sessionStorage.removeItem("thunai.guest"); } catch (e) { /* ignore */ } }

function hideGate() { $("#gate")?.remove(); document.body.classList.remove("gated"); }

function showGate() {
  hideGate();
  document.body.classList.add("gated");
  const g = document.createElement("section");
  g.id = "gate";
  g.className = "gate container";
  g.innerHTML = `
    <div class="gate-card panel-box">
      <div class="panel-head"><h2>${esc(t("gateTitle"))}</h2><p>${esc(t("gateSub"))}</p></div>
      <form id="gateForm" class="gate-form" autocomplete="on">
        <label class="field">${esc(t("phone"))}<input id="lgPhone" autocomplete="username" inputmode="text" required></label>
        <label class="field">${esc(t("pin"))}<input id="lgPin" type="password" autocomplete="current-password" required></label>
        <label class="check"><input type="checkbox" id="lgConsent"> <span class="small">${esc(t("consentLogin"))}</span></label>
        <div id="lgErr" class="form-err hidden" role="alert"></div>
        <div class="row-btns wrap"><button class="btn btn-primary" id="lgLogin" type="submit">${esc(t("login"))}</button>
          <button class="btn btn-outline" id="lgReg" type="button">${esc(t("register"))}</button></div>
        <p class="muted small">${esc(t("loginNote"))}</p>
        <div class="gate-or"><span>${esc(t("or"))}</span></div>
        <button class="btn btn-outline gate-guest" id="lgGuest" type="button">${esc(t("guest"))}</button>
        <p class="muted small">${esc(t("guestNote"))}</p>
      </form>
    </div>
    <div class="gate-info panel-box">
      <div class="panel-head"><h2>${esc(t("gateInfoTitle"))}</h2></div>
      <ol class="gate-steps">
        <li><strong>${esc(t("gFind"))}</strong><span>${esc(t("gFindT"))}</span></li>
        <li><strong>${esc(t("gFix"))}</strong><span>${esc(t("gFixT"))}</span></li>
        <li><strong>${esc(t("gFollow"))}</strong><span>${esc(t("gFollowT"))}</span></li>
      </ol>
      <div class="gate-rule">${esc(t("gRule"))}</div>
      <ul class="gate-privacy small">${t("gPrivacy").map((x) => `<li>${esc(x)}</li>`).join("")}</ul>
    </div>`;
  document.querySelector(".navbar").after(g);
  const err = (m) => { const e = $("#lgErr"); e.textContent = m; e.classList.remove("hidden"); };
  const creds = () => ({ phone: $("#lgPhone").value.trim(), pin: $("#lgPin").value.trim() });
  const enter = (r) => {
    setGuest(false);
    try { localStorage.setItem("thunai.consent", "1"); } catch (e) { /* ignore */ }
    $("#consent")?.classList.add("hidden");
    setUser(r.token, r.user);
    hideGate();
    toast(t("loggedIn"));
    autosave();
  };
  $("#gateForm").onsubmit = async (e) => {
    e.preventDefault();
    try { enter(await authApi("POST", "/api/auth/login", creds())); } catch (x) { err(x.message); }
  };
  $("#lgReg").onclick = async () => {
    if (!$("#lgConsent").checked) { err(t("needConsent")); return; }
    try { enter(await authApi("POST", "/api/auth/register", { ...creds(), consent: true })); } catch (x) { err(x.message); }
  };
  $("#lgGuest").onclick = () => { setGuest(true); hideGate(); };
  setTimeout(() => $("#lgPhone")?.focus(), 50);
}

async function openHistory() {
  let chats = [];
  try { chats = (await authApi("GET", "/api/history")).chats; } catch (e) { toast(`${t("warn")} ${e.message}`); return; }
  modal(`<h2>${esc(t("history"))}</h2>` +
    (chats.length ? `<ul class="p2-list">` + chats.map((c) => `<li class="row"><span><strong>${esc(c.title)}</strong>
      <div class="muted small">${esc(inr(c.rupees_per_year || 0))} · ${esc(c.updated || "")}</div></span>
      <button class="btn btn-outline btn-sm" data-chat="${esc(c.chat_id)}">${esc(t("open"))}</button></li>`).join("") + "</ul>"
      : `<p class="muted">${esc(t("noChats"))}</p>`) +
    `<div class="row-btns wrap"><button class="btn btn-outline btn-sm danger" id="delMe">${esc(t("deleteMe"))}</button>
     <button class="link-btn" id="mClose">${esc(t("close"))}</button></div>`);
  document.querySelectorAll("[data-chat]").forEach((b) => b.onclick = () => reopen(b.dataset.chat));
  $("#mClose").onclick = closeModal;
  $("#delMe").onclick = async () => {
    if (!confirm(t("confirmDelete"))) return;
    try { await authApi("DELETE", "/api/me"); setUser(null, null); setGuest(false); closeModal(); startSession(); showGate(); toast(t("deleted")); }
    catch (e) { toast(`${t("warn")} ${e.message}`); }
  };
}

async function reopen(chatId) {
  try {
    const r = await authApi("GET", `/api/history/${encodeURIComponent(chatId)}`);
    closeModal();
    state.sid = r.session_id;
    $("#agentLog").innerHTML = ""; $("#chatLog").innerHTML = ""; state.snap = null;
    if (typeof p2 !== "undefined") { p2.doctor = null; p2.drafts = []; p2.outbox = []; p2.cards = []; }
    handle(r, false);
    bubble("agent", t("reopened"), "", { en: T.en.reopened, ta: T.ta.reopened });
  } catch (e) { toast(`${t("warn")} ${e.message}`); }
}

function logEvents() {
  return Array.from(document.querySelectorAll("#agentLog li")).slice(-200)
    .map((li) => ({ type: li.dataset.type, icon: "", text_en: li.dataset.en, text_ta: li.dataset.ta, detail: {} }));
}

function autosave() {
  if (!acct.token || !state.sid) return;
  clearTimeout(acct.timer);
  acct.timer = setTimeout(async () => {
    if (!state.snap || !(state.snap.facts.members || []).length) return;
    try { await authApi("POST", "/api/history/save", { session_id: state.sid, events: logEvents() }); } catch (e) { /* saving is best effort */ }
  }, 2500);
}

// Save after every agent response while logged in.
const _handleBase = handle;
handle = function (r, showReply = true) { _handleBase(r, showReply); autosave(); };

// Helper-only: official source check, shown at the end of the Helper tab.
const _renderHelperBase = renderHelper;
renderHelper = function () {
  _renderHelperBase();
  if (!acct.user || acct.user.role !== "helper") return;
  const sec = document.createElement("div");
  sec.innerHTML = `<h3 class="p2-h">${esc(t("sourcesTitle"))}</h3>
    <button class="btn btn-outline btn-sm" id="srcBtn">${esc(t("checkSources"))}</button><div id="srcOut"></div>
    <h3 class="p2-h">${esc(t("rematchTitle"))}</h3><p class="muted small">${esc(t("rematchNote"))}</p>
    <button class="btn btn-outline btn-sm" id="rmBtn">${esc(t("rematchBtn"))}</button><div id="rmOut"></div>`;
  $("#panel-helper").appendChild(sec);
  $("#srcBtn").onclick = checkSources;
  $("#rmBtn").onclick = rematchFamilies;
};

async function checkSources() {
  $("#srcOut").innerHTML = `<p class="muted small">${esc(t("thinking"))}</p>`;
  try {
    const r = await authApi("GET", "/api/admin/check_sources");
    const lvl = { unchanged: "GREEN", baseline: "GREEN", changed: "YELLOW", unreachable: "RED" };
    $("#srcOut").innerHTML = `<table class="data-table"><tbody>` + r.results.map((x) => `<tr><td>${esc(x.name_en)}</td>
      <td><span class="lvl ${lvl[x.status] || "YELLOW"}">${esc(t("sources")[x.status] || x.status)}</span>${x.stale ? ` <span class="lvl YELLOW">${esc(t("stale"))}</span>` : ""}</td>
      <td class="small">${x.url ? `<a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(new URL(x.url).hostname)}</a>` : ""}</td></tr>`).join("") +
      `</tbody></table><p class="muted small">${esc(state.lang === "ta" ? r.note_ta : r.note_en)}</p>`;
  } catch (e) { $("#srcOut").innerHTML = ""; toast(`${t("warn")} ${e.message}`); }
}

async function rematchFamilies() {
  $("#rmOut").innerHTML = `<p class="muted small">${esc(t("thinking"))}</p>`;
  try {
    const r = await authApi("POST", "/api/admin/rematch");
    enqueue(r.events || []);
    const hits = (r.results || []).filter((x) => (x.new || []).length);
    $("#rmOut").innerHTML = `<p class="small">${esc(t("rmChecked"))}: <strong>${r.checked}</strong> · ${esc(t("rmAlerted"))}: <strong>${r.alerted}</strong>` +
      (r.schemes_enabled ? ` · ${esc(t("rmSchemes"))}: ${r.schemes_enabled}` : "") + "</p>" +
      (hits.length ? `<ul class="p2-list">` + hits.map((x) => `<li><strong>${esc(x.title)}</strong><div class="small">` +
        x.new.map((n) => `${esc(short(state.lang === "ta" ? n.name_ta : n.name_en))}${n.member_name ? " (" + esc(n.member_name) + ")" : ""}: ${esc(state.lang === "ta" ? n.benefit_ta : n.benefit_en)}`).join("<br>") +
        "</div></li>").join("") + "</ul>" : `<p class="muted small">${esc(t("rmNone"))}</p>`) +
      ((r.messages || []).length ? `<ul class="p2-list">` + r.messages.map((m) => `<li><div class="sms">${esc(m.text)}</div><div class="muted small">${esc(m.to)} · ${esc(m.status)}</div></li>`).join("") + "</ul>" : "");
  } catch (e) { $("#rmOut").innerHTML = ""; toast(`${t("warn")} ${e.message}`); }
}

document.addEventListener("DOMContentLoaded", () => setTimeout(() => {
  const tools = document.querySelector(".header-tools");
  const box = document.createElement("div");
  box.id = "acctBox"; box.className = "acct";
  tools.insertBefore(box, tools.firstChild);
  renderAccount();
  if (!acct.user && !isGuest()) showGate();
  $$(".lang-switch button").forEach((b) => b.addEventListener("click", () => {
    renderAccount();
    if ($("#gate")) { const ph = $("#lgPhone").value, pn = $("#lgPin").value; showGate(); $("#lgPhone").value = ph; $("#lgPin").value = pn; }
  }));
}, 0));
