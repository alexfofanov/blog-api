from datetime import UTC, datetime, timedelta

import asyncpg
import pytest
from fastapi import Depends
from httpx import ASGITransport, AsyncClient
from sqlalchemy import NullPool, insert
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.core.auth import get_current_user, hash_password
from src.core.config import settings
from src.db.postgres import get_session
from src.main import app
from src.models import Base, Post, User

URL_PREFIX_AUTH = '/api/v1/users'
URL_PREFIX_POST = '/api/v1/posts'
TEST_USER = {'login': 'test_user', 'password': 'password'}
SUCCESSFUL_ACCESS = {"message": "Access granted"}
MAX_NUM_POSTS = 10
USER_ID = 1


@pytest.fixture(scope='session')
def anyio_backend():
    return 'asyncio'


@pytest.fixture(scope='session')
async def create_test_database():
    conn = await asyncpg.connect(
        settings.dsn.replace('postgresql+asyncpg', 'postgresql')
    )

    await conn.execute(f'DROP DATABASE IF EXISTS {settings.postgres_test_db}')
    await conn.execute(f'CREATE DATABASE {settings.postgres_test_db}')
    await conn.close()

    yield

    conn = await asyncpg.connect(
        settings.dsn.replace('postgresql+asyncpg', 'postgresql')
    )
    await conn.execute(f'DROP DATABASE IF EXISTS {settings.postgres_test_db}')
    await conn.close()


@pytest.fixture(scope='module')
async def db_engine(create_test_database):
    engine = create_async_engine(
        settings.dsn_test, echo=False, future=True, poolclass=NullPool
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture(scope='module')
async def db_session_factory(db_engine):
    return async_sessionmaker(
        bind=db_engine, class_=AsyncSession, expire_on_commit=False
    )


@pytest.fixture(scope='module')
async def db_session(db_session_factory):
    async with db_session_factory() as session:
        yield session


@pytest.fixture(scope='module')
async def async_client(db_session_factory):
    async def override_get_session():
        async with db_session_factory() as session:
            yield session

    app.dependency_overrides[get_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac


@pytest.fixture(scope='module')
async def create_test_user(db_session):
    stmt = insert(User).values(
        login=TEST_USER['login'],
        password=hash_password(TEST_USER['password']),
    )
    await db_session.execute(stmt)
    await db_session.commit()


@pytest.fixture(scope='module')
async def headers(create_test_user):
    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url='http://test'
    ) as async_client:
        response = await async_client.post(
            f'{URL_PREFIX_AUTH}/auth', json=TEST_USER
        )
        token = response.json()
        headers = {'Authorization': f'Bearer {token["access_token"]}'}
        return headers


@pytest.fixture(scope='module')
def posts_data():
    data = []
    day_offset = 10
    current_time = datetime.now(UTC).replace(tzinfo=None)
    for i in range(1, MAX_NUM_POSTS + 1):
        data.append(
            {
                'user_id': 1,
                'title': f'Заголовок сообщения #{i}',
                'content': f'Текст сообщения #{i}',
                'created_at': current_time - timedelta(days=day_offset),
            }
        )
        day_offset += 30
    return data


@pytest.fixture(scope='module')
async def create_test_posts(db_session, posts_data, create_test_user):
    stmt = insert(Post).values(posts_data)
    await db_session.execute(stmt)
    await db_session.commit()


@app.get('/protected-route')
async def ping(user: User = Depends(get_current_user)) -> dict:
    return SUCCESSFUL_ACCESS
