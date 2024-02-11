from .context_manager import query_hunter


def QueryHunterMiddleware(get_response):
    def middleware(request):
        with query_hunter(url=request.path, method=request.method):
            return get_response(request)

    return middleware
