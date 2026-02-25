---
name: fastapi-python
description: FastAPI Python web framework covering async endpoints, Pydantic models, dependency injection, OAuth2 authentication, WebSocket support, background tasks, middleware, and OpenAPI documentation.
---

# FastAPI Python

This skill should be used when building Python web APIs with FastAPI. It covers async endpoints, Pydantic validation, dependency injection, authentication, and production deployment.

## When to Use This Skill

Use this skill when you need to:

- Build high-performance Python APIs with async support
- Define request/response models with Pydantic
- Implement dependency injection patterns
- Add OAuth2 or JWT authentication
- Generate automatic OpenAPI documentation

## Basic Application

```python
# main.py
from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from datetime import datetime

app = FastAPI(title="My API", version="1.0.0")

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    description: str | None = None

class ItemResponse(BaseModel):
    id: int
    name: str
    price: float
    description: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

items_db: dict[int, dict] = {}
counter = 0

@app.post("/items", response_model=ItemResponse, status_code=201)
async def create_item(item: ItemCreate):
    global counter
    counter += 1
    db_item = {
        "id": counter,
        **item.model_dump(),
        "created_at": datetime.now(),
    }
    items_db[counter] = db_item
    return db_item

@app.get("/items", response_model=list[ItemResponse])
async def list_items(skip: int = Query(0, ge=0), limit: int = Query(20, le=100)):
    return list(items_db.values())[skip : skip + limit]

@app.get("/items/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int):
    if item_id not in items_db:
        raise HTTPException(status_code=404, detail="Item not found")
    return items_db[item_id]
```

## Dependency Injection

```python
from fastapi import Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/db")
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_current_user(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user = await verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@app.get("/profile")
async def get_profile(
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await db.get(User, user.id)
```

## OAuth2 with JWT

```python
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict) -> str:
    encoded = jwt.encode(
        {**data, "exp": datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm="HS256",
    )
    return encoded

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return await get_user(username)
```

## WebSockets

```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active: list[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, message: str):
        for conn in self.active:
            await conn.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{room}")
async def websocket_endpoint(ws: WebSocket, room: str):
    await manager.connect(ws)
    try:
        while True:
            data = await ws.receive_text()
            await manager.broadcast(f"{room}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(ws)
```

## Background Tasks

```python
from fastapi import BackgroundTasks

async def send_notification(email: str, message: str):
    # Simulate sending email
    await asyncio.sleep(2)
    print(f"Sent to {email}: {message}")

@app.post("/orders")
async def create_order(order: OrderCreate, background_tasks: BackgroundTasks):
    result = await process_order(order)
    background_tasks.add_task(send_notification, order.email, f"Order {result.id} confirmed")
    return result
```

## Middleware

```python
from fastapi.middleware.cors import CORSMiddleware
import time

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_timing_header(request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - start
    response.headers["X-Process-Time"] = str(duration)
    return response
```

## Additional Resources

- FastAPI docs: https://fastapi.tiangolo.com/
- Pydantic v2: https://docs.pydantic.dev/latest/
- SQLAlchemy async: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
