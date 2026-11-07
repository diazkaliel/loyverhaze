import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from .models import Membership


@require_POST
@csrf_protect
def choose_organization(request):
    if not request.user.is_authenticated:
        return JsonResponse({"detail": "Debes iniciar sesión."}, status=401)
    try:
        data = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"detail": "JSON no válido."}, status=400)
    if not isinstance(data, dict) or not isinstance(data.get("organization_id"), str):
        return JsonResponse({"detail": "Indica organization_id."}, status=400)
    membership = Membership.objects.filter(user=request.user, organization_id=data["organization_id"]).first()
    if membership is None:
        return JsonResponse({"detail": "Organización no disponible."}, status=403)
    request.session["organization_id"] = str(membership.organization_id)
    return JsonResponse({"organization_id": str(membership.organization_id)})
