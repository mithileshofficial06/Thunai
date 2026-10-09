/* Thunai UI (government-portal style). Talks to the FastAPI backend (shapes: docs/06_CONTRACTS.md). */
const $ = (s) => document.querySelector(s);
const $$ = (s) => Array.from(document.querySelectorAll(s));

const T = {
  ta: {
    tagline: "நலத்திட்ட உதவியாளர் · தமிழ்நாடு (முன்மாதிரி)", clear: "புதிதாகத் தொடங்கு",
    navTitle: "குடிமக்கள் உதவி சேவை", demoLabel: "மாதிரி குடும்பங்கள்:",
    loadMurugan: "முருகன் குடும்பம்", loadMeena: "மீனா", loadLakshmi: "லட்சுமி",
    chatTitle: "உதவியாளர்", chatHint: "உங்கள் குடும்பத்தைப் பற்றித் தமிழில் அல்லது ஆங்கிலத்தில் சொல்லுங்கள்.",
    consent: "நீங்கள் சொல்வதை மட்டுமே பயன்படுத்துவோம். ஆதார் எண், வங்கிக் கணக்கு எண், OTP ஒருபோதும் கேட்க மாட்டோம். உங்கள் பதில்கள் புரிந்துகொள்ள இலவச AI சேவைக்கு அனுப்பப்படும். உங்கள் விவரங்கள் இந்தச் சாதனத்தில் மட்டுமே சேமிக்கப்படும்.",
    consentOk: "ஏற்கிறேன், தொடரவும்", chatPlaceholder: "உங்கள் குடும்பத்தைப் பற்றிச் சொல்லுங்கள்", send: "அனுப்பு", mic: "பேசு",
    rupeesLabel: "மதிப்பிடப்பட்ட ஆண்டு நன்மை", perYearNote: "திட்டங்களிலிருந்து", tripsLabel: "தேவையான அலுவலகப் பயணங்கள்", insteadOf: "தயாரிப்பு இல்லாமல்:",
    familyCard: "குடும்ப விவரங்கள்", familyHint: "தவறு இருந்தால் 'திருத்து' அழுத்தவும்; முடிவுகள் உடனே மாறும்.",
    colName: "பெயர்", colRelation: "உறவு", colAge: "வயது",
    schemesTitle: "தகுதி முடிவுகள்", schemesHint: "அதிகாரப்பூர்வ விதிகளின் அடிப்படையில் கணக்கிடப்பட்டது.",
    tabFix: "சரிசெய்ய வேண்டியவை", tabDoctor: "பணம் வரவில்லையா?", tabLetters: "கடிதங்கள்", tabHelper: "உதவியாளர் ஒப்புதல்",
    comingSoon: "இந்தப் பகுதி அடுத்த கட்டத்தில் சேர்க்கப்படும்.",
    agentTitle: "முகவர் செயல்பாட்டுப் பதிவு", agentHint: "முகவர் எடுக்கும் ஒவ்வொரு முடிவும் செயலும் இங்கே காட்டப்படும்.",
    mChat: "உதவியாளர்", mFamily: "குடும்பம்", mSchemes: "முடிவுகள்", mAgent: "செயல்பாடு",
    disclaimerTitle: "அறிவிப்பு:", disclaimer: "இங்கு காட்டப்படும் தகுதி ஒரு மதிப்பீடு மட்டுமே. இறுதி முடிவு சம்பந்தப்பட்ட துறையினுடையது. உங்கள் OTP-ஐ யாரிடமும் பகிர வேண்டாம்.",
    footerMeta: "திட்ட விதிகள் அதிகாரப்பூர்வ ஆதாரங்களிலிருந்து 9 அக்டோபர் 2026 அன்று சரிபார்க்கப்பட்டன · Thunai முன்மாதிரி",
    hello: "வணக்கம். நான் துணை. உங்கள் வீட்டில் யார் யார் இருக்கிறார்கள்? ஒவ்வொருவரின் பெயர், உறவு, வயது சொல்லுங்கள்.",
    who: "துணை", you: "நீங்கள்", why: "தகுதி அளவுகோல்கள்", source: "அதிகாரப்பூர்வ ஆதாரம்", verified: "சரிபார்த்த நாள்",
    schemes: "திட்டங்கள்", edit: "திருத்து", confirm: "உறுதிசெய்", toConfirm: "உறுதிப்படுத்த வேண்டும்",
    income: "ஆண்டு குடும்ப வருமானம்", card: "குடும்ப அட்டை வகை", wet: "நன்செய் நிலம் (ஏக்கர்)", dry: "புன்செய் நிலம் (ஏக்கர்)", units: "ஆண்டு மின் பயன்பாடு (யூனிட்)",
    st: { ELIGIBLE: "தகுதி உண்டு", NEED_INFO: "தகவல் தேவை", NOT_ELIGIBLE: "தகுதி இல்லை" },
    crit: { met: "பொருந்துகிறது", notmet: "பொருந்தவில்லை", unknown: "தெரியவில்லை" },
    kind: { goal: "இலக்கு", plan: "திட்டம்", decided: "முடிவு", tool: "செயல்", replan: "மறுதிட்டம்", privacy: "தனியுரிமை", fallback: "அறிவிப்பு", reply: "பயனர்", error: "பிழை" },
    rel: { self: "விண்ணப்பதாரர்", spouse_f: "மனைவி", spouse_m: "கணவர்", daughter: "மகள்", son: "மகன்", mother: "தாய்", father: "தந்தை", other: "உறவினர்" },
    unknown: "குறிப்பிடப்படவில்லை", thinking: "சிந்திக்கிறது...", noFamily: "இன்னும் குடும்ப விவரங்கள் இல்லை.", noSchemes: "குடும்ப விவரங்கள் கிடைத்ததும் முடிவுகள் இங்கே தோன்றும்.",
    welcomeBack: "மீண்டும் வருக.", next: "அடுத்து:", warn: "எச்சரிக்கை:",
  },
  en: {
    tagline: "Welfare Scheme Assistant · Tamil Nadu (Prototype)", clear: "Start over",
    navTitle: "Citizen Assistance Service", demoLabel: "Demo families:",
    loadMurugan: "Murugan family", loadMeena: "Meena", loadLakshmi: "Lakshmi",
    chatTitle: "Assistant", chatHint: "Describe your family in Tamil or English.",
    consent: "We only use what you tell us. We never ask for your Aadhaar number, bank account number or OTP. Your answers are sent to a free AI service to understand them. Your details are stored only on this device.",
    consentOk: "I agree, continue", chatPlaceholder: "Tell us about your family", send: "Send", mic: "Speak",
    rupeesLabel: "Estimated annual benefit", perYearNote: "schemes", tripsLabel: "Office visits needed", insteadOf: "Without preparation:",
    familyCard: "Family details", familyHint: "Select 'Edit' to correct any detail; results update immediately.",
    colName: "Name", colRelation: "Relation", colAge: "Age",
    schemesTitle: "Eligibility results", schemesHint: "Assessed against official scheme rules.",
    tabFix: "What to fix", tabDoctor: "Payment stopped?", tabLetters: "Letters", tabHelper: "Helper review",
    comingSoon: "This section will be added in the next phase.",
    agentTitle: "Agent activity log", agentHint: "Every decision and action taken by the agent is recorded here.",
    mChat: "Assistant", mFamily: "Family", mSchemes: "Results", mAgent: "Activity",
    disclaimerTitle: "Disclaimer:", disclaimer: "Eligibility shown here is an estimate. The concerned department makes the final decision. Never share your OTP with anyone.",
    footerMeta: "Scheme rules verified from official sources on 9 October 2026 · Thunai prototype",
    hello: "Welcome. I am Thunai. Who lives in your home? Please tell me each person's name, relation and age.",
    who: "Thunai", you: "You", why: "Eligibility criteria", source: "Official source", verified: "Verified on",
    schemes: "schemes", edit: "Edit", confirm: "Confirm", toConfirm: "to be confirmed",
    income: "Annual family income", card: "Ration card type", wet: "Wet land (acres)", dry: "Dry land (acres)", units: "Electricity use per year (units)",
    st: { ELIGIBLE: "Eligible", NEED_INFO: "Needs information", NOT_ELIGIBLE: "Not eligible" },
    crit: { met: "Met", notmet: "Not met", unknown: "Unknown" },
    kind: { goal: "Goal", plan: "Plan", decided: "Decision", tool: "Action", replan: "Re-plan", privacy: "Privacy", fallback: "Notice", reply: "User", error: "Error" },
    rel: { self: "Applicant", spouse_f: "Wife", spouse_m: "Husband", daughter: "Daughter", son: "Son", mother: "Mother", father: "Father", other: "Relative" },
    unknown: "Not provided", thinking: "Working...", noFamily: "No family details yet.", noSchemes: "Results will appear here once family details are available.",
    welcomeBack: "Welcome back.", next: "Next:", warn: "Warning:",
  },
};

