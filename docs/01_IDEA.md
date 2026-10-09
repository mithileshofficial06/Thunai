# Thunai (துணை) — FINAL IDEA 🔒 LOCKED (9 Oct 2026, v-final; no further idea changes, only data corrections from Stage 2)
### A Scheme Sathi agent for Tamil Nadu families

**Event:** CTRL+AI Inter-College Agentic AI Challenge · Sri Sairam Engineering College · 9 Oct 2026 · 6 hrs · team of 3
**Problem statement PS-10 (Scheme Sathi):** *"Develop a multilingual AI agent that learns a citizen's situation through conversation, checks eligibility against government scheme rules, lists the missing documents, prepares the application, and tracks pending actions."*

> **Why the name:** every PS-10 team will call their app "Scheme Sathi". **Thunai** (துணை, Tamil for *support* or *companion*) is ours: short, Tamil, memorable.

---

## 1. One line
> **"Other tools tell you which schemes exist. Thunai helps your family get it right the first time."**

**Find → Fix → Follow:** an AI agent that **finds** the schemes a Tamil Nadu family qualifies for, **fixes** the paperwork problems that get applications rejected or payments stopped, and **follows** up on pending actions, in Tamil.

**Principle:** *Rules decide. AI explains. Humans approve.*

---

## 2. PS-10 compliance check ✅

| PS-10 requirement | How Thunai meets it | Hero piece | Status |
|---|---|---|---|
| **"multilingual AI agent"** | Tamil and English throughout (chat, verdicts, documents, letters); **Tamil voice mode** (speak in Tamil via Groq Whisper; replies spoken by a Tamil neural voice via edge-tts), must-have for Eval 2. A real agent: goal → plan → AI-chosen actions → tools → observe → re-plan, shown live. | H1, H3, H5 | ✅ |
| **"learns a citizen's situation through conversation"** | Adaptive interview of the **whole family**; asks only the next relevant question; live family card; **corrections trigger automatic re-planning** | H1 | ✅ |
| **"checks eligibility against government scheme rules"** | Deterministic rules engine over 4 core schemes (6 if time allows) (from JSON rule files with sources); ✅ / ❓ / ❌ per member, **rule quoted + source link**; the LLM never decides | H2 | ✅ |
| **"lists the missing documents"** | Per-scheme document checklist → **"Missing documents"** list with where to get each one and what to bring, **plus** the Consistency Matrix for name mismatches | H4 | ✅ |
| **"prepares the application"** | **Application Pack** per eligible scheme: pre-filled application details from the conversation + document checklist + where to submit, printable. Plus a **pre-filled appeal letter** for rejected cases (helper-approved). | H5 | ✅ |
| **"tracks pending actions"** | Fix plan = a **task tracker** (To do / Done); marking a task done makes the agent **re-plan** the next step; Rejection Doctor for stopped payments; proactive ⏩ reminders as stretch S1 | H4, H5 | ✅ |

**All six PS-10 requirements are met by the must-build hero pieces (H1–H5), with no dependency on stretch items.**

---

## 3. The problem (verified evidence)

Eligible families lose scheme money **after** they are found eligible, at three points:

