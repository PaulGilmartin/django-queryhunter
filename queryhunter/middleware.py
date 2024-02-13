from .context_manager import queryhunter


def QueryHunterMiddleware(get_response):
    def middleware(request):
        with queryhunter(meta_data=dict(url=request.path, method=request.method)):
            return get_response(request)

    return middleware
