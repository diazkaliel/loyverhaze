from rest_framework.exceptions import PermissionDenied
from .models import Membership


def current_membership(request):
    """Resolve an active organization only from memberships, never a client-supplied unrestricted ID."""
    if not request.user.is_authenticated:
        raise PermissionDenied("Debes iniciar sesión.")
    memberships = Membership.objects.select_related("organization").filter(user=request.user).order_by("organization__created_at", "organization_id")
    selected_id = request.session.get("organization_id")
    membership = memberships.filter(organization_id=selected_id).first() if selected_id else None
    if membership is None:
        membership = memberships.first()
        if membership is not None:
            request.session["organization_id"] = str(membership.organization_id)
    if membership is None:
        raise PermissionDenied("No tienes una organización asignada.")
    return membership
