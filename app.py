"""FastAPI backend: ask the Council, approve or undo actions, start a watch, WhatsApp webhook."""
import os
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

load_dotenv()
from council.moderator import run_session  # noqa: E402
from council import store, actions  # noqa: E402
from council.watcher import check_watches  # noqa: E402

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app):
    scheduler.add_job(check_watches, "interval", minutes=int(os.getenv("WATCH_INTERVAL_MIN", "10")))
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(title="The Council", lifespan=lifespan)


class Ask(BaseModel):
    question: str
    phone: str | None = None


@app.post("/session")
async def session(body: Ask):
    result = await run_session(body.question)
    sid = store.save_session(result)
    if result["status"] == "watching":
        store.add_watch(sid, body.question, body.phone)
    return {"session_id": sid, **result, "actions": store.list_actions(sid)}


@app.post("/actions/{action_id}/approve")
def approve(action_id: int):
    action = store.set_action(action_id, "approved")
    return {**action, "result": actions.execute(action)}


@app.post("/actions/{action_id}/undo")
def undo(action_id: int):
    return store.set_action(action_id, "undone")


@app.get("/watches")
def watches():
    return store.active_watches()


@app.post("/watches/check")
async def check_now():
    """Demo button: run the watcher now instead of waiting for the interval."""
    return await check_watches()


@app.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp(Body: str = Form(...), From: str = Form(...)):
    """Twilio webhook: ask the Council over WhatsApp."""
    result = await run_session(Body)
    sid = store.save_session(result)
    phone = From.replace("whatsapp:", "")
    if result["status"] == "watching":
        store.add_watch(sid, Body, phone)
    lines = [result["verdict"]] + [f"• {o['member']}: {o['reason']}" for o in result["opinions"]]
    return "\n".join(lines)


@app.get("/")
def root():
    return {"name": "The Council", "docs": "/docs"}
