/* Thunai Phase 2 UI: Fix, Doctor, Letters, Helper, Follow tabs + voice. Uses globals from app.js. */
Object.assign(T.ta, {
  loadRevathi: "ரேவதி (மாதிரி ஆவணங்கள்)", tabFollow: "பின்தொடர்தல்",
  sampleTitle: "மாதிரி ஆவணங்கள்", sample: "மாதிரி", have: "உள்ளது", missingDoc: "இல்லை",
  namesTitle: "ஆவணங்களில் பெயர் சரிபார்ப்பு", namePrinted: "அச்சிடப்பட்ட பெயர்", document: "ஆவணம்",
  lvl: { GREEN: "பொருந்துகிறது", YELLOW: "பெயர் அபாயம்", RED: "முரண்பாடு" },
  missingTitle: "இல்லாத ஆவணங்கள்", planTitle: "சரிசெய்யும் திட்டம் (அலுவலக வாரியாக)", bring: "எடுத்துச் செல்ல", unblocks: "திட்டங்களைத் திறக்கும்",
  visits: "அலுவலகப் பயணங்கள்", noFix: "குடும்ப விவரங்கள் கிடைத்ததும் சரிசெய்ய வேண்டியவை இங்கே தோன்றும்.", nothingToFix: "சரிசெய்ய எதுவும் இல்லை.",
  docIntro: "பணம் நின்றுவிட்டதா அல்லது விண்ணப்பம் நிராகரிக்கப்பட்டதா? உங்கள் நிலையைத் தேர்ந்தெடுக்கவும்.",
  yes: "ஆம்", no: "இல்லை", dontKnow: "தெரியாது", likely: "பெரும்பாலும் காரணம்", check1: "1 நிமிடத்தில் சரிபார்க்க", fixSteps: "சரிசெய்யும் வழிமுறைகள்",
  draftLetter: "கடித வரைவு தயாரி", restart: "மீண்டும் தொடங்கு", srcLabel: "ஆதாரம்", office: "அலுவலகம்",
  suggested: "பரிந்துரைக்கப்பட்ட கடிதங்கள்", drafts: "வரைவுகள்", draft: "வரைவு தயாரி", open: "திற", noLetters: "இப்போது பரிந்துரைக்க கடிதம் இல்லை.", noDrafts: "இன்னும் வரைவுகள் இல்லை.",
  stDraft: "வரைவு", stApproved: "ஒப்புதல் பெற்றது", stOpen: "நிலுவையில்", stReviewed: "பரிசீலிக்கப்பட்டது",
  helperName: "உதவியாளர் பெயர்", approve: "ஒப்புதல் அளி", reviewed: "பரிசீலிக்கப்பட்டது எனக் குறி", noQueue: "ஒப்புதலுக்குக் காத்திருப்பவை இல்லை.",
  helperIntro: "e-சேவை / NSS உதவியாளர் ஒவ்வொரு கடிதத்தையும் சரிபார்த்து ஒப்புதல் அளிக்கிறார். ஒப்புதல் இல்லாமல் அச்சிட முடியாது.",
  followIntro: "முகவர் தானாகவே நினைவூட்டுகிறது, காலக்கெடுவை எச்சரிக்கிறது, தேங்கிய பணிகளை உதவியாளரிடம் அனுப்புகிறது.",
  sendSummary: "சுருக்கக் குறுஞ்செய்தி தயாரி", shareWa: "WhatsApp-இல் பகிர்", simulate: "15 நாட்களுக்குப் பிறகு (உருவகப்படுத்து)",
  outbox: "குறுஞ்செய்தி அனுப்புப் பெட்டி (outbox)", outboxNote: "முன்மாதிரியில் குறுஞ்செய்திகள் இங்கே தயாராகும்; உண்மையான அனுப்புதலுக்கு SMS சேவை இணைக்கப்பட வேண்டும்.", noOutbox: "இன்னும் செய்திகள் இல்லை.",
  speakerOn: "குரல் பதில்: இயக்கத்தில்", speakerOff: "குரல் பதில்: அணைப்பு", recording: "பதிவு செய்கிறது... நிறுத்த மீண்டும் அழுத்தவும்", heard: "கேட்டது (சரிபார்த்து அனுப்பவும்)",
});
Object.assign(T.en, {
  loadRevathi: "Revathi (sample documents)", tabFollow: "Follow-up",
  sampleTitle: "Sample documents", sample: "SAMPLE", have: "Available", missingDoc: "Missing",
  namesTitle: "Name check across documents", namePrinted: "Name as printed", document: "Document",
  lvl: { GREEN: "Match", YELLOW: "Name risk", RED: "Conflict" },
  missingTitle: "Missing documents", planTitle: "Fix plan (by office)", bring: "Bring", unblocks: "scheme(s) unblocked",
  visits: "Office visits", noFix: "What to fix will appear here once family details are available.", nothingToFix: "Nothing to fix.",
  docIntro: "Has a payment stopped or an application been rejected? Choose your situation.",
  yes: "Yes", no: "No", dontKnow: "Don't know", likely: "Most likely cause", check1: "Check in 1 minute", fixSteps: "Steps to fix",
  draftLetter: "Draft the letter", restart: "Start again", srcLabel: "Source", office: "Office",
  suggested: "Suggested letters", drafts: "Drafts", draft: "Draft", open: "Open", noLetters: "No letter is suggested right now.", noDrafts: "No drafts yet.",
  stDraft: "Draft", stApproved: "Approved", stOpen: "Open", stReviewed: "Reviewed",
  helperName: "Helper name", approve: "Approve", reviewed: "Mark reviewed", noQueue: "Nothing waiting for approval.",
  helperIntro: "An e-Sevai / NSS helper checks and approves every letter. Letters cannot be printed without approval.",
  followIntro: "The agent reminds, warns about deadlines and escalates stuck tasks to a helper on its own.",
  sendSummary: "Prepare summary SMS", shareWa: "Share on WhatsApp", simulate: "Simulate 15 days later",
  outbox: "SMS outbox", outboxNote: "In the prototype, messages are prepared here; real sending needs an SMS provider.", noOutbox: "No messages yet.",
  speakerOn: "Voice replies: on", speakerOff: "Voice replies: off", recording: "Recording... press again to stop", heard: "Heard (check and send)",
});
T.ta.kind.autonomous = "தானியங்கி பின்தொடர்தல்";
T.en.kind.autonomous = "Follow-up (automatic)";

