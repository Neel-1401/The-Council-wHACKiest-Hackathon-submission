import asyncio
from council.moderator import run_session


def test_goa_goes_with_conditions():
    r = asyncio.run(run_session("Goa trip this weekend?"))
    assert r["status"] == "decided"
    assert r["real_total"] == 5040
    assert all(not o["veto"] for o in r["opinions"])


def test_mysuru_vetoed_then_reconvenes():
    r = asyncio.run(run_session("Friend's wedding in Mysuru?"))
    assert r["status"] == "watching"
    assert any(o["member"] == "TRIP" and o["veto"] for o in r["opinions"])
    r2 = asyncio.run(run_session("Friend's wedding in Mysuru?", recheck=True))
    assert r2["status"] == "decided"


def test_advisors_cannot_veto():
    r = asyncio.run(run_session("Goa trip this weekend?"))
    assert all(not o["veto"] for o in r["opinions"] if o["role"] == "advisor")
