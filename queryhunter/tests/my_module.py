from queryhunter.tests.models import Post, Author


def get_authors() -> list[Author]:
    authors = []
    posts = Post.objects.all()
    for post in posts:
        authors.append(post.author.name)
    return authors




