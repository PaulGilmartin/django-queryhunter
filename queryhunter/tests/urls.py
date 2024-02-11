from django.urls import path
from .views import authors_view

urlpatterns = [
    path('authors/', authors_view, name='authors'),
]