const p2 = { suggested: [], drafts: [], doctor: null, entries: [], persona: null, cards: [], outbox: [], helper: "Priya", speaker: false, fromVoice: false };
const L = (o, k) => (state.lang === "ta" ? o[k + "_ta"] ?? o.ta : o[k + "_en"] ?? o.en);

async function apiGet(path) {
  const r = await fetch(path);
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText);
  return r.json();
}

function takeExtras(r) {
  if (r.suggested_letters) p2.suggested = r.suggested_letters;
  if (r.drafts) p2.drafts = r.drafts;
  if ("doctor" in r) p2.doctor = r.doctor;
}

function renderPhase2() {
  if (!state.snap) return;
  renderFix(); renderDoctor(); renderLetters(); renderHelper(); renderFollow();
}

// ---------------------------------------------------------------- Fix
function renderFix() {
  const s = state.snap, box = $("#panel-fix");
  const parts = [];
  if (p2.cards.length) {
    parts.push(`<h3 class="p2-h">${esc(t("sampleTitle"))}</h3><div class="doc-cards">` + p2.cards.map((c) => `
      <div class="doc-card ${c.status}"><div class="doc-card-top"><strong>${esc(L(c, "doc"))}</strong><span class="sample-tag">${esc(t("sample"))}</span></div>
      <div class="doc-name">${c.name_printed ? esc(c.name_printed) : "&mdash;"}</div>
      ${(state.lang === "ta" ? c.lines_ta : c.lines_en).map((l) => `<div class="muted small">${esc(l)}</div>`).join("")}
      <span class="lvl ${c.status === "missing" ? "RED" : "GREEN"}">${esc(c.status === "missing" ? t("missingDoc") : t("have"))}</span></div>`).join("") + "</div>");
  }
  if (s.matrix.length) {
    parts.push(`<h3 class="p2-h">${esc(t("namesTitle"))}</h3><table class="data-table"><thead><tr><th>${esc(t("colName"))}</th><th>${esc(t("document"))}</th><th>${esc(t("namePrinted"))}</th><th></th></tr></thead><tbody>` +
      s.matrix.flatMap((m) => m.cells.map((c, i) => `<tr><td>${i ? "" : esc(m.member_name)}</td><td>${esc(L(c, "doc"))}</td><td>${esc(c.name_printed)}</td>
        <td><span class="lvl ${c.level}" title="${esc(L(c, "reason"))}">${esc(t("lvl")[c.level])}</span></td></tr>`)).join("") + "</tbody></table>");
  }
  if (s.missing_documents.length) {
    parts.push(`<h3 class="p2-h">${esc(t("missingTitle"))}</h3><ul class="p2-list">` + s.missing_documents.map((d) =>
      `<li><strong>${esc(d.member_name)}</strong>: ${esc(L(d, ""))}<div class="muted small">${esc(L(d, "where"))}</div></li>`).join("") + "</ul>");
  }
  if (s.plan.length) {
    parts.push(`<h3 class="p2-h">${esc(t("planTitle"))} <span class="muted small">${esc(t("visits"))}: ${s.trips.with} (${esc(t("insteadOf"))} ${s.trips.without})</span></h3>` +
      s.plan.map((o, i) => `<div class="office"><div class="office-top"><strong>${i + 1}. ${esc(L(o, "office"))}</strong>
        ${o.unblocks.length ? `<span class="muted small">${o.unblocks.length} ${esc(t("unblocks"))}</span>` : ""}</div>` +
        o.tasks.map((k) => `<label class="task ${k.done ? "done" : ""}"><input type="checkbox" data-task="${esc(k.task_id)}" ${k.done ? "checked" : ""}>
          <span><strong>${esc(k.member_name)}</strong>: ${esc(L(k, "short"))}<span class="muted small"> · ${esc(t("bring"))}: ${esc(L(k, "bring"))}</span>
          ${k.url ? ` · <a href="${esc(k.url)}" target="_blank" rel="noopener">${esc(t("check1"))}</a>` : ""}</span></label>`).join("") + "</div>").join(""));
  }
  box.innerHTML = parts.length ? parts.join("") : `<p class="muted">${esc(s.facts.members.length ? t("nothingToFix") : t("noFix"))}</p>`;
  box.querySelectorAll("[data-task]").forEach((cb) => cb.onchange = () => setTask(cb.dataset.task, cb.checked));
}

