# Thunai (துணை) — FINAL IDEA 🔒 v2 (9 Oct 2026, after Evaluation 1)
### A Scheme Sathi agent for Tamil Nadu families

**Event:** CTRL+AI Inter-College Agentic AI Challenge · Sri Sairam Engineering College · 9 Oct 2026 · 6 hrs · team of 3
**Problem statement PS-10 (Scheme Sathi):** *"Develop a multilingual AI agent that learns a citizen's situation through conversation, checks eligibility against government scheme rules, lists the missing documents, prepares the application, and tracks pending actions."*

> **Why the name:** every PS-10 team will call their app "Scheme Sathi". **Thunai** (துணை, Tamil for *support* or *companion*) is ours: short, Tamil, memorable.

**What changed in v2:**
- **"Follow" now means Remember + Remind + Re-match:** login and chat history, an SMS outbox with a summary and reminders, and alerts when a new scheme matches a saved family.
- A **sample-documents family (Revathi)** shows document problems being found and fixed.
- **Six letter types**, all drafted from templates and approved by a helper.
- Up to **8–9 verified schemes** (only with an official source), plus a **source check**.
- The UiPath robot is **dropped**: Thunai prepares the application and the family submits it.
- The UI is a **government-portal style** with no emojis.
- The principle is now *Rules decide · AI understands · Humans approve*.

---

## 1. One line
> **"Other tools tell you which schemes exist. Thunai helps your family get the money: finds what you're owed, fixes what would get you rejected, and follows up until it arrives."**

**Find → Fix → Follow**, in Tamil, for the whole family.

**Principle:** *Rules decide · AI understands · Humans approve.*
- **Rules decide:** eligibility comes from deterministic rules taken from official documents.
- **AI understands:** two AI models read everyday Tamil and English (and Tamil voice) and must agree, quoting the user's own words as proof.
- **Humans approve:** every letter and every unclear case goes to a helper.

---

## 2. PS-10 compliance check ✅

| PS-10 requirement | How Thunai meets it | Status |
|---|---|---|
| **"multilingual AI agent"** | Tamil and English everywhere; **Tamil voice in and out** (Groq Whisper and edge-tts). A real agent: goal → plan → actions → tools → observe → **re-plan**, plus **actions it takes by itself** (reminders, re-match), all shown live in the activity log. | ✅ |
| **"learns a citizen's situation through conversation"** | Adaptive interview of the **whole family**; asks only the next relevant question; two-model accuracy check; any correction triggers a re-plan | ✅ |
| **"checks eligibility against government scheme rules"** | Deterministic rules engine over the verified schemes; Eligible / Needs information / Not eligible per member, with the rule and official source quoted; the AI never decides | ✅ |
| **"lists the missing documents"** | Missing documents with where to get each one and what to bring, plus the **name check across documents** (Match / Name risk / Conflict) | ✅ |
| **"prepares the application"** | **Application pack** per eligible scheme, plus **letters**: name correction, bank (Aadhaar) linking request, complaint, KMUT appeal and pension petition. Drafted from templates, approved by a helper, then printed. The family or helper submits on the official site. | ✅ |
| **"tracks pending actions"** | Fix plan as a task tracker (ticking a task triggers a re-plan); **login + history** so a family can return; **SMS outbox** (summary + reminders); **"15 days later"** follow-up with escalation; **Doctor** when money stops | ✅ |

---

## 3. The problem (verified evidence)

Eligible families lose scheme money **after** they are found eligible, at three points:

| Failure point | Reported evidence | Cost to the family |
|---|---|---|
| **A. Never applied, or not for all schemes** | Schemes are spread across central and state portals; low awareness is the main barrier reported by field groups (Haqdarshak) | Unclaimed ₹ every year |
| **B. Rejected at application** | Magalir Urimai: **1.63 crore** applications (Aug 2023); **1.06 crore** initially selected; **1.48 lakh** rejected applicants started receiving ₹1,000/month **after their appeals were considered** (DT Next, July 2024) | Months of lost benefit; repeated office visits |
| **C. Enrolled, but payment stops** | PM-KISAN: **2,14,75,001** farmers had not completed eKYC (Rajya Sabha written reply, reported July 2023); about **6.65 lakh** Telangana farmers lost the benefit (about ₹133 crore) because eKYC wasn't updated (Deccan Chronicle, Dec 2022). DBT credits can bounce when Aadhaar is seeded to a dormant account or names don't match *(a known cause, not a statistic)*. | Money stops silently; the family doesn't know why |

**Root cause:** mostly **fixable paperwork problems**:
- name mismatches across documents (common with Tamil names written with initials)
- Aadhaar–bank seeding
- pending eKYC
- missing certificates

