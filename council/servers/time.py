"""TIME (gatekeeper): Google Calendar. Uses the real calendar when GOOGLE_CALENDAR_TOKEN is set."""
import os
from datetime import datetime, timedelta, timezone
import httpx
from fastmcp import FastMCP
from council.data import member_data, opinion

mcp = FastMCP("time-mcp")


def _events(scenario: str) -> tuple[list[dict], str]:
    token = os.getenv("GOOGLE_CALENDAR_TOKEN")  # OAuth access token, calendar.readonly scope
    if not token:
        return member_data(scenario, "time")["events"], "sample"
    try:
        now = datetime.now(timezone.utc)
        r = httpx.get("https://www.googleapis.com/calendar/v3/calendars/primary/events",
                      headers={"Authorization": f"Bearer {token}"},
                      params={"timeMin": now.isoformat(), "timeMax": (now + timedelta(days=7)).isoformat(),
                              "singleEvents": "true", "orderBy": "startTime"}, timeout=8)
        r.raise_for_status()
        out = []
        for e in r.json().get("items", []):
            start = e["start"].get("dateTime") or e["start"].get("date")
            when = datetime.fromisoformat(start.replace("Z", "+00:00")).strftime("%A %-I:%M %p")
            out.append({"title": e.get("summary", "Busy"), "when": when, "hard": True})
        return out, "google_calendar"
    except Exception:
        return member_data(scenario, "time")["events"], "sample"


@mcp.tool
def upcoming(scenario: str) -> list[dict]:
    """Calendar events for the next 7 days."""
    return _events(scenario)[0]


@mcp.tool
def assess(question: str, scenario: str, recheck: bool = False) -> dict:
    """TIME's opinion: what can't move, and what does that allow?"""
    events, src = _events(scenario)
    hard = [e for e in events if e.get("hard")]
    facts = [f"{e['title']}: {e['when']}" for e in events]
    if hard:
        return opinion("TIME", "gatekeeper", "conditional",
                       "Possible if you are back before: " + "; ".join(f"{e['title']} ({e['when']})" for e in hard),
                       facts, source=src)
    return opinion("TIME", "gatekeeper", "go", "Nothing fixed in the way.", facts, source=src)


if __name__ == "__main__":
    mcp.run()
