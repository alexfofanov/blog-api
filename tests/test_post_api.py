import pytest
from fastapi import status

from src.repositories.post import post_crud
from src.schemas.post import PostCreate
from tests.conftest import MAX_NUM_POSTS, URL_PREFIX_POST, posts_data, USER_ID

POST_ID = 1
NEW_POST = {'title': 'Новый заголовок', 'content': 'Новый текст'}


@pytest.mark.anyio
async def test_get_posts_empty(async_client):
    response = await async_client.get(f'{URL_PREFIX_POST}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []


@pytest.mark.anyio
async def test_get_posts(async_client, create_test_posts, posts_data):
    response = await async_client.get(f'{URL_PREFIX_POST}/')
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == MAX_NUM_POSTS
    for post, i in zip(response.json(), range(MAX_NUM_POSTS)):
        assert post['title'] == posts_data[i]['title']


@pytest.mark.anyio
async def test_get_post_by_id(async_client, create_test_posts, posts_data):
    response = await async_client.get(f'{URL_PREFIX_POST}/{POST_ID}')
    assert response.status_code == status.HTTP_200_OK
    post = response.json()
    assert post['id'] == POST_ID
    assert post['title'] == posts_data[0]['title']


@pytest.mark.anyio
async def test_get_post_not_found(async_client, create_test_posts):
    response = await async_client.get(f'{URL_PREFIX_POST}/{MAX_NUM_POSTS + 1}')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        'detail': f'Post(id={MAX_NUM_POSTS + 1}) not found'
    }


@pytest.mark.anyio
async def test_create_post(async_client, create_test_posts, headers):
    response = await async_client.post(
        f'{URL_PREFIX_POST}/', json=NEW_POST, headers=headers
    )
    assert response.status_code == status.HTTP_201_CREATED
    post = response.json()
    assert post['id'] == MAX_NUM_POSTS + 1
    assert post['title'] == NEW_POST['title']
    assert post['content'] == NEW_POST['content']


@pytest.mark.anyio
async def test_delete_post(async_client, headers, db_session):
    post = PostCreate(
        user_id=USER_ID,
        title='Пост для проверки удаления',
        content='Текст поста для проверки удаления',
    )
    create_post = await post_crud.create(db=db_session, obj=post)
    response = await async_client.delete(
        f'{URL_PREFIX_POST}/{create_post.id}', headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == create_post.id

    deleted_post = await post_crud.get(db=db_session, obj_id=create_post.id)
    assert deleted_post is None


@pytest.mark.anyio
async def test_update_post(async_client, headers, db_session):
    post = PostCreate(
        user_id=USER_ID, title='Старый заголовок', content='Старый текст поста'
    )
    create_post = await post_crud.create(db=db_session, obj=post)
    update_data = {
        'title': 'Изменённый заголовок',
        'content': 'Изменённый текст поста',
    }
    response = await async_client.patch(
        f'{URL_PREFIX_POST}/{create_post.id}',
        json=update_data,
        headers=headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['title'] == update_data['title']
    assert response.json()['content'] == update_data['content']


@pytest.mark.anyio
async def test_search_posts(async_client, create_test_posts, posts_data):
    response = await async_client.get(
        f'{URL_PREFIX_POST}/search/{str(MAX_NUM_POSTS)}'
    )
    assert response.status_code == status.HTTP_200_OK
    assert (
        response.json()[0]['title'] == posts_data[MAX_NUM_POSTS - 1]['title']
    )
