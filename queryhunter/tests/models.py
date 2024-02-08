from django.db import models


class Author(models.Model):
    name = models.TextField()


class Post(models.Model):
    content = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
