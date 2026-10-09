"""Letters: deterministic Tamil + English drafts filled from the family's facts (no AI).

Unknown details are left as a blank line (________) for the family to write by hand;
Thunai never invents data and never prints Aadhaar or bank account numbers.
Every letter stays a DRAFT (watermark, no Print) until a helper approves it.
"""
import datetime as dt
from html import escape

import config
from engine.data import DOCUMENTS, SCHEMES_BY_ID
from engine.documents import BANK_DOCS, name_check, office_info, relative_name

BLANK = "________"

KINDS = {
    "application_pack": ("Application pack", "விண்ணப்பத் தொகுப்பு"),
    "bank_seeding_request": ("Request to link Aadhaar with bank account", "வங்கிக் கணக்குடன் ஆதார் இணைப்புக் கோரிக்கை"),
    "name_correction_request": ("Request to correct name on a document", "ஆவணத்தில் பெயர் திருத்தக் கோரிக்கை"),
    "grievance": ("Complaint: benefit not received", "புகார்: உதவித்தொகை வரவில்லை"),
    "appeal_kmut": ("Appeal: Magalir Urimai Thogai rejection", "மேல்முறையீடு: மகளிர் உரிமைத் தொகை நிராகரிப்பு"),
    "appeal_pension": ("Petition: pension application rejected", "மனு: ஓய்வூதிய விண்ணப்ப நிராகரிப்பு"),
}

# Who corrects a name on each document (the name on Aadhaar is the reference).
CORRECTION_OFFICE = {
    "ration_card": ("The Taluk Supply Officer (Civil Supplies)", "வட்ட வழங்கல் அலுவலர் அவர்கள் (குடிமைப் பொருள் வழங்கல்)"),
    "bank_passbook": (f"The Branch Manager, {BLANK} Bank", f"கிளை மேலாளர் அவர்கள், {BLANK} வங்கி"),
    "patta_land_record": ("The Tahsildar", "வட்டாட்சியர் அவர்கள்"),
    "school_records_6_to_12": (f"The Headmaster, {BLANK} School", f"தலைமையாசிரியர் அவர்கள், {BLANK} பள்ளி"),
    "college_admission_proof": (f"The Principal, {BLANK} College", f"முதல்வர் அவர்கள், {BLANK} கல்லூரி"),
    "husband_death_certificate": ("The Registrar of Births and Deaths (Panchayat / Municipality)",
                                  "பிறப்பு இறப்பு பதிவாளர் அவர்கள் (ஊராட்சி / நகராட்சி)"),
}
# Schemes paid by DBT, used to name the purpose in the bank letter.
DBT_SCHEMES = ("kmut", "pm_kisan", "pudhumai_penn", "destitute_widow_pension", "old_age_pension")


def _e(value):
    return escape(str(value)) if value not in (None, "") else f'<span class="blank">{BLANK}</span>'


def _short(name):
    return name.split(" (")[0]


def _member(facts, member_id):
    return next((m for m in facts.get("members", []) if m.get("id") == member_id), None)


def _bank_problem(member):
    return bool(member and member.get("has_own_bank_account") is True
                and (member.get("bank_aadhaar_seeded") is False or member.get("bank_account_active") is False))


def _name_mismatches(member, members):
    """(doc_id, printed name, Aadhaar name) for each document whose name differs from Aadhaar."""
    printed = (member or {}).get("names_as_printed") or {}
    ref = printed.get("aadhaar")
    if not ref:
        return []
    rel = relative_name(member, members)
    return [(doc, name, ref) for doc, name in printed.items()
            if doc != "aadhaar" and name and doc in CORRECTION_OFFICE and name_check(name, ref, rel) != "GREEN"]


