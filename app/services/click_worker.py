import asyncio
import json
from app.db.redis import get_redis, close_redis
from app.db.session import AsyncSessionLocal
from app.models.click import ClickEvent
from sqlalchemy.ext.asyncio import AsyncSession

_worker_task: asyncio.Task | None = None
_stop_event: asyncio.Event | None = None

QUEUE_KEY = "clicks"

async def enqueue_click(payload: dict) -> None:
    r = await get_redis()
    await r.rpush(QUEUE_KEY, json.dumps(payload))

async def _run_worker(stop_event: asyncio.Event):
    r = await get_redis()
    while not stop_event.is_set():
        # BLPOP blocks up to timeout, allowing graceful shutdown
        item = await r.blpop(QUEUE_KEY, timeout=1)
        if not item:
            continue
        _, raw = item
        data = json.loads(raw)
        async with AsyncSessionLocal() as db:  # type: AsyncSession
            db.add(ClickEvent(**data))
            await db.commit()

async def start_click_worker():
    global _worker_task, _stop_event
    if _worker_task:
        return
    _stop_event = asyncio.Event()
    _worker_task = asyncio.create_task(_run_worker(_stop_event))

async def stop_click_worker():
    global _worker_task, _stop_event
    if _stop_event:
        _stop_event.set()
    if _worker_task:
        await _worker_task
    _worker_task = None
    _stop_event = None
    await close_redis()
