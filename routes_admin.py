"""Helper-only admin routes: the official-source check and the new-scheme re-match.

Both need a helper sign-in (routes_auth.helper_user): 401 without a token, 403 for a family account.
"""
import threading

from fastapi import APIRouter, Depends

import routes_auth  # routes_auth never imports this module, so there is no import cycle
import sms
import store
from engine import data, recompute, short, sources

router = APIRouter()

SMS_HEAD = "துணை: நல்ல செய்தி. உங்கள் குடும்பத்துக்குப் புதிய திட்டம் பொருந்தலாம்:"
SMS_TAIL = "விவரங்களுக்கு துணையைத் திறக்கவும். OTP-ஐ யாரிடமும் பகிர வேண்டாம்."
SMS_MAX = 480
NEW_FIELDS = ("key", "name_en", "name_ta", "member_name", "benefit_en", "benefit_ta")
_REMATCH_LOCK = threading.Lock()  # two helpers clicking at once must not send the same SMS twice


@router.get("/api/admin/check_sources")
def check_sources(helper=Depends(routes_auth.helper_user)):
    return {
        "results": sources.check_all(fetcher=sources.fetch),
        "note_en": "Changed pages need review by a person; rules are never changed automatically.",
        "note_ta": "மாறிய பக்கங்களை ஒருவர் சரிபார்க்க வேண்டும்; விதிகள் தானாக மாற்றப்படுவதில்லை.",
    }


def _sms_text(new):
    """One Tamil SMS per family (at most SMS_MAX characters): short scheme name, member, benefit."""
    items = [f"{short(v['name_ta'])}{' (' + v['member_name'] + ')' if v.get('member_name') else ''}: {v['benefit_ta']}"
             for v in new]
    for n in range(len(items), 0, -1):
        rest = len(items) - n
        more = f"; மேலும் {rest} {'திட்டம்' if rest == 1 else 'திட்டங்கள்'}" if rest else ""
        text = f"{SMS_HEAD} {'; '.join(items[:n])}{more}. {SMS_TAIL}"
        if len(text) <= SMS_MAX:
            return text
    room = SMS_MAX - len(SMS_HEAD) - len(SMS_TAIL) - 3  # even one scheme is too long: cut it
    return f"{SMS_HEAD} {items[0][:max(room, 0)]}… {SMS_TAIL}"


def _event(en, ta, **detail):
    return {"type": "autonomous", "icon": "", "text_en": en, "text_ta": ta, "detail": detail}


def _plural(n, one, many):
    return f"{n} {one if n == 1 else many}"


@router.post("/api/admin/rematch")
def rematch(helper=Depends(routes_auth.helper_user)):
    """Re-check every saved family against the current schemes.json; SMS the families newly ELIGIBLE.

    A chat with no recorded eligibility (saved before this feature) is only baselined -- no alert.
    The recorded set is updated after every check, so the same scheme is never announced twice.
    """
    with _REMATCH_LOCK:
        enabled = data.reload()
        checked = baselined = 0
        results, messages, family_events = [], [], []
        for row in store.all_family_chats():
            if not row["facts"]:
                continue
            checked += 1
            snap = recompute(row["facts"])
            now = {v["key"]: v for v in snap["verdicts"] if v["status"] == "ELIGIBLE"}
            if row["eligible"] is None:
                store.set_eligible(row["chat_id"], now.keys())
                baselined += 1
                continue
            before = set(row["eligible"])
            new = [now[k] for k in now if k not in before]
            if new:
                msg = sms.deliver(row["chat_id"], row["user_id"], row["phone"], _sms_text(new), "new_scheme")
                messages.append(msg)
                results.append({"chat_id": row["chat_id"], "title": row["title"],
                                "new": [{f: v.get(f) for f in NEW_FIELDS} for v in new]})
                names_en = ", ".join(short(v["name_en"]) + (f" ({v['member_name']})" if v.get("member_name") else "") for v in new)
                names_ta = ", ".join(short(v["name_ta"]) + (f" ({v['member_name']})" if v.get("member_name") else "") for v in new)
                family_events.append(_event(
                    f"{row['title']}: newly eligible for {names_en}. SMS to {msg['to']} ({msg['status']})",
                    f"{row['title']}: புதிதாகப் பொருந்தும் திட்டம் — {names_ta}. குறுஞ்செய்தி: {msg['to']}",
                    chat_id=row["chat_id"], schemes=[v["key"] for v in new], message_id=msg["id"]))
            store.set_eligible(row["chat_id"], now.keys())

    alerted = len(results)
    en = (f"Re-checked {_plural(checked, 'saved family', 'saved families')} against the current scheme rules "
          f"({enabled} schemes): " + (f"{_plural(alerted, 'family', 'families')} newly eligible; SMS prepared"
                                      if alerted else "no new matches"))
    ta = (f"சேமித்த குடும்பங்கள் தற்போதைய திட்ட விதிகளுடன் ({enabled} திட்டங்கள்) மீண்டும் சரிபார்க்கப்பட்டன — "
          f"சரிபார்த்தவை: {checked}; "
          + (f"புதிய திட்டம் பொருந்தும் குடும்பங்கள்: {alerted}; குறுஞ்செய்தி தயார்" if alerted else "புதிய பொருத்தம் இல்லை"))
    if baselined:
        en += f"; {_plural(baselined, 'family', 'families')} recorded as a starting point"
        ta += f"; தொடக்க நிலை பதிவானவை: {baselined}"
    summary = _event(en, ta, checked=checked, baselined=baselined, alerted=alerted, schemes_enabled=enabled)
    return {"checked": checked, "baselined": baselined, "alerted": alerted, "results": results,
            "messages": messages, "events": [summary] + family_events, "schemes_enabled": enabled}
