from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth import get_current_user
from src.db.postgres import get_session
from src.models import User
from src.repositories.post import post_crud
from src.schemas.post import PostCreate, PostInDB, PostUpdate
from src.services.avg_posts_per_month_for_user import (
    retrieve_avg_posts_per_month,
)

post_router = APIRouter()


@post_router.get(
    '/',
    response_model=list[PostInDB],
    summary='Получение постов',
    description='Возвращает список всех постов блога',
)
async def get_posts(
    *,
    db: AsyncSession = Depends(get_session),
    offset: int | None = None,
    limit: int | None = None,
) -> Any:
    """
    Получение списка всех постов блога
    """

    posts = await post_crud.get_multi(db=db, offset=offset, limit=limit)

    return posts


@post_router.get(
    '/{post_id}',
    response_model=PostInDB,
    summary='Получение поста',
    description='Возвращает пост по идентификатору',
)
async def get_post(
    post_id: int,
    *,
    db: AsyncSession = Depends(get_session),
) -> Any:
    """
    Получение поста по идентификатору
    """

    post = await post_crud.get(db=db, obj_id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post(id={post_id}) not found',
        )

    return post


@post_router.post(
    '/',
    response_model=PostInDB,
    summary='Создание поста',
    description='Создаёт пост в блоге',
)
async def create_post(
    *,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    post: PostCreate,
) -> Any:
    """
    Создание поста
    """
    post.user_id = user.id
    post = await post_crud.create(db=db, obj=post)

    return post


@post_router.delete(
    '/{post_id}',
    response_model=PostInDB,
    summary='Удаление поста',
    description='Удаляет пост в блоге',
)
async def delete_post(
    post_id: int,
    *,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    post: PostCreate,
) -> Any:
    """
    Удаление поста
    """

    post.user_id = user.id
    post = await post_crud.delete(db=db, obj_id=post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post(id={post_id}) not found',
        )

    return post


@post_router.patch(
    '/{post_id}',
    response_model=PostInDB,
    summary='Обновление поста',
    description='Обновляет содержимое поста в блоге',
)
async def update_post(
    post_id: int,
    *,
    db: AsyncSession = Depends(get_session),
    user: User = Depends(get_current_user),
    data: PostUpdate,
) -> Any:
    """
    Обновление содержимого поста
    """

    data.user_id = user.id
    post = await post_crud.patch(db=db, id=post_id, data=data)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post(id={post_id}) not found',
        )

    return post


@post_router.get(
    '/statistics/{user_id}',
    summary='Получение среднего количества постов пользователя за месяц',
    description='Возвращает среднее количества постов пользователя за месяц',
)
async def get_user_avg_posts_by_month(
    user_id: int,
    *,
    db: AsyncSession = Depends(get_session),
) -> dict[str, int]:
    """
    Получение среднего количества постов пользователя за месяц
    """

    avg_posts_per_month_for_user = await retrieve_avg_posts_per_month(
        db=db, user_id=user_id
    )

    return {'avg_posts_per_month_for_user': avg_posts_per_month_for_user}


@post_router.get(
    '/search/{search_str}',
    response_model=list[PostInDB],
    summary='Поиск постов по названию или содержанию',
    description='Возвращает посты отфильтрованные по названию или содержанию',
)
async def search_posts(
    search_str: str,
    *,
    db: AsyncSession = Depends(get_session),
    offset: int | None = None,
    limit: int | None = None,
) -> Any:
    """
    Получение списка постов отфильтрованных по названию или содержанию
    """

    posts = await post_crud.search_posts(
        db=db, search_str=search_str, offset=offset, limit=limit
    )

    return posts
