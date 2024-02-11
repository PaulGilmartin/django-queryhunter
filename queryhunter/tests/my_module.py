from queryhunter.tests.models import Post, Author


def create_posts():
    author = Author.objects.create(name='Billy')
    for i in range(5):
        Post.objects.create(content=f'content {i}', author=author)


def get_authors() -> list[Author]:
    authors = []
    posts = Post.objects.all()
    for post in posts:
        authors.append(post.author.name)
    return authors



