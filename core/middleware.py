import logging

from django.conf import settings
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404

from .error_views import ERROR_MESSAGES, json_error, render_error, wants_json

logger = logging.getLogger(__name__)


class RobustExceptionMiddleware:
    """Return consistent error responses for unexpected runtime exceptions."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, (Http404, PermissionDenied, SuspiciousOperation)):
            return None

        logger.exception("Unhandled exception on %s", request.path)

        if wants_json(request):
            return json_error(request, 500, ERROR_MESSAGES[500])

        if settings.DEBUG:
            return None

        return render_error(request, 500, exception=exception)
