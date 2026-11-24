"""HEALTH (advisor): sleep and activity (sample data). Can advise, cannot veto."""
from fastmcp import FastMCP
from council.data import member_data, opinion

mcp = FastMCP("health-mcp")


@mcp.tool
def assess(question: str, scenario: str, recheck: bool = False) -> dict:
    """HEALTH's opinion."""
    d = member_data(scenario, "health")
    facts = [f"Sleep avg {d['sleep_hours_avg']} h", f"Steps avg {d['steps_avg']:,}"]
    if d["sleep_hours_avg"] < 6.5:
        return opinion("HEALTH", "advisor", "conditional", "You're short on sleep: avoid an overnight journey.", facts)
    return opinion("HEALTH", "advisor", "go", "You're well rested.", facts)


if __name__ == "__main__":
    mcp.run()
