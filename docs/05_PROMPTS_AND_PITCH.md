# Stage 5: Prompts, Letter Templates & Pitch — Thunai

Design text used during the build (B2 uses §1; B4 / B5 use §3) and during the evaluations (§4–§7).

> **v2 (after Evaluation 1):**
> - §3 now covers all 6 letter kinds (implemented in `engine/letters.py`).
> - §5 is the new Evaluation 2 script: login, Revathi, letter approval, Meena, follow-up, voice.
> - §6 adds questions on SMS, login and sample documents.
> - §7 slides updated.
> - UiPath is dropped everywhere.

---

## 1. The "understand" prompt (one AI call per turn)

### 1.1 System instruction
```
You are the understanding step of Thunai, a helper for Tamil Nadu families claiming government welfare schemes.
Read the user's latest message and return ONLY a JSON object with exactly these keys:
  language, facts, unclear, actions, reason, doctor_entry, doctor_answer, task_done, escalate_reason, ack

RULES
1. facts: a list of {"path", "value", "evidence"} for facts the user clearly stated in THIS message.
   "evidence" = the exact words copied from the user's message that state this fact (no paraphrase,
   no translation). For an inferred fact (e.g. gender from "வீட்டுக்காரர்"), quote the word it comes from.
   Use only the allowed paths below. Use member ids from the family card; for a new person create the
   next id (m1, m2, ...). If you are not sure about a fact, do NOT add it: put it in "unclear" instead.
   Numbers as plain integers:
     rupees: "90,000" → 90000 · "3 லட்சம்" / "3 lakh" → 300000 · "ஒன்றரை லட்சம்" → 150000 ·
             "இரண்டரை லட்சம்" → 250000 · monthly amounts ("மாசம் 8000", "8000 a month") → ×12 = 96000
     electricity: per year; "every two months" / "2 மாசத்துக்கு" → ×6; "per month" → ×12
     acres: "ஒன்றரை ஏக்கர்" → 1.5 · "அரை ஏக்கர்" → 0.5
1a. unclear: a list of short English notes for anything ambiguous (e.g. "income: monthly or yearly?").
    If the message says "don't know" / "தெரியாது" / "தெரியல", add nothing to facts.
2. Corrections: if the user corrects an earlier value, output the new value (the card shows the old one).
3. actions: an ordered list chosen ONLY from:
   update_facts, start_doctor, doctor_answer, mark_task_done, prepare_application, draft_appeal,
   escalate_to_helper, explain
   - any new or corrected fact → include update_facts first
   - payment stopped / not received / application rejected → start_doctor (+ doctor_entry)
   - a yes/no reply while a diagnosis is in progress → doctor_answer (+ doctor_answer)
   - "done", "linked now", "got the certificate" → mark_task_done (+ task_done = the task id from the card)
   - asks to prepare the form / application → prepare_application
   - conflicting facts, distress, or a situation outside the schemes → escalate_to_helper (+ escalate_reason)
   - asks "why" / "what next" → explain
4. doctor_entry: one of kmut_payment_stopped, kmut_rejected, pmkisan_stopped, pension_rejected, or null.
5. doctor_answer: "yes", "no", "dont_know", or null.
6. reason: one short English sentence explaining why you chose these actions.
7. ack: ONE short, warm sentence in the user's language (Tamil if they wrote Tamil). Never say anyone is
   eligible or not eligible; the rules engine decides that. No promises.
8. Never output Aadhaar numbers, bank account numbers or OTPs, even if the user typed them.
9. language: "ta" or "en".
10. PATH FORMAT (exact): "family.<field>" or "member:<id>.<field>"  e.g. "family.annual_income",
    "member:m2.age", "member:m3.docs.aadhaar". Colon only after "member", a dot before the field.
11. Output ONLY facts stated in THIS message. Do not repeat facts already on the family card unless the
    user changed them.
12. MAPPING HINTS (Tamil / English → facts):
    - Relations: கணவர் / வீட்டுக்காரர் / husband → spouse, male · மனைவி / wife → spouse, female ·
      மகள் / daughter → daughter, female · மகன் / பையன் / son → son, male · அம்மா → mother, female ·
      அப்பா → father, male. The speaker is "self"; if the speaker mentions "my husband", the speaker is
      female and married; "my wife" → speaker male and married. Husband and wife → set spouse_of both ways.
    - Land: any acres of land → owns_cultivable_land = true; நன்செய் / wet → wet_land_acres;
      புன்செய் / dry → dry_land_acres; "நிலம் இல்லை" / no land → owns_cultivable_land = false,
      wet_land_acres = 0, dry_land_acres = 0; "பட்டா என் பேர்ல" / patta in my name →
      land_in_own_name = true and land_owner_member_id = the speaker's id.
    - Anyone in the family with a government / PSU / bank / cooperative job or such a pension
      (அரசு வேலை / கவர்மெண்ட் வேலை) → govt_or_psu_or_bank_or_coop_employee_or_pensioner = true.
    - கார் / ஜீப் / டிராக்டர் / car / jeep / tractor → owns_four_wheeler_personal_use = true.
    - Husband died (இறந்துட்டார் / passed away) → the speaker's marital_status = "widowed".
      No children or relatives look after them (யாரும் பார்த்துக்கல / no one supports me) → is_destitute = true.
    - Scheme names: மகளிர் உரிமை / உரிமைத் தொகை / ₹1000 → KMUT · பிஎம்-கிசான் / PM-KISAN → PM-KISAN ·
      ஓய்வூதியம் / pension → pension. Rejected / நிராகரி → *_rejected; stopped / didn't come / வரல →
      *_payment_stopped (PM-KISAN → pmkisan_stopped).
13. NAMES: always write member names in English letters (transliterate), e.g. முருகன் → Murugan,
    செல்வி → Selvi, காவ்யா → Kavya. names_as_printed values must be copied exactly as the user typed them.

ALLOWED FACT PATHS
family: has_ration_card, ration_card_type (PHH | PHH-AAY | NPHH | NPHH-S | NPHH-NC), ration_card_head_member_id,
  land_owner_member_id, annual_income, electricity_units_per_year, owns_cultivable_land, land_in_own_name,
  land_acquired_after_2019_02_01_not_inherited, wet_land_acres, dry_land_acres, owns_four_wheeler_personal_use,
  income_tax_payer_last_year, professional_tax_payer, govt_or_psu_or_bank_or_coop_employee_or_pensioner,
  govt_pension_10000_or_more, elected_representative, registered_practising_professional, nri,
  gst_turnover_over_50_lakh, receives_social_security_pension
member:<id>: name, relation (self | spouse | daughter | son | mother | father | other), spouse_of, gender
  (female | male | transgender), age, marital_status (married | unmarried | widowed | divorced | deserted),
  studied_class_6_to_12_in (government | government_aided | rte_private_6_8_then_government_9_12 | private),
  current_education (ug | diploma | iti | professional_ug | pg | none), is_first_higher_ed_course,
  education_mode (regular | distance | open_university), is_destitute, immovable_property_value,
  has_own_bank_account, bank_aadhaar_seeded, bank_account_active, pmkisan_ekyc_done
member:<id>.docs.<doc_id>: true/false   (doc ids: aadhaar, patta_land_record, school_records_6_to_12,
  college_admission_proof, husband_death_certificate)
member:<id>.names_as_printed.<doc_id>: the name exactly as printed
```