async function setTask(task_id, done) {
  try { handle(await api("/api/task", { session_id: state.sid, task_id, done }), false); }
  catch (e) { toast(`${t("warn")} ${e.message}`); }
}

// ---------------------------------------------------------------- Doctor
function renderDoctor() {
  const box = $("#panel-doctor"), d = p2.doctor;
  if (!d) {
    box.innerHTML = `<p>${esc(t("docIntro"))}</p><div class="entry-grid">` +
      p2.entries.map((e) => `<button class="btn btn-outline entry" data-entry="${esc(e.id)}">${esc(L(e, ""))}</button>`).join("") + "</div>";
    box.querySelectorAll("[data-entry]").forEach((b) => b.onclick = () => doctor({ entry_id: b.dataset.entry }));
    return;
  }
  if (d.kind === "question") {
    box.innerHTML = `<div class="dq"><div class="dq-text">${esc(L(d, ""))}</div><div class="dq-btns">
      <button class="btn btn-primary" data-a="yes">${esc(t("yes"))}</button><button class="btn btn-outline" data-a="no">${esc(t("no"))}</button>
      <button class="btn btn-outline" data-a="dont_know">${esc(t("dontKnow"))}</button></div></div>
      <button class="link-btn" id="docRestart">${esc(t("restart"))}</button>`;
    box.querySelectorAll("[data-a]").forEach((b) => b.onclick = () => doctor({ answer: b.dataset.a }));
  } else {
    const fix = state.lang === "ta" ? d.fix_ta : d.fix_en;
    const sug = p2.suggested.find((x) => x.kind === d.draft_letter);
    box.innerHTML = `<div class="outcome"><div class="small muted">${esc(t("likely"))}</div><div class="cause">${esc(L(d, "cause"))}</div>
      <div class="small muted">${esc(t("check1"))}</div><p>${esc(L(d, "verify"))}</p>
      <div class="small muted">${esc(t("fixSteps"))}</div><ol>${fix.map((f) => `<li>${esc(f)}</li>`).join("")}</ol>
      ${d.source ? `<div class="source">${esc(t("srcLabel"))}: ${esc(d.source)}</div>` : ""}
      ${sug ? `<button class="btn btn-primary" id="docLetter">${esc(t("draftLetter"))}</button>` : ""}</div>
      <button class="link-btn" id="docRestart">${esc(t("restart"))}</button>`;
    if (sug) $("#docLetter").onclick = () => draftLetter(sug);
  }
  $("#docRestart").onclick = () => { p2.doctor = null; renderDoctor(); };
}

async function doctor(body) {
  try { const r = await api("/api/doctor", { session_id: state.sid, ...body }); handle(r, false); }
  catch (e) { toast(`${t("warn")} ${e.message}`); }
}

// ---------------------------------------------------------------- Letters
const stText = (s) => ({ DRAFT: t("stDraft"), APPROVED: t("stApproved"), OPEN: t("stOpen"), REVIEWED: t("stReviewed") }[s] || s);
const stClass = (s) => (s === "APPROVED" || s === "REVIEWED" ? "ELIGIBLE" : "NEED_INFO");

