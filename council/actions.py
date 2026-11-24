"""Executes approved drafts. Messages go out on WhatsApp via Twilio when configured; bookings stay simulated in the MVP."""
import os


def send_whatsapp(to: str | None, body: str) -> str:
    sid, token = os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN")
    to = to or os.getenv("WHATSAPP_TO")
    if not (sid and token and to):
        print(f"[whatsapp:simulated] -> {to or 'user'}: {body}")
        return "simulated"
    from twilio.rest import Client
    msg = Client(sid, token).messages.create(
        from_=os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886"), to=f"whatsapp:{to}", body=body)
    return msg.sid


def execute(action: dict) -> str:
    if action["type"] == "message":
        return send_whatsapp(None, f"To {action['to']}: {action['what']}")
    return f"simulated booking: {action['what']}"
