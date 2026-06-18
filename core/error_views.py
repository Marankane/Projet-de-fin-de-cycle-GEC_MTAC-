import logging

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


ERROR_MESSAGES = {
    400: "La requete envoyee est invalide.",
    403: "Vous n'avez pas les droits necessaires pour acceder a cette ressource.",
    404: "La page ou la ressource demandee est introuvable.",
    500: "Une erreur interne est survenue. Veuillez reessayer plus tard.",
}


def wants_json(request):
    accept = request.META.get("HTTP_ACCEPT", "")
    requested_with = request.META.get("HTTP_X_REQUESTED_WITH", "")
    return (
        request.path.startswith("/api/")
        or request.path.endswith("/api/process-document/")
        or "application/json" in accept
        or requested_with == "XMLHttpRequest"
    )


def json_error(request, status_code, message=None, extra=None):
    payload = {
        "success": False,
        "status_code": status_code,
        "error": message or ERROR_MESSAGES.get(status_code, ERROR_MESSAGES[500]),
    }
    if extra:
        payload.update(extra)
    return JsonResponse(payload, status=status_code)


def render_error(request, status_code, message=None, exception=None):
    message = message or ERROR_MESSAGES.get(status_code, ERROR_MESSAGES[500])
    if wants_json(request):
        return json_error(request, status_code, message)

    context = {
        "status_code": status_code,
        "message": message,
        "request_path": getattr(request, "path", ""),
        "show_details": settings.DEBUG,
        "exception": exception,
    }
    return render(request, "errors/error.html", context, status=status_code)


def bad_request(request, exception=None):
    logger.warning("400 Bad Request: %s (%s)", request.path, exception)
    return render_error(request, 400, exception=exception)


def permission_denied(request, exception=None):
    logger.warning("403 Permission denied: %s (%s)", request.path, exception)
    return render_error(request, 403, exception=exception)


def page_not_found(request, exception=None):
    logger.info("404 Not Found: %s (%s)", request.path, exception)
    return render_error(request, 404, exception=exception)


def server_error(request):
    logger.exception("500 Server Error: %s", getattr(request, "path", "unknown"))
    return render_error(request, 500)


def drf_exception_handler_with_json(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        request = context.get("request")
        logger.exception("Unhandled API exception on %s", getattr(request, "path", "unknown"))
        return JsonResponse(
            {"success": False, "status_code": 500, "error": ERROR_MESSAGES[500]},
            status=500,
        )

    detail = response.data.get("detail") if isinstance(response.data, dict) else None
    response.data = {
        "success": False,
        "status_code": response.status_code,
        "error": detail or ERROR_MESSAGES.get(response.status_code, "Erreur API."),
        "details": response.data,
    }
    return response

