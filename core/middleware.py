from django.conf import settings
from django.http import HttpResponse


class PublicCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'OPTIONS' and request.path.startswith('/api/'):
            response = HttpResponse(status=204)
        else:
            response = self.get_response(request)

        if not request.path.startswith('/api/'):
            return response

        origin = request.headers.get('Origin')
        allowed_origin = None

        if settings.CORS_ALLOW_ALL_ORIGINS:
            allowed_origin = '*'
        elif origin and origin in settings.CORS_ALLOWED_ORIGINS:
            allowed_origin = origin

        if allowed_origin:
            response['Access-Control-Allow-Origin'] = allowed_origin
            response['Vary'] = 'Origin'

        response['Access-Control-Allow-Headers'] = ', '.join(settings.CORS_ALLOW_HEADERS)
        response['Access-Control-Allow-Methods'] = ', '.join(settings.CORS_ALLOW_METHODS)
        response['Access-Control-Max-Age'] = '86400'
        return response