function renderLetters() {
  const box = $("#panel-letters");
  const letters = p2.drafts.filter((d) => d.kind !== "escalation");
  box.innerHTML = `<h3 class="p2-h">${esc(t("suggested"))}</h3>` +
    (p2.suggested.length ? `<ul class="p2-list">` + p2.suggested.map((s, i) => `<li class="row"><span><strong>${esc(L(s, ""))}</strong>
      <div class="muted small">${esc(L(s, "reason"))}</div></span><button class="btn btn-outline btn-sm" data-sug="${i}">${esc(t("draft"))}</button></li>`).join("") + "</ul>"
      : `<p class="muted">${esc(t("noLetters"))}</p>`) +
    `<h3 class="p2-h">${esc(t("drafts"))}</h3>` +
    (letters.length ? `<ul class="p2-list">` + letters.map((d) => `<li class="row"><span><strong>${esc(L(d, "title"))}</strong>${d.member_name ? " · " + esc(d.member_name) : ""}
      <span class="status ${stClass(d.status)}">${esc(stText(d.status))}</span></span><a class="btn btn-outline btn-sm" href="${esc(d.html_url)}" target="_blank" rel="noopener">${esc(t("open"))}</a></li>`).join("") + "</ul>"
      : `<p class="muted">${esc(t("noDrafts"))}</p>`);
  box.querySelectorAll("[data-sug]").forEach((b) => b.onclick = () => draftLetter(p2.suggested[+b.dataset.sug]));
}

async function draftLetter(s) {
  try {
    const r = await api("/api/letter", { session_id: state.sid, kind: s.kind, member_id: s.member_id, doc_id: s.doc_id });
    handle(r, false);
    showPanel("letters");
    window.open(r.draft.html_url, "_blank", "noopener");
  } catch (e) { toast(`${t("warn")} ${e.message}`); }
}

// ---------------------------------------------------------------- Helper
function renderHelper() {
  const box = $("#panel-helper");
  const items = p2.drafts;
  box.innerHTML = `<p class="muted small">${esc(t("helperIntro"))}</p>
    <label class="small">${esc(t("helperName"))} <input id="helperName" class="inline-input" value="${esc(p2.helper)}"></label>` +
    (items.length ? `<ul class="p2-list">` + items.map((d) => `<li class="row"><span><strong>${esc(L(d, "title"))}</strong>${d.member_name ? " · " + esc(d.member_name) : ""}
      <span class="status ${stClass(d.status)}">${esc(stText(d.status))}</span><div class="muted small">${esc(L(d, "reason"))}</div>
      ${d.approved_by ? `<div class="small">${esc(d.approved_by)}</div>` : ""}</span>
      <span class="row-btns">${d.html_url ? `<a class="btn btn-outline btn-sm" href="${esc(d.html_url)}" target="_blank" rel="noopener">${esc(t("open"))}</a>` : ""}
      ${d.status === "DRAFT" || d.status === "OPEN" ? `<button class="btn btn-primary btn-sm" data-approve="${esc(d.draft_id)}">${esc(d.kind === "escalation" ? t("reviewed") : t("approve"))}</button>` : ""}</span></li>`).join("") + "</ul>"
      : `<p class="muted">${esc(t("noQueue"))}</p>`);
  $("#helperName").onchange = (e) => { p2.helper = e.target.value.trim() || "Helper"; };
  box.querySelectorAll("[data-approve]").forEach((b) => b.onclick = () => approve(b.dataset.approve));
}

async function approve(draft_id) {
  try {
    const r = await api("/api/helper/approve", { draft_id, helper_name: p2.helper });
    enqueue(r.events || []);
    p2.drafts = (await apiGet(`/api/helper/queue?session_id=${state.sid}`)).items;
    renderLetters(); renderHelper();
  } catch (e) { toast(`${t("warn")} ${e.message}`); }
}

// ---------------------------------------------------------------- Follow
function renderFollow() {
  const box = $("#panel-follow");
  if (!box) return;
  box.innerHTML = `<p class="muted small">${esc(t("followIntro"))}</p><div class="row-btns wrap">
    <button class="btn btn-primary btn-sm" id="fSim">${esc(t("simulate"))}</button>
    <button class="btn btn-outline btn-sm" id="fSum">${esc(t("sendSummary"))}</button>
    <button class="btn btn-outline btn-sm" id="fWa">${esc(t("shareWa"))}</button></div>
    <h3 class="p2-h">${esc(t("outbox"))}</h3><p class="muted small">${esc(t("outboxNote"))}</p>` +
    (p2.outbox.length ? `<ul class="p2-list">` + p2.outbox.map((m) => `<li><div class="sms">${esc(m.text)}</div><div class="muted small">${esc(m.reason)} · ${esc(m.created || "")}</div></li>`).join("") + "</ul>"
      : `<p class="muted">${esc(t("noOutbox"))}</p>`);
  $("#fSim").onclick = followSimulate;
  $("#fSum").onclick = followSummary;
  $("#fWa").onclick = followShare;
}

