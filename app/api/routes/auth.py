from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest, LogoutRequest, MessageOut
from app.schemas.user import UserOut
from app.schemas.token import TokenPair
from app.services.auth_service import register, login, refresh, revoke_refresh_token

router = APIRouter()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await register(db, payload.email, payload.password)

@router.post("/login", response_model=TokenPair)
async def login_user(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login(db, payload.email, payload.password)

@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    return await refresh(db, payload.refresh_token)

@router.post("/logout", response_model=MessageOut)
async def logout(payload: LogoutRequest):
    await revoke_refresh_token(payload.refresh_token)
    return MessageOut(message="Refresh token revoked")
