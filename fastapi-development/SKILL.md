---
name: fastapi-development
description: This skill should be used when building production-ready APIs with FastAPI, covering async/await patterns, Pydantic v2 models, dependency injection, SQLAlchemy async integration, OAuth2 with JWT authentication, WebSockets, middleware, background tasks, CORS, rate limiting, file uploads, OpenAPI customization, and testing with httpx and pytest.
---

# FastAPI Development

This skill should be used when building modern, high-performance APIs with FastAPI. It covers repository and service layer patterns, async SQLAlchemy, Pydantic v2, OAuth2/JWT, WebSockets, background tasks, and production deployment.

## When to Use This Skill

- Build async REST APIs with FastAPI and Python 3.12+
- Integrate SQLAlchemy 2.0 async ORM, Pydantic v2, dependency injection
- Add OAuth2/JWT auth, CORS, rate limiting, middleware, WebSockets
- Handle background tasks, file uploads, and OpenAPI auto-docs
- Test with httpx/pytest and deploy with uvicorn/gunicorn

## Project Structure

```
app/
├── main.py, config.py, database.py, dependencies.py
├── models/user.py          # SQLAlchemy ORM
├── schemas/user.py         # Pydantic v2 schemas
├── repositories/user.py    # Data access layer
├── services/auth.py, user.py
└── api/v1/auth.py, users.py, websocket.py
tests/conftest.py, test_users.py
```

## Config, Database, and App Factory
```python
# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    database_url: str = "postgresql+asyncpg://user:pass@localhost/mydb"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 30
    allowed_origins: list[str] = ["http://localhost:3000"]
@lru_cache
def get_settings() -> Settings:
    return Settings()

# app/database.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.config import get_settings
engine = create_async_engine(get_settings().database_url, pool_size=20, pool_pre_ping=True)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# app/main.py
from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config import get_settings
from app.database import engine
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await engine.dispose()
def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="My API", version="1.0.0", lifespan=lifespan)
    app.add_middleware(CORSMiddleware, allow_origins=settings.allowed_origins,
        allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
    from app.dependencies import limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    from app.api.router import api_router
    app.include_router(api_router, prefix="/api/v1")
    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}
    return app
app = create_app()
```

## SQLAlchemy Model and Pydantic Schemas
```python
# app/models/user.py
from datetime import datetime
from uuid import uuid4
from sqlalchemy import String, Boolean, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
class Base(DeclarativeBase):
    pass
class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

# app/schemas/user.py
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(min_length=8, max_length=128)
    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if not any(c.isupper() for c in v) or not any(c.isdigit() for c in v):
            raise ValueError("Must contain uppercase letter and digit")
        return v
class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(default=None, min_length=3, max_length=50)
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    username: str
    is_active: bool
    created_at: datetime
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
```

## Repository and Service Layer
```python
# app/repositories/user.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
    async def get_by_id(self, user_id: str) -> User | None:
        return await self.session.get(User, user_id)
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    async def list_users(self, *, skip: int = 0, limit: int = 20) -> list[User]:
        result = await self.session.execute(
            select(User).offset(skip).limit(limit).order_by(User.created_at.desc()))
        return list(result.scalars().all())
    async def create(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        await self.session.refresh(user)
        return user
    async def update(self, user: User, **kwargs: object) -> User:
        for k, v in kwargs.items():
            if v is not None: setattr(user, k, v)
        await self.session.flush()
        await self.session.refresh(user)
        return user

# app/services/user.py
from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.repositories.user import UserRepository
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self.repo = repo
    async def create_user(self, data: UserCreate) -> User:
        if await self.repo.get_by_email(data.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
        return await self.repo.create(User(email=data.email, username=data.username,
            hashed_password=pwd_context.hash(data.password)))
    async def authenticate(self, email: str, password: str) -> User:
        user = await self.repo.get_by_email(email)
        if not user or not pwd_context.verify(password, user.hashed_password):
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
        return user
    async def update_user(self, user_id: str, data: UserUpdate) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user: raise HTTPException(404, "User not found")
        return await self.repo.update(user, **data.model_dump(exclude_unset=True))
```

