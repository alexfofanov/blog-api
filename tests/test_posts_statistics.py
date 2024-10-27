import pytest

from tests.conftest import URL_PREFIX_POST, USER_ID

AVG_POSTS_MONTH = 1


@pytest.mark.anyio
async def test_get_user_avg_posts_month(async_client, create_test_posts):
    response = await async_client.get(
        f'{URL_PREFIX_POST}/statistics/{USER_ID}'
    )
    assert response.status_code == 200
    assert response.json() == {'avg_posts_month': AVG_POSTS_MONTH}
