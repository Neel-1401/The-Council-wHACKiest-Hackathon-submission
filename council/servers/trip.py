"""TRIP (gatekeeper): trains, buses, hotels and destination weather."""
import os
import httpx
from fastmcp import FastMCP
from council.data import member_data, opinion

mcp = FastMCP("trip-mcp")

CITY = {"goa": "Panaji", "mysuru": "Mysuru"}


def _weather(scenario: str, fallback: str) -> tuple[str, str]:
    """Real OpenWeather forecast when OPENWEATHER_API_KEY is set, else sample text."""
    key = os.getenv("OPENWEATHER_API_KEY")
    if not key:
        return fallback, "sample"
    try:
        r = httpx.get("https://api.openweathermap.org/data/2.5/forecast",
                      params={"q": CITY[scenario] + ",IN", "appid": key, "units": "metric"}, timeout=8)
        r.raise_for_status()
        rainy = [x for x in r.json()["list"] if "rain" in x["weather"][0]["main"].lower()]
        return ("Rain expected in the next 5 days" if rainy else "No rain in the next 5 days"), "openweather"
    except Exception:
        return fallback, "sample"


def _trains(scenario: str, recheck: bool) -> dict:
    """Train availability. Plug a RapidAPI IRCTC endpoint in here (RAPIDAPI_KEY); sample data otherwise."""
    d = member_data(scenario, "trip")
    return d["after_watch"] if recheck and "after_watch" in d else d["initial"]


@mcp.tool
def check_availability(scenario: str, recheck: bool = False) -> dict:
    """Trains, buses and rooms for the trip."""
    return _trains(scenario, recheck)


@mcp.tool
def assess(question: str, scenario: str, recheck: bool = False) -> dict:
    """TRIP's opinion: can you physically get there and stay?"""
    d = _trains(scenario, recheck)
    weather, wsrc = _weather(scenario, d["weather"])
    open_trains = [t for t in d.get("trains", []) if t["status"].startswith("AVAILABLE")]
    open_buses = [b for b in d.get("buses", []) if b["seats_left"]]
    facts = [f"{t['when']} train ({t['class']}): {t['status']}, ₹{t['fare']}" for t in d.get("trains", [])]
    facts += [f"Rooms from ₹{d['hotel']['from_price']:,} ({d['hotel']['rooms_left']} left)", weather]
    if not open_trains and not open_buses:
        return opinion("TRIP", "gatekeeper", "no", "Every train and bus is waitlisted or full.", facts, veto=True, source=wsrc)
    best = open_trains[0]
    full = [t for t in d.get("trains", []) if not t["status"].startswith("AVAILABLE")]
    lead = f"The {full[0]['when']} train is {full[0]['status']}; " if full else ""
    drafts = [{"type": "booking", "what": f"Book {best['when']} train ({best['class']}) x2", "amount": best["fare"] * 2},
              {"type": "booking", "what": f"Reserve room at {d['hotel']['name']}", "amount": d["hotel"]["from_price"]}]
    return opinion("TRIP", "gatekeeper", "go", f"{lead}seats open on the {best['when']} train.", facts,
                   drafts=drafts, source=wsrc)


if __name__ == "__main__":
    mcp.run()