# ---------------------------------------------------------------- suggestions
def suggestions(facts, snapshot, doctor_step=None, case=None):
    """Letters that make sense for this family right now: [{kind, member_id, doc_id, en, ta, reason_en, reason_ta}]."""
    case = case or {}
    out = []
    members = facts.get("members", [])
    eligible = [v for v in snapshot.get("verdicts", []) if v["status"] == "ELIGIBLE"]

    if any(v["counted"] for v in eligible):
        n = len([v for v in eligible if v["counted"]])
        out.append(_sug("application_pack", None, None,
                        f"Eligible for {n} scheme(s); the pack lists documents, where to apply and the official links",
                        f"{n} திட்டங்களுக்குத் தகுதி; ஆவணங்கள், விண்ணப்பிக்கும் இடம், அதிகாரப்பூர்வ இணைப்புகள் அடங்கியது"))

    for m in members:
        if _bank_problem(m):
            out.append(_sug("bank_seeding_request", m["id"], None,
                            f"{m.get('name') or m['id']}: Aadhaar is not linked to an active bank account, so DBT payments cannot reach it",
                            f"{m.get('name') or m['id']}: செயலில் உள்ள வங்கிக் கணக்குடன் ஆதார் இணைக்கப்படவில்லை; அரசுப் பணம் வர முடியாது"))
        for doc, name, ref in _name_mismatches(m, members):
            d = DOCUMENTS[doc]
            out.append(_sug("name_correction_request", m["id"], doc,
                            f"{m.get('name') or m['id']}: name on {d['en']} ('{name}') differs from Aadhaar ('{ref}'); risk of rejection",
                            f"{m.get('name') or m['id']}: {d['ta']} பெயர் ('{name}') ஆதாரிலிருந்து ('{ref}') வேறுபடுகிறது; நிராகரிப்பு அபாயம்"))

    if doctor_step and doctor_step.get("kind") == "outcome" and doctor_step.get("draft_letter") in KINDS:
        kind = doctor_step["draft_letter"]
        mid = case.get("member_id")
        if not any(s["kind"] == kind and s["member_id"] == mid for s in out):
            out.append(_sug(kind, mid, None, f"Problem finder result: {doctor_step['cause_en']}",
                            f"சிக்கல் கண்டறிதல் முடிவு: {doctor_step['cause_ta']}"))
    return out


def _sug(kind, member_id, doc_id, reason_en, reason_ta):
    return {"kind": kind, "member_id": member_id, "doc_id": doc_id, "en": KINDS[kind][0], "ta": KINDS[kind][1],
            "reason_en": reason_en, "reason_ta": reason_ta}


def available_kinds():
    return list(KINDS)


# ------------------------------------------------------------------- render
def render(kind, facts, snapshot, member_id=None, doc_id=None, doctor_step=None, case=None, today=None):
    """{"title_en", "title_ta", "body_ta", "body_en"} for one letter (HTML fragments)."""
    if kind not in KINDS:
        raise ValueError(f"unknown letter kind: {kind}")
    case = case or {}
    today = today or dt.date.today()
    ctx = {
        "facts": facts, "snapshot": snapshot, "family": facts.get("family", {}), "members": facts.get("members", []),
        "member": _member(facts, member_id), "doc_id": doc_id, "step": doctor_step or {}, "case": case,
        "date": today.strftime("%d-%m-%Y"),
    }
    m = ctx["member"]
    ctx["name"] = (m or {}).get("name") or case.get("applicant_name")
    ctx["age"] = (m or {}).get("age")
    ctx["district"] = ctx["family"].get("district")
    body_ta, body_en = globals()[f"_{kind}"](ctx)
    return {"title_en": KINDS[kind][0], "title_ta": KINDS[kind][1], "body_ta": body_ta, "body_en": body_en}


def _head(to_lines, from_lines, subject, ref=None):
    ref_html = f"<p><strong>{ref[0]}</strong> {ref[1]}</p>" if ref else ""
    return (f"<p class='block'><strong>{to_lines[0]}</strong>\n{to_lines[1]}</p>"
            f"<p class='block'><strong>{from_lines[0]}</strong>\n{from_lines[1]}</p>"
            f"<p><strong>{subject[0]}</strong> {subject[1]}</p>{ref_html}")


def _sign(ctx, ta):
    place, sign = ("இடம்", "இப்படிக்கு,") if ta else ("Place", "Yours faithfully,")
    date = "நாள்" if ta else "Date"
    return (f"<div class='sign'><div>{place}: {_e(ctx['district'])}<br>{date}: {ctx['date']}</div>"
            f"<div>{sign}<br><br>{_e(ctx['name'])}</div></div>")


def _from(ctx, ta):
    who = _e(ctx["name"])
    age = f", {ctx['age']} {'வயது' if ta else 'years'}" if ctx["age"] else ""
    return f"{who}{age}\n{_e(None)} ({'முகவரி' if ta else 'address'}), {_e(ctx['district'])}"


def _encl(items):
    return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"


