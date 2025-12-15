from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.url import ShortURL
from app.schemas.url import AnalyticsResponse

router = APIRouter()

@router.get("/analytics/{short_code}", response_model=AnalyticsResponse)
async def analytics(short_code: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ShortURL).where(ShortURL.short_code == short_code))
    row = result.scalar_one_or_none()

    if not row:
        raise HTTPException(404, "Not found")

    return AnalyticsResponse(
        short_code=row.short_code,
        original_url=row.original_url,
        total_clicks=row.click_count,
        created_at=row.created_at,
        last_clicked_at=row.last_clicked_at,
    )
