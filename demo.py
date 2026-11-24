"""Run both demo scenarios from the terminal: python demo.py"""
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("COUNCIL_DB", "demo.db")
from council.moderator import run_session  # noqa: E402
from council import store  # noqa: E402
from council.watcher import check_watches  # noqa: E402


def show(r: dict):
    print(f"\n=== {r['question']} ===")
    for o in r["opinions"]:
        flag = "VETO" if o["veto"] else o["stance"].upper()
        print(f"  {o['member']:<17} [{o['role']}] {flag:<12} {o['reason']}  ({o['source']})")
        for f in o["facts"]:
            print(f"  {'':<17}   - {f}")
    print(f"  VERDICT: {r['verdict']}")
    for d in r["drafts"]:
        amt = f" (₹{d['amount']:,})" if d.get("amount") else ""
        print(f"  DRAFT, needs your approval: {d['what']}{amt}")


async def main():
    if os.path.exists("demo.db"):
        os.remove("demo.db")
    r = await run_session("Can I do a Goa trip this weekend?")
    show(r)

    q = "Can I go to my friend's wedding in Mysuru on Saturday?"
    r = await run_session(q)
    show(r)
    sid = store.save_session(r)
    store.add_watch(sid, q, None)
    print("\n... watcher re-checks (a seat opens) ...")
    for change in await check_watches(simulate_change=True):
        print(f"  RECONVENED -> {change['verdict']}")


if __name__ == "__main__":
    asyncio.run(main())