def _scheme_names(ctx, ta):
    """Names of DBT schemes this member is (or may be) eligible for."""
    m = ctx["member"]
    names = [_short(v["name_ta"] if ta else v["name_en"]) for v in ctx["snapshot"].get("verdicts", [])
             if v["scheme_id"] in DBT_SCHEMES and v["status"] != "NOT_ELIGIBLE"
             and (v["member_id"] == (m or {}).get("id"))]
    if not names and ctx["step"].get("tree", "").startswith("kmut"):
        names = [_short(SCHEMES_BY_ID["kmut"]["name_ta" if ta else "name_en"])]
    return ", ".join(names) if names else ("அரசுத் திட்டங்கள்" if ta else "government schemes")


# ----------------------------------------------------------- application pack
def _application_pack(ctx):
    snap = ctx["snapshot"]
    head = next((x for x in ctx["members"] if x.get("relation") == "self"), None)
    counted = [v for v in snap.get("verdicts", []) if v["status"] == "ELIGIBLE" and v["counted"]]
    tasks_by_scheme = {}
    for o in snap.get("plan", []):
        for t in o["tasks"]:
            if t.get("kind") != "apply" and not t["done"]:
                for sid in o["unblocks"]:
                    tasks_by_scheme.setdefault(sid, []).append((o, t))

    def section(v, ta):
        s = SCHEMES_BY_ID[v["scheme_id"]]
        m = _member(ctx["facts"], v["member_id"]) or {}
        reasons = "".join(f"<li>{escape(r['ta'] if ta else r['en'])}</li>" for r in v["reasons"] if r["ok"] is True)
        docs = "".join(f"<li>&#9744; {escape(DOCUMENTS[d]['ta' if ta else 'en'])}</li>" for d in s.get("required_documents", []))
        before = "".join(f"<li>{escape(o['office_ta' if ta else 'office_en'])}: {escape(t['member_name'])}, "
                         f"{escape(t['short_ta' if ta else 'short_en'])}</li>"
                         for o, t in tasks_by_scheme.get(v["scheme_id"], []) if t["member_name"] == v["member_name"])
        src = v.get("source_url") or (s.get("official_sources") or [None])[0]
        L = (("விண்ணப்பதாரர்", "நன்மை", "தகுதிக்கான காரணம்", "எடுத்துச் செல்ல வேண்டிய ஆவணங்கள்", "எங்கு, எப்படி",
              "செல்லும் முன் முடிக்க வேண்டியவை", "அதிகாரப்பூர்வ ஆதாரம்", "குறிப்பு")
             if ta else ("Applicant", "Benefit", "Why likely eligible", "Documents to carry", "Where and how to apply",
                         "Finish before you go", "Official source", "Note"))
        note = v.get("conflict_note")
        note_html = f"<p><strong>{L[7]}:</strong> {escape(note['ta' if ta else 'en'])}</p>" if isinstance(note, dict) else ""
        return (f"<div class='box'><h2>{escape(v['name_ta'] if ta else v['name_en'])}</h2>"
                f"<p><strong>{L[0]}:</strong> {_e(m.get('name'))}{', ' + str(m['age']) if m.get('age') else ''}</p>"
                f"<p><strong>{L[1]}:</strong> {escape(v['benefit_ta'] if ta else v['benefit_en'])}</p>"
                f"<p><strong>{L[2]}:</strong></p><ul>{reasons}</ul>"
                f"<p><strong>{L[3]}:</strong></p><ul>{docs}</ul>"
                f"<p><strong>{L[4]}:</strong> {escape(s.get('how_to_apply_ta' if ta else 'how_to_apply_en', ''))}</p>"
                + (f"<p><strong>{L[5]}:</strong></p><ul>{before}</ul>" if before else "")
                + note_html
                + (f"<p><strong>{L[6]}:</strong> {escape(src)}</p>" if src else "") + "</div>")

    def body(ta):
        title = "விண்ணப்பத் தொகுப்பு" if ta else "Application pack"
        fam = (f"குடும்பம்: {_e((head or {}).get('name'))}, {_e(ctx['district'])} · தயாரித்த நாள்: {ctx['date']}" if ta
               else f"Family: {_e((head or {}).get('name'))}, {_e(ctx['district'])} · Prepared: {ctx['date']}")
        total = snap.get("rupees_per_year", 0)
        summary = (f"<p>மொத்தம் மதிப்பிடப்பட்ட நன்மை: ஆண்டுக்கு சுமார் ₹{total:,}. "
                   f"அலுவலகப் பயணங்கள்: {snap['trips']['with']} ({snap['trips']['without']} க்குப் பதிலாக).</p>" if ta
                   else f"<p>Total estimated benefit: about ₹{total:,} a year. Office visits: {snap['trips']['with']} "
                        f"(instead of {snap['trips']['without']}).</p>")
        note = ("<p>இது தயாராக உதவும் தொகுப்பு மட்டுமே. இறுதி முடிவு துறையினுடையது. OTP-ஐ யாரிடமும் பகிர வேண்டாம்.</p>" if ta
                else "<p>This pack helps you prepare. The department makes the final decision. Never share an OTP with anyone.</p>")
        return f"<h1>{title}</h1><div class='meta'>{fam}</div>{summary}" + "".join(section(v, ta) for v in counted) + note

    return body(True), body(False)


