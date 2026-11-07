from django.db import transaction
from rest_framework import permissions, status, viewsets
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from .context import current_membership
from .models import Membership, Organization, Store
from .serializers import EmployeeCreateSerializer, EmployeeSerializer, StoreSerializer


class OrganizationRoles(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        member = current_membership(request)
        allowed = {"owner", "manager"} if view.basename == "stores" else {"owner"}
        if request.method in permissions.SAFE_METHODS:
            return view.basename == "stores" or member.role in ("owner", "manager")
        return member.role in allowed


class StoreViewSet(viewsets.ModelViewSet):
    serializer_class = StoreSerializer
    permission_classes = [OrganizationRoles]
    http_method_names = ["get", "post", "patch", "head", "options"]
    basename = "stores"

    def get_queryset(self):
        return Store.objects.filter(organization=current_membership(self.request).organization).order_by("name")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = current_membership(self.request).organization
        return context

    def perform_create(self, serializer):
        serializer.save(organization=current_membership(self.request).organization)


class EmployeeViewSet(viewsets.GenericViewSet):
    permission_classes = [OrganizationRoles]
    http_method_names = ["get", "post", "patch", "head", "options"]
    basename = "employees"

    def get_queryset(self):
        return Membership.objects.select_related("user").filter(
            organization=current_membership(self.request).organization
        ).order_by("user__username")

    def get_serializer_class(self):
        return EmployeeCreateSerializer if self.action == "create" else EmployeeSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = current_membership(self.request).organization
        return context

    def list(self, request):
        return Response(EmployeeSerializer(self.get_queryset(), many=True).data)

    def create(self, request):
        serializer = EmployeeCreateSerializer(data=request.data, context=self.get_serializer_context())
        serializer.is_valid(raise_exception=True)
        member = serializer.save()
        return Response(EmployeeSerializer(member).data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    def partial_update(self, request, pk=None):
        if set(request.data) != {"role"}:
            raise ValidationError({"role": "Solo es posible modificar el rol."})
        new_role = request.data["role"]
        if new_role not in Membership.Role.values:
            raise ValidationError({"role": "Rol no válido."})
        org_id = current_membership(request).organization_id
        # Serialize role changes within the organization to prevent removing its final owner.
        Organization.objects.select_for_update().get(pk=org_id)
        member = self.get_object()
        if member.role == Membership.Role.OWNER and new_role != Membership.Role.OWNER:
            owners = Membership.objects.filter(organization_id=org_id, role=Membership.Role.OWNER).count()
            if owners <= 1:
                raise ValidationError({"role": "Debe existir al menos un propietario."})
        member.role = new_role
        member.save(update_fields=["role"])
        return Response(EmployeeSerializer(member).data)