async function refreshOutbox() { try { p2.outbox = (await apiGet(`/api/outbox?session_id=${state.sid}`)).messages; } catch (e) { /* ignore */ } renderFollow(); }
async function followSimulate() {
  try { const r = await api("/api/simulate", { session_id: state.sid, days: 15 }); handle(r, false); await refreshOutbox(); }
  catch (e) { toast(`${t("warn")} ${e.message}`); }
}
async function followSummary() {
  try { const r = await api("/api/sms/summary", { session_id: state.sid, lang: state.lang }); enqueue(r.events || []); await refreshOutbox(); }
  catch (e) { toast(`${t("warn")} ${e.message}`); }
}
async function followShare() {
  try {
    const r = await api("/api/sms/summary", { session_id: state.sid, lang: state.lang });
    enqueue(r.events || []); await refreshOutbox();
    window.open(`https://wa.me/?text=${encodeURIComponent(r.message.text)}`, "_blank", "noopener");
  } catch (e) { toast(`${t("warn")} ${e.message}`); }
}

// ---------------------------------------------------------------- tabs
function showPanel(name, scroll = false) {
  $$("#phase2Tabs button").forEach((x) => x.classList.toggle("active", x.dataset.panel === name));
  ["fix", "doctor", "letters", "helper", "follow"].forEach((p) => $(`#panel-${p}`)?.classList.toggle("hidden", p !== name));
  if (scroll) setTimeout(() => $("#phase2Tabs").scrollIntoView({ behavior: "smooth", block: "start" }), 300);
}

// ---------------------------------------------------------------- voice
let rec = null, chunks = [];
async function toggleMic() {
  const btn = $("#micBtn");
  if (rec && rec.state === "recording") { rec.stop(); return; }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    rec = new MediaRecorder(stream); chunks = [];
    rec.ondataavailable = (e) => chunks.push(e.data);
    rec.onstop = async () => {
      stream.getTracks().forEach((x) => x.stop());
      btn.classList.remove("rec"); btn.textContent = t("mic");
      const fd = new FormData();
      fd.append("audio", new Blob(chunks, { type: rec.mimeType || "audio/webm" }), "speech.webm");
      fd.append("lang", state.lang);
      try {
        const r = await fetch("/api/stt", { method: "POST", body: fd });
        if (!r.ok) throw new Error((await r.json().catch(() => ({}))).detail || r.statusText);
        const j = await r.json();
        $("#chatInput").value = j.text; $("#chatInput").focus(); p2.fromVoice = true;
        toast(t("heard"));
      } catch (e) { toast(`${t("warn")} ${e.message}`); }
    };
    rec.start(); btn.classList.add("rec"); btn.textContent = t("recording");
  } catch (e) { toast(`${t("warn")} ${e.message}`); }
}

async function speak(text) {
  if (!p2.speaker || !text) return;
  try {
    const r = await fetch("/api/tts", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, lang: state.lang }) });
    if (!r.ok) return;
    new Audio(URL.createObjectURL(await r.blob())).play();
  } catch (e) { /* text only */ }
}

function setSpeaker() { const b = $("#speakerBtn"); b.textContent = p2.speaker ? t("speakerOn") : t("speakerOff"); }

async function initPhase2() {
  $$("#phase2Tabs button").forEach((b) => b.onclick = () => showPanel(b.dataset.panel));
  try { p2.entries = (await apiGet("/api/doctor/entries")).entries; } catch (e) { /* offline */ }
  if (navigator.mediaDevices && window.MediaRecorder) { $("#micBtn").classList.remove("hidden"); $("#micBtn").onclick = toggleMic; }
  $("#speakerBtn").classList.remove("hidden");
  $("#speakerBtn").onclick = () => { p2.speaker = !p2.speaker; setSpeaker(); };
  setSpeaker();
  $$(".lang-switch button").forEach((b) => b.addEventListener("click", () => { setSpeaker(); renderPhase2(); }));
  renderPhase2();
}
document.addEventListener("DOMContentLoaded", () => setTimeout(initPhase2, 0));
