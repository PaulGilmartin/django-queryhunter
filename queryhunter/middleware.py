from .context_manager import queryhunter


def QueryHunterMiddleware(get_response):
    def middleware(request):
        with queryhunter(url=request.path, method=request.method):
            return get_response(request)

    return middleware
