from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.url import ShortURL
from app.models.click import ClickEvent

router = APIRouter()

@router.get("/summary")
async def summary(db: AsyncSession = Depends(get_db), user: User = Depends(get_current_user)):
    res_links = await db.execute(select(func.count(ShortURL.id)).where(ShortURL.owner_id == user.id))
    links = int(res_links.scalar_one())

    res_clicks = await db.execute(
        select(func.count(ClickEvent.id))
        .select_from(ClickEvent)
        .join(ShortURL, ClickEvent.link_id == ShortURL.id)
        .where(ShortURL.owner_id == user.id)
    )
    clicks = int(res_clicks.scalar_one())
    return {"links": links, "clicks": clicks}
