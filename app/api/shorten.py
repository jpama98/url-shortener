from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.url import ShortURL
from app.schemas.url import ShortenRequest, ShortenResponse
from app.services.shortener_service import generate_code
from app.core.config import settings
from app.main import limiter

router = APIRouter()

@router.post("/shorten", response_model=ShortenResponse)
@limiter.limit("10/minute")
async def shorten_url(request: Request, payload: ShortenRequest, db: AsyncSession = Depends(get_db)):
    for _ in range(5):
        code = generate_code()
        exists = await db.execute(select(ShortURL).where(ShortURL.short_code == code))
        if not exists.scalar_one_or_none():
            break
    else:
        raise HTTPException(500, "Code generation failed")

    row = ShortURL(original_url=str(payload.original_url), short_code=code)
    db.add(row)
    await db.commit()
    await db.refresh(row)

    return ShortenResponse(
        short_code=row.short_code,
        short_url=f"{settings.BASE_URL}/{row.short_code}",
        created_at=row.created_at,
    )
