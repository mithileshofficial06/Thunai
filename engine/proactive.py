"""Simulated follow-up: what Thunai does on its own N days later. Pure function, no I/O."""
from engine import notify

MAX_REMINDERS = 4


def _event(text_en: str, text_ta: str, detail: dict | None = None) -> dict:
    return {"type": "autonomous", "icon": "", "text_en": text_en, "text_ta": text_ta, "detail": detail or {}}


def simulate(snapshot: dict, drafts: list, days: int) -> dict:
    """Return {"events": [...], "messages": [...]} for a follow-up `days` after the plan was made."""
    days = max(0, int(days))
    events = [_event(f"Follow-up (automatic): {days} days later, checking pending actions",
                     f"தானியங்கி பின்தொடர்தல்: {days} நாட்களுக்குப் பிறகு, நிலுவையிலுள்ள செயல்கள் சரிபார்க்கப்படுகின்றன",
                     {"days": days})]
    messages = []

    reminders = 0
    open_nonapply = []
    for office in snapshot.get("plan", []):
        undone = [t for t in office.get("tasks", []) if not t.get("done")]
        open_nonapply += [t for t in undone if t.get("kind") != "apply"]
        if not undone or reminders >= MAX_REMINDERS:
            continue
        task = undone[0]
        o_en, o_ta = office.get("office_en", ""), office.get("office_ta", "")
        events.append(_event(f"Reminder sent: {o_en}: {task.get('short_en', '')}",
                             f"நினைவூட்டல் அனுப்பப்பட்டது: {o_ta}: {task.get('short_ta', '')}",
                             {"office_id": office.get("office_id"), "task_id": task.get("task_id"),
                              "open_tasks": len(undone)}))
        messages.append({"text": notify.reminder_sms(task, o_ta, o_en, "ta"), "reason": "reminder"})
        reminders += 1

    left = max(0, 30 - days)
    for d in drafts or []:
        if d.get("kind") in ("appeal_kmut", "appeal_pension") and d.get("status") in ("DRAFT", "APPROVED"):
            en = f"Appeal deadline: submit within 30 days of the rejection; about {left} days left"
            ta = f"மேல்முறையீட்டுக் காலக்கெடு: நிராகரிப்பிலிருந்து 30 நாட்களுக்குள் சமர்ப்பிக்கவும்; சுமார் {left} நாட்கள் உள்ளன"
            events.append(_event(en, ta, {"draft_id": d.get("id"), "kind": d.get("kind"), "days_left": left}))
            messages.append({"text": f"துணை: {ta}. {notify.OTP_TA}", "reason": "deadline"})

    if days >= 14 and open_nonapply:
        reason_en = f"{len(open_nonapply)} document task(s) still open after {days} days"
        reason_ta = f"{days} நாட்களுக்குப் பிறகும் {len(open_nonapply)} ஆவணப் பணி(கள்) நிலுவையில் உள்ளன"
        events.append(_event(f"Task open for {days} days: sent to a human helper for a call",
                             f"பணி {days} நாட்களாக நிலுவையில்: ஒரு உதவியாளர் உங்களை அழைப்பார்",
                             {"escalate": True, "reason_en": reason_en, "reason_ta": reason_ta,
                              "task_ids": [t.get("task_id") for t in open_nonapply]}))
        messages.append({"text": f"துணை: ஒரு உதவியாளர் விரைவில் உங்களை அழைப்பார். {notify.OTP_TA}",
                         "reason": "escalation"})

    events.append(_event(f"Follow-up done: {reminders} reminder(s) sent",
                         f"பின்தொடர்தல் முடிந்தது: {reminders} நினைவூட்டல்(கள்) அனுப்பப்பட்டன",
                         {"reminders": reminders, "messages": len(messages)}))
    return {"events": events, "messages": messages}
