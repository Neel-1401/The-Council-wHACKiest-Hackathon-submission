"""The moderator: convenes the members over MCP, applies the veto rule, counts votes, writes the verdict."""
import asyncio
import json
import os
from fastmcp import Client
from council.data import pick_scenario, DATA
from council.servers import GATEKEEPERS, ADVISORS

WEIGHT = {"go": 1.0, "conditional": 0.5, "no": 0.0}


async def ask(server, question: str, scenario: str, recheck: bool, **extra) -> dict:
    """Call one member's `assess` tool through an MCP client (in-memory transport)."""
    async with Client(server) as c:
        res = await c.call_tool("assess", {"question": question, "scenario": scenario, "recheck": recheck, **extra})
        return res.data


def _gemini_verdict(question: str, opinions: list[dict], fallback: str) -> str:
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return fallback
    try:
        from google import genai
        client = genai.Client(api_key=key)
        prompt = ("You moderate a council of apps advising a user. Using ONLY these member opinions, "
                  "write a verdict of at most 2 short sentences, starting with Go / Not yet. Use 12-hour times.\n"
                  f"Question: {question}\nOpinions: {json.dumps(opinions)}\nDraft verdict: {fallback}")
        out = client.models.generate_content(model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), contents=prompt)
        return out.text.strip() or fallback
    except Exception:
        return fallback


async def run_session(question: str, recheck: bool = False) -> dict:
    scenario = pick_scenario(question)

    # 1. Gatekeepers with hard facts, in parallel (WALLET goes last: it needs the real total)
    first = {k: v for k, v in GATEKEEPERS.items() if k != "wallet"}
    results = await asyncio.gather(*(ask(s, question, scenario, recheck) for s in first.values()))
    opinions = list(results)
    total = sum(d["amount"] for o in opinions for d in o["drafts"])
    opinions.append(await ask(GATEKEEPERS["wallet"], question, scenario, recheck, planned_spend=total))

    vetoes = [o for o in opinions if o["veto"]]
    if vetoes:
        reason = " ".join(f"{o['member']}: {o['reason']}" for o in vetoes)
        return {"question": question, "scenario": scenario, "status": "watching",
                "verdict": "Not possible yet. Watching.", "reason": reason,
                "opinions": opinions, "drafts": [], "score": 0.0}

    # 2. Advisors weigh in (cannot veto)
    opinions += await asyncio.gather(*(ask(s, question, scenario, recheck) for s in ADVISORS.values()))

    # 3. Vote and verdict
    score = round(sum(WEIGHT[o["stance"]] for o in opinions) / len(opinions), 2)
    conditions = [f"{o['member']}: {o['reason']}" for o in opinions if o["stance"] == "conditional"]
    headline = "Go" if not conditions else "Go, with conditions"
    fallback = headline + (". " + " ".join(conditions) if conditions else ".")
    drafts = [d for o in opinions for d in o["drafts"]]
    return {"question": question, "scenario": scenario, "status": "decided",
            "verdict": _gemini_verdict(question, opinions, fallback), "reason": fallback,
            "opinions": opinions, "drafts": drafts, "score": score, "real_total": total,
            "title": DATA[scenario]["title"]}