Nobody checks these **before** applying, explains them **after** a rejection, or **follows up** until the money arrives. So families pay middlemen, make repeated trips (each costing a day's wages), or give up.

**Real-user evidence:** put one real quote on the slide only if collected. **Never invent one.**

---

## 4. Existing solutions and the gap

| Existing | What it does | What it doesn't do |
|---|---|---|
| **myScheme** (Govt of India) | Form-based eligibility matching across thousands of schemes | Not conversational; one person at a time; no rejection prevention; no follow-up |
| **Jugalbandi** (Microsoft / AI4Bharat, May 2023) | WhatsApp bot answering scheme questions in local languages | Answers questions only |
| **Kisan e-Mitra** (Ministry of Agriculture, Sept 2023) | AI chatbot for **PM-KISAN only**; includes Tamil | One scheme; no cross-document checks; no appeals |
| **Haqdarshak** | Trained field agents with a rule-based app | Depends on human agents; limited reach |
| **e-Sevai / CSC / grievance camps** | Official places to apply and complain | Families arrive unprepared |
| **Typical hackathon team** | "Multilingual chatbot for government schemes" | Same as Jugalbandi |

**Our gap (to our knowledge):** a **family-level, cross-scheme agent** that covers the whole journey:
- prevents rejection **before** applying (document and name checks);
- prepares the pack and the letters;
- diagnoses stopped payments **after** enrolment;
- **follows up on its own** (reminders, escalation, new-scheme alerts).

It **works alongside** government tools (myAadhaar, PM-KISAN Know Your Status, e-Sevai) for official checks and submission.

---

## 5. Target users

| Role | Who | Need | How they sign in |
|---|---|---|---|
| **Beneficiary** | Low-income TN families: small farmers, women heads of family, elderly people and widows, government-school students | Every benefit they're owed, with the fewest office trips | Phone number + 4-digit PIN, or **guest** |
| **Primary user** | The family's smartphone user (son or daughter) | Do it for their parents in minutes, in Tamil, and come back later | Same account as the family |
| **Helper** | e-Sevai operator, NGO or **NSS volunteer** | Help many families; approve letters and unclear cases | Helper login (username + password) |

**Access:**
- a link or QR code, no install, guest mode always available
- Tamil default, English option
- mobile first, big buttons, simple words

**Why a PIN, not an OTP:** a real OTP SMS costs money, and Thunai tells people never to share an OTP.

---

## 6. How the agent works (what judges see)

```
GOAL     "Get the Murugan family every benefit they are owed, with the fewest trips"
PLAN     1. Learn the family  2. Check schemes  3. Check documents  4. Plan the fewest trips  5. Prepare the packs
ACT      understand (2 AIs) → check eligibility → check documents + names → plan fixes → draft letters
OBSERVE  ₹ per year, missing documents, name risks, office visits
RE-PLAN  a fact changes ("income is ₹3 lakh") or a task is done ("Selvi's bank is now linked")
ON ITS OWN  "15 days later": reminders, deadline warnings, escalation; new scheme → re-match → SMS
HUMAN    a helper approves every letter and every unclear case
```

The **agent activity log** shows each step live, labelled Goal / Plan / Action / Decision / Re-plan / Follow-up / Privacy.

---

## 7. The solution: Find → Fix → Follow

### FIND
1. **Consent:** *"We never ask for an Aadhaar number, bank number or OTP. Your answers are sent to a free AI service to understand them. If you log in, your family's details are saved under your phone number; you can delete them at any time."*
2. **Conversation** in Tamil or English (typed or **spoken**), covering the whole family; asks only the next relevant question.
3. **Two-AI accuracy check:**
   - Two models read each message.
   - Each must quote the user's words as proof.
   - Numbers are cross-checked by code.
   - If the models disagree, Thunai asks instead of guessing.
4. **Live family card** with Edit links. A correction leads to a re-check and a re-plan.
5. **Rules engine:** Eligible / Needs information / Not eligible per member, with **the rule, the official source and the checked date**.
6. **Estimated benefit:** ₹ per year.

### FIX
7. **Missing documents:** where to get each one and what to bring.
8. **Name check across documents** (Match / Name risk / Conflict). Each conflict is sent to **the office that issued that document** (for example a passbook fix happens at the bank, during the same visit as the Aadhaar linking).
9. **Fix plan = task tracker**, grouped by office and ordered by what unblocks the most schemes. Ticking a task leads to a re-plan. **Office visits saved** (formula in section 9).
10. **Revathi (sample documents):** document cards marked SAMPLE, with no numbers, show a name conflict, a missing death certificate and an unlinked bank account being found and planned.

### FOLLOW
11. **Application pack + letters:**
    - name correction
    - bank linking request
    - complaint
    - KMUT appeal
    - pension petition

    All are written in Tamil and English and drafted from templates (names and numbers are always exact). Unknown details are left blank to be written by hand. They stay **DRAFT** until a helper approves, then they can be printed.
12. **Doctor** ("money stopped" or "rejected"): yes/no questions lead to the **most likely cause, how to check it in 1 minute, fix steps, the office added to the plan, and the right letter**.
13. **Remember:** login and **previous conversations**; one-tap delete.
14. **Remind:** an **SMS outbox** with a short Tamil summary (benefit, next office, what to bring, "never share your OTP") plus a free **WhatsApp share** button. Real SMS sending plugs in later.
15. **Follow up on its own:** **"15 days later"** gives reminders for open tasks, warns about appeal deadlines and escalates stuck tasks to a helper. When a new scheme is added, **re-match** checks every saved family and alerts the ones who now qualify.
16. **Source check (stretch):** detects changed official pages and marks them "needs review". It never edits rules by itself.

---

## 8. Requirements

### 8.1 Must build (all of PS-10)
| ID | Requirement | Eval | Status |
|---|---|---|---|
| **H1** | Consent + Tamil/English chat → live family card → correction leads to re-plan; demo buttons | Eval 1 | ✅ built |
| **H2** | Rules engine → scheme results (rule + source + checked date) → ₹ per year | Eval 1 | ✅ built |
| **H3** | Agent activity log: goal, plan, actions, re-plan | Eval 1 | ✅ built |
| **H4** | Missing documents + name check + fix plan by office with Done tracking + office visits saved + **Revathi** | Eval 2 | backend ✅ · UI in B5 |
| **H5** | Application pack + 5 letters + **helper approval** + print; **Doctor** wired to plan and letters | Eval 2 | backend ✅ · UI in B5 |
| **H6** | **Voice:** speak Tamil (Whisper) and replies spoken (edge-tts) | Eval 2 | B4a P4 |

### 8.2 Should build (Follow), in this order
| ID | Requirement |
|---|---|
| **F1** | Login (phone + PIN, helper login), chat history, delete my data; guest mode for demos |
| **F2** | SMS outbox + summary SMS + WhatsApp share |
| **F3** | "15 days later" follow-up (reminders, deadline warning, escalation) + new-scheme re-match |

### 8.3 Stretch
| ID | Requirement |
|---|---|
| **S1** | 3–4 more **officially verified** schemes (otherwise they stay disabled) |
| **S2** | Source check: changed official page leads to "needs review" |

### 8.4 Non-functional
| ID | Requirement |
|---|---|
| NFR1 Accessibility | Mobile first, large targets, simple words, Tamil default, voice, guest mode |
| NFR2 Privacy | **Never** asks for or stores an Aadhaar number, bank account number or OTP; the privacy guard removes such numbers before any AI call. A login stores only the phone number, a **hashed** PIN and the family facts. Consent at registration; one-tap delete; letters leave account numbers blank. |
| NFR3 Trust | Eligibility by rules only; every result cites a rule, an official source and the checked date; "the department decides" |
| NFR4 Human in the loop | Every letter and unclear case needs a helper's approval. Drafts carry a DRAFT watermark and can't be printed until approved. |
| NFR5 Accuracy | Two AI models must agree, with evidence from the user's own words; spoken numbers are always confirmed; tested at **0 wrong facts** (16/18 automatic, 2 asked) |
| NFR6 Reliability | Backup AI (Gemini); offline mode with direct questions; demo families load instantly |
| NFR7 Maintainability | Each scheme is JSON with its source and checked date; adding a scheme needs no code change |

### 8.5 Out of scope (deliberately)
- Submitting to government portals
- Reading government databases
- Document uploads or OCR
- Real SMS sending (outbox only)
- Real OTP login
- Unverified schemes

---

## 9. Impact numbers: how we count them (shown openly)
- **₹ per year** = the sum of verified yearly benefits for Eligible schemes that are counted (only one of two conflicting schemes is counted; health cover is not added).
- **Visits without Thunai** = for each counted scheme: 1 application visit (0 if online) + 1 visit per problem found at the counter (missing document, unlinked account, pending eKYC, name risk or conflict). *Assumption: unprepared, each problem is discovered at a separate visit.*
- **Visits with Thunai** = the number of **distinct offices** in the grouped fix plan.
- **Murugan:** **6 → 2**; after income is corrected to ₹3L: **4 → 2**.
- **Revathi:** **4 → 3** (the passbook name fix joins the bank visit).
- These numbers are computed by code, never hard-coded; the formula is shown in a tooltip.

---

## 10. Schemes covered
**Rule:** a scheme is enabled only with an **official source + checked date**; otherwise it stays disabled and is never shown.

| Scheme | Level | For | Status |
|---|---|---|---|
| PM-KISAN | Central | Landholding farmer families | ✅ official |
| Kalaignar Magalir Urimai Thogai | TN | Woman head of family, 21+ | ✅ official FAQ |
| Pudhumai Penn | TN | Govt-school girls in their first UG / diploma / ITI | ✅ official |
| Destitute Widow Pension | TN | Destitute widows 18+ | ✅ official |
| Old Age Pension (IGNOAPS + state) | Central + TN | Destitute BPL elders 60+ | ✅ official |
| Tamil Pudhalvan, differently-abled assistance, unmarried / deserted women pension, PMMVY | — | — | **S1**: enabled only if officially verified on 9 Oct |
| CMCHIS | TN | — | Disabled |

---

## 11. Demo families (all fictional)
| Family | Situation | Shows |
|---|---|---|
| **Murugan family** (main) | Farmer 52, wife Selvi 47, daughter Kavya 18 (first-year B.Sc). Selvi's bank account isn't linked to Aadhaar; Kavya has no bank account; PM-KISAN eKYC is pending. | 3 schemes, **₹30,000/year** → correction → **₹18,000** → fix plan → **6 → 2** → application pack |
| **Revathi** (sample documents) | Widow 52, alone. Name forms differ: "Revathi Sekar" / "S. Revathi" / "REVATHI S". Death certificate missing; bank account not linked to Aadhaar. | Document problems found → fixes at the right offices → name correction and bank letters → helper approves → tick a fix → re-plan |
| **Meena** ("my ₹1,000 stopped") | Aadhaar is still linked to an old, inactive account | Doctor → bank linking cause → bank visit added to the plan → bank letter |
| **Lakshmi Paati** | 66, widow; pension rejected (no death certificate) | Doctor → pension petition → helper approves → print |

---

## 12. Pitch: Evaluation 2 story (5–7 min)
1. **Login:** previous conversations → reopen the Murugan chat. *(Remember)*
2. **Revathi:** sample documents → name conflict, missing certificate, unlinked bank → fix plan → tick → re-plan. *(Fix)*
3. **Letter:** name correction drafted → helper logs in and approves → print. *(Humans approve)*
4. **Meena:** money stopped → 2 questions → cause → bank letter. *(Doctor)*
5. **"15 days later":** reminders, escalation, SMS outbox; send summary / WhatsApp. *(Follow on its own)*
6. **Voice:** speak Tamil → hear Tamil. *(Inclusion)*
7. **Close:** *"Find. Fix. Follow. Rules decide, AI understands, humans approve. Pilot plan: NSS volunteers take Thunai to adopted villages."*

---

## 13. Prepared answers for judges
| Question | Answer |
|---|---|
| "Where's the agent?" | The activity log: goal → plan → actions → re-plan, and follow-up actions it takes on its own. |
| "How do you know the AI is right?" | Two models must agree and quote the user's words; code checks the numbers; if they disagree it asks. Tested: 0 wrong facts. And the AI never decides eligibility. |
| "Isn't this myScheme?" | myScheme matches. Thunai prevents rejection, fixes documents, drafts letters, diagnoses stopped payments and follows up, for the whole family. |
| "Does it send SMS?" | It prepares them in an outbox, ready for an SMS provider; WhatsApp share works today. We didn't pay for an SMS gateway in a hackathon. |
| "Why a PIN, not an OTP?" | Real OTP SMS costs money, and we teach people never to share an OTP. In production: the government SMS gateway. |
| "Are those real documents?" | No: sample cards marked SAMPLE, with no numbers. Thunai never reads or stores real IDs. |
| "Does it apply for me?" | It prepares everything; the family or helper submits on the official site. The department decides. |
| "Who updates the rules?" | JSON rule files with source and checked date; the source check flags changed pages for a human to review. |
| "Can it see government records?" | No, by design. It gives the most likely cause and the official tool to confirm it. |

---

## 14. Why this wins
1. **The whole journey:** it addresses the real loss (rejections and stopped payments), not just discovery.
2. **Visibly agentic:** live re-planning **and** follow-up on its own.
3. **Accurate by design:** rules decide, two AIs agree, a human approves.
4. **Memorable moments:** Revathi's name conflict, the helper approving a letter, "6 → 2" visits.
5. **Local insight:** Tamil first, Tamil voice, names with initials, Magalir Urimai, e-Sevai, NSS.
6. **Honest scope:** says what it doesn't do (submit, see records, send real SMS).

---

## 15. Risks and mitigations
| Risk | Mitigation |
|---|---|
| Running out of time | Strict order H4–H6 → F1–F3 → S1–S2, with the cut order in `04_BUILD_PLAN.md` §4a |
| Wrong scheme rule | Official sources only; checked dates shown; unverified schemes disabled |
| AI misreads | Two-model agreement + evidence + number checks; asks when unsure |
| Wi-Fi or API failure | Backup AI, offline mode, instant demo families, backup video |
| Privacy concern about login | Guest mode; phone + hashed PIN only; never IDs; one-tap delete |

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
