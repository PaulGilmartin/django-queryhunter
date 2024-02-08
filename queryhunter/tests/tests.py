from pprint import pprint

import pytest
from django.db import connection

from queryhunter.queryhunter import QueryHunter, query_hunter
from queryhunter.tests.models import Author, Post
from queryhunter.tests.my_module import get_authors


@pytest.mark.django_db(transaction=True)
def test_queryhunter():
    author = Author.objects.create(name='Billy')
    for i in range(5):
        Post.objects.create(content=f'content {i}', author=author)
    with query_hunter():
        get_authors()
