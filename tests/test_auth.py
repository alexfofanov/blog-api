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
ACCESS_TOKEN_EXPIRE_SECONDS = 1


@pytest.mark.anyio
async def test_auth_user_correct(async_client, create_test_user):
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/auth', json=TEST_USER
    )
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_auth_user_wrong_login(async_client, create_test_user):
    user_wrong_login = {
        'login': 'wrong_login',
        'password': TEST_USER['password'],
    }
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/auth', json=user_wrong_login
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_auth_user_wrong_password(async_client, create_test_user):
    user_wrong_password = {
        'login': TEST_USER['login'],
        'password': 'wrong_password',
    }
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/auth', json=user_wrong_password
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_access_protected_route_without_token(async_client):
    response = await async_client.get('/protected-route')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Not authenticated"}


@pytest.mark.anyio
async def test_access_protected_route_with_token(async_client, headers):
    response = await async_client.get('/protected-route', headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == SUCCESSFUL_ACCESS


@pytest.mark.anyio
async def test_access_with_invalid_token(async_client):
    invalid_token = "invalid_token"
    response = await async_client.get(
        "/protected-route",
        headers={"Authorization": f"Bearer {invalid_token}"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Invalid token"}


@pytest.mark.anyio
async def test_token_expiry(async_client, create_test_user):
    settings.access_token_expire_seconds = ACCESS_TOKEN_EXPIRE_SECONDS
    response = await async_client.post(
        f'{URL_PREFIX_AUTH}/auth', json=TEST_USER
    )
    token = response.json()
    headers = {'Authorization': f'Bearer {token["access_token"]}'}

    await asyncio.sleep(ACCESS_TOKEN_EXPIRE_SECONDS)

    response = await async_client.get('/protected-route', headers=headers)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Token expired'}
