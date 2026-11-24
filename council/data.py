"""Sample data loader. Real integrations replace parts of this when API keys are set."""
import json
from pathlib import Path

DATA = json.loads((Path(__file__).resolve().parent.parent / "data" / "scenarios.json").read_text())


def pick_scenario(question: str) -> str:
    q = question.lower()
    for key, sc in DATA.items():
        if any(word in q for word in sc["match"]):
            return key
    return "goa"


def member_data(scenario: str, member: str) -> dict:
    return DATA[scenario][member]


def opinion(member: str, role: str, stance: str, reason: str, facts: list[str],
            veto: bool = False, drafts: list[dict] | None = None, source: str = "sample") -> dict:
    """The shape every Council member returns from its `assess` tool."""
    return {"member": member, "role": role, "stance": stance, "veto": veto,
            "reason": reason, "facts": facts, "drafts": drafts or [], "source": source}
