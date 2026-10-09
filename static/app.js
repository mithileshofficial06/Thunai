/* Thunai UI — talks to the FastAPI backend (shapes: docs/06_CONTRACTS.md). */
const $ = (s) => document.querySelector(s);
const $$ = (s) => Array.from(document.querySelectorAll(s));

const T = {
  ta: {
    tagline: "திட்ட உதவியாளர்", loadMurugan: "முருகன் குடும்பம்", loadMeena: "மீனா", loadLakshmi: "லட்சுமி பாட்டி", clear: "அழி",
    consent: "நீங்கள் சொல்வதை மட்டுமே பயன்படுத்துவோம். ஆதார் எண், வங்கி எண், OTP ஒருபோதும் கேட்க மாட்டோம். உங்கள் பதில்கள் புரிந்துகொள்ள இலவச AI சேவைக்கு அனுப்பப்படும். உங்கள் திட்டம் இந்தக் கைபேசியில் மட்டுமே சேமிக்கப்படும்; அழிக்க 'அழி' அழுத்தவும்.",
    consentOk: "சரி, தொடங்குவோம்", chatPlaceholder: "உங்கள் குடும்பத்தைப் பற்றிச் சொல்லுங்கள்…", send: "அனுப்பு",
    rupeesLabel: "ஆண்டுக்குக் கிடைக்கக்கூடியது", perYear: "/ ஆண்டு", tripsLabel: "அலுவலகப் பயணங்கள்", tripsHow: "தயாரிப்பு இல்லாமல் → துணையுடன்",
    familyCard: "👪 குடும்ப அட்டை", schemesTitle: "✅ திட்டங்கள்", tabFix: "🛠️ சரிசெய்ய", tabDoctor: "🩺 பணம் வரவில்லையா?", tabLetters: "✉️ கடிதங்கள்", tabHelper: "👤 உதவியாளர்",
    comingSoon: "விரைவில்…", agentTitle: "முகவர் என்ன செய்கிறது", mChat: "உரையாடல்", mFamily: "குடும்பம்", mSchemes: "திட்டங்கள்", mAgent: "முகவர்",
    footer: "இறுதி முடிவு துறையினுடையது · OTP-ஐ யாரிடமும் பகிர வேண்டாம் · Thunai prototype",
    hello: "வணக்கம்! நான் துணை. உங்கள் வீட்டில் யார் யார் இருக்கிறார்கள்? பெயர், உறவு, வயது சொல்லுங்கள்.",
    why: "ஏன்?", source: "அதிகாரப்பூர்வ ஆதாரம்", checked: "சரிபார்த்த நாள்", schemes: "திட்டங்கள்", confirm: "உறுதி", pleaseConfirm: "உறுதிப்படுத்தவும்",
    income: "ஆண்டு வருமானம்", card: "குடும்ப அட்டை", wet: "நன்செய் (ஏக்கர்)", dry: "புன்செய் (ஏக்கர்)", units: "மின் யூனிட் / ஆண்டு", district: "மாவட்டம்", age: "வயது",
    st: { ELIGIBLE: "✅ தகுதி", NEED_INFO: "❓ தகவல் தேவை", NOT_ELIGIBLE: "❌ தகுதி இல்லை" },
    rel: { self: "நான்", spouse_f: "மனைவி", spouse_m: "கணவர்", daughter: "மகள்", son: "மகன்", mother: "அம்மா", father: "அப்பா", other: "உறவினர்" },
    yes: "ஆம்", no: "இல்லை", unknown: "—", thinking: "யோசிக்கிறேன்…",
  },
  en: {
    tagline: "Scheme Sathi agent", loadMurugan: "Murugan family", loadMeena: "Meena", loadLakshmi: "Lakshmi Paati", clear: "Clear",
    consent: "We only use what you tell us. We never ask for Aadhaar, bank numbers or OTPs. Your answers are sent to a free AI service to understand them. Your plan is saved only on this phone; tap Clear to delete it.",
    consentOk: "OK, let's start", chatPlaceholder: "Tell me about your family…", send: "Send",
    rupeesLabel: "Could get per year", perYear: "/ year", tripsLabel: "Office trips", tripsHow: "unprepared → with Thunai",
    familyCard: "👪 Family card", schemesTitle: "✅ Schemes", tabFix: "🛠️ What to fix", tabDoctor: "🩺 Money stopped?", tabLetters: "✉️ Letters", tabHelper: "👤 Helper",
    comingSoon: "Coming next…", agentTitle: "What the agent is doing", mChat: "Chat", mFamily: "Family", mSchemes: "Schemes", mAgent: "Agent",
    footer: "The department makes the final decision · Never share your OTP · Thunai prototype",
    hello: "Hello! I'm Thunai. Who lives in your home? Tell me each person's name, relation and age.",
    why: "Why?", source: "Official source", checked: "checked", schemes: "schemes", confirm: "Confirm", pleaseConfirm: "please confirm",
    income: "Yearly income", card: "Ration card", wet: "Wet land (acres)", dry: "Dry land (acres)", units: "Electricity units / yr", district: "District", age: "Age",
    st: { ELIGIBLE: "✅ Eligible", NEED_INFO: "❓ Need info", NOT_ELIGIBLE: "❌ Not eligible" },
    rel: { self: "Self", spouse_f: "Wife", spouse_m: "Husband", daughter: "Daughter", son: "Son", mother: "Mother", father: "Father", other: "Relative" },
    yes: "Yes", no: "No", unknown: "—", thinking: "Thinking…",
  },
};

