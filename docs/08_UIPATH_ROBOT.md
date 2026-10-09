# UiPath Robot Spec — "e-Sevai Form Filler" 🤖

**Built by:** one teammate in **UiPath Studio (Community)**, in parallel with the main build · **Demo:** Eval 2
**Story for the jury:** *"The AI agent decides, the UiPath robot does the paperwork, and a human approves."*

## 1. How it fits Thunai
```
Thunai: helper approves the Application Pack (Helper tab)
   └─► Thunai writes  handoff/application.json        (backend, B4: ~10 min)
        └─► 🤖 UiPath robot (teammate runs it from Studio / UiPath Assistant)
              1. Read application.json
              2. Open the mock e-Sevai form in Chrome
              3. Type each field, one by one (visible on screen)
              4. Tick the declaration, highlight "Submit"; does NOT click it
              5. Write handoff/robot_result.json  {"status": "filled", "filled_at": "..."}
   └─► Thunai shows 🤖 "UiPath robot filled the e-Sevai form; waiting for the human to submit" in the agent panel
```
The robot **never submits**. A human always clicks Submit (responsible AI, same principle as letters).

## 2. Files and locations (same laptop)
| File | Written by | Path |
|---|---|---|
| `application.json` | Thunai (backend) | `scheme-sathi/handoff/application.json` |
| `mock_esevai.html` | Thunai build (main session) | `scheme-sathi/static/mock_esevai.html`, opened as `http://localhost:8000/mock_esevai.html` |
| `robot_result.json` | UiPath robot | `scheme-sathi/handoff/robot_result.json` |
| UiPath project | Teammate | anywhere, e.g. `Documents/UiPath/ThunaiEsevaiFiller` |

If the robot runs on a **different laptop**, copy `application.json` over (USB or a shared folder) and open the form from the main laptop's IP address.

## 3. `application.json`: exact keys (flat, simple strings)
```json
{
  "scheme": "Kalaignar Magalir Urimai Thogai",
  "applicant_name": "Selvi",
  "applicant_name_as_on_aadhaar": "Selvi M",
  "age": "47",
  "gender": "Female",
  "relation_to_head": "Wife of head of family",
  "head_of_family": "Murugan",
  "district": "Villupuram",
  "ration_card_type": "PHH",
  "annual_income": "90000",
  "wet_land_acres": "0",
  "dry_land_acres": "1.5",
  "electricity_units_per_year": "1200",
  "bank_aadhaar_seeded": "Yes",
  "documents": "Aadhaar; Ration card; Bank passbook",
  "prepared_by": "Thunai",
  "approved_by_helper": "Yes"
}
```
No Aadhaar number, bank account number or phone number is ever included (privacy rule).

## 4. Mock e-Sevai form: field ids (made easy to automate)
Every input has a stable `id` **and** a matching `name`, plus a visible label:
| Label | Element | id |
|---|---|---|
| Applicant name | text input | `applicant_name` |
| Name as on Aadhaar | text input | `name_as_on_aadhaar` |
| Age | number input | `age` |
| Gender | `<select>` (Female / Male / Transgender) | `gender` |
| Relation to head of family | text input | `relation_to_head` |
| Head of family | text input | `head_of_family` |
| District | `<select>` (Tamil Nadu districts) | `district` |
| Ration card type | `<select>` (PHH / PHH-AAY / NPHH / NPHH-S / NPHH-NC) | `ration_card_type` |
| Annual family income (₹) | number input | `annual_income` |
| Wet land (acres) | number input | `wet_land_acres` |
| Dry land (acres) | number input | `dry_land_acres` |
| Electricity units per year | number input | `electricity_units_per_year` |
| Bank account linked with Aadhaar | `<select>` (Yes / No) | `bank_aadhaar_seeded` |
| Documents enclosed | textarea | `documents` |
| Declaration | checkbox | `declaration` |
| Submit | button (disabled styling until the declaration is ticked) | `submit_btn` |

The page title is **"e-Sevai (Demo) — Kalaignar Magalir Urimai Thogai Application"**, with a clear "DEMO, NOT A GOVERNMENT SITE" banner.

## 5. UiPath workflow (Studio, Modern design): ~10 activities
1. **Read Text File** → `scheme-sathi\handoff\application.json` → `jsonText`
2. **Deserialize JSON** → `app` (JObject)
3. **Use Application/Browser** → Chrome → `http://localhost:8000/mock_esevai.html`
4. **Type Into** `applicant_name` ← `app("applicant_name").ToString`
5. **Type Into** for each text/number field (name_as_on_aadhaar, age, relation_to_head, head_of_family, annual_income, wet_land_acres, dry_land_acres, electricity_units_per_year, documents)
6. **Select Item** for each dropdown (gender, district, ration_card_type, bank_aadhaar_seeded)
7. **Check/Uncheck** → `declaration` (Check)
8. **Highlight** → `submit_btn` (3 s), and **do not click it**
9. **Write Text File** → `handoff\robot_result.json` ← `{"status":"filled","filled_at":"<Now>"}`
10. **Message Box** → "Form filled by UiPath robot. Please review and submit."

Tip: add a **Delay of 0.3–0.5 s** between Type Into activities so judges can watch each field fill.

## 6. Teammate timeline (parallel)
| Time | Task |
|---|---|
| Before 9:00 | UiPath account + Studio installed + Chrome extension + "Hello" test |
| 09:15–10:00 | Build the workflow against a **hand-made copy** of `application.json` (§3) and a quick local copy of the form (or wait for the main build's `mock_esevai.html`) |
| ~12:40 | Main build provides the real `mock_esevai.html` + `application.json` (B4); switch the robot to them |
| 13:00–13:55 | Test end to end with Thunai; record a backup video of the robot filling the form |
| Eval 2 | Teammate runs the robot live and explains it |

## 7. Fallbacks
| Problem | Fallback |
|---|---|
| Studio not installed / no UiPath knowledge | Playwright robot (S5) with the same form and JSON |
| Selector errors | Use the `id` attributes (§4); re-indicate the element |
| Robot not ready by Eval 2 | Show the backup video, or say "next step: UiPath robot" and show `application.json` |
