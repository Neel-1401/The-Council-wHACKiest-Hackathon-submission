"""Watcher: re-checks vetoed plans and reconvenes the Council when the facts change."""
from council.moderator import run_session
from council import store
from council.actions import send_whatsapp


async def check_watches(simulate_change: bool = True) -> list[dict]:
    """Run once per interval (APScheduler in app.py). In the MVP the sample data 'opens a seat' on recheck."""
    reconvened = []
    for w in store.active_watches():
        result = await run_session(w["question"], recheck=simulate_change)
        if result["status"] == "decided":
            sid = store.save_session(result)
            store.close_watch(w["id"])
            send_whatsapp(w["phone"], f"The Council reconvened: {result['verdict']}")
            reconvened.append({"watch_id": w["id"], "new_session_id": sid, "verdict": result["verdict"]})
    return reconvened