| Failure point | Reported evidence | Cost to the family |
|---|---|---|
| **A. Never applied, or not for all schemes** | Schemes are spread across central and state portals; low awareness is the main barrier reported by field groups (Haqdarshak) | Unclaimed ₹ every year |
| **B. Rejected at application** | Magalir Urimai: **1.63 crore** applications (Aug 2023); **1.06 crore** initially selected; **1.48 lakh** rejected applicants started receiving ₹1,000/month **after their appeals were considered** (DT Next, July 2024) | Months of lost benefit; repeated office visits |
| **C. Enrolled, but payment stops** | PM-KISAN: **2,14,75,001** farmers had not completed eKYC (minister's written reply to the Rajya Sabha, reported July 2023); about **6.65 lakh** Telangana farmers lost the benefit (about ₹133 crore) because eKYC wasn't updated (Deccan Chronicle, Dec 2022). DBT credits can bounce when Aadhaar is seeded to a dormant account or names don't match *(a known cause, not a statistic)*. | Money stops silently; the family doesn't know why |

**Root cause:** mostly **fixable paperwork problems**: name mismatches across documents (common with Tamil names written with initials), Aadhaar–bank seeding, pending eKYC, missing certificates. Nobody checks these **before** applying or explains them **after** a rejection, so families pay middlemen, make repeated trips (each costing a day's wages) or give up.

**Real-user evidence (to collect on the morning of 9 Oct):** call 2–3 people (parents, relatives, college staff) and ask *"Have you or someone you know had a scheme application rejected or a payment stop? What happened?"* Put **one real quote** on the problem slide. **Never invent one;** if no one is reached, leave it out.

---

## 4. Existing solutions and the gap

| Existing | What it does | What it doesn't do |
|---|---|---|
| **myScheme** (Govt of India) | Form-based eligibility matching across thousands of central and state schemes | Not conversational; one person at a time; no rejection prevention; no follow-up |
| **Jugalbandi** (Microsoft / AI4Bharat, May 2023) | WhatsApp bot answering scheme questions in local languages | Answers questions only |
| **Kisan e-Mitra** (Ministry of Agriculture, Sept 2023) | AI chatbot for **PM-KISAN only** (status, payment, ineligibility); includes Tamil | One scheme; no state schemes; no cross-document checks; no appeals |
| **Haqdarshak** | Trained field agents with a rule-based app | Depends on human agents; limited reach |
| **e-Sevai / CSC / grievance camps** | Official places to apply and complain | Families arrive unprepared |
| **Typical hackathon team** | "Multilingual chatbot for government schemes" | Same as Jugalbandi |

**Our gap (to our knowledge, not covered by any existing tool):** a **family-level, cross-scheme agent** that **prevents rejection before applying, diagnoses and drafts appeals after rejection, prepares the application pack and tracks the fixes**. It **works alongside** government tools by pointing users to myAadhaar, PM-KISAN Know Your Status and e-Sevai for official verification and submission.

---

## 5. Target users

| Role | Who | Need |
|---|---|---|
| **Beneficiary** | Low-income Tamil Nadu families: small farmers, women heads of family, elderly people and widows, government school students | Every benefit they're owed, with the fewest office trips |
| **Primary user** | The family's smartphone user (son or daughter) | Do it for their parents in minutes, in Tamil |
| **Secondary user** | Community helper (e-Sevai operator, NGO or **NSS volunteer**) | Help many families quickly; approve letters and unclear cases |

**Access:** a link or QR code · no install · no login · Tamil default, English option · mobile first, big buttons, simple words.

---

## 6. How the agent works (what judges see)

```
GOAL  "Get the Murugan family every benefit they are owed, with the fewest trips"
PLAN  1. Learn the family  2. Check the schemes  3. Check documents  4. Plan the fewest trips  5. Prepare the packs
ACT   extract_facts → check_eligibility → check_documents → check_names → plan_fixes → prepare_pack
OBSERVE  results → ₹ unlocked, missing documents, risks
RE-PLAN  when a fact changes ("income is ₹3 lakh") or a task is done ("Selvi's bank account is now linked to Aadhaar")
HUMAN    helper approves letters and unclear cases
```

The **agent activity panel** shows the goal, the plan (ticked off step by step) and every tool call live, including **re-plan events**.

---

## 7. The solution: Find → Fix → Follow

### 🔍 FIND
1. **Consent screen (one line):** *"We only use what you tell us in this conversation. We never ask for an Aadhaar number, bank number or OTP. Your answers are sent to a free AI service to understand them. Your plan is saved only on this phone; tap Clear to delete it."* (Saved in the browser's local storage, so the family can come back days later and continue tracking.)
2. **Conversational intake** in Tamil or English, covering the whole family; asks only the next relevant question.
3. **Live family card:** facts appear as the user answers; **any correction triggers automatic re-checking and re-planning**.
4. **Rules engine:** ✅ / ❓ / ❌ per member per scheme, **rule quoted + official source link**.
5. **Impact meter:** **₹ unlocked per year**.

### 🛠️ FIX
6. **Missing documents:** per eligible scheme, "Have it? Yes / No" → a list of missing documents with **where to get each one and what to bring**.
7. **Document Consistency Matrix** ⭐: family members × the documents needed, names typed **as printed** → 🟢 match · 🟡 initials or spelling **risk** · 🔴 conflict. Unknowns (eKYC done? bank seeded?) → **"check in 1 minute"** tasks using official tools.
8. **Fix plan = task tracker:** tasks ordered so the one that **unblocks the most schemes** comes first, **grouped by office** (bank, e-Sevai, VAO), each with To do / Done. Marking a task done → **the agent re-plans**.
9. **Trips saved** on the impact meter (formula in section 9).

### 📋 FOLLOW
10. **Application Pack** per eligible scheme: pre-filled application details + document checklist + where to submit → print.
11. **Rejection Doctor:** "rejected" or "my payment stopped" → yes/no decision tree → **most likely cause + how to verify it officially + fix steps**.
12. **Appeal letter** (Tamil and English), pre-filled → **helper approves** → print.

---

## 8. Requirements

### 8.1 Hero pieces: must build (they cover all of PS-10)
| ID | Requirement | Eval | Acceptance criteria (shown in the demo) | Est. |
|---|---|---|---|---|
| **H1** | Consent line + Tamil/English intake → live family card → **correction triggers re-plan** + **"Load Murugan family" demo button** (feeds the scripted answers through the same agent, so the demo can't stall on stage) | Eval 1 | Murugan family captured in ≤10 turns; changing income to ₹3L flips Selvi's KMUT to ❌ and updates ₹ automatically | 1.5 h |
| **H2** | Rules engine (JSON rule files) over the **4 core schemes** → scheme cards (rule + source) → **₹ unlocked** | Eval 1 | Correct verdicts for all 3 personas; "₹30,000/year" shown | 1 h |
| **H3** | Agent panel: **goal + plan + live tool calls + re-plan events** | Eval 1 | Plan steps tick off in order; re-plan event appears on a correction | 45 min |
| **H4** | Missing documents + Consistency Matrix + fix plan grouped by office **with To do / Done tracking** + **trips saved** | Eval 2 | Kavya's missing bank account listed with where to get it; Kavya's row 🟡; "Bank visit (2 tasks, unblocks 2 schemes)" first; "trips 6 → 2"; marking done → re-plan | 1.5 h |
| **H5** | **One template engine** → (a) **Application Pack** per scheme, (b) **Rejection Doctor → appeal letter → helper approve** → print | Eval 2 | Murugan pack printed; Meena's case diagnosed; Lakshmi Paati's letter approved | 1.25 h |

About 6 hrs of work split across 3 people working in parallel → fits about 5 hrs of wall-clock time.

### 8.2 Stretch, strictly in this order and only after H1–H5 work end to end
| ID | Requirement | Est. |
|---|---|---|
| S1 | ⏩ **"15 days later": proactive reminders and escalation** (the agent acts on its own) | 30 min |
| ~~S2~~ | *Promoted to must-have:* **Tamil voice mode**, 🎤 speak (Groq Whisper) + 🔊 replies spoken (edge-tts Tamil neural voice) | in B4 + B5 |
| S3 | Bank Aadhaar-seeding request letter (second letter template) | 15 min |
| S4 | WhatsApp share (`wa.me`) of the family summary | 15 min |
| S5 | Robot fills a mock e-Sevai form (Playwright / UiPath) | 45 min |

### 8.3 Non-functional
| ID | Requirement |
|---|---|
| NFR1 Accessibility | Mobile first, large targets, simple words, Tamil default, no install or login |
| NFR2 Privacy | **Never** asks for or stores an Aadhaar number, bank account number or OTP; consent line; only names as printed and yes/no facts; no server database; the plan is saved **only on the user's phone** (browser local storage); one-tap Clear |
| NFR3 Trust | Eligibility by rules only; every verdict cites a rule and source; "likely eligible; the department decides" |
| NFR4 Human in the loop | Letters and unclear or conflicting cases need a helper's approval. **In the prototype:** a "Helper review" tab (the e-Sevai, NSS or NGO helper's view) lists pending items with the agent's reasoning, with Approve / Edit buttons. **In self mode**, unapproved letters are marked "DRAFT: get it checked by a helper or at e-Sevai". |
| NFR5 Speed | Under 5 s per agent turn; Murugan demo under 2 min |
| NFR6 Reliability | Every LLM step has a fallback (fixed question flow; Tamil templates for verdicts, documents and letters) |
| NFR7 Maintainability | Each scheme is a JSON rule file with `source_url` and `last_verified`; editable without touching code |

### 8.4 Out of scope (deliberately)
Real portal submission · reading government databases · document uploads or OCR · login · more than 6 schemes · a real WhatsApp bot.

---

## 9. Impact numbers: how we count them (shown openly)
- **₹ unlocked / year** = the sum of **verified** yearly benefits for ✅ schemes only (health cover shown separately, not added).
- **Trips without Thunai** = for each counted scheme: 1 application visit (0 if the scheme is applied for online) + 1 extra visit per problem found at the counter (missing document, unlinked/inactive account, pending eKYC, name risk) *(assumption: unprepared, each problem is discovered at a separate visit)*.
- **Trips with Thunai** = the number of **distinct offices** in the grouped fix plan, including the application offices.
- **Murugan family check (tested in Stage 2):** without = PM-KISAN 1 + 1 (eKYC) = 2; KMUT 1 + 1 (Selvi's account not linked) = 2; Pudhumai Penn 0 (applied online on Penkalvi) + 1 (Kavya has no account) + 1 (name risk) = 2 → **6**. With = bank (Selvi's linking + Kavya's account, one visit) + e-Sevai (PM-KISAN eKYC + KMUT application) = **2**. So the demo says **"6 → 2"**. After the re-plan (income ₹3L): **4 → 2**. *(KMUT officially needs no income certificate, so none is listed.)* The full algorithm is in `data/documents.json` → `trips_algorithm`; the number is **computed by code, never hard-coded**.
- The formula is shown in a tooltip and on the slide: *"here is how we count it."*

---

## 10. Schemes covered: 4 core, 2 if time allows
**Rule:** amounts and limits go into the JSON **only after they are confirmed on the official page** (Stage 2). The ₹30,000 demo total must come from verified numbers.

**Stage 2 done (9 Oct):** verified rules are in [`data/schemes.json`](../data/schemes.json); details in [02_DATA_VERIFICATION.md](02_DATA_VERIFICATION.md).

| Scheme | Priority | Level | For | Key rules (Stage 2 status) |
|---|---|---|---|---|
| PM-KISAN | **Core** | Central | Landholding farmer families | ₹6,000/year; eKYC mandatory ✅ (official) |
| Kalaignar Magalir Urimai Thogai | **Core** | TN | Woman head of family aged 21+ (ration-card rule) | Income < ₹2.5L; < 5 acres wet / < 10 acres dry; electricity < 3,600 units/yr; ₹1,000/month; no income certificate needed; appeal within 30 days via e-Sevai to the RDO ✅ official FAQ |
| Pudhumai Penn | **Core** | TN | Girls who studied Classes 6–12 in government schools, now in their first UG / diploma / ITI | ₹1,000/month by DBT; no income limit; with other scholarships; the student applies herself on the Penkalvi portal ✅ official (TN Social Welfare Dept). Aided / RTE route → "Need info" (news only) |
| Destitute Widow Pension / Old Age Pension | **Core** (needed for Lakshmi Paati) | TN | Destitute widows 18+ (property ≤ ₹1 lakh) / destitute BPL elders 60+ | ₹1,200/month since Aug 2023 ✅ official (TN Revenue Administration) |
| Tamil Pudhalvan | Disabled | TN | The boys' counterpart | Not verified, so switched off in the data |
| CMCHIS | Disabled | TN | Low-income families | Not verified, so switched off in the data |

---

## 11. Demo personas
| Persona | Situation | Shows |
|---|---|---|
| **Murugan family** (main, Tamil) | Murugan, 52, farmer with 1.5 acres; wife Selvi, 47, homemaker; daughter Kavya, 18, studied Classes 6–12 in a government school, **just admitted to first-year B.Sc**; about ₹90k/year. Selvi's bank account **is not Aadhaar-seeded**, Kavya **has no bank account of her own**, and Murugan **hasn't done PM-KISAN eKYC** (all scripted) | Plan → 3 schemes (PM-KISAN, Magalir Urimai, Pudhumai Penn), **₹30,000/year** → **re-plan when income is corrected (→ ₹18,000)** → missing: Kavya's bank account → Kavya 🟡 → fix plan by office → **trips 6 → 2** → Application Pack |
| **Meena: "My ₹1,000 stopped"** (a different family) | Has been receiving Magalir Urimai; payment stopped 3 months ago | Rejection Doctor → likely bank seeding moved to a dormant account → check on myAadhaar → fix |
| **Lakshmi Paati** | 66, widow, alone; pension rejected | Tamil appeal letter → **helper approves** → print |

---

## 12. Pitch and demo (5–7 min): a person first, statistics second
1. **Open with Meena (15 s):** "Meena's ₹1,000 stopped three months ago. Nobody told her why. She has lost two days' wages going to offices."
2. **The scale (15 s):** "In July 2024, 1.48 lakh women who had been rejected for Magalir Urimai started receiving it after appealing. How many never appealed?" (+ the real-user quote if collected)
3. **Live demo (4 min):**
   - Murugan family in Tamil (**"Load Murugan family"** button as backup) → the panel shows **goal and plan** → 3 schemes → **₹30,000/year**
   - *"Actually, income is ₹3 lakh"* → **the agent re-plans live** → change back
   - Missing documents → **Consistency Matrix: Kavya 🟡** → fix plan by office → **trips saved** → Application Pack
   - Meena → Rejection Doctor → cause + how to verify
   - Lakshmi Paati → Tamil appeal → **helper approves**
4. **How it's different (30 s):** one slide comparing myScheme, Jugalbandi, Kisan e-Mitra and Thunai.
5. **Architecture in automation terms (20 s):** agent (reasoning) → tools (rules engine, document checker, pack and letter generator) → human-in-the-loop approval → roadmap: an RPA robot fills the e-Sevai form.
6. **Close (15 s):** *"Find. Fix. Follow. Rules decide, AI explains, humans approve. Our pilot plan: NSS volunteers take Thunai to adopted villages."*

---

## 13. Prepared answers for judges
| Question | Answer |
|---|---|
| "Where's the agent?" | Show the panel: goal → plan → tools → re-plan on a correction or a completed task. |
| "Isn't this myScheme?" | myScheme matches; Thunai prevents rejection, diagnoses stopped payments, prepares packs and appeals, for the whole family. |
| "How do you count trips saved?" | Section 9 formula; it's an assumption, stated openly. |
| "Who updates the rules?" | JSON rule files with source + last-verified date, editable by a helper. Next: AI drafts updates from new government orders, and a human verifies them. |
| "Is 'M. Kavya' really rejected?" | It's a **risk flag**, not a rejection; mismatches are a known cause of DBT failure, and fixing them early is cheap. |
| "Can it see government records?" | No, by design. It gives the likely cause + the official tool to confirm it. |
| "Will an illiterate farmer use it?" | They don't need to. Their daughter or an NSS or e-Sevai helper runs it in Tamil. |
| "Does it solve everything?" | No. The family still visits the office once, prepared; the department decides; 4–6 schemes in the prototype. |

---

## 14. Why this wins
1. **It addresses the real loss** (rejections and stopped payments); most teams will build discovery.
2. **Visibly agentic:** goal → plan → act → **live re-planning** → human approval.
3. **A memorable visual:** the Consistency Matrix. **Measurable impact:** ₹ unlocked and trips saved, with an open formula.
4. **Responsible AI:** rules decide, consent, no sensitive IDs, a human approves.
5. **Local insight:** a Tamil name, Tamil-first, names with initials, Magalir Urimai, e-Sevai, NSS.
6. **Honest scope:** it knows what it doesn't solve.

---

## 15. Rules for the day
- **On arrival: ask an organiser for the exact Evaluation 1 time.** H1–H3 must work end to end by then; plan backwards from it.
- Start with the **4 core schemes**; add Tamil Pudhalvan or CMCHIS only if everything else works.
- Build H1–H5 first; stretch items only after all of them work end to end.
- Use the **"Load Murugan family"** button on stage if typing or the conversation is slow.
- **Stop adding features 45 min before each evaluation** and rehearse.
- Record a backup demo video before each evaluation.
- If the LLM intake is unstable after 30 min, switch to the fixed question flow.
- Say "reported" + year for statistics, "to our knowledge" for uniqueness, "pilot plan" for NSS.
- Ask the organisers whether pre-written code is allowed. Only data and design are prepared tonight.

## 16. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Running out of time | Strict H1–H5 → S1–S5 order; fallbacks |
| Wrong scheme rule in front of judges | Verify on official sites; show source links |
| Poor Tamil from the LLM | Tamil templates for key outputs; the LLM only for conversation |
| Wi-Fi or API failure | Ethernet cable; backup video; tested persona runs |
| Another team with a similar idea | Thunai's name, the matrix, live re-planning, Application Pack + Doctor |

---

## Source verification (checked 9 Oct 2026)

| Claim used | Status | Source |
|---|---|---|
| KMUT: 1.63 crore applications | ✅ Verified (22 Aug 2023) | https://newstodaynet.com/2023/08/22/1-63-cr-applications-received-for-magalir-urimai-thogai-scheme/ |
| KMUT: 1.06 crore initially selected; 1.48 lakh rejected applicants paid after appeals | ✅ Verified (DT Next, 16 July 2024) | https://www.dtnext.in/news/chennai/148-lakh-more-women-start-receiving-rs-1000-honorarium-under-kalaignar-mahalir-urimai-thogai-scheme-795031 |
| PM-KISAN: 2,14,75,001 farmers without eKYC (Rajya Sabha written reply, July 21) | ✅ Figure verified via report; year 2023 | https://housing.com/news/over-2-14-cr-farmers-yet-to-complete-pm-kisan-kyc-govt |
| Telangana: about 6.65 lakh farmers lost PM-KISAN (about ₹133 crore) over eKYC | ✅ Verified (6 Dec 2022) | https://deccanchronicle.com/nation/current-affairs/061222/665-lakh-farmers-lose-pm-kisan-scheme-benefits.html |
| PM-KISAN: ₹6,000/year, eKYC mandatory | ✅ Official | https://pmkisan.gov.in/ |
| Kisan e-Mitra: PM-KISAN queries, Tamil included, Sept 2023 | ✅ Verified | https://www.gktoday.in/ministry-of-agriculture-launches-ai-chatbot-for-pm-kisan-scheme/ |
| Jugalbandi: WhatsApp, multilingual, scheme information, May 2023 | ✅ Verified | https://www.businesstoday.in/amp/tech-today/trending/story/microsoft-launches-jugalbandi-a-multilingual-ai-chat-bot-for-rural-india-382521-2023-05-23 |
| myScheme: eligibility matching, links out to other portals | ⚠️ Count reworded to "thousands" | https://www.myscheme.gov.in/faqs |
| DBT bounce causes | ⚠️ Unofficial guide; a known cause, not a statistic | https://righttoinformation.wiki/check-status/dbt-money-not-credited-fix |
| TN ration and Aadhaar name problems | ⚠️ 2017 report; an example only | https://deccanchronicle.com/nation/current-affairs/270717/chennai-big-demand-fewer-centres-for-aadhaar.html |
| Haqdarshak model | ✅ Qualitative | https://unreasonablegroup.com/companies/haqdarshak |
| Hackathon precedent (multilingual government-services chatbot won) | ✅ | https://cbit.ac.in/wp-content/uploads/2024/10/CET-STUDENT-ACHEIVEMNTS-11.11.2024.pdf |
| UP 6.18 lakh name mismatch | ❌ Removed (couldn't verify) | — |
| Jugalbandi "171 schemes" | ❌ Removed (conflicting reports) | — |

**Scheme-fact sources (secondary; re-verify officially):** https://www.tnpscthervupettagam.com/currentaffairs-detail/kalaignar-magalir-urimai-thogai-%E2%80%93-guidelines ; https://sarkariyojana.com/?p=71515 ; https://www.citizennest.com/hi/guide/tn-pudhumai-penn-scholarship-government-school-girls ; https://www.indiascholarships.in/ta/scholarships/pudhumai-penn-scheme-tamil-nadu

**Demo maths:** PM-KISAN ₹6,000 + KMUT ₹12,000 + Pudhumai Penn ₹12,000 = **₹30,000/year** ✅. With income corrected to ₹3L: KMUT ❌ (over ₹2.5L) → **₹18,000/year** (PM-KISAN + Pudhumai Penn, which has no income limit).
