from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.api.router import api_router
from app.core.limiter import limiter
from app.db.session import get_db
from app.db.redis import get_redis
from app.services.url_service import resolve_code
from app.services.click_worker import start_click_worker, stop_click_worker, enqueue_click

app = FastAPI(title="URL Shortener Service", version="1.0.0")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def on_startup():
    await start_click_worker()

@app.on_event("shutdown")
async def on_shutdown():
    await stop_click_worker()

@app.get("/{code}", include_in_schema=False)
@limiter.limit("60/minute")
async def redirect(code: str, request: Request):
    r = await get_redis()
    target = await r.get(f"code:{code}")

    async for db in get_db():
        link = await resolve_code(db, code)
        if target is None:
            target = link.target_url
            await r.set(f"code:{code}", target, ex=60*60)  # 1h cache
        link_id = str(link.id)
        break

    await enqueue_click({
        "link_id": link_id,
        "ip": request.client.host if request.client else "",
        "user_agent": request.headers.get("user-agent", ""),
        "referer": request.headers.get("referer", ""),
    })

    return RedirectResponse(url=target, status_code=302)
