import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import DateTime, func, ForeignKey, String
from app.db.base import Base

class ClickEvent(Base):
    __tablename__ = "click_events"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    link_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("short_urls.id", ondelete="CASCADE"), index=True, nullable=False)

    ip: Mapped[str] = mapped_column(String(64), nullable=False)
    user_agent: Mapped[str] = mapped_column(String(512), nullable=False, default="")
    referer: Mapped[str] = mapped_column(String(512), nullable=False, default="")

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())

    link = relationship("ShortURL", back_populates="clicks")