const state = { sid: null, lang: localStorage.getItem("thunai.lang") || "ta", snap: null, unconfirmed: [], queue: [], replaying: false };
const t = (k) => T[state.lang][k];
const L = (obj, base) => (obj ? obj[`${base}_${state.lang}`] ?? obj[`${base}_en`] ?? "" : "");

// ---------------------------------------------------------------- storage
function save() {
  try {
    if (state.snap) localStorage.setItem("thunai.facts", JSON.stringify(state.snap.facts));
  } catch (e) { /* storage unavailable: the app still works */ }
}
function saved() {
  try { return JSON.parse(localStorage.getItem("thunai.facts") || "null"); } catch (e) { return null; }
}

// ---------------------------------------------------------------- API
async function api(path, body) {
  const r = await fetch(path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body || {}) });
  if (!r.ok) {
    const msg = (await r.json().catch(() => ({}))).detail || r.statusText;
    if (r.status === 404 && String(msg).includes("session")) { await startSession(); }
    throw new Error(msg);
  }
  return r.json();
}

// ---------------------------------------------------------------- i18n
function applyLang() {
  document.documentElement.lang = state.lang;
  $$("[data-i18n]").forEach((el) => { el.textContent = t(el.dataset.i18n); });
  $$("[data-i18n-placeholder]").forEach((el) => { el.placeholder = t(el.dataset.i18nPlaceholder); });
  $$(".lang-toggle button").forEach((b) => b.classList.toggle("on", b.dataset.lang === state.lang));
  if (state.snap) render(state.snap, false);
  $$("#agentLog li").forEach((li) => { li.querySelector(".txt").textContent = li.dataset[state.lang] || li.dataset.en; });
}

// ---------------------------------------------------------------- chat
function bubble(who, text, extraClass = "") {
  const div = document.createElement("div");
  div.className = `bubble ${who} ${extraClass}`;
  if (who === "agent") div.innerHTML = `<span class="who">துணை · Thunai</span>`;
  const span = document.createElement("span");
  span.textContent = text;
  div.appendChild(span);
  $("#chatLog").appendChild(div);
  $("#chatLog").scrollTop = $("#chatLog").scrollHeight;
  return div;
}

function replyText(reply) {
  if (!reply) return "";
  return (reply[state.lang] || reply.en || "").trim();
}

async function send(text, fromVoice = false) {
  text = text.trim();
  if (!text) return;
  bubble("user", text);
  const wait = bubble("agent", t("thinking"), "muted");
  try {
    const r = await api("/api/chat", { session_id: state.sid, text, lang: state.lang, from_voice: fromVoice });
    wait.remove();
    handle(r);
  } catch (e) {
    wait.remove();
    toast("⚠️ " + e.message);
  }
}

function handle(r, showReply = true) {
  state.unconfirmed = r.unconfirmed || [];
  enqueue(r.events || []);
  render(r.snapshot, true);
  renderAsk(r.pending_ask || []);
  if (showReply && r.reply) {
    const text = replyText(r.reply);
    if (text) { const b = bubble("agent", text); speak(text, b); }
  }
  save();
}

