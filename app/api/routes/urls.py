from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.url import ShortURL
from app.models.click import ClickEvent
from app.schemas.url import CreateShortURL, ShortURLOut, ClickStatsOut
from app.services.url_service import create_short_url, resolve_code, short_url_for
from app.core.limiter import limiter
from app.services.click_worker import enqueue_click

router = APIRouter()

@router.post("", response_model=ShortURLOut, status_code=status.HTTP_201_CREATED)
@limiter.limit('10/minute')
async def create_url(payload: CreateShortURL, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    link = await create_short_url(db, user.id, str(payload.target_url))
    return ShortURLOut(
        id=link.id,
        code=link.code,
        target_url=link.target_url,
        short_url=short_url_for(link.code),
        created_at=link.created_at,
    )

@router.get("", response_model=list[ShortURLOut])
async def list_my_urls(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    res = await db.execute(select(ShortURL).where(ShortURL.owner_id == user.id).order_by(ShortURL.created_at.desc()))
    links = res.scalars().all()
    return [
        ShortURLOut(id=l.id, code=l.code, target_url=l.target_url, short_url=short_url_for(l.code), created_at=l.created_at)
        for l in links
    ]

@router.get("/{code}/stats", response_model=ClickStatsOut)
async def stats(code: str, db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    res = await db.execute(select(ShortURL).where(ShortURL.code == code, ShortURL.owner_id == user.id))
    link = res.scalar_one_or_none()
    if not link:
        return ClickStatsOut(code=code, total_clicks=0)

    res2 = await db.execute(select(func.count(ClickEvent.id)).where(ClickEvent.link_id == link.id))
    total = int(res2.scalar_one())
    return ClickStatsOut(code=code, total_clicks=total)

