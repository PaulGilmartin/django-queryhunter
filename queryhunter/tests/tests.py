import pytest

from queryhunter.queryhunter import query_hunter
from queryhunter.tests.models import Author, Post
from queryhunter.tests.my_module import get_authors


@pytest.mark.django_db(transaction=True)
def test_queryhunter():
    author = Author.objects.create(name='Billy')
    for i in range(5):
        Post.objects.create(content=f'content {i}', author=author)
    with query_hunter() as qh:
        get_authors()
    query_info = qh.query_info
    assert len(query_info) == 1
    file_data = query_info['django-queryhunter/queryhunter/tests/my_module.py']
    assert len(file_data.line_data) == 2

    first_line = file_data.line_data[7]
    assert first_line.line_no == 7
    assert first_line.count == 1
    assert first_line.duration > 0
    assert first_line.sql == (
        'SELECT "tests_post"."id", "tests_post"."content", "tests_post"."author_id" FROM "tests_post"'
    )
    assert first_line.code == 'for post in posts:'

    second_line = file_data.line_data[8]
    assert second_line.line_no == 8
    assert second_line.count == 5
    assert second_line.duration > 0
    assert second_line.code == 'authors.add(post.author.name)'
