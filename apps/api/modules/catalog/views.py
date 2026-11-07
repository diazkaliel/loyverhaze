from rest_framework import permissions, viewsets
from modules.organization.context import current_membership
from .models import Category, Item
from .serializers import CategorySerializer, ItemSerializer


class OrganizationPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        membership = current_membership(request)
        return request.method in permissions.SAFE_METHODS or membership.role in ("owner", "manager")


class ScopedCatalogViewSet(viewsets.ModelViewSet):
    permission_classes = [OrganizationPermission]

    def get_queryset(self):
        return super().get_queryset().filter(organization_id=current_membership(self.request).organization_id)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["organization"] = current_membership(self.request).organization
        return context

    def perform_create(self, serializer):
        serializer.save(organization=current_membership(self.request).organization)


class CategoryViewSet(ScopedCatalogViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ItemViewSet(ScopedCatalogViewSet):
    queryset = Item.objects.select_related("category").all()
    serializer_class = ItemSerializer
