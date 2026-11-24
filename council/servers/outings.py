"""OUTINGS (gatekeeper): events, tickets and restaurant slots.
Restaurant slots come from Swiggy's official Dineout MCP when connected; sample data otherwise."""
from fastmcp import FastMCP
from council.data import member_data, opinion

mcp = FastMCP("outings-mcp")


@mcp.tool
def list_events(scenario: str) -> dict:
    """Events and dining slots around the plan."""
    return member_data(scenario, "outings")


@mcp.tool
def assess(question: str, scenario: str, recheck: bool = False) -> dict:
    """OUTINGS' opinion: is the thing you are going for actually available?"""
    d = member_data(scenario, "outings")
    facts, drafts = [], []
    for e in d["events"]:
        left = "invite only" if e["tickets_left"] is None else f"{e['tickets_left']} tickets left"
        facts.append(f"{e['name']}, {e['when']}: {left}" + (f", ₹{e['price']:,}" if e["price"] else ""))
        if e["tickets_left"] == 0:
            return opinion("OUTINGS", "gatekeeper", "no", f"{e['name']} is sold out.", facts, veto=True)
        if e["price"]:
            drafts.append({"type": "booking", "what": f"Buy ticket: {e['name']}", "amount": e["price"]})
    for t in d["dining"]:
        facts.append(f"Table for {t['party']}: {t['name']}, {t['slot']}")
        drafts.append({"type": "booking", "what": f"Reserve table: {t['name']} {t['slot']}", "amount": 0})
    return opinion("OUTINGS", "gatekeeper", "go", "What you're going for is available.", facts, drafts=drafts)


if __name__ == "__main__":
    mcp.run()
