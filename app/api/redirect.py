from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.db.session import get_db
from app.models.url import ShortURL
from app.db.redis import redis_client
from app.main import limiter

router = APIRouter()

@router.get("/{short_code}")
@limiter.limit("60/minute")
async def redirect_short_url(request: Request, short_code: str, db: AsyncSession = Depends(get_db)):
    cache_key = f"url:{short_code}"
    cached = redis_client.get(cache_key)

    if cached:
        return RedirectResponse(url=cached, status_code=302)

    result = await db.execute(select(ShortURL).where(ShortURL.short_code == short_code))
    row = result.scalar_one_or_none()

    if not row:
        raise HTTPException(404, "Not found")

    row.click_count += 1
    row.last_clicked_at = datetime.now(timezone.utc)
    await db.commit()

    redis_client.setex(cache_key, 3600, row.original_url)
    return RedirectResponse(url=row.original_url, status_code=302)