function renderAsk(asks) {
  const box = $("#askBox");
  box.innerHTML = "";
  if (!asks.length) { box.classList.add("hidden"); return; }
  box.classList.remove("hidden");
  asks.forEach((q) => {
    const div = document.createElement("div");
    div.innerHTML = `<div class="q">❓ ${state.lang === "ta" ? q.ta : q.en}</div>`;
    q.options.forEach((opt) => {
      const b = document.createElement("button");
      b.className = "btn-ghost";
      b.textContent = typeof opt === "number" && q.path.endsWith("income") ? `₹${opt.toLocaleString("en-IN")}` : String(opt);
      b.onclick = () => editFact(q.path, opt);
      div.appendChild(b);
    });
    box.appendChild(div);
  });
}

// ---------------------------------------------------------------- agent panel (event replay)
function enqueue(events) {
  state.queue.push(...events);
  if (!state.replaying) drain();
}
function drain() {
  const ev = state.queue.shift();
  if (!ev) { state.replaying = false; return; }
  state.replaying = true;
  const li = document.createElement("li");
  li.className = ev.type;
  li.dataset.en = ev.text_en;
  li.dataset.ta = ev.text_ta || ev.text_en;
  const meta = [ev.detail?.provider, ev.detail?.checks].filter(Boolean).join(" · ");
  li.innerHTML = `<span class="tag">${ev.icon} ${ev.type}</span><span class="txt"></span>${meta ? `<span class="meta"></span>` : ""}`;
  li.querySelector(".txt").textContent = state.lang === "ta" ? li.dataset.ta : li.dataset.en;
  if (meta) li.querySelector(".meta").textContent = meta;
  $("#agentLog").appendChild(li);
  $("#col-agent").scrollTop = $("#col-agent").scrollHeight;
  if (ev.type === "privacy") toast(`${ev.icon} ${state.lang === "ta" ? ev.text_ta : ev.text_en}`);
  setTimeout(drain, 250);
}

// ---------------------------------------------------------------- rendering
function render(snap, animate) {
  const prev = state.snap;
  state.snap = snap;
  renderPlanSteps(snap.plan_steps);
  renderMembers(snap.facts);
  renderFacts(snap.facts);
  renderSchemes(snap.verdicts, animate ? prev : null);
  renderMetrics(snap, animate ? prev : null);
}

function renderPlanSteps(steps) {
  $("#planSteps").innerHTML = steps.map((s) => `<span class="${s.done ? "done" : ""}">${s.done ? "✓" : "◻"} ${s[state.lang]}</span>`).join(" · ");
}

function relLabel(m) {
  const r = T[state.lang].rel;
  if (m.relation === "spouse") return m.gender === "male" ? r.spouse_m : r.spouse_f;
  return r[m.relation] || r.other;
}

function renderMembers(facts) {
  $("#members").innerHTML = "";
  (facts.members || []).forEach((m) => {
    const chip = document.createElement("div");
    chip.className = "chip";
    const name = m.name || m.id;
    chip.innerHTML = `<span class="ini"></span><span><b class="nm"></b> <small class="rl"></small></span>`;
    chip.querySelector(".ini").textContent = name.charAt(0).toUpperCase();
    chip.querySelector(".nm").textContent = name;
    chip.querySelector(".rl").textContent = `· ${relLabel(m)}${m.age != null ? " · " + m.age : ""}`;
    $("#members").appendChild(chip);
  });
}

const FACT_ROWS = [
  ["family.annual_income", "income", (v) => `₹${Number(v).toLocaleString("en-IN")}`],
  ["family.ration_card_type", "card", (v) => v],
  ["family.wet_land_acres", "wet", (v) => v],
  ["family.dry_land_acres", "dry", (v) => v],
  ["family.electricity_units_per_year", "units", (v) => v],
];