# ------------------------------------------------------------- bank seeding
def _bank_seeding_request(ctx):
    def body(ta):
        schemes = _scheme_names(ctx, ta)
        if ta:
            return (_head(("பெறுநர்:", f"கிளை மேலாளர் அவர்கள்,\n{_e(None)} வங்கி, {_e(None)} கிளை."),
                          ("அனுப்புநர்:", _from(ctx, True)),
                          ("பொருள்:", "சேமிப்புக் கணக்குடன் ஆதார் எண்ணை இணைத்து (seeding) அரசு நேரடிப் பணப் பரிமாற்றம் (DBT) பெற வசதி செய்யக் கோருதல்."))
                    + "<p>ஐயா / அம்மா,</p>"
                    + f"<p>நான் உங்கள் கிளையில் சேமிப்புக் கணக்கு வைத்துள்ளேன் (கணக்கு எண்: {_e(None)}). "
                      f"{escape(schemes)} போன்ற அரசுத் திட்ட உதவித்தொகை எனது கணக்கில் நேரடியாக வர, "
                      "எனது ஆதார் எண்ணை இந்தக் கணக்குடன் இணைத்து, அரசுப் பணப் பரிமாற்றத்திற்கு (NPCI mapper) பதிவு செய்யுமாறு "
                      "பணிவுடன் கேட்டுக்கொள்கிறேன். கணக்கு செயலற்ற நிலையில் இருந்தால் அதையும் செயல்படுத்தித் தருமாறு வேண்டுகிறேன்.</p>"
                    + "<p>இணைப்பு முடிந்ததற்கான ஒப்புகைச் சீட்டு வழங்குமாறும் கேட்டுக்கொள்கிறேன்.</p>"
                    + "<p><strong>இணைப்புகள்:</strong></p>" + _encl(["ஆதார் அட்டை நகல் (சுய சான்றொப்பம்)", "வங்கிப் புத்தக முதல் பக்க நகல்"])
                    + _sign(ctx, True)
                    + "<p class='blank'>கணக்கு எண் மற்றும் ஆதார் எண்ணை நீங்களே கையால் எழுதவும்; துணை இவற்றைச் சேமிப்பதில்லை.</p>")
        return (_head(("To:", f"The Branch Manager,\n{_e(None)} Bank, {_e(None)} Branch."),
                      ("From:", _from(ctx, False)),
                      ("Subject:", "Request to link (seed) my Aadhaar with my savings account for government Direct Benefit Transfer (DBT)."))
                + "<p>Sir / Madam,</p>"
                + f"<p>I hold a savings account in your branch (account number: {_e(None)}). So that government benefits such as "
                  f"{escape(schemes)} can be credited directly, I request you to link my Aadhaar with this account and map it for "
                  "DBT payments (NPCI mapper). If the account is inactive, kindly reactivate it as well.</p>"
                + "<p>Kindly give me an acknowledgement once the linking is done.</p>"
                + "<p><strong>Enclosures:</strong></p>" + _encl(["Copy of Aadhaar card (self-attested)", "Copy of the first page of the passbook"])
                + _sign(ctx, False)
                + "<p class='blank'>Write the account number and Aadhaar number by hand; Thunai never stores them.</p>")

    return body(True), body(False)