## Dependency Injection, JWT Auth, and Token Service
```python
# app/dependencies.py
from collections.abc import AsyncGenerator
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import Settings, get_settings
from app.database import AsyncSessionLocal
from app.repositories.user import UserRepository
from app.models.user import User
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
limiter = Limiter(key_func=get_remote_address)
async def get_db() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        async with session.begin(): yield session
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    settings: Annotated[Settings, Depends(get_settings)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id = payload.get("sub")
        if not user_id: raise JWTError()
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials",
                            headers={"WWW-Authenticate": "Bearer"})
    user = await UserRepository(session).get_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Inactive or missing user")
    return user
DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]

# app/services/auth.py
from datetime import datetime, timedelta, timezone
from jose import jwt as jose_jwt
from app.config import Settings
from app.schemas.user import TokenResponse
class AuthService:
    def __init__(self, settings: Settings) -> None:
        self.s = settings
    def create_tokens(self, user_id: str) -> TokenResponse:
        now = datetime.now(timezone.utc)
        access = jose_jwt.encode({"sub": user_id, "exp": now + timedelta(
            minutes=self.s.access_token_expire_minutes)}, self.s.secret_key, algorithm="HS256")
        refresh = jose_jwt.encode({"sub": user_id, "type": "refresh",
            "exp": now + timedelta(days=7)}, self.s.secret_key, algorithm="HS256")
        return TokenResponse(access_token=access, refresh_token=refresh)
```

## API Routes
```python
# app/api/v1/auth.py
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from app.config import Settings, get_settings
from app.dependencies import DbSession
from app.repositories.user import UserRepository
from app.services.user import UserService
from app.services.auth import AuthService
from app.schemas.user import TokenResponse, UserCreate, UserResponse
router = APIRouter(prefix="/auth", tags=["Auth"])
@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, session: DbSession):
    return UserResponse.model_validate(
        await UserService(UserRepository(session)).create_user(data))
@router.post("/login", response_model=TokenResponse)
async def login(form: Annotated[OAuth2PasswordRequestForm, Depends()],
                session: DbSession, settings: Annotated[Settings, Depends(get_settings)]):
    user = await UserService(UserRepository(session)).authenticate(form.username, form.password)
    return AuthService(settings).create_tokens(user.id)

# app/api/v1/users.py
from fastapi import APIRouter, Query, Request
from app.dependencies import DbSession, CurrentUser, limiter
from app.repositories.user import UserRepository
from app.services.user import UserService
from app.schemas.user import UserResponse, UserUpdate
router = APIRouter(prefix="/users", tags=["Users"])
@router.get("/me", response_model=UserResponse)
async def read_me(current_user: CurrentUser):
    return UserResponse.model_validate(current_user)
@router.get("/", response_model=list[UserResponse])
@limiter.limit("30/minute")
async def list_users(request: Request, session: DbSession,
                     skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
    return [UserResponse.model_validate(u)
            for u in await UserRepository(session).list_users(skip=skip, limit=limit)]
@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, data: UserUpdate, session: DbSession, _: CurrentUser):
    return UserResponse.model_validate(
        await UserService(UserRepository(session)).update_user(user_id, data))
```

