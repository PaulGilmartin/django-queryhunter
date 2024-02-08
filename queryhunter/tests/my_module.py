from queryhunter.tests.models import Post


def get_authors() -> None:
    authors = set()
    posts = Post.objects.all()
    for post in posts:
        authors.add(post.author.name)