function renderFacts(facts) {
  const box = $("#keyFacts");
  box.innerHTML = "";
  FACT_ROWS.forEach(([path, label, fmt]) => {
    const key = path.split(".")[1];
    const v = facts.family ? facts.family[key] : undefined;
    const row = document.createElement("div");
    row.className = "fact" + (state.unconfirmed.includes(path) ? " unconfirmed" : "");
    row.innerHTML = `<span class="k"></span><span class="v" tabindex="0" role="button"></span>`;
    row.querySelector(".k").textContent = t(label);
    const vEl = row.querySelector(".v");
    vEl.textContent = v == null ? t("unknown") : fmt(v);
    vEl.onclick = () => inlineEdit(row, path, v);
    vEl.onkeydown = (e) => { if (e.key === "Enter") inlineEdit(row, path, v); };
    if (state.unconfirmed.includes(path)) {
      const c = document.createElement("button");
      c.className = "btn-ghost";
      c.textContent = `✓ ${t("confirm")}`;
      c.style.minHeight = "30px";
      c.onclick = () => editFact(path, v);
      row.appendChild(c);
    }
    box.appendChild(row);
  });
}

function inlineEdit(row, path, current) {
  const vEl = row.querySelector(".v");
  const input = document.createElement("input");
  input.value = current ?? "";
  vEl.replaceWith(input);
  input.focus();
  let finished = false;
  const done = async (commit) => {
    if (finished) return;
    finished = true;
    if (commit && input.value.trim() !== "" && input.value !== String(current ?? "")) {
      await editFact(path, input.value.trim());
    } else { render(state.snap, false); }
  };
  input.onkeydown = (e) => { if (e.key === "Enter") done(true); if (e.key === "Escape") done(false); };
  input.onblur = () => done(true);
}

async function editFact(path, value) {
  try {
    const r = await api("/api/facts", { session_id: state.sid, path, value });
    handle(r, false);
  } catch (e) { toast("⚠️ " + e.message); }
}

function renderSchemes(verdicts, prev) {
  const before = {};
  (prev?.verdicts || []).forEach((v) => { before[v.key] = v.status; });
  const box = $("#schemes");
  box.innerHTML = "";
  const order = { ELIGIBLE: 0, NEED_INFO: 1, NOT_ELIGIBLE: 2 };
  [...verdicts].sort((a, b) => order[a.status] - order[b.status]).forEach((v) => {
    const card = document.createElement("article");
    card.className = `scheme ${v.status}` + (before[v.key] && before[v.key] !== v.status ? " flip" : "");
    const reasons = v.reasons.map((r) => `<li>${r.ok === true ? "✓" : r.ok === false ? "✗" : "?"} ${esc(state.lang === "ta" ? r.ta : r.en)}</li>`).join("");
    const conflict = v.conflict_note ? `<div class="conflict">⚖️ ${esc(state.lang === "ta" ? v.conflict_note.ta : v.conflict_note.en)}</div>` : "";
    const src = v.source_url ? `<span class="src">🔗 <a href="${v.source_url}" target="_blank" rel="noopener">${t("source")}</a> · ${t("checked")} ${v.checked_on}</span>` : "";
    card.innerHTML = `
      <span class="badge ${v.status}">${t("st")[v.status]}</span>
      <div class="name">${esc(state.lang === "ta" ? v.name_ta : v.name_en)}</div>
      <div class="name-en">${esc(state.lang === "ta" ? v.name_en : "")}${v.member_name ? " · " + esc(v.member_name) : ""}</div>
      <div class="benefit">${esc(state.lang === "ta" ? v.benefit_ta : v.benefit_en)}</div>
      <details><summary>${t("why")}</summary><ul>${reasons}</ul></details>
      ${conflict}${src}`;
    box.appendChild(card);
  });
}

function renderMetrics(snap, prev) {
  const from = prev ? prev.rupees_per_year : 0;
  countTo($("#rupees"), from, snap.rupees_per_year);
  const counted = snap.verdicts.filter((v) => v.counted).length;
  $("#schemeCount").textContent = `${counted} ${t("schemes")}`;
  $("#tripsWithout").textContent = snap.trips.without;
  $("#tripsWith").textContent = snap.trips.with;
  $(".metric.trips").title = state.lang === "ta"
    ? "தயாரிப்பு இல்லாமல்: ஒவ்வொரு திட்டத்துக்கும் 1 விண்ணப்பப் பயணம் + கவுண்டரில் கண்டுபிடிக்கப்படும் ஒவ்வொரு பிரச்சினைக்கும் 1 பயணம். துணையுடன்: திட்டத்தில் உள்ள தனித்த அலுவலகங்கள்."
    : "Unprepared: 1 application visit per scheme + 1 visit per problem found at the counter. With Thunai: the distinct offices in the grouped plan.";
  if (prev && (prev.rupees_per_year !== snap.rupees_per_year)) flash(".metric.money");
  if (prev && JSON.stringify(prev.trips) !== JSON.stringify(snap.trips)) flash(".metric.trips");
}

