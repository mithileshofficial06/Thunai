# Stage 2: Scheme Data — FINAL ✅ 🔒 LOCKED (9 Oct 2026)

> Locked. Data changes only if an official source contradicts it; after any change, re-run `python -I tools/verify_data.py data` (must stay ALL PASS).

**Completed:** 9 Oct 2026 · **Tests:** 31 / 31 pass (`python -I tools/verify_data.py data`) · **Cross-references:** all resolve (`python -I tools/check_links.py data`)

## 1. Files
| File | What it holds |
|---|---|
| `data/schemes.json` | Rules for 5 enabled schemes (+2 disabled): eligibility, exclusions, need-info flags, derived facts (KMUT head of family, mixed land), benefit amounts, total rules (exclusive groups, conflicts), how to apply, appeal, sources, verification status |
| `data/documents.json` | Offices (with trip/online flag), documents (+ where to get each), `doc_fact_map`, tasks (PM-KISAN eKYC), **name-check algorithm + 6 test cases**, **trips algorithm** |
| `data/doctor_tree.json` | 4 Rejection Doctor trees: KMUT payment stopped, KMUT rejected, PM-KISAN instalment stopped, pension rejected |
| `data/questions.json` | Question bank (Tamil + English) in ask order; every rule field is covered by a question or derived |
| `data/personas.json` | Murugan family, Meena, Lakshmi Paati: Tamil + English scripted answers ("Load Murugan family" button), final facts, expected results |
| `tools/verify_data.py` | Reference implementation of every algorithm, used to test the data (verdicts, totals, derived facts, name check, trips, doctor paths, edge cases, question coverage) |
| `tools/check_links.py` | Checks every document / office / task / letter / tree reference |

> If pre-written code isn't allowed at the event, the two scripts were only used to validate the data tonight. The data files and docs are design artefacts.

## 2. Verification status (all official except where noted)
| Scheme | Status | Official source | Confirmed |
|---|---|---|---|
| **PM-KISAN** | ✅ Official | Revised Operational Guidelines (PDF) + portal | ₹6,000/yr DBT; family = husband, wife, minor children owning cultivable land; name in land records; exclusions 4.1 (a)–(c); cut-off 01-02-2019; eKYC mandatory |
| **Magalir Urimai (KMUT)** | ✅ Official | kmut.tn.gov.in FAQ (Tamil) | Head-of-family rule; 21+; income < ₹2.5L; < 5 ac wet / < 10 ac dry; < 3,600 units; 8 exclusion categories incl. **families already on a social-security pension**; documents (Aadhaar, ration card, Aadhaar-linked account; **no income certificate**); **appeal within 30 days via e-Sevai to the RDO**; payment-failure causes; application windows; call centre 1913 |
| **Pudhumai Penn** | ✅ Official | TN Social Welfare Dept scheme page | Govt school Classes 6–12; ₹1,000/month DBT until first UG / diploma / ITI is completed; with other scholarships; any number of girls per family; **student applies herself on the Penkalvi portal**; college certifies status every 6 months; zero-balance accounts (Indian Bank, Canara, IOB, SBI). *Aided / RTE route and distance-mode exclusion: news / secondary → shown as NEED_INFO* |
| **Destitute Widow Pension** | ✅ Official | cra.tn.gov.in (Tamil) | Destitute widow 18+; property ≤ ₹1 lakh (free govt house not counted); ₹1,200/month since Aug 2023; tnesevai; decided in 30 days; Special Tahsildar (SSS); DBT since Sept 2024 |
| **Old Age Pension (IGNOAPS)** | ✅ Official | cra.tn.gov.in | Destitute, BPL, 60+; ₹1,200 (central 200 + state 1,000 for ages 60–79; 500 + 700 for 80+) |
| Tamil Pudhalvan, CMCHIS | ❌ Disabled | — | Not verified → `enabled: false` |

**Labelled approximations (shown in the UI):** ration-card type (PHH / AAY) as the BPL indicator; "destitute" = final assessment by Revenue officials; mixed wet + dry land → NEED_INFO; pension grievance office → "confirm locally".

## 3. Fixes made in this final pass
1. **"Rules decide" leak closed:** the KMUT head of family is now a **derived fact computed by the rules engine** from the ration-card head and spouse link (official FAQ 21), never by the LLM.
2. **Question bank added** (`questions.json`): 15 questions in Tamil and English, in order, with conditions; a test confirms every rule field is covered.
3. **Relevance hacks removed:** Pudhumai Penn now filters on *is she in higher education* (asked by the question bank); the old-age pension filters on the official 60+ rule.
4. **Pudhumai Penn verified officially** (Social Welfare Dept page). This corrected the application route to **online by the student on Penkalvi**, which changed the demo trips to **6 → 2**.
5. **Pension grievance route** tied to mechanisms listed on the official CRA site (Special Tahsildar for pensions, people's grievance day); exact office → "confirm locally".
6. **Name check specified and tested:** 6 cases, including initials (M. Kavya), spelling (Lakshmi / Laxmi), spacing (Senthil Kumar / Senthilkumar) and different names (Kavya / Kavitha).
7. **Trips algorithm made exact** and tested: counts only schemes in the ₹ total, merges tasks at the same office, and gives 0 visits for online applications.
8. **Tamil:** the persona name was corrected to காவ்யா (Kavya) and all strings self-reviewed.

## 4. Test results (verify_data.py)
| Group | Checks |
|---|---|
| Name check | 6 / 6 |
| Murugan family | KMUT head = Selvi · verdicts · **₹30,000** · names (Green, Green, Yellow) · **trips 6 → 2** · re-plan income ₹3L → KMUT ❌, **₹18,000**, trips 4 → 2 |
| Lakshmi Paati | KMUT head = Lakshmi · verdicts · **₹14,400** (one pension; KMUT conflict resolved) · name Yellow (Lakshmi / Laxmi) · Doctor path → fix document + petition |
| Meena | Doctor path → Aadhaar not linked to the active account |
| Edge cases (7) | unknown head · tractor · aided school · unknown income · mixed land · income tax · no wife linked |
| Coverage | every rule field has a question or is derived; ask_order covers all questions |

## 5. Still open (honestly)
- **Tamil strings:** self-reviewed; a native speaker's 5-minute read is still recommended.
- **Aided-school route for Pudhumai Penn:** news only, so it shows NEED_INFO by design.
- **Exact pension grievance office per district:** labelled "confirm locally".

## 6. Sources
- PM-KISAN Operational Guidelines: https://pmkisan.gov.in/Documents/RevisedPM-KISANOperationalGuidelines(English).pdf · Portal: https://pmkisan.gov.in/
- KMUT FAQ (official): https://kmut.tn.gov.in/faq.html
- Pudhumai Penn (TN Social Welfare Dept): https://www.tnsocialwelfare.tn.gov.in/en/specilisationswoman-welfare/pudhumai-penn
- TN social security pensions (CRA): https://www.cra.tn.gov.in/about_schemes_t.php · https://www.cra.tn.gov.in/eleg_schemes_t.php
- Aided-school extension (news): https://www.thenewsminute.com/amp/story/tamil-nadu/stalin-to-inaugurate-extension-of-pudhumai-penn-scheme-for-school-girls
- Pension hike to ₹1,200 (news, corroborates CRA): https://www.deccanherald.com/india/tamil-nadu-enhances-monthly-pension-for-elders-to-rs-1200-1239636.html
