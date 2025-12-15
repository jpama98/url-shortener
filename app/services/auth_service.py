from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.schemas.token import TokenPair
from app.db.redis import get_redis
from datetime import datetime, timezone

async def register(db: AsyncSession, email: str, password: str) -> User:
    res = await db.execute(select(User).where(User.email == email))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(email=email, password_hash=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

async def login(db: AsyncSession, email: str, password: str) -> TokenPair:
    res = await db.execute(select(User).where(User.email == email))
    user = res.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    return TokenPair(access_token=access, refresh_token=refresh)

async def refresh(db: AsyncSession, refresh_token: str) -> TokenPair:
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")

    r = await get_redis()
    if await r.get(f"revoked:{refresh_token}"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token revoked")

    sub = payload.get("sub")
    # ensure user exists
    res = await db.execute(select(User).where(User.id == sub))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    access = create_access_token(str(user.id))
    new_refresh = create_refresh_token(str(user.id))
    # rotate: revoke old
    await revoke_refresh_token(refresh_token)
    return TokenPair(access_token=access, refresh_token=new_refresh)

async def revoke_refresh_token(refresh_token: str) -> None:
    payload = decode_token(refresh_token)
    exp = payload.get("exp")
    if not exp:
        return
    ttl = max(0, int(exp - datetime.now(timezone.utc).timestamp()))
    r = await get_redis()
    await r.set(f"revoked:{refresh_token}", "1", ex=ttl)
