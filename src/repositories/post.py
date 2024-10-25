from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.post import Post as PostModel
from src.schemas.post import PostCreate, PostUpdate

from .base import RepositoryDB, ModelType


class RepositoryPost(RepositoryDB[PostModel, PostCreate, PostUpdate]):
    async def get_avg_posts_per_month_for_user(
        self, db: AsyncSession, user_id: int
    ) -> int:
        """
        Получение среднего количества постов пользователя за месяц
        """

        monthly_counts = (
            select(func.count(self._model.id).label('post_count'))
            .where(self._model.user_id == user_id)
            .group_by(
                extract('year', self._model.created_at),
                extract('month', self._model.created_at),
            )
            .subquery()
        )
        stmt = select(
            func.avg(monthly_counts.c.post_count).label('avg_posts_per_month')
        )
        result = await db.execute(statement=stmt)

        return int(result.scalar())

    async def search_posts(
        self, db: AsyncSession, *, search_str: str, offset: int, limit: int
    ) ->list[ModelType]:
        """
        Поиск постов по названию или содержанию
        """

        stmt = (
            select(self._model)
            .where(
                self._model.title.ilike(f'%{search_str}%')
                | self._model.content.ilike(f'%{search_str}%')
            )
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(statement=stmt)

        return result.scalars().all()


post_crud = RepositoryPost(PostModel)
