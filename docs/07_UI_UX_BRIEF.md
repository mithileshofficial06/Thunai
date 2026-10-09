# UI/UX Design Brief — Thunai (துணை) 🔒 FINAL

**Chosen design: "Two faces".** Built **last in each phase**, on the finished backend: B3 (chat, family card, scheme cards, ₹, agent panel) and B5 (Fix, Doctor, Letters, Helper tabs).

**Why this design was chosen for Thunai:**
- **Users are families on phones, often an older parent with a daughter:** big Tamil text, calm cards, symbols plus words, no clutter.
- **Trust is the product:** teal (government-adjacent but friendly), official-source chips, DRAFT watermarks, "a helper approves".
- **Judges must see an agent, not a chatbot:** the dark agent panel shows every decision, tool and re-plan, and the re-plan moment is animated (glow, card flip, ₹ count-down).
- **Demo-ready:** 3 columns on the projector, `?present=1` large mode, works offline.
**One idea behind the whole design:** **two faces on one screen.**
- **The family side** (chat, family card, results, fix plan): *calm, warm, simple*. It's for a daughter helping her parents, in Tamil.
- **The agent side** (agent panel): *dark, precise, technical*. It's for the judges to **watch the agent think**.

The contrast itself tells the story: *"a gentle helper for the family, a serious agent underneath."*

---

## 1. Design principles
1. **Tamil first, simple words.** Tamil is the default; every label has an English twin (toggle). Short sentences.
2. **Never colour alone.** Every status has a symbol + word: ✅ தகுதி / Eligible · ❓ தகவல் தேவை / Need info · ❌ தகுதி இல்லை / Not eligible.
3. **Big and tappable.** Base text 18 px (16 px on phones), buttons ≥ 44 px tall: older users and the projector.
4. **Show change.** When something changes, *animate the change* (old value struck through → new value). That's how judges see re-planning.
5. **Trust signals everywhere.** Source link, "official · checked 9 Oct 2026", DRAFT watermark, "a helper approves".
6. **Calm, not busy.** White space, cards, one accent colour. No clutter, no stock illustrations.

---

## 2. Colours (CSS variables)
| Token | Hex | Use |
|---|---|---|
| `--brand` | `#0F766E` (deep teal) | Header, primary buttons, links: trust, government-adjacent but friendly |
| `--brand-soft` | `#CCFBF1` | Selected tab, chat bubble (user) |
| `--accent` | `#F59E0B` (marigold) | ₹ meter, highlights, re-plan glow: warm, Tamil-festive |
| `--ok` | `#16A34A` | ✅ eligible, 🟢 names match, Done |
| `--warn` | `#D97706` | ❓ need info, 🟡 name risk |
| `--bad` | `#DC2626` | ❌ not eligible, 🔴 conflict |
| `--bg` | `#FAFAF7` (warm off-white) | Family side background |
| `--card` | `#FFFFFF` | Cards |
| `--ink` | `#1F2937` | Main text |
| `--muted` | `#6B7280` | Secondary text, sources |
| `--agent-bg` | `#0F172A` (slate night) | Agent panel background |
| `--agent-ink` | `#E2E8F0` | Agent panel text |
| `--agent-replan` | `#FBBF24` | Re-plan line highlight in the panel |

Contrast: all text ≥ WCAG AA (4.5:1).

## 3. Typography (works offline)
- **Family side:** `font-family: "Nirmala UI", "Noto Sans Tamil", "Latha", system-ui, sans-serif;` (Nirmala UI ships with Windows and renders Tamil well).
- **Tamil line height 1.6** (Tamil glyphs are tall); English 1.5.
- **Agent panel:** `ui-monospace, "Cascadia Mono", Consolas, monospace` at 14–15 px. It reads as a "log", so it looks like the agent working.
- **Numbers** (₹, trips): 40–56 px, bold, tabular figures.

---

## 4. Layout
### Desktop / projector (≥ 1024 px): 3 columns
```
┌──────────────────────────── Top bar (teal) ─────────────────────────────┐
│ துணை Thunai · TA|EN · [Load Murugan] [Meena] [Lakshmi] · [⏩] · [Clear] │
├──────────────┬──────────────────────────────────┬────────────────────────┤
│ CHAT  (28%)  │ FAMILY + RESULTS (42%)           │ AGENT PANEL (30%, dark)│
│              │ ┌ ₹ meter ┐ ┌ trips 6 → 2 ┐      │ 🎯 GOAL                 │
│ bubbles      │ family card (member chips)       │ 📋 PLAN ✓ ✓ ◻ ◻ ◻       │
│              │ scheme cards                     │ 🧠 DECIDED …            │
│              │ tabs: Fix · Doctor · Letters ·   │ 🔧 TOOL …               │
│ [input] 🎤   │       Helper                     │ 🔁 RE-PLAN … (glow)     │
└──────────────┴──────────────────────────────────┴────────────────────────┘
```
### Phone (< 768 px): one column + bottom tab bar
- **Sticky top strip:** ₹ meter + trips (always visible).
- **Bottom tabs (5):** 💬 Chat · 👪 Family · ✅ Schemes · 🛠️ Fix · 🧠 Agent.
- Doctor / Letters / Helper sit inside the Fix and Schemes tabs as sections.

