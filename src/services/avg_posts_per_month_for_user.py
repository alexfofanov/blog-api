from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.post import post_crud
from src.repositories.user import user_crud


async def retrieve_avg_posts_per_month(db: AsyncSession, user_id: int):
    """
    Получение среднего количества постов пользователя за месяц
    """

    user = await user_crud.get(db=db, obj_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'User(id={user_id}) not found',
        )
    avg_posts = await post_crud.get_avg_posts_per_month_for_user(
        db=db, user_id=user_id
    )

    return avg_posts
