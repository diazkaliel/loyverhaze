import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST


def session_payload(request):
    user = request.user
    return {"authenticated": user.is_authenticated, "username": user.get_username() if user.is_authenticated else None,
            "is_staff": bool(user.is_authenticated and user.is_staff)}


@require_GET
@ensure_csrf_cookie
def session(request):
    return JsonResponse(session_payload(request))


@require_POST
@csrf_protect
def sign_in(request):
    try:
        data = json.loads(request.body)
    except (UnicodeDecodeError, json.JSONDecodeError):
        return JsonResponse({"detail": "JSON no válido."}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({"detail": "Solicitud no válida."}, status=400)
    username, password = data.get("username"), data.get("password")
    if not isinstance(username, str) or not isinstance(password, str) or not username or not password:
        return JsonResponse({"detail": "Usuario y contraseña son obligatorios."}, status=400)
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"detail": "Credenciales incorrectas."}, status=401)
    login(request, user)
    return JsonResponse(session_payload(request))


@require_POST
@csrf_protect
def sign_out(request):
    logout(request)
    return JsonResponse(session_payload(request))
