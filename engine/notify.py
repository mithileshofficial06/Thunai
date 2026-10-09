"""SMS texts built from a snapshot: a plan summary and per-office reminders. No ID numbers ever."""

MAX_SMS = 480
OTP_TA = "OTP-ஐ யாரிடமும் பகிர வேண்டாம்."
OTP_EN = "Never share your OTP."


def _fit(head: str, middle: list, tail: str) -> str:
    """Join head + middle parts + tail, dropping middle parts from the end until it fits MAX_SMS."""
    parts = list(middle)
    while parts and len(" ".join([head, *parts, tail])) > MAX_SMS:
        parts.pop()
    text = " ".join([head, *parts, tail])
    if len(text) > MAX_SMS:  # head alone too long: cut it, keep the OTP warning
        text = head[: MAX_SMS - len(tail) - 2].rstrip() + "… " + tail
    return text


def _first_undone(office: dict):
    for task in office.get("tasks", []):
        if not task.get("done"):
            return task
    return None


def summary_sms(snapshot: dict, lang: str = "ta") -> str:
    """Short SMS: eligible count, rupees a year, first undone step at up to 2 offices, OTP warning."""
    ta = lang != "en"
    tail = OTP_TA if ta else OTP_EN
    eligible = [v for v in snapshot.get("verdicts", []) if v.get("status") == "ELIGIBLE" and v.get("counted")]
    if not eligible:
        if ta:
            head = ("துணை: இப்போது உங்கள் குடும்பத்துக்குப் பொருந்தும் திட்டம் எதுவும் இல்லை. "
                    "விவரங்கள் மாறினால் மீண்டும் சரிபார்க்கலாம்.")
        else:
            head = "Thunai: Sorry, no scheme matches your family right now. We can check again if anything changes."
        return _fit(head, [], tail)

    n = len(eligible)
    rupees = int(snapshot.get("rupees_per_year") or 0)
    if ta:
        head = f"துணை: உங்கள் குடும்பம் {n} திட்டங்களில் ஆண்டுக்கு சுமார் ₹{rupees:,} பெறலாம்."
    else:
        plural = "s" if n != 1 else ""
        head = f"Thunai: Your family can get {n} scheme{plural}, about Rs {rupees:,} a year."

    steps = []
    for office in snapshot.get("plan", []):
        task = _first_undone(office)
        if not task:
            continue
        if ta:
            where = office.get("office_ta") or office.get("office_en", "")
            what = task.get("short_ta") or task.get("short_en", "")
        else:
            where, what = office.get("office_en", ""), task.get("short_en", "")
        steps.append(f"{where}: {what}.")
        if len(steps) == 2:
            break
    if steps:
        steps[0] = ("அடுத்து: " if ta else "Next: ") + steps[0]
    return _fit(head, steps, tail)


def reminder_sms(task: dict, office_ta: str, office_en: str, lang: str = "ta") -> str:
    """Reminder SMS for one pending task at one office, ending with the OTP warning."""
    ta = lang != "en"
    tail = OTP_TA if ta else OTP_EN
    who = f" ({task['member_name']})" if task.get("member_name") else ""
    if ta:
        head = f"துணை நினைவூட்டல்: {office_ta or office_en}{who}: {task.get('short_ta') or task.get('short_en', '')}."
        extra = [f"கொண்டு வர வேண்டியவை: {task['bring_ta']}."] if task.get("bring_ta") else []
    else:
        head = f"Thunai reminder: {office_en}{who}: {task.get('short_en', '')}."
        extra = [f"Bring: {task['bring_en']}."] if task.get("bring_en") else []
    return _fit(head, extra, tail)
