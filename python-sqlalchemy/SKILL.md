---
name: python-sqlalchemy
description: Python SQLAlchemy patterns covering ORM models, relationships, queries, sessions, migrations with Alembic, async support, and advanced query techniques.
---

# Python SQLAlchemy

This skill should be used when working with databases in Python using SQLAlchemy. It covers ORM models, relationships, queries, sessions, Alembic migrations, and async support.

## When to Use This Skill

Use this skill when you need to:

- Define database models with SQLAlchemy ORM
- Build complex queries with relationships and joins
- Manage database sessions and transactions
- Run migrations with Alembic
- Use async SQLAlchemy with FastAPI or other frameworks

## Setup

```bash
pip install sqlalchemy alembic psycopg2-binary
# For async: pip install sqlalchemy[asyncio] asyncpg
```

## Models

```python
from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    posts: Mapped[list["Post"]] = relationship(back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    published: Mapped[bool] = mapped_column(default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    author: Mapped["User"] = relationship(back_populates="posts")
    tags: Mapped[list["Tag"]] = relationship(secondary="post_tags", back_populates="posts")
```

## Engine and Session

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine("postgresql://user:pass@localhost/mydb", echo=True)
SessionLocal = sessionmaker(bind=engine)

# Create tables
Base.metadata.create_all(engine)

# Using sessions
with SessionLocal() as session:
    user = User(name="Alice", email="alice@example.com")
    session.add(user)
    session.commit()
    session.refresh(user)
    print(user.id)
```

## Queries

```python
from sqlalchemy import select, func, or_, and_

with SessionLocal() as session:
    # Get by ID
    user = session.get(User, 1)

    # Select with filter
    stmt = select(User).where(User.active == True).order_by(User.created_at.desc())
    users = session.scalars(stmt).all()

    # Pagination
    stmt = select(User).limit(10).offset(20)
    users = session.scalars(stmt).all()

    # Search
    stmt = select(User).where(
        or_(
            User.name.ilike(f"%alice%"),
            User.email.ilike(f"%alice%"),
        )
    )
    results = session.scalars(stmt).all()

    # Aggregation
    count = session.scalar(select(func.count()).select_from(User))

    # Join
    stmt = (
        select(Post, User)
        .join(User)
        .where(Post.published == True)
        .order_by(Post.created_at.desc())
    )
    results = session.execute(stmt).all()
```

## Relationships

```python
# One-to-many (User has many Posts)
user = session.get(User, 1)
for post in user.posts:
    print(post.title)

# Many-to-many
post_tags = Table(
    "post_tags", Base.metadata,
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    posts: Mapped[list["Post"]] = relationship(secondary="post_tags", back_populates="tags")
```

## Transactions

```python
with SessionLocal() as session:
    try:
        user = User(name="Bob", email="bob@example.com")
        session.add(user)
        session.flush()  # get user.id without committing

        post = Post(title="First Post", body="Content", user_id=user.id)
        session.add(post)
        session.commit()
    except Exception:
        session.rollback()
        raise
```

## Async SQLAlchemy

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/mydb")
async_session = async_sessionmaker(engine, class_=AsyncSession)

async def get_user(user_id: int) -> User:
    async with async_session() as session:
        stmt = select(User).where(User.id == user_id)
        result = await session.scalars(stmt)
        return result.first()

async def create_user(name: str, email: str) -> User:
    async with async_session() as session:
        user = User(name=name, email=email)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
```

## Alembic Migrations

```bash
alembic init migrations
alembic revision --autogenerate -m "create users table"
alembic upgrade head
alembic downgrade -1
```

## Additional Resources

- SQLAlchemy: https://docs.sqlalchemy.org/
- Alembic: https://alembic.sqlalchemy.org/
- Tutorial: https://docs.sqlalchemy.org/en/20/tutorial/