## Middleware, WebSocket, Background Tasks, File Uploads
```python
# app/middleware.py - register via app.add_middleware(RequestTimingMiddleware)
import time, logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
logger = logging.getLogger(__name__)
class RequestTimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.perf_counter()
        response = await call_next(request)
        dur = time.perf_counter() - start
        response.headers["X-Process-Time"] = f"{dur:.4f}"
        if dur > 1.0: logger.warning("Slow: %s %s %.3fs", request.method, request.url.path, dur)
        return response

# WebSocket with room-based broadcasting
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from collections import defaultdict
class ConnectionManager:
    def __init__(self) -> None:
        self.rooms: dict[str, list[WebSocket]] = defaultdict(list)
    async def connect(self, ws: WebSocket, room: str) -> None:
        await ws.accept(); self.rooms[room].append(ws)
    def disconnect(self, ws: WebSocket, room: str) -> None:
        self.rooms[room].remove(ws)
    async def broadcast(self, room: str, msg: dict) -> None:
        for ws in self.rooms[room]: await ws.send_json(msg)
manager = ConnectionManager()
ws_router = APIRouter(tags=["WebSocket"])
@ws_router.websocket("/ws/{room}")
async def ws_endpoint(websocket: WebSocket, room: str) -> None:
    await manager.connect(websocket, room)
    try:
        while True: await manager.broadcast(room, await websocket.receive_json())
    except WebSocketDisconnect: manager.disconnect(websocket, room)

# Background tasks: inject BackgroundTasks, call bg.add_task(send_email, user.email)
# File uploads with type and size validation
from fastapi import UploadFile, File, HTTPException
import aiofiles
from pathlib import Path
ALLOWED = {"image/jpeg", "image/png", "application/pdf"}
async def upload_file(file: UploadFile = File(...)) -> dict[str, str]:
    if file.content_type not in ALLOWED: raise HTTPException(400, "Type not allowed")
    contents = await file.read()
    if len(contents) > 10 * 1024 * 1024: raise HTTPException(413, "Max 10MB")
    dest = Path("uploads") / file.filename
    dest.parent.mkdir(exist_ok=True)
    async with aiofiles.open(dest, "wb") as f: await f.write(contents)
    return {"filename": file.filename, "size": len(contents)}
```

## Testing with httpx and pytest
```python
# tests/conftest.py - Override get_db with in-memory SQLite for isolation
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import create_app
from app.dependencies import get_db
from app.models.user import Base
@pytest.fixture
async def client():
    engine = create_async_engine("sqlite+aiosqlite:///./test.db")
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        async with session.begin():
            app = create_app()
            app.dependency_overrides[get_db] = lambda: session
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                yield ac
    async with engine.begin() as conn: await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
# tests/test_users.py
@pytest.mark.anyio
async def test_register(client):
    r = await client.post("/api/v1/auth/register", json={
        "email": "alice@example.com", "username": "alice", "password": "Secure1234"})
    assert r.status_code == 201 and r.json()["email"] == "alice@example.com"
@pytest.mark.anyio
async def test_login_and_protected_route(client):
    await client.post("/api/v1/auth/register", json={
        "email": "bob@example.com", "username": "bob", "password": "Secure1234"})
    login = await client.post("/api/v1/auth/login",
        data={"username": "bob@example.com", "password": "Secure1234"})
    assert login.status_code == 200
    me = await client.get("/api/v1/users/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"})
    assert me.status_code == 200 and me.json()["username"] == "bob"
@pytest.mark.anyio
async def test_unauthenticated(client):
    assert (await client.get("/api/v1/users/me")).status_code == 401
```

## Deployment
```bash
# Local:   uvicorn app.main:app --reload --port 8000
# Prod:    gunicorn app.main:app -k uvicorn.workers.UvicornWorker -w 4 --timeout 120
# Migrate: alembic revision --autogenerate -m "init" && alembic upgrade head
# Docker:  FROM python:3.12-slim / COPY pyproject.toml . / RUN pip install . / COPY app/ app/
#          CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", "-w", "4"]
```

## Additional Resources
- FastAPI: https://fastapi.tiangolo.com/
- Pydantic v2: https://docs.pydantic.dev/latest/
- SQLAlchemy async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- slowapi: https://github.com/laurentS/slowapi
- httpx: https://www.python-httpx.org/
