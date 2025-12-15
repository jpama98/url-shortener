import secrets
import string
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.url import ShortURL
from app.db.redis import get_redis
from app.core.config import settings

ALPHABET = string.ascii_letters + string.digits

def generate_code(length: int = 7) -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))

async def create_short_url(db: AsyncSession, owner_id, target_url: str) -> ShortURL:
    # try a few times to avoid collisions
    for _ in range(8):
        code = generate_code()
        res = await db.execute(select(ShortURL).where(ShortURL.code == code))
        if not res.scalar_one_or_none():
            link = ShortURL(code=code, target_url=str(target_url), owner_id=owner_id)
            db.add(link)
            await db.commit()
            await db.refresh(link)

            # cache mapping
            r = await get_redis()
            await r.set(f"code:{code}", link.target_url, ex=60*60)  # 1h cache
            return link

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to allocate short code")

async def resolve_code(db: AsyncSession, code: str) -> ShortURL:
    # cache target for speed; still return DB row for owner/click id
    res = await db.execute(select(ShortURL).where(ShortURL.code == code))
    link = res.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Code not found")
    return link

def short_url_for(code: str) -> str:
    return f"{settings.base_url.rstrip('/')}/{code}"