const state = { sid: null, lang: localStorage.getItem("thunai.lang") || "ta", snap: null, unconfirmed: [], queue: [], replaying: false };
const t = (k) => T[state.lang][k];
const short = (name) => String(name || "").split(" (")[0];
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const inr = (n) => `₹${Number(n || 0).toLocaleString("en-IN")}`;

// ---------------------------------------------------------------- storage
function save() { try { if (state.snap) localStorage.setItem("thunai.facts", JSON.stringify(state.snap.facts)); } catch (e) { /* storage unavailable */ } }
function saved() { try { return JSON.parse(localStorage.getItem("thunai.facts") || "null"); } catch (e) { return null; } }

// ---------------------------------------------------------------- API
async function api(path, body) {
  const auth = typeof acct !== "undefined" && acct.token ? { Authorization: `Bearer ${acct.token}` } : {};
  const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json", ...auth }, body: JSON.stringify(body || {}) });
  if (!r.ok) {
    const msg = (await r.json().catch(() => ({}))).detail || r.statusText;
    if (r.status === 404 && String(msg).includes("session")) await startSession();
    throw new Error(msg);
  }
  return r.json();
}

// ---------------------------------------------------------------- language
function applyLang() {
  document.documentElement.lang = state.lang;
  $$("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
  $$("[data-i18n-placeholder]").forEach((el) => { el.placeholder = t(el.dataset.i18nPlaceholder); });
  $$(".lang-switch button").forEach((b) => b.classList.toggle("on", b.dataset.lang === state.lang));
  if (state.snap) render(state.snap, false);
  $$("#chatLog .bubble").forEach((b) => {
    b.querySelector(".who").textContent = b.dataset.who === "agent" ? t("who") : t("you");
    if (b.dataset.en !== undefined) b.querySelector(".body").textContent = (state.lang === "ta" ? b.dataset.ta : b.dataset.en) || b.dataset.en;
  });
  $$("#agentLog li").forEach((li) => {
    li.querySelector(".txt").textContent = li.dataset[state.lang] || li.dataset.en;
    li.querySelector(".kind").textContent = t("kind")[li.dataset.type] || li.dataset.type;
  });
}

// ---------------------------------------------------------------- chat
function bubble(who, text, extra = "", both = null) {
  const div = document.createElement("div");
  div.className = `bubble ${who} ${extra}`;
  div.dataset.who = who;
  if (both) { div.dataset.en = both.en || ""; div.dataset.ta = both.ta || both.en || ""; }
  div.innerHTML = `<span class="who"></span><span class="body"></span>`;
  div.querySelector(".who").textContent = who === "agent" ? t("who") : t("you");
  div.querySelector(".body").textContent = text;
  $("#chatLog").appendChild(div);
  $("#chatLog").scrollTop = $("#chatLog").scrollHeight;
  return div;
}
const replyText = (reply) => (reply ? (reply[state.lang] || reply.en || "").trim() : "");

async function send(text, fromVoice = false) {
  text = text.trim();
  if (!text) return;
  bubble("user", text);
  const wait = bubble("agent", t("thinking"), "muted");
  try {
    if (typeof p2 !== "undefined" && p2.fromVoice) { fromVoice = true; p2.fromVoice = false; }
    const r = await api("/api/chat", { session_id: state.sid, text, lang: state.lang, from_voice: fromVoice });
    wait.remove();
    handle(r);
  } catch (e) { wait.remove(); toast(`${t("warn")} ${e.message}`); }
}

function handle(r, showReply = true) {
  state.unconfirmed = r.unconfirmed || [];
  if (typeof takeExtras === "function") takeExtras(r);
  enqueue(r.events || []);
  render(r.snapshot, true);
  renderAsk(r.pending_ask || []);
  if (showReply && r.reply) { const text = replyText(r.reply); if (text) { bubble("agent", text, "", r.reply); if (typeof speak === "function") speak(text); } }
  save();
}

function renderAsk(asks) {
  const box = $("#askBox");
  box.innerHTML = "";
  box.classList.toggle("hidden", !asks.length);
  asks.forEach((q) => {
    const div = document.createElement("div");
    div.innerHTML = `<div class="q"></div>`;
    div.querySelector(".q").textContent = state.lang === "ta" ? q.ta : q.en;
    q.options.forEach((opt) => {
      const b = document.createElement("button");
      b.className = "btn btn-outline btn-sm";
      b.textContent = typeof opt === "number" && q.path.endsWith("income") ? inr(opt) : String(opt);
      b.onclick = () => editFact(q.path, opt);
      div.appendChild(b);
    });
    box.appendChild(div);
  });
}

// ---------------------------------------------------------------- activity log (paced replay)
function enqueue(events) { state.queue.push(...events); if (!state.replaying) drain(); }
function drain() {
  const ev = state.queue.shift();
  if (!ev) { state.replaying = false; return; }
  state.replaying = true;
  const li = document.createElement("li");
  li.className = ev.type;
  li.dataset.type = ev.type;
  li.dataset.en = ev.text_en;
  li.dataset.ta = ev.text_ta || ev.text_en;
  const meta = [ev.detail?.provider, ev.detail?.checks].filter(Boolean).join(" · ");
  li.innerHTML = `<span class="kind"></span><span><span class="txt"></span>${meta ? '<span class="meta"></span>' : ""}</span>`;
  li.querySelector(".kind").textContent = t("kind")[ev.type] || ev.type;
  li.querySelector(".txt").textContent = state.lang === "ta" ? li.dataset.ta : li.dataset.en;
  if (meta) li.querySelector(".meta").textContent = meta;
  $("#agentLog").appendChild(li);
  $("#agentLog").scrollTop = $("#agentLog").scrollHeight;
  if (ev.type === "privacy") toast(state.lang === "ta" ? ev.text_ta : ev.text_en);
  setTimeout(drain, 220);
}

// ---------------------------------------------------------------- rendering
function render(snap, animate) {
  const prev = state.snap;
  state.snap = snap;
  $("#planSteps").innerHTML = snap.plan_steps.map((s, i) => `<li class="${s.done ? "done" : ""}">${i + 1}. ${esc(s[state.lang])}</li>`).join("");
  renderMembers(snap.facts);
  renderFacts(snap.facts);
  renderSchemes(snap.verdicts, animate ? prev : null);
  renderSummary(snap, animate ? prev : null);
  if (typeof renderPhase2 === "function") renderPhase2();
}

function relLabel(m) {
  const r = t("rel");
  if (m.relation === "spouse") return m.gender === "male" ? r.spouse_m : r.spouse_f;
  return r[m.relation] || r.other;
}

function renderMembers(facts) {
  const rows = (facts.members || []).map((m) => `<tr><td>${esc(m.name || m.id)}</td><td>${esc(relLabel(m))}</td><td>${m.age ?? "-"}</td></tr>`);
  $("#members").innerHTML = rows.length ? rows.join("") : `<tr class="empty-row"><td colspan="3">${esc(t("noFamily"))}</td></tr>`;
}

const FACT_ROWS = [
  ["family.annual_income", "income", (v) => inr(v)],
  ["family.ration_card_type", "card", (v) => v],
  ["family.wet_land_acres", "wet", (v) => v],
  ["family.dry_land_acres", "dry", (v) => v],
  ["family.electricity_units_per_year", "units", (v) => Number(v).toLocaleString("en-IN")],
];

function renderFacts(facts) {
  const tbody = $("#keyFacts");
  tbody.innerHTML = "";
  FACT_ROWS.forEach(([path, label, fmt]) => {
    const v = (facts.family || {})[path.split(".")[1]];
    const pending = state.unconfirmed.includes(path);
    const tr = document.createElement("tr");
    if (pending) tr.className = "unconfirmed";
    tr.innerHTML = `<td></td><td class="val"><span class="v"></span><button class="edit-link" type="button"></button></td>`;
    tr.children[0].textContent = t(label);
    tr.querySelector(".v").textContent = v == null ? t("unknown") : fmt(v);
    const editBtn = tr.querySelector(".edit-link");
    editBtn.textContent = t("edit");
    editBtn.onclick = () => inlineEdit(tr, path, v);
    if (pending) {
      const note = document.createElement("span");
      note.className = "tag-confirm";
      note.textContent = t("toConfirm");
      const ok = document.createElement("button");
      ok.className = "edit-link";
      ok.type = "button";
      ok.textContent = t("confirm");
      ok.onclick = () => editFact(path, v);
      tr.querySelector(".val").append(note, ok);
    }
    tbody.appendChild(tr);
  });
}

function inlineEdit(tr, path, current) {
  const cell = tr.querySelector(".val");
  const input = document.createElement("input");
  input.value = current ?? "";
  cell.innerHTML = "";
  cell.appendChild(input);
  input.focus();
  let finished = false;
  const done = async (commit) => {
    if (finished) return;
    finished = true;
    if (commit && input.value.trim() !== "" && input.value !== String(current ?? "")) await editFact(path, input.value.trim());
    else render(state.snap, false);
  };
  input.onkeydown = (e) => { if (e.key === "Enter") done(true); if (e.key === "Escape") done(false); };
  input.onblur = () => done(true);
}

async function editFact(path, value) {
  try { handle(await api("/api/facts", { session_id: state.sid, path, value }), false); }
  catch (e) { toast(`${t("warn")} ${e.message}`); }
}

function renderSchemes(verdicts, prev) {
  const before = {};
  (prev?.verdicts || []).forEach((v) => { before[v.key] = v.status; });
  const box = $("#schemes");
  if (!verdicts.length) { box.innerHTML = `<div class="empty">${esc(t("noSchemes"))}</div>`; return; }
  const order = { ELIGIBLE: 0, NEED_INFO: 1, NOT_ELIGIBLE: 2 };
  box.innerHTML = "";
  [...verdicts].sort((a, b) => order[a.status] - order[b.status]).forEach((v) => {
    const ta = state.lang === "ta";
    const changed = before[v.key] && before[v.key] !== v.status;
    const crit = v.reasons.map((r) => {
      const k = r.ok === true ? "met" : r.ok === false ? "notmet" : "unknown";
      return `<li><span class="crit ${k}">${esc(t("crit")[k])}</span><span>${esc(ta ? r.ta : r.en)}</span></li>`;
    }).join("");
    const el = document.createElement("article");
    el.className = `scheme ${v.status}${changed ? " changed" : ""}`;
    el.innerHTML = `
      <div class="scheme-top">
        <div>
          <div class="name">${esc(short(ta ? v.name_ta : v.name_en))}</div>
          <div class="sub">${esc(short(ta ? v.name_en : v.name_ta))}${v.member_name ? " · " + esc(v.member_name) : ""}</div>
        </div>
        <span class="status ${v.status}">${esc(t("st")[v.status])}</span>
      </div>
      <div class="benefit">${esc(ta ? v.benefit_ta : v.benefit_en)}</div>
      <details><summary>${esc(t("why"))}</summary><ul class="criteria">${crit}</ul></details>
      ${v.conflict_note ? `<div class="conflict">${esc(ta ? v.conflict_note.ta : v.conflict_note.en)}</div>` : ""}
      ${v.source_url ? `<div class="source">${esc(t("source"))}: <a href="${esc(v.source_url)}" target="_blank" rel="noopener">${esc(new URL(v.source_url).hostname)}</a> · ${esc(t("verified"))} ${esc(v.checked_on)}</div>` : ""}`;
    box.appendChild(el);
  });
}

function renderSummary(snap, prev) {
  countTo($("#rupees"), prev ? prev.rupees_per_year : 0, snap.rupees_per_year);
  $("#schemeCount").textContent = `${snap.verdicts.filter((v) => v.counted).length}`;
  $("#tripsWith").textContent = snap.trips.with;
  $("#tripsWithout").textContent = snap.trips.without;
  $("#tripsBox").title = state.lang === "ta"
    ? "தயாரிப்பு இல்லாமல்: ஒவ்வொரு திட்டத்துக்கும் ஒரு விண்ணப்பப் பயணம், மேலும் கவுண்டரில் கண்டறியப்படும் ஒவ்வொரு பிரச்சினைக்கும் ஒரு பயணம். துணையுடன்: திட்டத்தில் உள்ள தனித்த அலுவலகங்கள் மட்டும்."
    : "Without preparation: one application visit per scheme plus one visit for every problem found at the counter. With Thunai: only the distinct offices in the grouped plan.";
  if (prev && prev.rupees_per_year !== snap.rupees_per_year) mark($(".summary-box"));
  if (prev && JSON.stringify(prev.trips) !== JSON.stringify(snap.trips)) mark($("#tripsBox"));
}
function mark(el) { el.classList.remove("changed"); void el.offsetWidth; el.classList.add("changed"); }
function countTo(el, from, to) {
  const start = performance.now(), dur = 600;
  const step = (now) => {
    const p = Math.min(1, (now - start) / dur);
    el.textContent = inr(Math.round(from + (to - from) * (1 - Math.pow(1 - p, 3))));
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
function toast(text) {
  const d = document.createElement("div");
  d.className = "toast";
  d.textContent = text;
  $("#toasts").appendChild(d);
  setTimeout(() => d.remove(), 4000);
}

// ---------------------------------------------------------------- session + actions
async function startSession(facts) {
  const r = await api("/api/session", { saved_facts: facts || null });
  state.sid = r.session_id;
  state.queue = [];
  $("#agentLog").innerHTML = "";
  $("#chatLog").innerHTML = "";
  state.snap = null;
  if (typeof p2 !== "undefined") { p2.doctor = null; p2.drafts = []; p2.suggested = []; p2.outbox = []; p2.cards = []; }
  handle(r, false);
  const q = r.snapshot.next_question;
  const msg = (lang) => (r.snapshot.facts.members.length
    ? `${T[lang].welcomeBack}${q ? " " + T[lang].next + " " + q[lang] : ""}` : T[lang].hello);
  bubble("agent", msg(state.lang), "", { en: msg("en"), ta: msg("ta") });
}

async function loadPersona(name) {
  try {
    await startSession();
    const hasP2 = typeof p2 !== "undefined";
    if (hasP2) { p2.cards = []; p2.outbox = []; p2.doctor = null; }
    const r = await api(`/api/demo/${name}?session_id=${state.sid}`);
    if (hasP2) { try { p2.cards = (await apiGet(`/api/sample_docs/${name}`)).cards; } catch (e) { p2.cards = []; } }
    handle(r);
    if (hasP2) showPanel(name === "meena" || name === "lakshmi_paati" ? "doctor" : "fix", name !== "murugan_family");
  }
  catch (e) { toast(`${t("warn")} ${e.message}`); }
}

function setupTabs() {
  const show = (name) => {
    $$("[data-tab]").forEach((el) => el.classList.toggle("show", el.dataset.tab === name || (["family", "schemes"].includes(name) && el.id === "col-main")));
    $$(".bottom-tabs button").forEach((x) => x.classList.toggle("active", x.dataset.show === name));
  };
  $$(".bottom-tabs button").forEach((b) => b.onclick = () => show(b.dataset.show));
  show("chat");
}

function init() {
  if (new URLSearchParams(location.search).get("present") === "1") document.body.classList.add("present");
  applyLang();
  setupTabs();
  $$(".lang-switch button").forEach((b) => b.onclick = () => { state.lang = b.dataset.lang; localStorage.setItem("thunai.lang", state.lang); applyLang(); });
  $$("[data-persona]").forEach((b) => b.onclick = () => loadPersona(b.dataset.persona));
  $("#clearBtn").onclick = () => { try { localStorage.removeItem("thunai.facts"); } catch (e) { /* ignore */ } startSession(); };
  $("#chatForm").onsubmit = (e) => { e.preventDefault(); const v = $("#chatInput").value; $("#chatInput").value = ""; send(v); };
  if (!localStorage.getItem("thunai.consent")) {
    $("#consent").classList.remove("hidden");
    $("#consentOk").onclick = () => { localStorage.setItem("thunai.consent", "1"); $("#consent").classList.add("hidden"); };
  }
  startSession(saved()).catch((e) => toast(`${t("warn")} ${e.message}`));
}

document.addEventListener("DOMContentLoaded", init);