### Presentation mode
`?present=1` in the URL → base font 20 px, agent panel 16 px, hides the sidebar chrome. Use it on the projector.

---

## 5. Components
| Component | Design |
|---|---|
| **Top bar** | Teal background, white "துணை Thunai" wordmark (Tamil larger), TA/EN pill toggle, persona buttons as white outline pills |
| **Consent banner** | First visit only; soft teal card above the chat; text from architecture §10; one button "சரி, தொடங்குவோம் / OK, let's start" |
| **Chat bubbles** | Agent: white card, left, small teal "துணை" label. User: `--brand-soft`, right. Next question shown **bold** at the end of the agent's reply |
| **Family card** | Row of **member chips**: circle with initial + name + relation + age (e.g. "செ · Selvi · மனைவி · 47"). Key facts below as small editable rows (income, land, ration card); tap → inline input → Save |
| **₹ meter** | Big marigold number counting up/down over 600 ms: "₹30,000 / ஆண்டு"; small "3 திட்டங்கள்" below |
| **Trips** | "🚌 6 → 2" with the 6 struck through; tooltip "how we count" |
| **Scheme card** | Left colour bar (ok/warn/bad) · badge (✅ தகுதி) · scheme name (TA big, EN small) · member name · benefit in bold · "ஏன்? / Why?" expandable list of rules with ✓ ✗ ? · footer chip "🔗 Official source · checked 9 Oct 2026" · conflict note as an amber box |
| **Agent panel** | Dark log; each event a line: icon + type tag + text; **new lines fade in 250 ms apart**; `decided` shows a grey "Qwen · 0.6 s" tag; **`replan` lines glow marigold for 2 s** and show `old → new` with the old value struck through |
| **Consistency Matrix** | Table: rows = people, columns = documents; cells show the printed name + a coloured dot (🟢🟡🔴); tapping a 🟡 shows "முதலெழுத்து / முழுப் பெயர் வேறுபாடு — நிராகரிப்பு அபாயம்" |
| **Fix plan** | One card per office with a big icon (🏦 / 🏢 / 📱), "unblocks 2 schemes" pill, task checklist (what to bring in grey); ticking a task → strike-through + green tick + a re-plan line in the panel |
| **Doctor** | 4 large entry buttons with icons; each question as a big card with **ஆம் / Yes**, **இல்லை / No**, **தெரியாது / Don't know** buttons (green / red / grey); outcome card: "Most likely cause" (bold), "Check in 1 minute" (link button), "Fix steps" (numbered) |
| **Letters** | Paper-style preview (white, shadow, A4 ratio) with a diagonal light-red **DRAFT / வரைவு** watermark; after approval the watermark disappears and a teal **Print** button appears |
| **Helper tab** | List of drafts: member, kind, the agent's reason, time; green **Approve** button; approved items get a ✓ "Approved by helper" stamp |
| **Toasts** | Small bottom-right: "🔒 Privacy: a number was removed", "⚠️ Backup AI answered", "Offline mode" |

---

## 6. Motion (small, meaningful)
| Moment | Animation | Why |
|---|---|---|
| Agent events | Fade-in one by one, 250 ms apart | Judges can follow the agent's steps |
| Re-plan | Marigold glow on the panel line + the changed scheme card flips (✅ → ❌) + the ₹ meter counts to the new value | **The key demo moment**: change must be visible |
| Task Done | Strike-through + green tick | Progress feels real |
| Verdict appears | Card slides up 8 px + fade | Calm, not flashy |
Respect `prefers-reduced-motion` (turn the animations off).

---

## 7. Key microcopy (Tamil / English)
| Place | Tamil | English |
|---|---|---|
| Chat placeholder | உங்கள் குடும்பத்தைப் பற்றிச் சொல்லுங்கள்… | Tell me about your family… |
| First agent message | வணக்கம்! உங்கள் வீட்டில் யார் யார் இருக்கிறார்கள்? | Hello! Who lives in your home? |
| ₹ label | ஆண்டுக்குக் கிடைக்கக்கூடியது | Could get per year |
| Trips label | அலுவலகப் பயணங்கள் | Office trips |
| Fix tab title | சரிசெய்ய வேண்டியவை | What to fix |
| Doctor tab title | பணம் வரவில்லையா? | Money stopped? |
| Helper approve | ஒப்புதல் அளி | Approve |
| Disclaimer (footer) | இறுதி முடிவு துறையினுடையது · OTP-ஐ யாரிடமும் பகிர வேண்டாம் | The department decides · Never share your OTP |

---

## 8. Accessibility & quality checklist
- [ ] Tamil default; TA/EN toggle switches **every** label
- [ ] No status shown by colour alone (symbol + word)
- [ ] Touch targets ≥ 44 px; base font 18 px desktop / 16 px phone
- [ ] Contrast ≥ 4.5:1 (check the marigold text on white → use `#B45309` for text, `#F59E0B` only for large numbers and glows)
- [ ] Works offline (local Tailwind, system fonts)
- [ ] Works at 360 px wide (cheap Android) and on the projector (`?present=1`)
- [ ] Keyboard: Enter sends a message; Tab reaches all buttons
- [ ] `prefers-reduced-motion` respected