### 1.2 User content (built by `llm.py` each turn)
```
FAMILY CARD (current): <compact JSON of facts, without names_as_printed>
OPEN TASKS: <task ids + one-line labels>
LAST QUESTION ASKED: <next_question.en>
DIAGNOSIS IN PROGRESS: <entry id + current question, or "none">
USER MESSAGE: <text after the PII guard>
```

### 1.3 Few-shot examples (include all three)
*(In Example 1 every fact also carries `"evidence"`, e.g. `"evidence":"எனக்கு 52 வயசு"` for `member:m1.age`, and the object has `"unclear":[]`. It's abbreviated below for readability; write it in full in `llm.py`.)*

**Example 1: family intro (Tamil)**
User: `எங்க வீட்ல நான் முருகன், என் மனைவி செல்வி, மகள் காவ்யா — மூணு பேர் இருக்கோம். எனக்கு 52 வயசு, செல்விக்கு 47, காவ்யாவுக்கு 18.`
```json
{"language":"ta",
 "facts":[{"path":"member:m1.name","value":"Murugan"},{"path":"member:m1.relation","value":"self"},{"path":"member:m1.gender","value":"male"},{"path":"member:m1.age","value":52},{"path":"member:m1.marital_status","value":"married"},{"path":"member:m1.spouse_of","value":"m2"},
          {"path":"member:m2.name","value":"Selvi"},{"path":"member:m2.relation","value":"spouse"},{"path":"member:m2.gender","value":"female"},{"path":"member:m2.age","value":47},{"path":"member:m2.marital_status","value":"married"},{"path":"member:m2.spouse_of","value":"m1"},
          {"path":"member:m3.name","value":"Kavya"},{"path":"member:m3.relation","value":"daughter"},{"path":"member:m3.gender","value":"female"},{"path":"member:m3.age","value":18},{"path":"member:m3.marital_status","value":"unmarried"}],
 "actions":["update_facts"],"reason":"User described the household members and ages",
 "doctor_entry":null,"doctor_answer":null,"task_done":null,"escalate_reason":null,
 "ack":"நன்றி! உங்கள் குடும்ப விவரங்களைக் குறித்துக்கொண்டேன்."}
```
**Example 2: correction + negations (Tamil)**
User: `இல்லங்க, வருமானம் 90,000 இல்ல, 3 லட்சம். அப்புறம் செல்வி கணக்குல ஆதார் இணைக்கல. காவ்யாவுக்கு தனி வங்கிக் கணக்கே இல்ல.`
```json
{"language":"ta",
 "facts":[{"path":"family.annual_income","value":300000,"evidence":"3 லட்சம்"},
          {"path":"member:m2.bank_aadhaar_seeded","value":false,"evidence":"செல்வி கணக்குல ஆதார் இணைக்கல"},
          {"path":"member:m3.has_own_bank_account","value":false,"evidence":"காவ்யாவுக்கு தனி வங்கிக் கணக்கே இல்ல"}],
 "unclear":[],
 "actions":["update_facts","explain"],"reason":"User corrected the income and gave bank details",
 "doctor_entry":null,"doctor_answer":null,"task_done":null,"escalate_reason":null,
 "ack":"சரி, வருமானத்தை ₹3 லட்சமாக மாற்றினேன்."}
```
**Example 3: payment stopped (Tamil)**
User: `எனக்கு வந்துகிட்டு இருந்த 1000 ரூபாய் மூணு மாசமா வரல.`
```json
{"language":"ta","facts":[],"unclear":[],
 "actions":["start_doctor"],"reason":"User reports that the Magalir Urimai payment stopped",
 "doctor_entry":"kmut_payment_stopped","doctor_answer":null,"task_done":null,"escalate_reason":null,
 "ack":"கவலைப்படாதீர்கள், காரணத்தைக் கண்டுபிடிப்போம்."}
```

### 1.4 Reply composition (in code, verified text; no AI)
| Part | Tamil | English |
|---|---|---|
| New eligible scheme | `✅ {name_ta} — {benefit_ta}` | `✅ {name_en} — {benefit_en}` |
| Lost eligibility | `❌ {name_ta}: {reason_ta}` | `❌ {name_en}: {reason_en}` |
| Total | `மொத்தம்: ஆண்டுக்கு சுமார் ₹{total}` | `Total: about ₹{total} a year` |
| Trips | `அலுவலகப் பயணங்கள்: {without} → {with}` | `Office trips: {without} → {with}` |
| Next question | `அடுத்து: {question_ta}` | `Next: {question_en}` |
| Offline mode | `இணைய இணைப்பு இல்லை — கேள்விகளை நேரடியாகத் தொடர்கிறேன்.` | `Offline — continuing with direct questions.` |

---

## 2. Agent panel wording (events)
| Event | Example (EN) | Example (TA) |
|---|---|---|
| 🎯 goal | Get this family every benefit they're owed, with the fewest trips | இந்தக் குடும்பத்திற்கு உரிய அனைத்து நலன்களையும் குறைந்த பயணங்களில் பெற்றுத் தருதல் |
| 📋 plan | Learn the family → Check schemes → Check documents → Plan trips → Prepare packs | குடும்பம் → திட்டங்கள் → ஆவணங்கள் → பயணங்கள் → விண்ணப்பங்கள் |
| 🧠 decided | Decided: update_facts → explain — "User corrected the income" (Qwen · 0.6 s) | முடிவு: update_facts → explain |
| 🔒 privacy | Privacy: removed a number before sending to the AI | தனியுரிமை: AI-க்கு அனுப்பும் முன் ஒரு எண் நீக்கப்பட்டது |
| ⚠️ fallback | Backup: Gemini answered · Offline mode | மாற்று: Gemini பதிலளித்தது · இணையமில்லா முறை |
| 🤖 autonomous (S1) | 15 days later: reminder sent: "Selvi — link Aadhaar at the bank" | 15 நாட்களுக்குப் பிறகு: நினைவூட்டல் அனுப்பப்பட்டது |

---

## 3. Letter templates (Tamil + English; DRAFT until a helper approves)

### 3.1 Application Pack (one section per counted scheme)
```
THUNAI — APPLICATION PACK / விண்ணப்பத் தொகுப்பு                               [DRAFT / வரைவு]
Family: {head_name}, {district} · Prepared: {date}
For each scheme:
  {name_ta} / {name_en}
  Applicant / விண்ணப்பதாரர்: {member_name}, {age}
  Benefit / நன்மை: {benefit_ta} / {benefit_en}
  Why likely eligible / தகுதிக்கான காரணம்: {reasons_ta} / {reasons_en}  (source: {source_url})
  Documents to carry / எடுத்துச் செல்ல வேண்டிய ஆவணங்கள்: ☐ {doc_ta} / {doc_en} …
  Where & how to apply / எங்கு, எப்படி: {how_to_apply_ta} / {how_to_apply_en}
  Before you go / செல்லும் முன்: {open fix tasks for this scheme}
Footer: "This pack helps you prepare. The department makes the final decision. Never share OTPs.
         இது தயாராக உதவும் தொகுப்பு மட்டுமே; இறுதி முடிவு துறையினுடையது. OTP-ஐ யாரிடமும் பகிர வேண்டாம்."
```

### 3.2 KMUT appeal (`appeal_kmut`): to the RDO through e-Sevai, within 30 days of the rejection SMS
**Tamil:**
```
பெறுநர்:
வருவாய் கோட்ட அலுவலர் அவர்கள்,
{revenue_division} வருவாய் கோட்டம்.
(இ-சேவை மையம் வழியாக)

அனுப்புநர்:
{member_name}, க/பெ {husband_name},
{address_line}, {district}.

பொருள்: கலைஞர் மகளிர் உரிமைத் தொகை — விண்ணப்ப நிராகரிப்புக்கு எதிரான மேல்முறையீடு.
பார்வை: நிராகரிப்பு குறுஞ்செய்தி நாள் {sms_date}.

ஐயா / அம்மா,
நான் எனது குடும்ப அட்டையில் குடும்பத் தலைவியாக உள்ளேன். எனது விண்ணப்பம் "{rejection_reason}" என்ற காரணத்தால்
நிராகரிக்கப்பட்டது. ஆனால் எனது குடும்பம் திட்ட விதிமுறைகளைப் பூர்த்தி செய்கிறது:
  • {met_rule_1_ta}
  • {met_rule_2_ta}
இதற்கான ஆதார ஆவணங்களை இணைத்துள்ளேன். எனது விண்ணப்பத்தை மறுபரிசீலனை செய்து உரிமைத் தொகை வழங்குமாறு
பணிவுடன் கேட்டுக்கொள்கிறேன்.

இணைப்புகள்: {documents_list_ta}

இடம்: {place}                                                      இப்படிக்கு,
நாள்: {date}                                                        {member_name}
```
**English (same structure):** To: The Revenue Divisional Officer, {revenue_division} (through e-Sevai centre) · Subject: Appeal against rejection of Kalaignar Magalir Urimai Thogai application · Ref: rejection SMS dated {sms_date} · Body: head of family on the ration card; rejected for "{rejection_reason}"; the family meets the rules (bullets); documents enclosed; request reconsideration · Enclosures · Place, date, signature.

### 3.3 Pension petition (`appeal_pension`): to the Special Tahsildar (Social Security Scheme)
**Tamil:**
```
பெறுநர்:
தனி வட்டாட்சியர் அவர்கள் (சமூகப் பாதுகாப்புத் திட்டம்),
{taluk} வட்டம்.

அனுப்புநர்:
{member_name}, {age} வயது,
{address_line}, {district}.

பொருள்: ஆதரவற்ற விதவையர் ஓய்வூதியம் — நிராகரிக்கப்பட்ட விண்ணப்பத்தை மறுபரிசீலனை செய்யக் கோருதல்.

ஐயா / அம்மா,
நான் கணவரை இழந்த, ஆதரவற்ற {age} வயது பெண். எனது ஓய்வூதிய விண்ணப்பம் "{rejection_reason}" என்ற காரணத்தால்
நிராகரிக்கப்பட்டது. தேவையான {missing_document_ta} தற்போது இணைத்துள்ளேன். எனது விண்ணப்பத்தை மறுபரிசீலனை
செய்து ஓய்வூதியம் வழங்குமாறு பணிவுடன் கேட்டுக்கொள்கிறேன்.

இணைப்புகள்: {documents_list_ta}

இடம்: {place}                                                      இப்படிக்கு,
நாள்: {date}                                                        {member_name}
```
**English:** To: The Special Tahsildar (Social Security Scheme), {taluk} Taluk · Subject: Request to reconsider rejected Destitute Widow Pension application · Body: widow, destitute, {age}; rejected for "{rejection_reason}"; {missing_document_en} now enclosed; request reconsideration · Enclosures · Place, date, signature.

### 3.4 More letters (v2, same rules)
| Kind | To | Purpose | Offered when |
|---|---|---|---|
| `bank_seeding_request` | Branch Manager, ________ Bank | Link (seed) Aadhaar to the savings account for DBT (NPCI mapper); reactivate if inactive; ask for an acknowledgement | A member's account isn't linked or is inactive, or the Doctor finds a bank linking cause |
| `name_correction_request` | The office that issued the document (ration card: Taluk Supply Officer; passbook: bank; patta: Tahsildar; school / college; death certificate: Registrar of Births and Deaths) | Correct the printed name to match Aadhaar | A document's name differs from Aadhaar |
| `grievance` | KMUT grievance cell (portal / CM Helpline 1100) | Benefit not received; request status check and release | Doctor outcome "cause not clear" |

Each letter is in Tamil and then English, polite and simple, with no AI-written text, so names and numbers are always exact.

### 3.5 Letter rules
- Placeholders not known → leave a blank line `________` (never invent data). Account and Aadhaar numbers are **always** blank, written by hand.
- Footer on every letter: "Prepared with Thunai · Draft reviewed by helper: {helper_name or ________}".
- DRAFT watermark until approved; Print button only after approval.
- Only letters the agent suggests for this family can be drafted (the API refuses others).

---

## 4. Evaluation 1 script (≤ 5 min): "It understands and decides"
| Time | Who | Say / do |
|---|---|---|
| 0:00 | Teammate 1 | "Meena from Villupuram got ₹1,000 every month from Magalir Urimai. Three months ago it stopped. Nobody told her why. She lost two days' wages going to offices." |
| 0:20 | Teammate 1 | "In July 2024, 1.48 lakh women who had been rejected for Magalir Urimai started receiving it after appealing (DT Next). How many never appealed? Eligible families lose money to fixable paperwork." (+ real-user quote if collected) |
| 0:45 | You | "Thunai is an agent for Tamil Nadu families. Rules decide, AI understands, humans approve." Click **Load Murugan family** (or type 2 Tamil lines live). |
| 1:00 | You | Point at the **agent panel**: "The AI decided to update the facts. Then the rules engine checked every scheme (8 today), using official rules with sources." |
| 1:45 | You | "3 schemes, about **₹30,000 a year** for this family." Open one card: rule + source + checked date. |
| 2:15 | You | **Live correction:** type "இல்லங்க, வருமானம் 3 லட்சம்" (or edit the card) → panel shows 🔁 **re-plan** → "Magalir Urimai no longer applies: ₹18,000." |
| 3:00 | You | Type "my Aadhaar is 1234 5678 9012" → 🔒 "The number is removed before it ever reaches the AI." |
| 3:20 | You | "Eligibility is never decided by the AI. It's tested rules from official pages: PM-KISAN guidelines, the KMUT FAQ, TN Revenue Administration." |
| 3:45 | Teammate 2 | "After lunch: documents, the name-mismatch matrix, trips saved, the Rejection Doctor for Meena, and appeal letters a helper approves." |
| 4:15 | All | Questions |

## 5. Evaluation 2 script (6–7 min): "It fixes and follows through"
| Time | Who | Say / do |
|---|---|---|
| 0:00 | Teammate 1 | "In the morning you saw Thunai **find** schemes. Now: **fix** the problems that get families rejected, and **follow** until the money arrives." |
| 0:20 | You | **Login** with phone + PIN → "Previous conversations" → reopen Murugan's chat. "The family can come back any day; nothing is lost." *(Remember)* |
| 0:50 | You | Click **Revathi (sample documents)**: "These are sample cards, no real IDs. Aadhaar says *Revathi Sekar*, the ration card says *S. Revathi*, the passbook *REVATHI S*. Her husband's death certificate is missing and her Aadhaar isn't linked to the bank." |
| 1:30 | You | **Fix tab:** name check shows the conflict → plan by office: "The passbook name fix happens **in the same bank visit** as the Aadhaar linking. Visits: **4 → 3**." Tick a task → the activity log shows **Re-plan: Completed**. |
| 2:15 | You | **Letters:** "Draft the name correction letter" → DRAFT preview (Tamil + English, account numbers left blank) → **Helper tab**: helper approves → **Print**. "A human always approves." |
| 3:00 | You | **Meena:** "My ₹1,000 stopped" → 2 questions → "Most likely her Aadhaar is linked to an old account. Check it in 1 minute on myAadhaar." The bank visit joins her plan; the bank letter is suggested. |
| 3:45 | You | **"15 days later":** the agent, **on its own**, reminds about open tasks, warns about the appeal deadline, escalates a stuck task to the helper → **SMS outbox** shows the Tamil summary → **Share on WhatsApp**. |
| 4:30 | You | **Voice:** speak a Tamil sentence → it understands → the reply is spoken in Tamil. |
| 5:00 | Teammate 2 | **How it's different** + **architecture:** "Rules decide, two AIs understand and must agree, a human approves. Letters come from templates, so no invented names or numbers." |
| 5:45 | Teammate 1 | Close: "**Find. Fix. Follow.** Pilot plan: NSS volunteers take Thunai to adopted villages." |

**Backup paths:**
- Login fails → use the demo buttons (guest).
- Voice fails → type.
- AI down → demo families load instantly.

## 6. Judge Q&A (who answers)
| Question | Answer | Who |
|---|---|---|
| Where's the agent? | Panel: goal → plan → AI chooses actions with a reason → tools → re-plan on any change; human approval for letters | You |
| Isn't this myScheme? | myScheme matches; Thunai prevents rejection (names, bank linking, eKYC), diagnoses stopped payments, prepares packs and appeals, for the whole family, in Tamil | Teammate 2 |
| What if the AI is wrong? | It never decides eligibility. Wrong facts show on the card and are corrected in one tap; code guards drop anything outside the schema | You |
| How are rules kept up to date? | Each scheme is a data file with source + checked date; a helper can update it; next: AI drafts updates from new government orders, a human verifies | Teammate 2 |
| How do you count trips? | One application visit per scheme + one per problem found at the counter, versus distinct offices in our grouped plan; shown openly | You |
| Is "M. Kavya" really rejected? | It's a risk flag, not a rejection; name mismatches are an officially noted cause of payment failure, and fixing them early is cheap | You |
| Privacy? | No Aadhaar/bank/OTP asked; numbers stripped before the AI; login stores only phone + hashed PIN + family facts; one-tap delete; guest mode; production would use a paid or government-hosted model | Teammate 2 |
| Does it really send SMS? | It prepares each message in an outbox, ready for an SMS provider; WhatsApp share works today. Real SMS needs a paid, DLT-registered sender. | You |
| Why a PIN, not an OTP? | Real OTP SMS costs money, and we tell people never to share an OTP. Production: the government SMS gateway. | You |
| Are those real documents? | No: sample cards marked SAMPLE, with no numbers. Thunai never reads or stores real IDs. | Teammate 1 |
| Who writes the letters, the AI? | No: fixed templates filled from the family's facts, so names and numbers are exact. Unknown details stay blank. A helper approves. | You |
| Will an illiterate farmer use it? | They don't need to: their daughter or an NSS / e-Sevai helper runs it in Tamil | Teammate 1 |
| Why free AI models? | Cost ₹0 and three providers in a chain; it falls back offline. The AI is isolated in one file, so it's easy to swap | You |
| Does it apply for me? | It prepares the pack and letters; the family or helper submits on the official site. Roadmap: an RPA robot fills the e-Sevai form from the approved pack, still stopping before Submit. | You |
| What doesn't it solve? | The family still visits the office, prepared; the department decides; it can't see government records; SMS is an outbox; the prototype covers only officially verified schemes | Teammate 1 |

## 7. Slides (Teammate 2, 5 slides)
1. **The problem:** Meena's story · 1.48 lakh paid only after appealing (DT Next, Jul 2024) · 2.14 crore PM-KISAN eKYCs pending (Rajya Sabha reply, Jul 2023)
2. **How it's different:** table: myScheme · Jugalbandi · Kisan e-Mitra · Thunai (prevent · diagnose · prepare · follow up · whole family · Tamil)
3. **How it works:** Find → Fix → Follow; "Rules decide · AI understands · humans approve"
4. **Architecture:** agent loop (perceive → decide → act → re-plan) · rules engine · 3-provider AI chain · privacy guard · helper approval
5. **Follow + impact:** login and history · SMS outbox + WhatsApp · "15 days later" follow-up · new-scheme alerts · ₹30,000/year + 6 → 2 visits for one family · roadmap: NSS pilot, real SMS gateway, RPA form filling, more verified schemes
