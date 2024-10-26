import asyncio

import pytest
from fastapi import status

from src.core.config import settings

from .conftest import (
    SUCCESSFUL_ACCESS,
    TEST_USER,
    URL_PREFIX_AUTH,
    URL_PREFIX_POST,
)

PROTECTED_ROUTE = f'{URL_PREFIX_POST}/'


@pytest.mark.anyio
async def test_add_user(async_client):
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/register', json=TEST_USER
    )
    assert response.status_code == status.HTTP_201_CREATED
    user = response.json()
    assert user == {'id': 1, 'login': TEST_USER['login']}


@pytest.mark.anyio
async def test_add_user_exist(async_client):
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/register', json=TEST_USER
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.anyio
async def test_auth_user_correct(async_client):
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/auth', json=TEST_USER
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_auth_user_wrong_login(async_client):
    TEST_USER['login'] = 'wrong_login'
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/auth', json=TEST_USER
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_auth_user_wrong_password(async_client):
    TEST_USER['password'] = 'wrong_password'
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/auth', json=TEST_USER
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_access_protected_route_without_token(async_client):
    response = await async_client.get('/protected-route')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


async def test_access_protected_route_with_token(async_client, headers):
    response = async_client.get("/protected-route", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == SUCCESSFUL_ACCESS


async def test_token_expiry(async_client):
    settings.access_token_expire_seconds = 1
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/auth', json=TEST_USER
    )
    token = response.json()
    headers = {'Authorization': f'Bearer {token["access_token"]}'}

    await asyncio.sleep(1)

    response = await async_client.get("/protected-route", headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Token expired"}


async def test_access_with_invalid_token(async_client):
    invalid_token = "invalid_token"
    response = await async_client.get(
        "/protected-route",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}