# ----------------------------------------------------------- name correction
def _name_correction_request(ctx):
    m, doc = ctx["member"], ctx["doc_id"]
    match = next((x for x in _name_mismatches(m, ctx["members"]) if x[0] == doc), None)
    if not match:
        raise ValueError("no name difference found for this member and document")
    _, wrong, right = match
    office_en, office_ta = CORRECTION_OFFICE[doc]
    d = DOCUMENTS[doc]

    def body(ta):
        if ta:
            return (_head(("பெறுநர்:", f"{office_ta},\n{_e(ctx['district'])}."),
                          ("அனுப்புநர்:", _from(ctx, True)),
                          ("பொருள்:", f"{escape(d['ta'])} — பெயர் திருத்தம் கோருதல்."))
                    + "<p>ஐயா / அம்மா,</p>"
                    + f"<p>எனது {escape(d['ta'])} இல் எனது பெயர் <strong>\"{escape(wrong)}\"</strong> என அச்சிடப்பட்டுள்ளது. "
                      f"எனது ஆதார் அட்டையில் எனது பெயர் <strong>\"{escape(right)}\"</strong> என உள்ளது. இரண்டும் ஒரே நபரான என்னையே குறிக்கின்றன.</p>"
                    + "<p>பெயர் வேறுபாட்டால் அரசுத் திட்ட விண்ணப்பங்கள் நிராகரிக்கப்படும் அபாயம் உள்ளதால், "
                      f"ஆதாரில் உள்ளபடி எனது பெயரை <strong>\"{escape(right)}\"</strong> எனத் திருத்தித் தருமாறு பணிவுடன் கேட்டுக்கொள்கிறேன்.</p>"
                    + "<p><strong>இணைப்புகள்:</strong></p>" + _encl(["ஆதார் அட்டை நகல் (சுய சான்றொப்பம்)", f"{escape(d['ta'])} நகல்"])
                    + _sign(ctx, True)
                    + "<p class='blank'>ஆதாரில் உள்ள பெயரே தவறு என்றால், முதலில் ஆதார் மையத்தில் ஆதாரைத் திருத்தவும்.</p>")
        return (_head(("To:", f"{office_en},\n{_e(ctx['district'])}."),
                      ("From:", _from(ctx, False)),
                      ("Subject:", f"Request to correct my name on the {escape(d['en'])}."))
                + "<p>Sir / Madam,</p>"
                + f"<p>My name is printed as <strong>\"{escape(wrong)}\"</strong> on my {escape(d['en'])}, while my Aadhaar card shows "
                  f"<strong>\"{escape(right)}\"</strong>. Both refer to me, the same person.</p>"
                + "<p>As this difference can lead to rejection of my government scheme applications, I request you to correct my name "
                  f"to <strong>\"{escape(right)}\"</strong> as per Aadhaar.</p>"
                + "<p><strong>Enclosures:</strong></p>" + _encl(["Copy of Aadhaar card (self-attested)", f"Copy of the {escape(d['en'])}"])
                + _sign(ctx, False)
                + "<p class='blank'>If the name on Aadhaar itself is wrong, correct Aadhaar first at an Aadhaar centre.</p>")

    return body(True), body(False)


# ------------------------------------------------------------------ grievance
def _grievance(ctx):
    step = ctx["step"]

    def body(ta):
        cause = step.get("cause_ta" if ta else "cause_en")
        schemes = _scheme_names(ctx, ta)
        if ta:
            return (_head(("பெறுநர்:", "குறைதீர்ப்புப் பிரிவு,\nகலைஞர் மகளிர் உரிமைத் தொகைத் திட்டம்\n(KMUT குறைதீர்ப்பு இணையதளம் / முதல்வரின் முகவரி 1100 வழியாக)"),
                          ("அனுப்புநர்:", _from(ctx, True)),
                          ("பொருள்:", f"{escape(schemes)} — உதவித்தொகை வரவில்லை; சரிசெய்யக் கோருதல்."))
                    + "<p>ஐயா / அம்மா,</p>"
                    + f"<p>எனக்கு {escape(schemes)} உதவித்தொகை {_e(None)} மாதம் முதல் வரவில்லை. "
                      "எனது வங்கிக் கணக்கு மற்றும் ஆதார் இணைப்பைச் சரிபார்த்தேன்.</p>"
                    + (f"<p>இதுவரை கண்டறிந்தது: {escape(cause)}</p>" if cause else "")
                    + "<p>எனது விண்ணப்ப நிலையைச் சரிபார்த்து, நிலுவைத் தொகையை வழங்குமாறு பணிவுடன் கேட்டுக்கொள்கிறேன்.</p>"
                    + "<p><strong>இணைப்புகள்:</strong></p>" + _encl(["ஆதார் அட்டை நகல்", "வங்கிப் புத்தக நகல் (சமீபத்திய பதிவுகளுடன்)", "தேர்வுக் குறுஞ்செய்தி (இருந்தால்)"])
                    + _sign(ctx, True))
        return (_head(("To:", "The Grievance Cell,\nKalaignar Magalir Urimai Thogai scheme\n(through the KMUT grievance portal / CM Helpline 1100)"),
                      ("From:", _from(ctx, False)),
                      ("Subject:", f"{escape(schemes)}: benefit not received; request to resolve."))
                + "<p>Sir / Madam,</p>"
                + f"<p>I have not received my {escape(schemes)} benefit since {_e(None)}. I have checked my bank account and its Aadhaar link.</p>"
                + (f"<p>What we found so far: {escape(cause)}</p>" if cause else "")
                + "<p>I request you to check the status of my application and release the pending amount.</p>"
                + "<p><strong>Enclosures:</strong></p>" + _encl(["Copy of Aadhaar card", "Copy of bank passbook (recent entries)", "Selection SMS (if any)"])
                + _sign(ctx, False))

    return body(True), body(False)