function countTo(el, from, to) {
  const start = performance.now(), dur = 600;
  const step = (now) => {
    const p = Math.min(1, (now - start) / dur);
    const val = Math.round(from + (to - from) * (1 - Math.pow(1 - p, 3)));
    el.textContent = `₹${val.toLocaleString("en-IN")}`;
    if (p < 1) requestAnimationFrame(step);
  };
  requestAnimationFrame(step);
}
function flash(sel) { const el = $(sel); el.classList.remove("flash"); void el.offsetWidth; el.classList.add("flash"); }
function esc(s) { return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }
function toast(text) {
  const d = document.createElement("div");
  d.className = "toast";
  d.textContent = text;
  $("#toasts").appendChild(d);
  setTimeout(() => d.remove(), 4000);
}
function speak() { /* voice output arrives in B5 */ }

// ---------------------------------------------------------------- session + actions
async function startSession(facts) {
  const r = await api("/api/session", { saved_facts: facts || null });
  state.sid = r.session_id;
  $("#agentLog").innerHTML = "";
  $("#chatLog").innerHTML = "";
  state.snap = null;
  handle(r, false);
  bubble("agent", r.snapshot.facts.members.length ? replyResume(r.snapshot) : t("hello"));
}
function replyResume(snap) {
  const q = snap.next_question;
  return q ? (state.lang === "ta" ? `மீண்டும் வருக! அடுத்து: ${q.ta}` : `Welcome back! Next: ${q.en}`) : (state.lang === "ta" ? "மீண்டும் வருக!" : "Welcome back!");
}

async function loadPersona(name) {
  try {
    await startSession();
    const r = await api(`/api/demo/${name}?session_id=${state.sid}`);
    handle(r);
  } catch (e) { toast("⚠️ " + e.message); }
}

function setupTabs() {
  $$("#phase2Tabs button").forEach((b) => b.onclick = () => {
    $$("#phase2Tabs button").forEach((x) => x.classList.toggle("active", x === b));
    ["fix", "doctor", "letters", "helper"].forEach((p) => $(`#panel-${p}`).classList.toggle("hidden", p !== b.dataset.panel));
  });
  const show = (name) => {
    $$("[data-tab]").forEach((el) => el.classList.toggle("show", el.dataset.tab === name || (name === "family" && el.id === "col-main")));
    $$(".bottom-tabs button").forEach((x) => x.classList.toggle("active", x.dataset.show === name));
    if (name === "schemes") $("#col-main").classList.add("show");
  };
  $$(".bottom-tabs button").forEach((b) => b.onclick = () => show(b.dataset.show));
  show("chat");
}

function init() {
  if (new URLSearchParams(location.search).get("present") === "1") document.body.classList.add("present");
  applyLang();
  setupTabs();
  $$(".lang-toggle button").forEach((b) => b.onclick = () => { state.lang = b.dataset.lang; localStorage.setItem("thunai.lang", state.lang); applyLang(); });
  $$("[data-persona]").forEach((b) => b.onclick = () => loadPersona(b.dataset.persona));
  $("#clearBtn").onclick = () => { try { localStorage.removeItem("thunai.facts"); } catch (e) {} startSession(); };
  $("#chatForm").onsubmit = (e) => { e.preventDefault(); const v = $("#chatInput").value; $("#chatInput").value = ""; send(v); };
  if (!localStorage.getItem("thunai.consent")) {
    $("#consent").classList.remove("hidden");
    $("#consentOk").onclick = () => { localStorage.setItem("thunai.consent", "1"); $("#consent").classList.add("hidden"); };
  }
  startSession(saved()).catch((e) => toast("⚠️ " + e.message));
}

document.addEventListener("DOMContentLoaded", init);
