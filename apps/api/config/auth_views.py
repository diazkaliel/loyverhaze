import json

from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST
from modules.organization.models import Membership


def session_payload(request):
    user = request.user
    if not user.is_authenticated:
        return {"authenticated": False, "username": None, "is_staff": False, "organizations": [], "active_organization_id": None}
    memberships = list(Membership.objects.select_related("organization").filter(user=user).order_by("organization__created_at"))
    selected_id = request.session.get("organization_id")
    active = next((m for m in memberships if str(m.organization_id) == selected_id), None)
    if active is None and memberships:
        active = memberships[0]
        request.session["organization_id"] = str(active.organization_id)
    return {
        "authenticated": True,
        "username": user.get_username(),
        "is_staff": bool(active and active.role in ("owner", "manager")),
        "organizations": [{"id": str(m.organization_id), "name": m.organization.name, "role": m.role} for m in memberships],
        "active_organization_id": str(active.organization_id) if active else None,
    }


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
