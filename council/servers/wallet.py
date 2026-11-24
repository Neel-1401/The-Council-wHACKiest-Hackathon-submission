"""WALLET (gatekeeper): reads bank SMS balance (sample data) and adds up the real cost."""
from fastmcp import FastMCP
from council.data import member_data, opinion

mcp = FastMCP("wallet-mcp")


@mcp.tool
def balance(scenario: str) -> dict:
    """Money left this month."""
    return member_data(scenario, "wallet")


@mcp.tool
def assess(question: str, scenario: str, recheck: bool = False, planned_spend: int = 0) -> dict:
    """WALLET's opinion: can you afford the real total, not the advertised price?"""
    d = member_data(scenario, "wallet")
    left = d["balance_left"]
    facts = [f"Real total ₹{planned_spend:,} against ₹{left:,} left", f"{d['month_days_left']} days left this month"]
    if planned_spend > left:
        return opinion("WALLET", "gatekeeper", "no", "The plan costs more than you have left.", facts, veto=True)
    if planned_spend > 0.8 * left:
        return opinion("WALLET", "gatekeeper", "conditional", "Affordable, but it leaves very little.", facts)
    return opinion("WALLET", "gatekeeper", "go", "Affordable.", facts)


if __name__ == "__main__":
    mcp.run()