# ------------------------------------------------------------------- appeals
def _met_rules(ctx, scheme_id, ta):
    m = ctx["member"] or {}
    v = next((v for v in ctx["snapshot"].get("verdicts", []) if v["scheme_id"] == scheme_id
              and v["member_id"] in (m.get("id"), None)), None)
    return [escape(r["ta"] if ta else r["en"]) for r in (v or {}).get("reasons", []) if r["ok"] is True]


def _reason(ctx, ta):
    r = ctx["case"].get("rejection_reason_ta" if ta else "rejection_reason_en")
    return escape(r) if r else f'<span class="blank">{BLANK}</span>'


def _appeal_kmut(ctx):
    def body(ta):
        rules = _met_rules(ctx, "kmut", ta)
        if ta:
            return (_head(("பெறுநர்:", f"வருவாய் கோட்ட அலுவலர் அவர்கள்,\n{_e(None)} வருவாய் கோட்டம்.\n(இ-சேவை மையம் வழியாக)"),
                          ("அனுப்புநர்:", _from(ctx, True)),
                          ("பொருள்:", "கலைஞர் மகளிர் உரிமைத் தொகை — விண்ணப்ப நிராகரிப்புக்கு எதிரான மேல்முறையீடு."),
                          ("பார்வை:", f"நிராகரிப்பு குறுஞ்செய்தி நாள் {_e(None)}."))
                    + "<p>ஐயா / அம்மா,</p>"
                    + f"<p>நான் எனது குடும்ப அட்டையில் குடும்பத் தலைவியாக உள்ளேன். எனது விண்ணப்பம் \"{_reason(ctx, True)}\" என்ற காரணத்தால் "
                      "நிராகரிக்கப்பட்டது. ஆனால் எனது குடும்பம் திட்ட விதிமுறைகளைப் பூர்த்தி செய்கிறது:</p>"
                    + _encl(rules or [BLANK])
                    + "<p>இதற்கான ஆதார ஆவணங்களை இணைத்துள்ளேன். எனது விண்ணப்பத்தை மறுபரிசீலனை செய்து உரிமைத் தொகை வழங்குமாறு பணிவுடன் கேட்டுக்கொள்கிறேன்.</p>"
                    + "<p><strong>இணைப்புகள்:</strong></p>" + _encl(["ஆதார் அட்டை நகல்", "குடும்ப அட்டை நகல்", "வங்கிப் புத்தக நகல்"])
                    + _sign(ctx, True))
        return (_head(("To:", f"The Revenue Divisional Officer,\n{_e(None)} Revenue Division.\n(through the e-Sevai centre)"),
                      ("From:", _from(ctx, False)),
                      ("Subject:", "Appeal against rejection of my Kalaignar Magalir Urimai Thogai application."),
                      ("Ref:", f"Rejection SMS dated {_e(None)}."))
                + "<p>Sir / Madam,</p>"
                + f"<p>I am the head of the family on my ration card. My application was rejected for the reason \"{_reason(ctx, False)}\". "
                  "However, my family meets the scheme rules:</p>"
                + _encl(rules or [BLANK])
                + "<p>I have enclosed the supporting documents. I request you to reconsider my application and sanction the entitlement.</p>"
                + "<p><strong>Enclosures:</strong></p>" + _encl(["Copy of Aadhaar card", "Copy of ration card", "Copy of bank passbook"])
                + _sign(ctx, False))

    return body(True), body(False)


