"""SMS delivery: a real SMS provider when configured (Twilio REST API), otherwise the prototype outbox.

Every message is recorded in the outbox (store.add_outbox) with a status:
  outbox  - no provider configured (the prototype default) or no phone number (guest)
  sent    - accepted by the provider
  failed  - the provider refused it (detail has the reason)
Messages never contain ID numbers; the recipient is shown masked (98xxxxxx10).
"""
import httpx

import config
import store


def provider():
    """'twilio' when all its settings are present, else None (outbox only)."""
    ok = config.SMS_PROVIDER == "twilio" and config.TWILIO_ACCOUNT_SID and config.TWILIO_AUTH_TOKEN and config.TWILIO_FROM
    return "twilio" if ok else None


def _send_twilio(phone, text, transport=None):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{config.TWILIO_ACCOUNT_SID}/Messages.json"
    with httpx.Client(timeout=10, transport=transport) as client:
        r = client.post(url, auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN),
                        data={"To": f"+91{phone}", "From": config.TWILIO_FROM, "Body": text})
    if r.status_code in (200, 201):
        return "sent", r.json().get("sid", "")
    return "failed", f"provider error {r.status_code}"


def deliver(session_id, user_id, phone, text, reason, transport=None):
    """Send (if a provider is configured and we have a number) and always record it in the outbox."""
    to = store.mask(phone) if phone else "(guest: no number)"
    if not phone:
        status, detail = "outbox", "guest session: no phone number"
    elif provider() is None:
        status, detail = "outbox", "prototype: no SMS provider configured"
    else:
        try:
            status, detail = _send_twilio(phone, text, transport)
        except httpx.HTTPError as exc:
            status, detail = "failed", f"network error: {type(exc).__name__}"
    return store.add_outbox(session_id, user_id, to, text, reason, status, detail)
