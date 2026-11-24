# The Council

**Team AROS · wHACKiest 2026 · Track 1: Make MCP Matter · Team ID 359de872**

Your apps, one table. They argue so you don't have to, and nothing moves without your nod.

Ask a life decision ("Can I do a Goa trip this weekend?"). Six AI members, each one an **MCP server** speaking for one of your apps, check your real data and debate it. Gatekeepers can **veto** with hard facts (no seat, no money, a deadline); advisors weigh in but can't block. The moderator returns a verdict plus **drafted actions you approve one by one**. If the answer is "not yet", a **watcher** keeps checking and the Council **reconvenes on its own** when something changes, like a seat opening up.

## The members

| Member | Role | Data | MVP status |
|---|---|---|---|
| TRIP | Gatekeeper | Trains, buses, hotels, destination weather | OpenWeather live (with key); trains/hotels sample (RapidAPI IRCTC slot ready) |
| OUTINGS | Gatekeeper | Events, tickets, restaurant slots | Sample (Swiggy Dineout MCP next) |
| WALLET | Gatekeeper | Bank SMS balance, real total cost | Sample |
| TIME | Gatekeeper | Google Calendar | Live (with token), else sample |
| HEALTH | Advisor | Sleep, steps | Sample |
| FRIENDS & FAMILY | Advisor | Family calendar, WhatsApp | Drafts messages; sends via Twilio WhatsApp |

## How it works

```
question (API or WhatsApp)
  └─ moderator (council/moderator.py)
       ├─ gatekeepers in parallel over MCP: trip-mcp, outings-mcp, time-mcp → wallet-mcp (gets the real total)
       ├─ any veto? ── yes → "Not possible yet. Watching." → watcher re-checks every 10 min → reconvene
       │            └─ no  → advisors: health-mcp, family-mcp
       └─ vote + verdict (Gemini when GEMINI_API_KEY is set) → drafted actions → you approve / undo
```

```
app.py                  FastAPI: /session, /actions/{id}/approve, /actions/{id}/undo, /watches, /watches/check, /whatsapp
demo.py                 Runs both demo scenarios in the terminal
council/servers/*.py    Six FastMCP servers, each exposing an `assess` tool (+ data tools)
council/moderator.py    Convenes members through MCP clients, veto rule, vote, verdict
council/watcher.py      Re-checks vetoed plans and reconvenes the Council
council/actions.py      Executes approved drafts (Twilio WhatsApp; bookings simulated)
council/store.py        SQLite: sessions, approvals + undo log, watches
data/scenarios.json     Labelled sample data for both demo scenarios
```

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python demo.py          # both scenarios, no API keys needed
pytest -q               # veto, advisor and reconvene tests
```

API server:

```bash
cp .env.example .env    # optional keys: Gemini, OpenWeather, Google Calendar, Twilio
uvicorn app:app --reload
# open http://127.0.0.1:8000/docs
curl -X POST localhost:8000/session -H "Content-Type: application/json" \
     -d '{"question": "Can I go to my friend'\''s wedding in Mysuru on Saturday?"}'
curl -X POST localhost:8000/watches/check
```

Each member also runs as a standalone MCP server, so any MCP client can use it:

```bash
python -m council.servers.trip
```

## Demo scenarios

1. **Goa weekend:** Friday train is WL 34, Saturday 6:00 AM has seats; real total ₹5,040 against ₹7,450 left; lab record due Monday 9:00 AM; Mom's birthday dinner Sunday 8:00 PM. Verdict: go, Saturday only, back for dinner. Drafts: train, room, gig ticket, table, a message to Mom.
2. **Friend's wedding in Mysuru:** every train and bus is waitlisted, so TRIP vetoes: "Not possible yet. Watching." The watcher re-checks, a seat opens, the Council reconvenes and sends a WhatsApp alert.

## Next, before and during the 24-hour build

- Connect Swiggy's official Dineout MCP server to OUTINGS
- Live train availability through the RapidAPI IRCTC endpoint (cached for the demo)
- Gemini-written debate turns per member
- Web app for the debate and approval cards

Sample data is clearly labelled in every member's output (`"source": "sample"`).

## Team AROS

Pranav Swaroop Boggarapu (lead) · Nama Sai Nikith · Neel Kamal · Vignesh S
