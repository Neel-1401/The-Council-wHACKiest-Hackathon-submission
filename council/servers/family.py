"""FRIENDS & FAMILY (advisor): family calendar and WhatsApp groups. Drafts messages; sending needs approval."""
from fastmcp import FastMCP
from council.data import member_data, opinion

mcp = FastMCP("family-mcp")


@mcp.tool
def assess(question: str, scenario: str, recheck: bool = False) -> dict:
    """FRIENDS & FAMILY's opinion."""
    d = member_data(scenario, "family")
    facts = [f"{e['title']}: {e['when']}" for e in d["events"]]
    if d["events"]:
        e = d["events"][0]
        msg = f"Going for the weekend, back in time for {e['title'].lower()} ({e['when']})."
        return opinion("FRIENDS & FAMILY", "advisor", "conditional", f"Be back for {e['title']}.", facts,
                       drafts=[{"type": "message", "to": d["contact"], "what": msg, "amount": 0}])
    return opinion("FRIENDS & FAMILY", "advisor", "go", "Nothing planned with family.", facts,
                   drafts=[{"type": "message", "to": d["contact"], "what": "I'm in! See you there.", "amount": 0}])


if __name__ == "__main__":
    mcp.run()