def _appeal_pension(ctx):
    m = ctx["member"] or {}
    missing = [x for x in ctx["snapshot"].get("missing_documents", []) if x["member_id"] == m.get("id")]
    if not missing and m.get("docs", {}).get("husband_death_certificate") is False:
        missing = [{"en": DOCUMENTS["husband_death_certificate"]["en"], "ta": DOCUMENTS["husband_death_certificate"]["ta"]}]

    def body(ta):
        docs_now = ", ".join(escape(x["ta" if ta else "en"]) for x in missing) or f'<span class="blank">{BLANK}</span>'
        if ta:
            return (_head(("பெறுநர்:", f"தனி வட்டாட்சியர் அவர்கள் (சமூகப் பாதுகாப்புத் திட்டம்),\n{_e(None)} வட்டம்."),
                          ("அனுப்புநர்:", _from(ctx, True)),
                          ("பொருள்:", "ஆதரவற்ற விதவையர் ஓய்வூதியம் — நிராகரிக்கப்பட்ட விண்ணப்பத்தை மறுபரிசீலனை செய்யக் கோருதல்."))
                    + "<p>ஐயா / அம்மா,</p>"
                    + f"<p>நான் கணவரை இழந்த, ஆதரவற்ற {_e(ctx['age'])} வயது பெண். எனது ஓய்வூதிய விண்ணப்பம் \"{_reason(ctx, True)}\" "
                      f"என்ற காரணத்தால் நிராகரிக்கப்பட்டது. தேவையான {docs_now} தற்போது இணைத்துள்ளேன். "
                      "எனது விண்ணப்பத்தை மறுபரிசீலனை செய்து ஓய்வூதியம் வழங்குமாறு பணிவுடன் கேட்டுக்கொள்கிறேன்.</p>"
                    + "<p><strong>இணைப்புகள்:</strong></p>" + _encl([docs_now, "ஆதார் அட்டை நகல்", "வங்கிப் புத்தக நகல்"])
                    + _sign(ctx, True))
        return (_head(("To:", f"The Special Tahsildar (Social Security Scheme),\n{_e(None)} Taluk."),
                      ("From:", _from(ctx, False)),
                      ("Subject:", "Request to reconsider my rejected Destitute Widow Pension application."))
                + "<p>Sir / Madam,</p>"
                + f"<p>I am a destitute widow, aged {_e(ctx['age'])}. My pension application was rejected for the reason "
                  f"\"{_reason(ctx, False)}\". I now enclose the required {docs_now}. I request you to reconsider my application "
                  "and sanction the pension.</p>"
                + "<p><strong>Enclosures:</strong></p>" + _encl([docs_now, "Copy of Aadhaar card", "Copy of bank passbook"])
                + _sign(ctx, False))

    return body(True), body(False)


# ---------------------------------------------------------------- full page
def page(letter, approved, helper_name=None):
    """Printable A4 page. DRAFT watermark and no Print button until a helper approves."""
    with open(config.ROOT / "templates" / "letter.html", encoding="utf-8") as fh:
        html = fh.read()
    title = f"{letter['title_ta']} / {letter['title_en']}"
    status = ('<span class="status approved">உதவியாளர் ஒப்புதல் அளித்தது / Approved by helper</span>' if approved
              else '<span class="status draft">வரைவு: உதவியாளர் ஒப்புதல் தேவை / Draft: needs helper approval</span>')
    footer = ("துணை மூலம் தயாரிக்கப்பட்டது · இறுதி முடிவு துறையினுடையது · OTP-ஐ யாரிடமும் பகிர வேண்டாம்<br>"
              f"Prepared with Thunai · Draft reviewed by helper: {escape(helper_name) if approved and helper_name else BLANK}")
    for key, value in {
        "{{title}}": escape(title), "{{status}}": status,
        "{{print}}": '<button onclick="window.print()">அச்சிடு / Print</button>' if approved else "",
        "{{watermark}}": "" if approved else '<div class="watermark"><span>வரைவு / DRAFT</span></div>',
        "{{body_ta}}": letter["body_ta"], "{{body_en}}": letter["body_en"], "{{footer}}": footer,
    }.items():
        html = html.replace(key, value)
    return html
