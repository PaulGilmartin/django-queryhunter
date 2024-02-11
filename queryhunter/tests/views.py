# views.py

from django.http import JsonResponse

from queryhunter.tests.my_module import get_authors


def authors_view(request):
    authors = get_authors()
    return JsonResponse({'authors': authors})
